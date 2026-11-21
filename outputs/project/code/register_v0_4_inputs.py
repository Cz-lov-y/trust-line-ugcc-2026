"""Map verified v0.4 scenario/batch files without claiming final admission."""
from pathlib import Path
import csv
import json

from analyze_city_missingness import FIELDS, source_statistics

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(rows)


def legacy_json(path, value):
    Path(path).write_bytes(json.dumps(value, indent=2).replace("\n", "\r\n").encode())


def register(root=ROOT):
    root = Path(root)
    data = root / "data"
    _, original = read_csv(data / "city_standardized_scores_v0.1.csv")
    stats = source_statistics(original)
    fields, sources = read_csv(data / "source_log_v0.1.csv")
    additions = [
        {"source_id": "CITY_MISSING_POLICY_V04", "title": "User-authorized missing City score scenario policy", "publisher": "Team analytical configuration",
         "publication_date": "2026-11-21", "retrieval_date": "2026-11-21", "url": "", "source_type": "declared_analysis_method",
         "source_locator": "data/missing_data_policy_v0.4.json; outputs/missingness_v0.4/imputation_trace.csv", "scope": "22 source blanks in five selected City score columns",
         "notes": "Observed-column minimum is an explicit analysis assumption, not an observed value or verified theoretical lower bound. Mean and dynamic-weight diagnostics are sensitive. Original City source is preserved."},
        {"source_id": "CITY_CENTRELINE_CKAN_CURRENT", "title": "Toronto Centreline Version 2 - 4326 GeoJSON", "publisher": "City of Toronto",
         "publication_date": "", "retrieval_date": "2026-11-21", "url": "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/1d079757-377b-4564-82df-eb5638583bfb/resource/7bc94ccf-7bcf-4a7d-88b1-bdfc8ec5aaf1/download/centreline-version-2-4326.geojson",
         "source_type": "acquired_official_download_subset", "source_locator": "evidence/corridor_batch_v0.4/road_acquisition_manifest.json", "scope": "Named-road subset of 64,384 current City road features",
         "notes": "Full 93 MB download checksum recorded; only selected original features archived in project. Source node/segment IDs retained. Current road proxies are not approved future alignments."},
        {"source_id": "STATION_ENDPOINT_REVIEW_V04", "title": "Operator station/route descriptions used for endpoint proxies", "publisher": "TTC; GO Transit",
         "publication_date": "", "retrieval_date": "2026-11-21", "url": "https://www.ttc.ca/en/subway-stations/pioneer-village-station",
         "source_type": "reviewed_operator_web_sources", "source_locator": "evidence/corridor_batch_v0.4/station_endpoint_review.json", "scope": "Pioneer Village, Milliken GO and Wilson approach",
         "notes": "Pioneer Village near Northwest Gate/Steeles; Milliken address 39 Redlea Avenue; TTC 96 description connects Wilson via Walsh Avenue. Intersection proxies remain provisional."}
    ]
    for source in additions:
        if source["source_id"] not in {r["source_id"] for r in sources}:
            sources.append(source)
    write_csv(data / "source_log_v0.1.csv", fields, sources)
    record_path = data / "workbook_records_v0.1.json"
    records = json.loads(record_path.read_text())
    proxy_fields, proxy_rows = read_csv(data / "supplemental_model_inputs_v0.4.csv")
    missing_proxy = [r["corridor_id"] for r in proxy_rows if r["low_income_population_share_500m"] == ""]
    for section, rows in records.items():
        for row in rows:
            key = row["indicator_id"]
            if key in FIELDS:
                row.update(input_file="data/city_analysis_inputs_v0.4.csv", input_column=key,
                           input_value_type="city_score_imputation_scenario")
                row["published_source_coverage_count"] = stats[key]["observed_count"]
                row["scenario_substitution_count"] = stats[key]["missing_count"]
                row["missing_data_policy"] = "imputed_conservative_min; observed minimum, not a theoretical bound"
                marker = "v0.4:"
                addition = (f"v0.4: Analysis input uses imputed_conservative_min with {stats[key]['missing_count']} scenario substitutions; "
                            f"published source coverage remains {stats[key]['observed_count']}/24. Original scores and blanks are preserved. "
                            "Repeated missingness is concentrated in seven corridors. Mean/dynamic diagnostics change ranks materially; baseline/scenario comparability remains under review.")
                row["notes"] = row.get("notes", "").split(marker)[0].rstrip() + " " + addition
                if section == "indicator_admission":
                    row.update(coverage_count=24, missing_corridor_ids="", admission_status="pending_baseline_and_missingness_review",
                               raw_value_available="scenario_input_available",
                               decision_reason="Scenario matrix complete and substitution provenance verified; source coverage and policy sensitivity do not establish final baseline comparability.")
            if key == "low_income_population_share_500m":
                row.update(input_file="data/supplemental_model_inputs_v0.4.csv", input_column=key,
                           input_value_type="area_weighted_census_share")
                addition = ("v0.4: Batch has 17 current-road proxies and 15 complete provisional CT estimates. Seven alignments remain unresolved; "
                            "corridors 3 and 21 intersect positive-population CTs with suppressed LIM counts (5350205.00 and 5350006.00). "
                            "Census suppression is not imputed. All station, alignment and cartographic-frame reviews remain pending.")
                row["notes"] = row.get("notes", "").split("v0.4:")[0].rstrip() + " " + addition
                if section == "indicator_admission":
                    row.update(coverage_count=24-len(missing_proxy), missing_corridor_ids=";".join(missing_proxy),
                               admission_status="pending_geometry_and_source_completion", raw_value_available="provisional_estimates_available",
                               spatial_comparability="consistent_CT_policy; provisional_road_proxies; seven_alignments_pending",
                               decision_reason="15 provisional estimates, 9 missing, and all geographic reviews pending; no final admission.")
                else:
                    row["data_availability"] = f"provisional_estimates_{24-len(missing_proxy)}_of_24"
    legacy_json(record_path, records)
    selection_path = data / "model_input_selection_v0.1.json"
    selection = json.loads(selection_path.read_text())
    selection.update(strategy="Five City score observed-minimum analysis scenarios plus provisional CT area-weighted equity estimates",
                     analysis_score_file="data/city_analysis_inputs_v0.4.csv", supplemental_inputs_file="data/supplemental_model_inputs_v0.4.csv",
                     city_missingness_policy="data/missing_data_policy_v0.4.json",
                     missing_data_policy="Original source missingness preserved; user-authorized City minimum substitutions exist only in the separate analysis scenario. Census suppression remains missing.")
    legacy_json(selection_path, selection)
    schema_path = data / "schema_v0.1.json"
    schema = json.loads(schema_path.read_text())
    for section in ["data_dictionary", "indicator_admission"]:
        for field in ["published_source_coverage_count", "scenario_substitution_count", "missing_data_policy"]:
            if field not in schema[section]: schema[section].append(field)
    schema["city_analysis_inputs"] = read_csv(data / "city_analysis_inputs_v0.4.csv")[0]
    schema["low_income_proxy_inputs"] = proxy_fields
    legacy_json(schema_path, schema)
    coverage_fields = ["indicator_id", "input_file", "coverage_count", "missing_corridor_ids", "admission_status",
                       "published_source_coverage_count", "scenario_substitution_count"]
    by_id = {r["indicator_id"]: r for r in records["indicator_admission"]}
    write_csv(data / "model_input_coverage_v0.1.csv", coverage_fields,
              [{field: by_id[key].get(field, "") for field in coverage_fields} for key in selection["selected_indicator_ids"]])
    geometry_path = data / "corridor_geometry_review_v0.1.csv"
    geometry_fields, geometry_rows = read_csv(geometry_path)
    batch = {r["corridor_id"]: r for r in read_csv(root / "outputs/corridor_batch_v0.4/geometry_status.csv")[1]}
    for row in geometry_rows:
        status = batch[row["corridor_id"]]
        row["alignment_geometry_status"] = status["geometry_status"]
        row["station_set_status"] = "not_defined"
        row["catchment_status"] = "500m_road_buffer_pending_review" if status["measured_route_length_km"] != "" else "pending_alignment"
        row["full_alignment_length_km"] = status["measured_route_length_km"]
        row["geometry_source_id"] = "CITY_CENTRELINE_CURRENT" if row["corridor_id"] == "1" else "CITY_CENTRELINE_CKAN_CURRENT;STATION_ENDPOINT_REVIEW_V04"
        row["next_action"] = "Review endpoint proxies, route/case agreement and source length anomalies." if status["measured_route_length_km"] else status["reason_or_limitations"]
        row["notes"] = "Measured length is a road proxy, not a verified full future alignment. " + status["reason_or_limitations"]
    write_csv(geometry_path, geometry_fields, geometry_rows)
    fields, acquisition_log = read_csv(data / "acquisition_log_v0.1.csv")
    aid = "ACQ_V04_BATCH_AND_MISSINGNESS"
    if aid not in {r["acquisition_id"] for r in acquisition_log}:
        acquisition_log.append({"acquisition_id": aid, "indicator_scope": "City missing-data scenarios and batch equity",
                                "source_id": "CITY_MISSING_POLICY_V04;CITY_CENTRELINE_CKAN_CURRENT;STATCAN2021_LIM_PROFILE",
                                "status": "City_scenarios_24; equity_15_of_24", "last_checked": "2026-11-21",
                                "evidence": "22 City source gaps located in seven corridors; derived min/mean scenarios and dynamic-weight diagnostics archived. Official centreline subset yields 17 proxies; 249 CT profiles acquired; 15 equity estimates available.",
                                "required_input": "Seven future alignments and two suppressed Census contributions; geographic and baseline comparability review.",
                                "next_action": "Do not claim robustness (rank changes 14/16), theoretical bounds, or final readiness. Preserve raw sources and all 24 alternatives."})
    write_csv(data / "acquisition_log_v0.1.csv", fields, acquisition_log)
    print(json.dumps({"City_analysis_coverage_per_column": 24, "original_City_observed_values": 98,
                      "City_scenario_substitutions": 22, "equity_coverage": 24-len(missing_proxy), "equity_missing_ids": missing_proxy}, indent=2))


if __name__ == "__main__":
    register()
