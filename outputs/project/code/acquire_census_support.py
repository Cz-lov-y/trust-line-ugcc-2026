"""Archive public census support for the corridor 01 pilot; never calculate PPI."""
from pathlib import Path
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer"
GAF_OFFICIAL = "https://www12.statcan.gc.ca/census-recensement/2021/geo/aip-pia/attribute-attribs/files-fichiers/2021_92-151_X.zip"
GAF_MIRROR = "https://data.source.coop/dataforcanada/d4c-datapkg-statistical/archive/statcan/geographic_attribute_file/2021_92-151_X.zip"
PPI_MAP = "https://www.toronto.ca/wp-content/uploads/2024/07/8efd-Equity-PriorityPop.pdf"
GAF_GUIDE = "https://publications.gc.ca/collections/collection_2022/statcan/92-151-g2021001-eng.pdf"
CITY_CENSUS = "https://www.toronto.ca/wp-content/uploads/2022/02/92e3-City-Planning-2021-Census-Backgrounder-Population-Dwellings-Backgrounder.pdf"


def acquire(root=ROOT):
    root = Path(root)
    evidence = root / "evidence/census_support_v0.2"
    evidence.mkdir(parents=True, exist_ok=True)
    manifest_path = evidence / "acquisition_manifest.json"
    manifest = {"started_utc": datetime.now(timezone.utc).isoformat(), "resources": []}

    def save_manifest():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    def fetch(url, filename, source_id, role):
        target = evidence / filename
        record = {"source_id": source_id, "url": url, "role": role,
                  "retrieved_utc": datetime.now(timezone.utc).isoformat()}
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = response.read()
                record.update(http_status=response.status, final_url=response.url)
            if filename.endswith((".json", ".geojson")):
                parsed = json.loads(payload)
                if "error" in parsed:
                    raise ValueError(f"ArcGIS error: {parsed['error']}")
            if filename.endswith(".zip") and not zipfile.is_zipfile(io.BytesIO(payload)):
                raise ValueError("Response is not a ZIP archive")
            if filename.endswith(".pdf") and not payload.startswith(b"%PDF-"):
                raise ValueError("Response is not a PDF")
            target.write_bytes(payload)
            record.update(status="acquired", file=str(target.relative_to(root)),
                          size_bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
            return payload
        except Exception as exc:
            record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
            if isinstance(exc, urllib.error.HTTPError):
                record["http_status"] = exc.code
            raise
        finally:
            manifest["resources"].append(record)
            save_manifest()

    fetch(PPI_MAP, "city_priority_populations_map_2024.pdf", "CITY2024_PRIORITY_MAP",
          "Official map: component definitions and classes only; no exact tract scores")
    try:
        fetch(GAF_GUIDE, "gaf_reference_guide_2021.pdf", "STATCAN2021_GAF_GUIDE",
              "Official reference guide prospect; verify PDF content before saving")
    except (urllib.error.URLError, TimeoutError, ValueError):
        # Guide acquisition is evidence preparation, not a requirement for
        # downloading boundaries. The failed response remains in the manifest.
        pass
    fetch(CITY_CENSUS, "city_2021_population_backgrounder.pdf", "CITY2021_CENSUS_BENCHMARK",
          "Independent municipal total from Table 2, printed page 9: 2,794,356")
    try:
        gaf = fetch(GAF_OFFICIAL, "2021_92-151_X.zip", "STATCAN2021_GAF",
                    "Official geographic attribute file")
        gaf_transport = "official_download"
    except (urllib.error.URLError, TimeoutError):
        gaf = fetch(GAF_MIRROR, "2021_92-151_X.zip", "D4C2021_GAF_ARCHIVE",
                    "Third-party archive of StatCan GAF; official binary checksum unverified")
        gaf_transport = "third_party_archive_official_checksum_unverified"

    population_rows = []
    columns = {"DBUID_IDIDU": "DBUID", "DBDGUID_IDIDUGD": "DB_DGUID",
               "DAUID_ADIDU": "DAUID", "CTUID_SRIDU": "CTUID",
               "CTDGUID_SRIDUGD": "CT_DGUID", "CSDUID_SDRIDU": "CSDUID",
               "DBPOP2021_IDPOP2021": "population_2021",
               "DBTDWELL2021_IDTLOG2021": "total_private_dwellings_2021",
               "DBAREA2021_IDSUP2021": "source_land_area_km2",
               "DBIR2021_IDRI2021": "incompletely_enumerated_reserve_flag"}
    with zipfile.ZipFile(io.BytesIO(gaf)) as archive:
        with archive.open("2021_92-151_X.csv") as stream:
            # The archive contains single-byte accented names. Latin-1 is a
            # reversible byte mapping; selected identifier/count fields are ASCII.
            reader = csv.DictReader(io.TextIOWrapper(stream, encoding="latin-1"))
            if not set(columns).issubset(reader.fieldnames or []):
                raise ValueError("GAF schema does not match documented 2021 fields")
            for row in reader:
                if row["CSDUID_SDRIDU"] == "3520005":
                    population_rows.append({new: row[old] for old, new in columns.items()})
    if not population_rows or len({r["DBUID"] for r in population_rows}) != len(population_rows):
        raise ValueError("Toronto GAF DB keys are empty or duplicated")
    target = root / "data/toronto_db_population_2021_v0.2.csv"
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(columns.values()))
        writer.writeheader()
        writer.writerows(population_rows)

    # Fetch whole intersecting polygons, using an envelope only to limit acquisition.
    # The overlay script performs the actual polygon intersection.
    catchment = json.loads((root / "outputs/sheppard_west_pilot/corridor_01_buffer_500m.geojson").read_text())
    points = []

    def collect(value):
        if value and isinstance(value[0], (float, int)):
            points.append(value)
        else:
            for child in value:
                collect(child)

    for feature in catchment["features"]:
        collect(feature["geometry"]["coordinates"])
    envelope = {"xmin": min(p[0] for p in points), "ymin": min(p[1] for p in points),
                "xmax": max(p[0] for p in points), "ymax": max(p[1] for p in points),
                "spatialReference": {"wkid": 4326}}
    for layer, name in [(11, "ct"), (13, "db")]:
        sid = f"STATCAN2021_{name.upper()}_BOUNDARIES"
        metadata = json.loads(fetch(f"{BASE}/{layer}?f=pjson", f"{name}_layer_metadata.json", sid,
                                    "Official 2021 cartographic boundary metadata"))
        query = {"f": "json", "where": "1=1", "returnIdsOnly": "true",
                 "geometry": json.dumps(envelope), "geometryType": "esriGeometryEnvelope",
                 "inSR": 4326, "spatialRel": "esriSpatialRelIntersects"}
        ids = json.loads(fetch(f"{BASE}/{layer}/query?" + urllib.parse.urlencode(query),
                               f"{name}_object_ids.json", sid, "Complete ID list intersecting pilot envelope"))
        object_ids = sorted(ids.get("objectIds") or [])
        if not object_ids:
            raise ValueError(f"No {name} boundary IDs returned")
        features = []
        for offset in range(0, len(object_ids), 500):
            batch = object_ids[offset:offset + 500]
            query = {"f": "geojson", "objectIds": ",".join(map(str, batch)), "outFields": "*",
                     "returnGeometry": "true", "outSR": 4326}
            page = json.loads(fetch(f"{BASE}/{layer}/query?" + urllib.parse.urlencode(query),
                                    f"{name}_page_{offset // 500:03}.geojson", sid,
                                    "Whole polygons, no geometry simplification"))
            if page.get("exceededTransferLimit") or len(page.get("features", [])) != len(batch):
                raise ValueError(f"Incomplete {name} page")
            features.extend(page["features"])
        returned = [f["properties"]["OBJECTID"] for f in features]
        if len(returned) != len(set(returned)) or set(returned) != set(object_ids):
            raise ValueError(f"{name} object IDs do not reconcile")
        merged = {"type": "FeatureCollection", "features": features}
        (evidence / f"pilot_{name}_2021.geojson").write_text(json.dumps(merged) + "\n", encoding="utf-8")
        manifest[f"{name}_feature_count"] = len(features)
        manifest[f"{name}_source_layer_name"] = metadata["name"]
        print(f"Archived {len(features)} {name} polygons", flush=True)

    derived_paths = [target, evidence / "pilot_ct_2021.geojson", evidence / "pilot_db_2021.geojson"]
    manifest["derived_files"] = [{"file": str(path.relative_to(root)),
                                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                   "role": "Exact field subset or concatenation of archived source pages"}
                                  for path in derived_paths]
    manifest.update(gaf_transport=gaf_transport, gaf_csv_decoding="latin-1; selected fields are ASCII", census_year=2021,
                    population_scope="Toronto census subdivision 3520005 only",
                    toronto_db_count=len(population_rows),
                    toronto_population_2021=sum(int(r["population_2021"]) for r in population_rows),
                    geographic_acquisition_envelope=envelope,
                    exact_ppi_scores_acquired=False, completed_utc=datetime.now(timezone.utc).isoformat())
    save_manifest()
    print(json.dumps({k: v for k, v in manifest.items() if k != "resources"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    acquire(parser.parse_args().project)
