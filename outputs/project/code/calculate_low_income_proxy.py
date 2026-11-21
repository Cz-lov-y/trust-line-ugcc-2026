"""Calculate the CT area-weighted equity pilot, retaining suppression and all 24 alternatives."""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math

import pyproj
import shapely
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
INDICATOR = "low_income_population_share_500m"


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def weighted_share(rows):
    """Rows have area_fraction, population and low_income; None stays unavailable."""
    population = 0.0
    known_income = 0.0
    missing_population = False
    missing_income = False
    unknown_income_upper = 0.0
    for row in rows:
        fraction = row["area_fraction"]
        if not math.isfinite(fraction) or not 0 <= fraction <= 1 + 1e-10:
            raise ValueError("Invalid area fraction")
        if fraction == 0:
            continue
        total, income = row["population"], row["low_income"]
        for value in [total, income]:
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError("Negative or nonfinite source count")
        if total is None:
            missing_population = True
        else:
            population += fraction * total
        if income is None:
            missing_income = True
            if total is not None:
                unknown_income_upper += fraction * total
        else:
            if total is not None and income > total:
                raise ValueError("Low-income count exceeds total source population")
            known_income += fraction * income
    denominator = None if missing_population else population
    numerator = None if missing_income else known_income
    share = numerator / denominator if numerator is not None and denominator and denominator > 0 else None
    return {"population_estimate": denominator, "low_income_estimate": numerator,
            "known_low_income_contribution": known_income,
            "share": share, "missing_source_income": missing_income,
            "suppression_only_share_lower": known_income / denominator if denominator and denominator > 0 else None,
            "suppression_only_share_upper": (known_income + unknown_income_upper) / denominator if denominator and denominator > 0 else None}


def calculate(root=ROOT, output=None, model_output=None):
    root = Path(root)
    output = Path(output) if output else root / "outputs/low_income_pilot_v0.3"
    output.mkdir(parents=True, exist_ok=True)
    model_output = Path(model_output) if model_output else root / "data/supplemental_model_inputs_v0.3.csv"
    method_path = root / "data/equity_proxy_method_v0.3.json"
    method = json.loads(method_path.read_text())
    if method["primary_geography"] != "CT" or method["allocation_method"] != "ct_area_fraction_uniform_density":
        raise ValueError("The reviewed production pilot contract requires CT area weighting")
    evidence = root / "evidence/low_income_support_v0.3"
    manifest_path = evidence / "acquisition_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for record in manifest["resources"]:
        if hashlib.sha256((root / record["file"]).read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Source checksum mismatch: {record['file']}")
    counts_path = root / manifest["processed_file"]
    if hashlib.sha256(counts_path.read_bytes()).hexdigest() != manifest["processed_sha256"]:
        raise ValueError("Processed Census counts checksum mismatch")
    # The original CT boundary file is an audited concatenation of source pages.
    census_manifest = json.loads((root / "evidence/census_support_v0.2/acquisition_manifest.json").read_text())
    ct_path = root / "evidence/census_support_v0.2/pilot_ct_2021.geojson"
    ct_hash = next(r["sha256"] for r in census_manifest["derived_files"] if r["file"] == str(ct_path.relative_to(root)))
    if hashlib.sha256(ct_path.read_bytes()).hexdigest() != ct_hash:
        raise ValueError("CT boundary checksum mismatch")
    profiles = read_csv(counts_path)
    count_by_key = {(r["geography_level"], r["geography_id"]): r for r in profiles}
    if len(count_by_key) != len(profiles):
        raise ValueError("Duplicate Census geography key")
    transformer = Transformer.from_crs(4326, 2952, always_xy=True)
    repairs = []

    def project(geometry, identifier):
        result = shapely.transform(shape(geometry), transformer.transform, interleaved=False)
        if result.is_empty:
            raise ValueError(f"Empty geometry: {identifier}")
        if not result.is_valid:
            repaired = shapely.make_valid(result)
            change = repaired.area - result.area
            if not repaired.is_valid or repaired.geom_type not in {"Polygon", "MultiPolygon"} or abs(change) > 1:
                raise ValueError(f"Geometry repair needs additional review: {identifier}")
            repairs.append({"id": identifier, "reason": shapely.is_valid_reason(result),
                            "method": "make_valid", "area_change_m2": change})
            result = repaired
        return result

    buffer_path = root / "outputs/sheppard_west_pilot/corridor_01_buffer_500m.geojson"
    catchment = unary_union([project(f["geometry"], "corridor_01") for f in json.loads(buffer_path.read_text())["features"]])
    allocations = []
    results = {}
    paths = {"CT": ct_path, "DA": evidence / "pilot_da_2021.geojson"}
    for level, path in paths.items():
        source_features = json.loads(path.read_text())["features"]
        seen = set()
        pieces = []
        rows = []
        universe_complete = True
        allocated_universe = 0.0
        missing_ids = []
        for feature in source_features:
            identifier = feature["properties"][level + "UID"]
            if not isinstance(identifier, str) or identifier in seen:
                raise ValueError("Geographic identifiers must be unique strings")
            seen.add(identifier)
            geometry = project(feature["geometry"], identifier)
            intersection = geometry.intersection(catchment)
            if intersection.area <= method["intersection_area_tolerance_m2"]:
                continue
            source = count_by_key.get((level, identifier))
            if source is None:
                raise ValueError(f"No profile record for intersecting {level} {identifier}")
            fraction = intersection.area / geometry.area
            def number(field):
                return float(source[field]) if source[field] != "" else None
            total = number("population_2021")
            income = number("low_income_lim_at_2020")
            universe = number("lim_applicable_population_2020")
            if universe is None:
                universe_complete = False
            else:
                if not math.isfinite(universe) or universe < 0:
                    raise ValueError("Invalid LIM universe count")
                allocated_universe += fraction * universe
            if income is None:
                missing_ids.append(identifier)
            rows.append({"area_fraction": fraction, "population": total, "low_income": income})
            pieces.append(intersection)
            allocations.append({"corridor_id": 1, "geography_level": level, "geography_id": identifier,
                                "whole_polygon_area_m2": geometry.area, "intersection_area_m2": intersection.area,
                                "area_fraction": fraction, "source_population_2021": "" if total is None else total,
                                "source_lim_applicable_population": "" if universe is None else universe,
                                "source_low_income_population": "" if income is None else income,
                                "source_low_income_flag": source["low_income_lim_at_2020_flag"],
                                "allocated_population_estimate": "" if total is None else fraction * total,
                                "allocated_low_income_estimate": "" if income is None else fraction * income,
                                "allocation_method": level.lower() + "_area_fraction_uniform_density",
                                "income_status": source["income_data_status"]})
        if not rows:
            raise ValueError(f"No {level} intersections")
        union = unary_union(pieces)
        overlap = sum(g.area for g in pieces) - union.area
        uncovered = catchment.difference(union).area
        if overlap > 1 or uncovered > 1:
            raise ValueError(f"Incomplete/overlapping {level} support: uncovered={uncovered}, overlap={overlap}")
        result = weighted_share(rows)
        result.update(geography_count=len(rows), missing_low_income_ids=missing_ids,
                      lim_applicable_population_estimate=allocated_universe if universe_complete else None,
                      lim_applicable_population_share=(result["low_income_estimate"] / allocated_universe
                                                       if universe_complete and allocated_universe > 0 and result["low_income_estimate"] is not None else None),
                      uncovered_buffer_area_m2=uncovered, duplicated_area_m2=overlap)
        results[level] = result
    main = results["CT"]
    source_ids = "STATCAN2021_LIM_PROFILE;STATCAN2021_CT_BOUNDARIES;CITY_CENTRELINE_CURRENT"
    model_rows = []
    for cid in range(1, 25):
        available = cid == 1 and main["share"] is not None
        model_rows.append({"corridor_id": cid, INDICATOR: main["share"] if available else "",
                           "low_income_population_estimate": main["low_income_estimate"] if available else "",
                           "total_population_estimate": main["population_estimate"] if available else "",
                           "lim_applicable_population_estimate": main["lim_applicable_population_estimate"] if available else "",
                           "allocation_method": method["allocation_method"],
                           "estimation_status": "pilot_estimate" if available else "pending_collection",
                           "source_id": source_ids,
                           "notes": "CT area-weighted spatial estimate; uniformity assumed; trial geometry; not official LIM prevalence." if cid == 1 else "No reviewed catchment or corridor estimate collected."})
    write_csv(model_output, model_rows)
    write_csv(output / "geographic_allocations.csv", allocations)
    bounds_path = root / "outputs/census_overlay_pilot_v0.2/overlay_summary.json"
    bounds = json.loads(bounds_path.read_text())
    # These are denominator-only stress scenarios, not a fill for missing source
    # values or an assertion that the numerator is known without spatial error.
    denominators = {"ct_area_weighted": main["population_estimate"],
                    "midpoint_population": (bounds["population_lower_bound"] + bounds["population_upper_bound"]) / 2,
                    "low_bound": bounds["population_lower_bound"], "high_bound": bounds["population_upper_bound"]}
    scenarios = []
    for name, denominator in denominators.items():
        for cid in range(1, 25):
            available = cid == 1 and main["low_income_estimate"] is not None and denominator and denominator > 0
            scenarios.append({"corridor_id": cid, "scenario_id": name,
                              "low_income_numerator": main["low_income_estimate"] if available else "",
                              "population_denominator": denominator if available else "",
                              INDICATOR: main["low_income_estimate"] / denominator if available else "",
                              "status": "pilot_stress_scenario" if available else "pending_collection",
                              "interpretation": "Denominator-only stress; fixed CT-allocated numerator; no ranking performed."})
    write_csv(output / "population_stress_scenarios.csv", scenarios)
    summary = {"indicator_id": INDICATOR, "primary_geography": "CT", "corridor_id": 1,
               "method_file": str(method_path.relative_to(root)), "results": results,
               "db_population_lower_bound": bounds["population_lower_bound"],
               "db_population_upper_bound": bounds["population_upper_bound"],
               "db_population_midpoint": denominators["midpoint_population"],
               "midpoint_is_area_weighted": False,
               "ct_population_within_db_bounds": bounds["population_lower_bound"] <= main["population_estimate"] <= bounds["population_upper_bound"],
               "da_population_within_db_bounds": bounds["population_lower_bound"] <= results["DA"]["population_estimate"] <= bounds["population_upper_bound"],
               "da_vs_ct_population_relative_difference": results["DA"]["population_estimate"] / main["population_estimate"] - 1,
               "model_facing_coverage_count": sum(row[INDICATOR] != "" for row in model_rows),
               "remaining_corridors_status": "pending_collection", "admission_status": "pending_collection",
               "model_ready": False, "ranking_run": False, "geometry_repairs": repairs,
               "counts_rounding_note": "Income counts are published Census counts subject to confidentiality rounding. Spatial estimates and stress scenarios are not exact counts or confidence intervals.",
               "denominator_note": method["denominator_scope"],
               "input_sha256": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in [method_path, manifest_path, counts_path, ct_path, paths["DA"], buffer_path, bounds_path]},
               "versions": {"shapely": shapely.__version__, "pyproj": pyproj.__version__},
               "run_utc": datetime.now(timezone.utc).isoformat()}
    (output / "proxy_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    calculate(args.project, args.output)
