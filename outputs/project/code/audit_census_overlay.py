"""Audit 2021 census geography against the existing pilot without estimating partial-block population."""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import platform

import pyproj
import shapely
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
AREA_TOLERANCE_M2 = 1e-6


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def classify_block(block, catchment):
    """Return geometric overlap only; a partial fraction is never a population weight."""
    if not block.is_valid or block.is_empty or block.area <= 0:
        raise ValueError("Block geometry must be valid with positive area")
    intersection = block.intersection(catchment)
    overlap = intersection.area
    if overlap <= AREA_TOLERANCE_M2:
        return "outside", 0.0, overlap, intersection
    # covers() avoids treating a tiny uncovered fragment as fully populated inside.
    status = "fully_inside" if catchment.covers(block) else "partially_inside"
    return status, overlap / block.area, overlap, intersection


def population_bounds(status, population):
    if population is None:
        return None, None
    if not isinstance(population, int) or population < 0:
        raise ValueError("Population must be a nonnegative integer or missing")
    if status == "fully_inside":
        return population, population
    if status == "partially_inside":
        return 0, population
    if status == "outside":
        return 0, 0
    raise ValueError(f"Unknown overlap status {status}")


def audit(root=ROOT, output=None, repair_invalid=False):
    root = Path(root)
    output = Path(output) if output else root / "outputs/census_overlay_pilot_v0.2"
    output.mkdir(parents=True, exist_ok=True)
    evidence = root / "evidence/census_support_v0.2"
    paths = [root / "outputs/sheppard_west_pilot/corridor_01_buffer_500m.geojson",
             evidence / "pilot_db_2021.geojson", evidence / "pilot_ct_2021.geojson",
             root / "data/toronto_db_population_2021_v0.2.csv",
             evidence / "acquisition_manifest.json"]
    acquisitions = json.loads(paths[-1].read_text())
    if not acquisitions.get("completed_utc") or len(acquisitions.get("derived_files", [])) != 3:
        raise ValueError("Acquisition is incomplete or lacks derived-file checksums")
    population_source_id = "D4C2021_GAF_ARCHIVE" if "third_party" in acquisitions["gaf_transport"] else "STATCAN2021_GAF"
    # Refuse silently modified downloaded evidence.
    for record in acquisitions["resources"]:
        if record["status"] == "acquired":
            source_path = root / record["file"]
            if hashlib.sha256(source_path.read_bytes()).hexdigest() != record["sha256"]:
                raise ValueError(f"Evidence checksum mismatch: {source_path}")
    for record in acquisitions["derived_files"]:
        if hashlib.sha256((root / record["file"]).read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Derived input checksum mismatch: {record['file']}")
    to_metric = Transformer.from_crs(4326, 2952, always_xy=True)
    to_lonlat = Transformer.from_crs(2952, 4326, always_xy=True)

    repair_log = []

    def project(geometry, properties, filename):
        result = shapely.transform(shape(geometry), to_metric.transform, interleaved=False)
        if result.is_empty:
            raise ValueError("Empty geometry")
        if not result.is_valid:
            if not repair_invalid:
                raise ValueError("Invalid geometry; inspect and rerun with --repair-invalid to log make_valid")
            repaired = shapely.make_valid(result)
            change = repaired.area - result.area
            if not repaired.is_valid or repaired.geom_type not in {"Polygon", "MultiPolygon"} or abs(change) > 1:
                raise ValueError("Geometry repair requires further review (type or area change >1 m2)")
            repair_log.append({"source_file": filename, "geography_id": properties.get("DBUID", properties.get("CTUID")),
                               "reason": shapely.is_valid_reason(result), "method": "shapely.make_valid",
                               "original_area_m2": result.area, "repaired_area_m2": repaired.area,
                               "area_change_m2": change, "result_type": repaired.geom_type})
            result = repaired
        return result

    def load(path):
        data = json.loads(path.read_text())
        if data.get("type") != "FeatureCollection":
            raise ValueError(f"Expected RFC 7946 GeoJSON FeatureCollection: {path}")
        return [(f["properties"], project(f["geometry"], f["properties"], str(path.relative_to(root)))) for f in data["features"]]

    buffer_features = load(paths[0])
    catchment = unary_union([g for _, g in buffer_features])
    blocks, tracts = load(paths[1]), load(paths[2])
    tract_by_id = {p["CTUID"]: g for p, g in tracts}
    if len(tract_by_id) != len(tracts):
        raise ValueError("Duplicate CTUID in boundary source")
    if any(p["DGUID"] != "2021S0507" + p["CTUID"] for p, _ in tracts):
        raise ValueError("Unexpected CT DGUID/vintage in boundary source")
    population_rows = read_csv(paths[3])
    pop_by_id = {r["DBUID"]: r for r in population_rows}
    if len(pop_by_id) != len(population_rows):
        raise ValueError("Duplicate DBUID in GAF subset")
    if any(not r["DBUID"].isdigit() or len(r["DBUID"]) != 11 for r in population_rows):
        raise ValueError("Invalid string DBUID")
    if any(not r["CT_DGUID"].startswith("2021S0507") for r in population_rows):
        raise ValueError("Unexpected CT vintage in GAF")

    block_rows, clipped_features, clipped_geometries = [], [], []
    groups = {}
    seen_ids = set()
    for properties, geometry in blocks:
        dbid = properties["DBUID"]
        if not isinstance(dbid, str) or dbid in seen_ids:
            raise ValueError("DBUID must be a unique string")
        seen_ids.add(dbid)
        status, fraction, area, intersection = classify_block(geometry, catchment)
        if status == "outside":
            continue
        source = pop_by_id.get(dbid)
        population = int(source["population_2021"]) if source and source["population_2021"] != "" else None
        if source and source["DB_DGUID"] != properties["DGUID"]:
            raise ValueError(f"DB DGUID mismatch for {dbid}")
        ctid = source["CTUID"] if source else ""
        if source and (ctid not in tract_by_id or source["CT_DGUID"] != "2021S0507" + ctid):
            raise ValueError(f"CT join mismatch for {dbid}")
        if source and source["incompletely_enumerated_reserve_flag"] != "F":
            raise ValueError(f"Incomplete enumeration needs review: {dbid}")
        if source and geometry.difference(tract_by_id[ctid]).area > 1.0:
            raise ValueError(f"DB boundary extends outside GAF parent CT by more than 1 m2: {dbid}")
        lower, upper = population_bounds(status, population)
        row = {"corridor_id": 1, "DBUID": dbid, "DB_DGUID": properties["DGUID"], "CTUID": ctid,
               "source_population_2021": "" if population is None else population,
               "geometry_status": status, "block_geometry_area_m2": geometry.area,
               "intersection_area_m2": area, "geometric_area_fraction": fraction,
               "covered_population_lower_bound": "" if lower is None else lower,
               "covered_population_upper_bound": "" if upper is None else upper,
               "estimated_covered_population": "", "ppi": "",
               "population_allocation_status": "no_point_estimate; partial-block distribution unknown",
               "population_source_id": population_source_id,
               "boundary_source_id": "STATCAN2021_DB_BOUNDARIES"}
        block_rows.append(row)
        clipped_geometries.append(intersection)
        lonlat = shapely.transform(intersection, to_lonlat.transform, interleaved=False)
        clipped_features.append({"type": "Feature", "geometry": mapping(lonlat), "properties": row})
        groups.setdefault(ctid, []).append(row)

    if not block_rows:
        raise ValueError("No positive-area DB intersections")
    missing_population = [r["DBUID"] for r in block_rows if r["source_population_2021"] == ""]
    clipped_union = unary_union(clipped_geometries)
    duplication = sum(g.area for g in clipped_geometries) - clipped_union.area
    if duplication > 1.0:
        raise ValueError(f"Overlapping DB polygons would duplicate more than 1 m2: {duplication}")
    tract_rows = []
    for ctid, rows in sorted(groups.items()):
        complete = all(r["source_population_2021"] != "" for r in rows)
        tract_rows.append({"corridor_id": 1, "CTUID": ctid, "intersecting_db_count": len(rows),
                           "fully_inside_db_count": sum(r["geometry_status"] == "fully_inside" for r in rows),
                           "partially_inside_db_count": sum(r["geometry_status"] == "partially_inside" for r in rows),
                           "covered_population_lower_bound": sum(r["covered_population_lower_bound"] for r in rows) if complete else "",
                           "covered_population_upper_bound": sum(r["covered_population_upper_bound"] for r in rows) if complete else "",
                           "estimated_covered_population": "", "tract_ppi": "",
                           "status": "exact_ppi_missing; partial_block_allocation_not_adopted"})
    lower = sum(r["covered_population_lower_bound"] for r in block_rows) if not missing_population else ""
    upper = sum(r["covered_population_upper_bound"] for r in block_rows) if not missing_population else ""
    audit_rows = []
    for cid in range(1, 25):
        audit_rows.append({"corridor_id": cid, "priority_populations_index": "",
                           "geometry_status": "road_proxy_pending_review" if cid == 1 else "not_digitized",
                           "intersecting_ct_count": len(groups) if cid == 1 else "",
                           "intersecting_db_count": len(block_rows) if cid == 1 else "",
                           "covered_population_lower_bound": lower if cid == 1 else "",
                           "covered_population_upper_bound": upper if cid == 1 else "",
                           "estimated_covered_population": "", "ppi_numerator": "", "ppi_denominator": "",
                           "ppi_status": "not_computed",
                           "reason": "exact_tract_ppi_and_method_missing; catchment_not_adopted; partial_block_population_unallocated" if cid == 1 else "geometry_and_exact_tract_ppi_missing"})
    write_csv(output / "pilot_db_intersections.csv", block_rows, list(block_rows[0]))
    write_csv(output / "pilot_ct_population_bounds.csv", tract_rows, list(tract_rows[0]))
    write_csv(output / "corridor_ppi_audit_v0.2.csv", audit_rows, list(audit_rows[0]))
    (output / "pilot_db_intersections.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": clipped_features}) + "\n", encoding="utf-8")
    summary = {"corridor_id": 1, "census_year": 2021, "measurement_crs": "EPSG:2952",
               "catchment": "Existing 500 m road buffer; trial geometry pending adoption",
               "catchment_area_m2": catchment.area, "intersecting_ct_count": len(groups),
               "intersecting_db_count": len(block_rows),
               "fully_inside_db_count": sum(r["geometry_status"] == "fully_inside" for r in block_rows),
               "partially_inside_db_count": sum(r["geometry_status"] == "partially_inside" for r in block_rows),
               "population_lower_bound": lower, "population_upper_bound": upper,
               "population_point_estimate": None, "priority_populations_index": None,
               "missing_population_db_ids": missing_population,
               "db_overlap_area_m2": duplication,
               "buffer_area_without_db_polygon_m2": catchment.difference(clipped_union).area,
               "geometry_repairs": repair_log, "positive_intersection_area_tolerance_m2": AREA_TOLERANCE_M2,
               "gaf_transport": acquisitions["gaf_transport"],
               "interpretation": "Bounds on published census counts under the trial boundary; no within-block density assumption. Bounds are not a corridor population estimate or PPI denominator.",
               "model_ready": False, "audit_corridor_row_count": len(audit_rows),
               "source_ids": ["STATCAN2021_CT_BOUNDARIES", "STATCAN2021_DB_BOUNDARIES", population_source_id],
               "input_sha256": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
               "versions": {"python": platform.python_version(), "shapely": shapely.__version__, "pyproj": pyproj.__version__, "proj": pyproj.proj_version_str},
               "run_utc": datetime.now(timezone.utc).isoformat()}
    if not math.isfinite(catchment.area) or not 0 < catchment.area:
        raise ValueError("Invalid catchment area")
    (output / "overlay_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repair-invalid", action="store_true", help="Log make_valid repairs; reject area change >1 m2")
    args = parser.parse_args()
    audit(args.project, args.output, args.repair_invalid)
