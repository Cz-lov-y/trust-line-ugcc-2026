"""Validate the evidence inventory without imputing, ranking, or dropping corridors."""
from pathlib import Path
import argparse, csv, json, math, sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IDS = {str(i) for i in range(1, 25)}
CITY_NON_COST_FIELDS = {"current_speed", "unimproved_load", "current_max_load", "current_ridership", "competitiveness"}

def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)

def validate(root=ROOT):
    root = Path(root)
    errors, warnings = [], []
    fields, rows = read_csv(root / "data/corridor_master_v0.1.csv")
    required = {"corridor_id", "corridor_name", "endpoint_a", "endpoint_b", "length_km", "source_id", "notes"}
    if not required.issubset(fields): errors.append("Missing master fields: " + str(sorted(required-set(fields))))
    ids = [r.get("corridor_id", "") for r in rows]
    if len(rows) != 24 or set(ids) != EXPECTED_IDS or len(set(ids)) != 24:
        errors.append("The master must retain exactly one row for each corridor ID 1 through 24.")
    indicator_fields = [c for c in fields if c.startswith("indicator_")]
    if not indicator_fields: warnings.append("No candidate indicator columns have been added yet.")
    for r in rows:
        for key in ["length_km", *indicator_fields]:
            value = r.get(key, "")
            if value == "": continue
            try:
                number = float(value)
                if not math.isfinite(number): raise ValueError()
                if key == "length_km" and number <= 0: raise ValueError()
            except ValueError: errors.append(f"Corridor {r.get('corridor_id')}: invalid numeric {key}={value!r}")
        if not r.get("corridor_name") or not r.get("endpoint_a") or not r.get("endpoint_b"):
            warnings.append(f"Corridor {r.get('corridor_id')}: metadata not yet complete.")
    _, sources = read_csv(root / "data/source_log_v0.1.csv")
    source_ids = {s["source_id"] for s in sources}
    if len(source_ids) != len(sources): errors.append("Duplicate source IDs.")
    for r in rows:
        for sid in r.get("source_id", "").split(";"):
            if sid.strip() and sid.strip() not in source_ids: errors.append(f"Unknown master source ID {sid!r}")
    observation_path = root / "data/indicator_observations_v0.1.csv"
    if observation_path.exists():
        _, observations = read_csv(observation_path)
        observed_keys = set()
        master_by_id = {r["corridor_id"]: r for r in rows}
        for o in observations:
            key = (o["corridor_id"], o["indicator_id"])
            if key in observed_keys: errors.append(f"Duplicate observation: {key}")
            observed_keys.add(key)
            if o["corridor_id"] not in EXPECTED_IDS: errors.append(f"Unknown observation corridor: {key}")
            col = "indicator_" + o["indicator_id"]
            if col not in fields: errors.append(f"Observation without master column: {col}")
            value = o.get("value", "")
            if value == "" and not o.get("value_status"): errors.append(f"Missing value lacks status: {key}")
            if value != "":
                try:
                    if not math.isfinite(float(value)): raise ValueError()
                except ValueError: errors.append(f"Invalid observation value: {key}")
            mvalue = master_by_id.get(o["corridor_id"], {}).get(col, "")
            if value != mvalue:
                try: equal = value != "" and mvalue != "" and float(value) == float(mvalue)
                except ValueError: equal = False
                if not equal: errors.append(f"Observation/master disagreement: {key}")
            for sid in o.get("source_id", "").split(";"):
                if sid.strip() and sid.strip() not in source_ids: errors.append(f"Unknown observation source: {sid}")
        expected = {(i, c.removeprefix("indicator_")) for i in EXPECTED_IDS for c in indicator_fields}
        if observed_keys != expected: errors.append(f"Observation grid incomplete: expected {len(expected)}, found {len(observed_keys)} keys.")
    readiness_issues = []
    admitted_ids = []
    input_cache = {}
    selection_path = root / "data/model_input_selection_v0.1.json"
    selected_ids = json.loads(selection_path.read_text(encoding="utf-8")).get("selected_indicator_ids", []) if selection_path.exists() else []
    records_path = root / "data/workbook_records_v0.1.json"
    if records_path.exists():
        records = json.loads(records_path.read_text(encoding="utf-8"))
        dictionary = records.get("data_dictionary", [])
        admissions = records.get("indicator_admission", [])
        admission_by_id = {a["indicator_id"]: a for a in admissions}
        for selected in selected_ids:
            if admission_by_id.get(selected, {}).get("admission_status", "").lower() != "admitted":
                readiness_issues.append(f"{selected}: selected model input is not admitted")
        for a in admissions:
            if a.get("input_file"):
                rel = a["input_file"]
                resolved = (root / rel).resolve()
                if not resolved.is_relative_to(root.resolve()):
                    errors.append(f"Input path escapes project: {rel}")
                    continue
                if rel not in input_cache:
                    if not resolved.exists():
                        errors.append(f"Missing input dataset: {rel}")
                        input_cache[rel] = ({}, [])
                    else:
                        ff, rr = read_csv(resolved)
                        input_cache[rel] = ({r.get("corridor_id", ""):r for r in rr}, ff)
                        if len(rr) != 24 or {r.get("corridor_id") for r in rr} != EXPECTED_IDS:
                            errors.append(f"{rel}: input must retain exactly 24 unique corridor IDs")
                by_id, ff = input_cache[rel]
                col = a.get("input_column", a["indicator_id"])
                if col not in ff:
                    errors.append(f"{a['indicator_id']}: missing input column {col}")
                missing_ids = []
                for cid in sorted(EXPECTED_IDS, key=int):
                    value = by_id.get(cid, {}).get(col, "")
                    if value == "": missing_ids.append(cid)
                    else:
                        try:
                            if not math.isfinite(float(value)): raise ValueError()
                        except ValueError: errors.append(f"{a['indicator_id']}: invalid input for corridor {cid}")
                    if a.get("input_value_type") == "area_weighted_census_share" and value != "":
                        record = by_id.get(cid, {})
                        try:
                            share = float(value)
                            numerator = float(record.get("low_income_population_estimate", ""))
                            denominator = float(record.get("total_population_estimate", ""))
                            if not all(math.isfinite(v) for v in [share, numerator, denominator]): raise ValueError()
                            if not 0 <= share <= 1 or numerator < 0 or denominator <= 0: raise ValueError()
                            if not math.isclose(share, numerator / denominator, rel_tol=1e-10, abs_tol=1e-12): raise ValueError()
                            if record.get("allocation_method") != "ct_area_fraction_uniform_density": raise ValueError()
                            if record.get("estimation_status") not in {"pilot_estimate", "reviewed_estimate"}: raise ValueError()
                        except ValueError:
                            errors.append(f"{a['indicator_id']}: invalid area-weighted share contract at corridor {cid}")
                        if a.get("admission_status", "").lower() == "admitted" and record.get("estimation_status") != "reviewed_estimate":
                            readiness_issues.append(f"{a['indicator_id']}: corridor {cid} estimate has not completed geographic review")
                if str(a.get("coverage_count")) != str(24-len(missing_ids)):
                    errors.append(f"{a['indicator_id']}: claimed coverage does not match input values")
                declared = {x.strip() for x in str(a.get("missing_corridor_ids", "")).split(";") if x.strip()}
                if declared != set(missing_ids): errors.append(f"{a['indicator_id']}: declared missing IDs do not match input")
                if a["indicator_id"] in selected_ids and missing_ids:
                    readiness_issues.append(f"{a['indicator_id']}: {len(missing_ids)} selected input values are missing (corridors {';'.join(missing_ids)})")
                if a.get("input_value_type") == "city_standardized_score":
                    if a["indicator_id"] not in CITY_NON_COST_FIELDS:
                        errors.append(f"{a['indicator_id']}: no verified City non-cost-scaling evidence")
                    _, archive = read_csv(root / "evidence/city_2024_published_scores_NOT_RAW_v0.1.csv")
                    expected_values = {r["corridor_id"]:r["reported_value"] for r in archive if r["field_id"] == a["indicator_id"] and r["table_number"] in {"6", "7"}}
                    for cid in EXPECTED_IDS:
                        actual = by_id.get(cid, {}).get(col, "")
                        original = expected_values.get(cid, "")
                        try: same = actual == original or (actual != "" and original != "" and float(actual)==float(original))
                        except ValueError: same = False
                        if not same: errors.append(f"{a['indicator_id']}: City score differs from source archive at corridor {cid}")
        for a in admissions:
            if a.get("admission_status", "").lower() in {"admitted", "include", "included", "accepted"}:
                admitted_ids.append(a["indicator_id"])
                cost = str(a.get("cost_dependence", "")).strip().lower()
                if cost not in {"none", "no", "cost_independent"}:
                    errors.append(f"{a['indicator_id']}: admitted indicator cost dependence is {cost or 'unspecified'}; verify the actual input and document evidence before declaring it cost_independent")
                available = str(a.get("raw_value_available", "")).lower()
                if available == "standardized_score_available":
                    if a.get("input_value_type") != "city_standardized_score" or not a.get("input_file"):
                        errors.append(f"{a['indicator_id']}: standardized availability needs an explicit standardized input dataset")
                elif available not in {"yes", "true", "confirmed", "complete"}:
                    readiness_issues.append(f"{a['indicator_id']}: input availability is unresolved")
                for field in ["definition_clear", "unit_clear", "temporal_comparability", "spatial_comparability", "baseline_comparability"]:
                    if str(a.get(field, "")).lower() not in {"yes", "true", "confirmed", "comparable", "verified", "complete"}:
                        readiness_issues.append(f"{a['indicator_id']}: {field} is unresolved")
                if str(a.get("direction", "")).lower() not in {"higher_is_better", "lower_is_better", "target", "higher", "lower"}:
                    readiness_issues.append(f"{a['indicator_id']}: direction is unresolved")
                if not str(a.get("notes", "")).strip():
                    readiness_issues.append(f"{a['indicator_id']}: direction rationale must be documented in notes")
                if str(a.get("direction", "")).strip().lower() == "target":
                    readiness_issues.append(f"{a['indicator_id']}: target-based scoring requires a documented target and scoring rule; validator does not yet verify these")
                if a.get("input_file"):
                    dataset, _ = input_cache.get(a["input_file"], ({}, []))
                    incomplete = any(dataset.get(cid, {}).get(a.get("input_column", a["indicator_id"]), "") == "" for cid in EXPECTED_IDS)
                else:
                    col = "indicator_" + a["indicator_id"]
                    incomplete = any(r.get(col, "") == "" for r in rows)
                if incomplete:
                    readiness_issues.append(f"{a['indicator_id']}: admitted data incomplete across 24 corridors")
        if indicator_fields:
            wanted = {c.removeprefix("indicator_") for c in indicator_fields}
            if {d["indicator_id"] for d in dictionary} != wanted: errors.append("Dictionary IDs do not match master indicator columns.")
            if {a["indicator_id"] for a in admissions} != wanted: errors.append("Admission IDs do not match master indicator columns.")
    missing = sum(r.get(c, "") == "" for r in rows for c in indicator_fields)
    if not admitted_ids: readiness_issues.append("No indicators have been admitted to the model.")
    return {"valid_structure": not errors, "corridor_count": len(rows), "indicator_count": len(indicator_fields), "missing_indicator_cells": missing, "selected_indicator_count": len(selected_ids), "admitted_indicator_count": len(admitted_ids), "model_ready": not errors and not readiness_issues, "readiness_issues": readiness_issues, "errors": errors, "warnings": warnings}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(args.project)
    payload = json.dumps(report, indent=2)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    sys.exit(0 if report["valid_structure"] else 1)
