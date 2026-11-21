"""Locate City score gaps and build auditable missing-data analysis scenarios."""
from pathlib import Path
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["current_speed", "unimproved_load", "current_max_load", "current_ridership", "competitiveness"]


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def source_statistics(rows):
    result = {}
    for field in FIELDS:
        observed = [float(r[field]) for r in rows if r[field] != ""]
        if not observed or not all(math.isfinite(v) for v in observed):
            raise ValueError("Each scenario needs at least one finite observed value per column")
        result[field] = {"observed_count": len(observed), "missing_count": len(rows) - len(observed),
                         "observed_minimum": min(observed), "observed_mean": statistics.fmean(observed)}
    return result


def scenario_rows(rows, method):
    stats = source_statistics(rows)
    statistic = {"imputed_conservative_min": "observed_minimum", "imputed_observed_mean": "observed_mean"}[method]
    result, trace = [], []
    for source in rows:
        missing = [field for field in FIELDS if source[field] == ""]
        record = {"corridor_id": source["corridor_id"]}
        for field in FIELDS:
            record[field] = source[field] if source[field] != "" else stats[field][statistic]
        for field in FIELDS:
            record[field + "_value_status"] = "source_observed" if source[field] != "" else method
        record.update(imputed_indicator_ids=";".join(missing), scenario_method=method,
                      source_id="CITY2024_ATTACHMENT;CITY_MISSING_POLICY_V04",
                      notes=(method + ": scenario substitutions in " + ";".join(missing)) if missing else "All five published source values retained.")
        result.append(record)
        for field in missing:
            trace.append({"corridor_id": source["corridor_id"], "indicator_id": field,
                          "source_value": "", "source_status": "published_missing",
                          "analysis_value": stats[field][statistic], "analysis_value_status": method,
                          "statistic_observed_n": stats[field]["observed_count"],
                          "is_observed_or_theoretical_bound": False})
    return result, trace


def competition_ranks(scores):
    return {cid: 1 + sum(value > score + 1e-12 for value in scores.values()) for cid, score in scores.items()}


def analyze(root=ROOT, output=None, data_output=None):
    root = Path(root)
    output = Path(output) if output else root / "outputs/missingness_v0.4"
    output.mkdir(parents=True, exist_ok=True)
    data_output = Path(data_output) if data_output else root / "data"
    data_output.mkdir(parents=True, exist_ok=True)
    source_path = root / "data/city_standardized_scores_v0.1.csv"
    rows = read_csv(source_path)
    if len(rows) != 24 or {r["corridor_id"] for r in rows} != {str(i) for i in range(1, 25)}:
        raise ValueError("All 24 source alternatives must be retained uniquely")
    master = {r["corridor_id"]: r for r in read_csv(root / "data/corridor_master_v0.1.csv")}
    stats = source_statistics(rows)
    by_corridor = []
    missing_cells = []
    for row in rows:
        cid = row["corridor_id"]
        missing = [field for field in FIELDS if row[field] == ""]
        record = {"corridor_id": cid, "corridor_name": master[cid]["corridor_name"],
                  "missing_count": len(missing), "missing_indicator_ids": ";".join(missing),
                  "prerequisite_corridor_ids": master[cid]["prerequisite_corridor_ids"]}
        for field in FIELDS:
            record[field + "_missing"] = row[field] == ""
            if row[field] == "":
                missing_cells.append({"corridor_id": cid, "corridor_name": master[cid]["corridor_name"],
                                      "indicator_id": field, "source_value": "", "status": "published_missing"})
        by_corridor.append(record)
    write_csv(output / "by_corridor.csv", by_corridor)
    write_csv(output / "by_indicator.csv", [{"indicator_id": field, **stats[field]} for field in FIELDS])
    write_csv(output / "missing_source_cells.csv", missing_cells)
    scenarios = {}
    all_trace = []
    for method, filename in [("imputed_conservative_min", "city_analysis_inputs_v0.4.csv"),
                             ("imputed_observed_mean", "city_mean_sensitivity_v0.4.csv")]:
        values, trace = scenario_rows(rows, method)
        scenarios[method] = values
        all_trace.extend(trace)
        write_csv(data_output / filename, values)
    write_csv(output / "imputation_trace.csv", all_trace)
    scores = {method: {r["corridor_id"]: statistics.fmean(float(r[field]) for field in FIELDS) for r in values}
              for method, values in scenarios.items()}
    dynamic_weights = []
    scores["available_case_dynamic_weights"] = {}
    for row in rows:
        available = [field for field in FIELDS if row[field] != ""]
        if not available:
            raise ValueError("No observed criterion available for a dynamic-weight diagnostic")
        cid = row["corridor_id"]
        scores["available_case_dynamic_weights"][cid] = statistics.fmean(float(row[field]) for field in available)
        dynamic_weights.append({"corridor_id": cid, **{field + "_effective_weight": 1 / len(available) if field in available else 0 for field in FIELDS}})
    write_csv(output / "dynamic_effective_weights.csv", dynamic_weights)
    ranks = {method: competition_ranks(values) for method, values in scores.items()}
    diagnostic = []
    for source in rows:
        cid = source["corridor_id"]
        record = {"corridor_id": cid, "corridor_name": master[cid]["corridor_name"],
                  "source_missing_count": sum(source[f] == "" for f in FIELDS)}
        for method in scores:
            record[method + "_score"] = scores[method][cid]
            record[method + "_rank"] = ranks[method][cid]
        diagnostic.append(record)
    write_csv(output / "equal_weight_policy_diagnostic.csv", diagnostic)
    top3 = {method: sorted([cid for cid, rank in values.items() if rank <= 3], key=int) for method, values in ranks.items()}
    max_shift = {method: max(abs(ranks[method][cid] - ranks["imputed_conservative_min"][cid]) for cid in ranks[method])
                 for method in ["imputed_observed_mean", "available_case_dynamic_weights"]}
    source_counts = Counter(r["missing_count"] for r in by_corridor)
    summary = {"source_file": str(source_path.relative_to(root)), "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
               "policy_file": "data/missing_data_policy_v0.4.json", "pattern": "B_concentrated_corridors_repeated_column_patterns",
               "observed_values": sum(stats[f]["observed_count"] for f in FIELDS), "missing_values": len(missing_cells),
               "missing_corridor_ids": [r["corridor_id"] for r in by_corridor if r["missing_count"]],
               "row_missing_count_distribution": dict(sorted(source_counts.items())),
               "column_statistics": stats, "top3_or_tied_top3_by_policy": top3,
               "maximum_rank_change_from_observed_minimum": max_shift,
               "diagnostic_scope": "Five City columns; equal weights; missing-policy comparison only. No equity or final recommendation.",
               "observed_minimum_is_theoretical_lower_bound": False,
               "random_missingness_assumed": False, "all_24_alternatives_retained": True,
               "raw_source_overwritten": False, "model_readiness_established": False}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    args = parser.parse_args()
    analyze(args.project)
