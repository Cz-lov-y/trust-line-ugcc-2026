"""Acquire matching CT inputs and calculate all available provisional catchments."""
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import urllib.parse
import urllib.request

import shapely
from shapely.geometry import shape
from shapely.ops import unary_union
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
CT_LAYER = "https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer/11"
PROFILE = "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_CT/"
KEY = "low_income_population_share_500m"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def metric_geometries(path):
    transform = Transformer.from_crs(4326, 2952, always_xy=True)
    result = []
    repairs = []
    for feature in json.loads(Path(path).read_text())["features"]:
        geometry = shapely.transform(shape(feature["geometry"]), transform.transform, interleaved=False)
        if not geometry.is_valid:
            fixed = shapely.make_valid(geometry)
            if not fixed.is_valid or fixed.geom_type not in {"Polygon", "MultiPolygon"} or abs(fixed.area - geometry.area) > 1:
                raise ValueError("Geometry needs manual repair review")
            repairs.append({"properties": feature["properties"], "reason": shapely.is_valid_reason(geometry),
                            "method": "make_valid", "area_change_m2": fixed.area - geometry.area})
            geometry = fixed
        if geometry.is_empty or geometry.area <= 0:
            raise ValueError("Empty or nonpositive-area source polygon")
        result.append((feature["properties"], geometry))
    return result, repairs


def acquire(root=ROOT, version="v0.4"):
    root = Path(root)
    evidence = root / f"evidence/corridor_batch_{version}"
    evidence.mkdir(parents=True, exist_ok=True)
    buffer_path = root / f"outputs/corridor_batch_{version}/corridor_buffers_500m.geojson"
    features = json.loads(buffer_path.read_text())["features"]
    bounds = unary_union([shape(f["geometry"]) for f in features]).bounds
    envelope = {"xmin": bounds[0], "ymin": bounds[1], "xmax": bounds[2], "ymax": bounds[3], "spatialReference": {"wkid": 4326}}
    manifest = {"buffer_sha256": sha(buffer_path), "resources": [], "geographic_envelope": envelope}

    def persist():
        (evidence / "census_acquisition_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    def fetch(filename, url):
        record = {"file": str((evidence / filename).relative_to(root)), "url": url,
                  "retrieved_utc": datetime.now(timezone.utc).isoformat()}
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                data = response.read()
            if filename.endswith(("json", "geojson")):
                parsed = json.loads(data)
                if parsed.get("error"):
                    raise ValueError(str(parsed["error"]))
            (evidence / filename).write_bytes(data)
            record.update(status="acquired", size_bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        except Exception as error:
            record.update(status="failed", error=f"{type(error).__name__}: {error}")
        return record

    query = {"f": "json", "where": "1=1", "returnIdsOnly": "true", "geometry": json.dumps(envelope),
             "geometryType": "esriGeometryEnvelope", "inSR": 4326, "spatialRel": "esriSpatialRelIntersects"}
    record = fetch("batch_ct_ids.json", CT_LAYER + "/query?" + urllib.parse.urlencode(query))
    manifest["resources"].append(record); persist()
    if record["status"] != "acquired":
        raise ValueError("CT ID-list acquisition failed; see manifest")
    ids = sorted(json.loads((evidence / "batch_ct_ids.json").read_text()).get("objectIds") or [])
    if not ids:
        raise ValueError("No CT source IDs returned")
    requests = []
    for start in range(0, len(ids), 400):
        batch = ids[start:start + 400]
        query = {"f": "geojson", "objectIds": ",".join(map(str, batch)), "outFields": "*", "outSR": 4326, "returnGeometry": "true"}
        requests.append((f"batch_ct_page_{start // 400:03}.geojson", CT_LAYER + "/query?" + urllib.parse.urlencode(query)))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for record in pool.map(lambda item: fetch(*item), requests):
            manifest["resources"].append(record); persist()
            if record["status"] != "acquired":
                raise ValueError("CT geometry acquisition failed; see manifest")
    all_features = []
    for filename, _ in requests:
        page = json.loads((evidence / filename).read_text())
        if page.get("exceededTransferLimit"):
            raise ValueError("CT geometry page truncated")
        all_features.extend(page["features"])
    returned = [f["properties"]["OBJECTID"] for f in all_features]
    if len(returned) != len(set(returned)) or set(returned) != set(ids):
        raise ValueError("CT boundary IDs do not reconcile")
    geometry_path = evidence / "batch_ct_boundaries.geojson"
    geometry_path.write_text(json.dumps({"type": "FeatureCollection", "features": all_features}) + "\n")
    tracts, repairs = metric_geometries(geometry_path)
    catchments, _ = metric_geometries(buffer_path)
    tree = shapely.STRtree([g for _, g in tracts])
    required_cts = set()
    for _, catchment in catchments:
        for index in tree.query(catchment):
            properties, geometry = tracts[index]
            if geometry.intersection(catchment).area > 1e-6:
                required_cts.add(properties["CTUID"])
    requests = []
    ordered = sorted(required_cts)
    for start in range(0, len(ordered), 40):
        batch = ordered[start:start + 40]
        keys = "+".join("2021S0507" + ctid.replace(".", "_") for ctid in batch)
        requests.append((f"batch_profile_{start // 40:03}.csv", PROFILE + f"A5.{keys}.1.1+321+326+331.1?format=csv"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        for record in pool.map(lambda item: fetch(*item), requests):
            manifest["resources"].append(record); persist()
            print(record["file"], record["status"], flush=True)
    index = {}
    for record in manifest["resources"]:
        if record["status"] != "acquired" or not record["file"].endswith(".csv"):
            continue
        for row in read_csv(root / record["file"]):
            if row["GENDER"] != "1" or row["STATISTIC"] != "1" or row["TIME_PERIOD"] != "2021":
                raise ValueError("Unexpected Census dimensions")
            key = row["ALT_GEO_CODE"], row["CHARACTERISTIC"]
            if key in index:
                raise ValueError("Duplicate Census count")
            index[key] = row
    rows = []
    for ctid in ordered:
        row = {"CTUID": ctid}
        for code, field in [("1", "population_2021"), ("321", "lim_applicable_population"), ("326", "low_income_population"), ("331", "published_lim_prevalence_percent")]:
            original = index.get((ctid, code))
            row[field] = original["OBS_VALUE"] if original and original["FLAG"] == "" else ""
            row[field + "_source_flag"] = original["FLAG"] if original else "not_returned"
        row["source_id"] = "STATCAN2021_LIM_PROFILE"
        rows.append(row)
    count_path = root / f"data/census_ct_batch_{version}.csv"
    write_csv(count_path, rows)
    manifest.update(required_CT_count=len(required_cts), boundary_feature_count=len(all_features),
                    geometry_file=str(geometry_path.relative_to(root)), geometry_sha256=sha(geometry_path),
                    processed_file=str(count_path.relative_to(root)), processed_sha256=sha(count_path),
                    geometry_repairs=repairs, complete_utc=datetime.now(timezone.utc).isoformat())
    persist()
    print("Intersecting CT profiles requested:", len(required_cts), flush=True)


def calculate(root=ROOT, output=None, model_output=None):
    root = Path(root)
    output = Path(output) if output else root / "outputs/corridor_batch_v0.4"
    output.mkdir(parents=True, exist_ok=True)
    model_output = Path(model_output) if model_output else root / "data/supplemental_model_inputs_v0.4.csv"
    evidence = root / "evidence/corridor_batch_v0.4"
    manifest = json.loads((evidence / "census_acquisition_manifest.json").read_text())
    buffer_path = root / "outputs/corridor_batch_v0.4/corridor_buffers_500m.geojson"
    if sha(buffer_path) != manifest["buffer_sha256"]:
        raise ValueError("Catchments changed since Census acquisition")
    for record in manifest["resources"]:
        if record["status"] == "acquired" and sha(root / record["file"]) != record["sha256"]:
            raise ValueError("Archived source checksum mismatch")
    for path_key, hash_key in [("geometry_file", "geometry_sha256"), ("processed_file", "processed_sha256")]:
        if sha(root / manifest[path_key]) != manifest[hash_key]:
            raise ValueError("Derived source input checksum mismatch")
    counts = {r["CTUID"]: r for r in read_csv(root / manifest["processed_file"])}
    tracts, repairs = metric_geometries(root / manifest["geometry_file"])
    catchments, _ = metric_geometries(buffer_path)
    tree = shapely.STRtree([g for _, g in tracts])
    calculated = {}
    allocations = []
    for properties, catchment in catchments:
        cid = int(properties["corridor_id"])
        population = income = universe = unknown_income_upper = 0.0
        missing_population = False
        missing = []
        pieces = []
        structural_zeros = []
        for index in tree.query(catchment):
            metadata, geometry = tracts[index]
            intersection = geometry.intersection(catchment)
            if intersection.area <= 1e-6:
                continue
            ctid = metadata["CTUID"]
            source = counts[ctid]
            fraction = intersection.area / geometry.area
            total = float(source["population_2021"]) if source["population_2021"] != "" else None
            low = float(source["low_income_population"]) if source["low_income_population"] != "" else None
            private = float(source["lim_applicable_population"]) if source["lim_applicable_population"] != "" else None
            status = "source_counts_available"
            if total == 0 and low is None:
                # A subset of an observed empty population has zero members.
                # Keep the suppressed source cell blank; log only this derived contribution.
                low = 0.0; private = 0.0; structural_zeros.append(ctid)
                status = "zero_contribution_from_observed_zero_total_population"
            if total is None or low is None:
                missing.append(ctid)
            if total is None:
                missing_population = True
            elif low is None:
                unknown_income_upper += fraction * total
            if any(value is not None and (not math.isfinite(value) or value < 0) for value in [total, low, private]):
                raise ValueError("Invalid nonnegative Census count")
            if total is not None:
                population += fraction * total
            if low is not None:
                income += fraction * low
            if private is not None:
                universe += fraction * private
            pieces.append(intersection)
            allocations.append({"corridor_id": cid, "CTUID": ctid, "area_fraction": fraction,
                                "source_population_2021": source["population_2021"],
                                "source_low_income_population": source["low_income_population"],
                                "low_income_source_flag": source["low_income_population_source_flag"],
                                "allocated_population": fraction * total if total is not None else "",
                                "allocated_low_income": fraction * low if low is not None else "", "status": status})
        covered = unary_union(pieces)
        overlap = sum(g.area for g in pieces) - covered.area
        if overlap > 1:
            raise ValueError("Duplicate area from overlapping CT polygons")
        share = income / population if not missing and population > 0 else None
        if share is not None and not 0 <= share <= 1:
            raise ValueError("Derived share outside [0,1]")
        calculated[cid] = {"share": share, "low_income_population_estimate": income if not missing else None,
                           "total_population_estimate": population, "intersecting_CT_count": len(pieces),
                           "missing_source_CTUIDs": sorted(missing), "structural_zero_CTUIDs": sorted(structural_zeros),
                           "known_low_income_contribution": income,
                           "suppression_only_share_lower": income / population if not missing_population and population > 0 else None,
                           "suppression_only_share_upper": (income + unknown_income_upper) / population if not missing_population and population > 0 else None,
                           "area_outside_CT_cartographic_frame_m2": catchment.difference(covered).area,
                           "cartographic_frame_note": "CT cartographic polygons define source land support. Uncovered area is reported, not assigned a population; coastline/land-support review pending.",
                           "geographic_review": "pending"}
    geometry_status = {int(r["corridor_id"]): r for r in read_csv(root / "outputs/corridor_batch_v0.4/geometry_status.csv")}
    rows = []
    for cid in range(1, 25):
        result = calculated.get(cid)
        available = result is not None and result["share"] is not None
        rows.append({"corridor_id": cid, KEY: result["share"] if available else "",
                     "low_income_population_estimate": result["low_income_population_estimate"] if available else "",
                     "total_population_estimate": result["total_population_estimate"] if available else "",
                     "allocation_method": "ct_area_fraction_uniform_density",
                     "estimation_status": "pilot_estimate" if available else ("pending_source_counts" if result else "pending_alignment"),
                     "geographic_review_status": "pending", "source_id": "STATCAN2021_LIM_PROFILE;STATCAN2021_CT_BOUNDARIES;CITY_CENTRELINE_CKAN_CURRENT",
                     "notes": ("Provisional named-road 500 m buffer and uniform-CT area allocation; not station access or approved alignment. " +
                               ("Missing CT inputs: " + ";".join(result["missing_source_CTUIDs"]) if result and not available else geometry_status[cid]["reason_or_limitations"]))})
    write_csv(model_output, rows)
    write_csv(output / "corridor_CT_allocations.csv", allocations)
    summary = {"available_equity_corridor_ids": [r["corridor_id"] for r in rows if r[KEY] != ""],
               "pending_equity_corridor_ids": [r["corridor_id"] for r in rows if r[KEY] == ""],
               "coverage_count": sum(r[KEY] != "" for r in rows), "all_corridor_count": len(rows),
               "per_corridor": calculated, "geometry_repairs": repairs,
               "model_ready": False, "all_geographic_reviews_pending": True,
               "source_missingness_not_imputed": True, "new_model_input_file": str(model_output.relative_to(root)) if model_output.is_relative_to(root) else str(model_output),
               "buffer_sha256": sha(buffer_path), "count_sha256": sha(root / manifest["processed_file"])}
    (output / "equity_batch_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in {"per_corridor", "geometry_repairs"}}, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--acquire", action="store_true")
    args = parser.parse_args()
    if args.acquire:
        acquire(args.project)
    calculate(args.project)
