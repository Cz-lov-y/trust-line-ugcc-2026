"""Register the user-approved equity pivot without admitting incomplete inputs."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
KEY = "low_income_population_share_500m"
NAME = "Low-income population share in 500 m catchment (CT area-weighted estimate)"
SOURCE = "STATCAN2021_LIM_PROFILE;STATCAN2021_CT_BOUNDARIES"


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def write_csv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_legacy_json(path, value):
    # Preserve the existing v0.1 files' CRLF layout and absent final newline so
    # reviews show the actual policy/record changes instead of all JSON lines.
    Path(path).write_bytes(json.dumps(value, indent=2).replace("\n", "\r\n").encode("utf-8"))


def register(root=ROOT):
    root = Path(root)
    data = root / "data"
    source_path = data / "source_log_v0.1.csv"
    source_fields, sources = read_csv(source_path)
    for sid, title, url, scope, source_notes in [
        ("STATCAN2021_LIM_PROFILE", "Census Profile 2021: official CT and DA population and LIM-AT counts",
         "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/", "14 CT and 48 DA for corridor 01 pilot",
         "Characteristics 1, 321, 326 and 331; total gender, statistic 1; 2021 geography/population, 2020 income. All 14 CT counts complete. DA 35202414 LIM counts are suppressed (FLAG=6), not zero. Archived queries, labels, flags and checksums in evidence/low_income_support_v0.3."),
        ("STATCAN2021_DA_BOUNDARIES", "2021 Cartographic boundary files - Dissemination areas",
         "https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer/12", "Whole polygons of 48 pilot DAs",
         "Official 2021 DA polygons for comparison only. CT area weighting is the approved primary proxy method; DA suppression remains unresolved.")]:
        if sid not in {r["source_id"] for r in sources}:
            sources.append({"source_id": sid, "title": title, "publisher": "Statistics Canada",
                            "publication_date": "2022", "retrieval_date": "2026-11-21", "url": url,
                            "source_type": "acquired_official_api", "source_locator": "evidence/low_income_support_v0.3/acquisition_manifest.json",
                            "scope": scope, "notes": source_notes})
    write_csv(source_path, source_fields, sources)
    model_fields, model_rows = read_csv(data / "supplemental_model_inputs_v0.3.csv")
    if {r["corridor_id"] for r in model_rows} != {str(i) for i in range(1, 25)} or len(model_rows) != 24:
        raise ValueError("Proxy model table must preserve all 24 alternatives")
    missing = [r["corridor_id"] for r in model_rows if r[KEY] == ""]
    coverage = 24 - len(missing)
    notes = ("User replaced PPI with an independent LIM-AT share. Main numerator is CT Census characteristic 326; denominator is characteristic 1 (all residents). "
             "Characteristic 321 provides a separate private-household-universe comparator. CT and DA populations are spatial estimates under uniform within-area density. "
             "DA 35202414 has confidentiality suppression; its missing count is preserved and the complete DA share is unavailable. "
             "User approved a consistent CT area-weighting policy after this finding. This proxy measures resident concentration, not benefits or a Palma ratio. "
             "Income reference year is 2020, Census geography/population are 2021; trial road geometry is from 2026. Only corridor 01 has a pilot; remaining 23 and geographic review are pending. "
             "Population midpoint 32679.5 is a denominator-only stress scenario; it is not an area-weighted estimate. No source value is imputed.")
    definition = "sum_t(area(buffer intersect CT_t)/area(CT_t) * LIM_AT_count_t) / sum_t(area(buffer intersect CT_t)/area(CT_t) * total_population_t)"
    dictionary = {"indicator_id": KEY, "indicator_name": NAME, "primary_principle": "Serve People",
                  "definition": definition, "unit": "fraction [0,1]; multiply by 100 for percent",
                  "spatial_scope": "500 m continuous corridor buffer; CT area weighting; corridor 01 trial geometry only",
                  "population_scope": "LIM-AT private-household numerator / all Census residents denominator; custom proxy, not official prevalence",
                  "reference_year": "2021 Census; 2020 income", "measurement_period": "2020 income status; 2021 Census population",
                  "value_type": "area_weighted_census_share", "technology_dependence": "none in Census counts; catchment assumptions apply",
                  "cost_dependence": "none", "potential_overlap": "population coverage; other resident equity indicators",
                  "data_availability": f"pilot_estimate_{coverage}_of_24", "source_id": SOURCE,
                  "source_locator": "Census Profile characteristics 1, 321, 326; evidence/low_income_support_v0.3/acquisition_manifest.json",
                  "master_column": "indicator_" + KEY, "notes": notes,
                  "input_file": "data/supplemental_model_inputs_v0.3.csv", "input_column": KEY,
                  "input_value_type": "area_weighted_census_share", "input_unit": "fraction [0,1]", "input_cost_dependence": "none"}
    admission = {"indicator_id": KEY, "indicator_name": NAME, "primary_principle": "Serve People",
                 "admission_status": "pending_collection", "cost_dependence": "none", "raw_value_available": "pilot_estimate_available",
                 "definition_clear": "confirmed", "unit_clear": "confirmed", "direction": "higher_is_better",
                 "temporal_comparability": "2020_income_2021_population; City_2022_2051_alignment_unresolved",
                 "spatial_comparability": "CT_policy_approved; only_corridor_01_trial_geometry_available",
                 "baseline_comparability": "not_established_across_24", "coverage_count": coverage,
                 "missing_corridor_ids": ";".join(sorted(missing, key=int)),
                 "potential_overlap": dictionary["potential_overlap"],
                 "decision_reason": "Replacement sixth candidate; pilot only. Final admission requires 24 reviewed estimates and confirmed comparability, not changed labels.",
                 "source_id": SOURCE, "reviewer": "Codex", "review_date": "2026-11-21", "notes": notes,
                 "input_file": dictionary["input_file"], "input_column": KEY, "input_value_type": dictionary["input_value_type"]}
    record_path = data / "workbook_records_v0.1.json"
    records = json.loads(record_path.read_text())
    for section, replacement in [("data_dictionary", dictionary), ("indicator_admission", admission)]:
        records[section] = [row for row in records[section] if row["indicator_id"] != KEY]
        records[section].append(replacement)
        for row in records[section]:
            if row["indicator_id"] == "priority_populations_index":
                suffix = " v0.3: Withdrawn from selected criteria at user request; superseded by low_income_population_share_500m. No further PPI acquisition is required."
                if suffix not in row["notes"]:
                    row["notes"] += suffix
                if section == "indicator_admission":
                    row["admission_status"] = "withdrawn_from_selection"
                    row["decision_reason"] = "User abandoned PPI in favour of the independent Census low-income proxy."
                else:
                    row["data_availability"] = "withdrawn_from_selection"
    write_legacy_json(record_path, records)
    selection_path = data / "model_input_selection_v0.1.json"
    selection = json.loads(selection_path.read_text())
    selection["strategy"] = "Five preserved City non-cost standardized scores plus a CT area-weighted Census low-income proxy"
    selection["selected_indicator_ids"] = ["current_speed", "unimproved_load", "current_max_load", "current_ridership", "competitiveness", KEY]
    selection["withdrawn_indicator_ids"] = ["priority_populations_index"]
    selection["missing_data_policy"] = "Preserve source missingness; no source-value imputation. Explicit CT spatial allocation and denominator stress scenarios are estimates, not missing-data fills."
    selection["supplemental_inputs_file"] = dictionary["input_file"]
    selection["equity_method_file"] = "data/equity_proxy_method_v0.3.json"
    write_legacy_json(selection_path, selection)
    master_path = data / "corridor_master_v0.1.csv"
    fields, rows = read_csv(master_path)
    if dictionary["master_column"] not in fields:
        fields.append(dictionary["master_column"])
        for row in rows:
            row[dictionary["master_column"]] = ""
        write_csv(master_path, fields, rows)
    schema_path = data / "schema_v0.1.json"
    schema = json.loads(schema_path.read_text())
    schema["corridor_master"] = fields
    schema["low_income_proxy_inputs"] = model_fields
    write_legacy_json(schema_path, schema)
    observation_path = data / "indicator_observations_v0.1.csv"
    obs_fields, observations = read_csv(observation_path)
    observations = [r for r in observations if r["indicator_id"] != KEY]
    for cid in range(1, 25):
        observations.append({"corridor_id": str(cid), "indicator_id": KEY, "value": "",
                             "value_status": "derived_estimate_stored_separately", "source_id": SOURCE,
                             "source_locator": dictionary["input_file"], "reference_year": "2021 Census; 2020 income",
                             "scenario_id": "ct_area_weighted_pilot", "transformation_id": "ct_area_fraction_uniform_density",
                             "notes": "No raw observation inserted. Derived proxy is stored in its mapped supplemental model-input file."})
    write_csv(observation_path, obs_fields, observations)
    longlist_path = data / "candidate_indicator_longlist_v0.1.csv"
    long_fields, longlist = read_csv(longlist_path)
    longlist = [r for r in longlist if r["indicator_id"] != KEY]
    new_row = {field: dictionary.get(field, "") for field in long_fields}
    new_row.update(city_rtef_category="Independent Census equity proxy", direction="higher_is_better", city_scaling="not_applicable",
                   admission_status="pending_collection", definition_status="CT_area_weighting_approved_for_pilot",
                   raw_source_status="Census_counts_archived; derived_proxy_not_a_raw_observation")
    longlist.append(new_row)
    for row in longlist:
        if row["indicator_id"] == "priority_populations_index":
            row["admission_status"] = "withdrawn_from_selection"
    write_csv(longlist_path, long_fields, longlist)
    gap_path = data / "data_gap_register_v0.1.csv"
    gap_fields, gaps = read_csv(gap_path)
    gaps = [r for r in gaps if r["indicator_id"] != KEY]
    gaps.append({"indicator_id": KEY, "nonmissing_corridors": 0, "missing_corridors": 24,
                 "status": "raw_placeholder_empty; derived_estimate_separate",
                 "next_action": "See supplemental model coverage (1/24); collect reviewed CT-weighted estimates for other corridors."})
    for row in gaps:
        if row["indicator_id"] == "priority_populations_index":
            row["status"] = "withdrawn_from_selection"
            row["next_action"] = "Historical placeholder only; PPI acquisition abandoned by user."
    write_csv(gap_path, gap_fields, gaps)
    coverage_fields = ["indicator_id", "input_file", "coverage_count", "missing_corridor_ids", "admission_status"]
    by_id = {a["indicator_id"]: a for a in records["indicator_admission"]}
    write_csv(data / "model_input_coverage_v0.1.csv", coverage_fields,
              [{field: by_id[key][field] for field in coverage_fields} for key in selection["selected_indicator_ids"]])
    acq_path = data / "acquisition_log_v0.1.csv"
    acq_fields, acquisitions = read_csv(acq_path)
    aid = "ACQ_V03_LIM_CENSUS"
    if aid not in {row["acquisition_id"] for row in acquisitions}:
        acquisitions.append({"acquisition_id": aid, "indicator_scope": KEY, "source_id": SOURCE + ";STATCAN2021_DA_BOUNDARIES",
                             "status": "CT_counts_complete_for_pilot; DA_suppression_preserved", "last_checked": "2026-11-21",
                             "evidence": "14 CT and 48 DA official Census Profile records archived. DA 35202414 suppressed. User selected a consistent CT area-weighted primary method; corridor 01 proxy available.",
                             "required_input": "Reviewed catchments and CT intersections for the remaining 23 corridors; review cross-criterion comparability.",
                             "next_action": "Keep source blanks and pending_collection statuses. PPI is withdrawn; the 22 missing City score cells still block the current selection."})
    write_csv(acq_path, acq_fields, acquisitions)
    print(json.dumps({"selected_criteria": selection["selected_indicator_ids"], "proxy_coverage": coverage,
                      "missing_proxy_corridors": missing, "proxy_admission": admission["admission_status"]}, indent=2))


if __name__ == "__main__":
    register()
