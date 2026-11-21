"""Archive official 2021 Census CT/DA inputs for the corridor 01 equity pilot."""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import shutil
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/"
DA_LAYER = "https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer/12"
CHARACTERISTICS = {
    "1": "Population, 2021",
    "321": "Total - LIM low-income status in 2020 for the population in private households - 100% data",
    "326": "In low income based on the Low-income measure, after tax (LIM-AT)",
    "331": "Prevalence of low income based on the Low-income measure, after tax (LIM-AT) (%)",
}


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def acquire(root=ROOT, seed_dir=None):
    root = Path(root)
    out = root / "evidence/low_income_support_v0.3"
    out.mkdir(parents=True, exist_ok=True)
    block_ids = {r["DBUID"] for r in read_csv(root / "outputs/census_overlay_pilot_v0.2/pilot_db_intersections.csv")}
    population = read_csv(root / "data/toronto_db_population_2021_v0.2.csv")
    da_ids = sorted({r["DAUID"] for r in population if r["DBUID"] in block_ids})
    ct_ids = sorted({r["CTUID"] for r in population if r["DBUID"] in block_ids})
    queries = {}
    for level, ids, prefix in [("da", da_ids, "2021S0512"), ("ct", ct_ids, "2021S0507")]:
        # SDMX CT codes use an underscore for the decimal separator. Canonical
        # CTUIDs retain their period; ALT_GEO_CODE supplies the explicit crosswalk.
        keys = "+".join(prefix + identifier.replace(".", "_") for identifier in ids)
        queries[f"pilot_{level}_counts.csv"] = API + f"data/STC_CP,DF_{level.upper()}/A5.{keys}.1.1+321+326+331.1?format=csv"
    where = "DAUID IN (" + ",".join("'" + identifier + "'" for identifier in da_ids) + ")"
    queries["pilot_da_2021.geojson"] = DA_LAYER + "/query?" + urllib.parse.urlencode(
        {"where": where, "outFields": "*", "returnGeometry": "true", "outSR": 4326, "f": "geojson"})
    queries["da_metadata.json"] = DA_LAYER + "?f=pjson"
    queries["sample_da_profile.json"] = API + "data/STC_CP,DF_DA/A5.2021S051235202403.1..1?format=jsondata"
    queries["suppressed_da_metadata.json"] = API + "data/STC_CP,DF_DA/A5.2021S051235202414.1.1+321+326+331.1?format=jsondata"
    queries["ct_geo_codelist.xml"] = API + "codelist/STC_CP/CL_GEO_CT/latest"
    manifest = {"census_year": 2021, "income_reference_year": 2020,
                "CTUIDs": ct_ids, "DAUIDs": da_ids, "resources": []}
    for filename, url in queries.items():
        path = out / filename
        if seed_dir:
            seed = Path(seed_dir) / filename
            shutil.copyfile(seed, path)
            retrieved = datetime.fromtimestamp(seed.stat().st_mtime, timezone.utc).isoformat()
        else:
            with urllib.request.urlopen(url, timeout=45) as response:
                path.write_bytes(response.read())
            retrieved = datetime.now(timezone.utc).isoformat()
        payload = path.read_bytes()
        if filename.endswith((".json", ".geojson")):
            parsed = json.loads(payload)
            if parsed.get("error") or parsed.get("errors"):
                raise ValueError(f"Source API error in {filename}")
        manifest["resources"].append({"file": str(path.relative_to(root)), "url": url,
                                       "source_id": "STATCAN2021_DA_BOUNDARIES" if filename in {"da_metadata.json", "pilot_da_2021.geojson"} else "STATCAN2021_LIM_PROFILE",
                                       "retrieved_utc": retrieved, "size_bytes": len(payload),
                                       "sha256": hashlib.sha256(payload).hexdigest(),
                                       "transport": "official_public_api"})
    # Match the selected codes to authoritative labels, rather than guessing
    # characteristic codes from their order in the response.
    sample = json.loads((out / "sample_da_profile.json").read_text())
    dimensions = sample["data"]["structures"][0]["dimensions"]["series"]
    labels = {v["id"]: v["name"] for d in dimensions if d["id"] == "CHARACTERISTIC" for v in d["values"]}
    if any(labels.get(code) != label for code, label in CHARACTERISTICS.items()):
        raise ValueError("Census characteristic labels differ from the reviewed contract")
    flag_definitions = {}
    for attributes in sample["data"]["structures"][0]["attributes"].values():
        for attribute in attributes:
            if attribute["id"] == "FLAG":
                flag_definitions = {v["id"]: v["name"] for v in attribute["values"]}

    processed = []
    fields = {"1": "population_2021", "321": "lim_applicable_population_2020",
              "326": "low_income_lim_at_2020", "331": "published_lim_at_prevalence_percent"}
    for level, expected_ids in [("CT", ct_ids), ("DA", da_ids)]:
        rows = read_csv(out / f"pilot_{level.lower()}_counts.csv")
        index = {}
        for row in rows:
            identifier, code = row["ALT_GEO_CODE"], row["CHARACTERISTIC"]
            key = identifier, code
            if key in index or row["GENDER"] != "1" or row["STATISTIC"] != "1" or row["TIME_PERIOD"] != "2021":
                raise ValueError("Duplicate or incompatible Census Profile record")
            index[key] = row
        if set(index) != {(identifier, code) for identifier in expected_ids for code in fields}:
            raise ValueError(f"Incomplete {level} response")
        for identifier in expected_ids:
            record = {"geography_level": level, "geography_id": identifier,
                      "source_id": "STATCAN2021_LIM_PROFILE", "census_year": 2021, "income_reference_year": 2020}
            for code, field in fields.items():
                row = index[identifier, code]
                # A suppression/not-applicable flag never becomes an observed zero.
                record[field] = row["OBS_VALUE"] if row["FLAG"] == "" else ""
                record[field + "_flag"] = row["FLAG"]
            record["source_geography_code"] = index[identifier, "1"]["REF_AREA"]
            record["income_data_status"] = "available" if record["low_income_lim_at_2020"] != "" else "source_suppressed_or_unavailable"
            processed.append(record)
    target = root / "data/census_low_income_pilot_v0.3.csv"
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(processed[0]))
        writer.writeheader()
        writer.writerows(processed)
    geometries = json.loads((out / "pilot_da_2021.geojson").read_text())
    returned_ids = [f["properties"]["DAUID"] for f in geometries["features"]]
    if len(returned_ids) != len(set(returned_ids)) or set(returned_ids) != set(da_ids) or geometries.get("exceededTransferLimit"):
        raise ValueError("DA boundary acquisition is incomplete or duplicated")
    manifest.update(characteristics=CHARACTERISTICS, flag_definitions=flag_definitions,
                    processed_file=str(target.relative_to(root)),
                    processed_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                    completed_utc=datetime.now(timezone.utc).isoformat())
    (out / "acquisition_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"CT_count": len(ct_ids), "DA_count": len(da_ids),
                      "missing_income_geographies": [r["geography_level"] + ":" + r["geography_id"] for r in processed if r["income_data_status"] != "available"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    parser.add_argument("--seed-dir", type=Path, help="Archive already downloaded responses; their mtimes are retrieval-completion timestamps")
    args = parser.parse_args()
    acquire(args.project, args.seed_dir)
