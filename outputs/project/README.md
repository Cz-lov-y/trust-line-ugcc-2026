# TRUST-Line input strategy and evidence inventory

## v0.2 continuation: census support and overlay audit

The user-designated collaboration repository is `https://github.com/Cz-lov-y/trust-line-ugcc-2026`; its canonical working project is `outputs/project`. The original Windows workspace and the earlier cloud checkpoint paths are historical context. This continuation is synchronized as project files, without adding another duplicate project ZIP or any installed runtime/vendor trees.

The latest continuation is described in `CONTINUATION_v0.2.json` and `outputs/continuation_review_v0.2.html`. `HANDOFF_v0.1.md`, the v0.1 validation, workbooks, delivery checks and original pilot documentation are historical snapshots. The Windows paths in the handoff have not been verified from this Linux cloud environment. Work here is a continuation of the uploaded ZIP, with no write-back to the user's Windows project.

Official 2021 StatCan census-tract and dissemination-block polygons were acquired for the Sheppard West pilot envelope. A Data for Canada archive of the 2021 Geographic Attribute File supplied Toronto's 13,323 block records. Their population sum, 2,794,356, matches the archived official City census backgrounder. The official GAF download returned HTTP 403, and its binary checksum remains unverified. Aggregate reconciliation does not verify every block value independently.

The existing 500 m trial road buffer intersects 174 blocks across 14 tracts. Of these, 125 blocks are fully inside and 49 are partially inside. Bounds on published census counts are 25,300 to 40,059. No within-block population point estimate, population weights or PPI was calculated. A geometric area fraction is never treated as a population fraction. Two source polygon self-intersections were repaired only in working geometry, with logged area changes below 1e-9 m2. Original downloaded geometry is preserved.

`evidence/census_support_v0.2/acquisition_manifest.json` records URLs, retrieval times, failures, checksums, source transport and derived-file hashes. `outputs/census_overlay_pilot_v0.2/` contains the block intersections, tract-level bounds, all-24 corridor PPI audit and runtime/geometry QA. `data/ppi_source_components_v0.2.csv` records the eleven labels verified from the official May 2024 map; full construction definitions and exact tract scores remain missing. A 2022 public TEOZ candidate is archived separately and excluded because its authority, vintage and equivalence are unverified.

The complete competition guideline package, page 22, restricts AI use and requires disclosure. This continuation records that issue and this session's AI assistance; it does not establish that the work is eligible for submission. The attachment is treated as evidence of participation rules, not as a new user instruction.

Rebuild the offline overlay in an isolated Python environment with `code/requirements_census_v0.2.txt`, then run `python -B code/audit_census_overlay.py --repair-invalid`. Run `python -B -m unittest discover -s code -p test_census_overlay.py -v` for the six population-accounting and integration checks. `code/acquire_census_support.py` repeats network acquisition when explicitly run; archived inputs suffice for the overlay and tests.

All original model values, raw placeholders, selected criteria, admission records and alignment data are unchanged. The latest validation is `outputs/validation_v0.2.json`: structure valid, 24 alternatives retained, no criteria admitted, `model_ready=false`. The strategy below remains the original v0.1 baseline; its lack-of-census-evidence statements are superseded only by the specific v0.2 acquisitions above.

All project content is English. All 24 alternatives are retained. No ranking, optimization, imputation or simulation has been run.

For the complete successor-assistant handoff, read [HANDOFF_v0.1.md](HANDOFF_v0.1.md). Its file catalogue, environment notes and next-task contracts supplement this strategy README. The machine-readable file inventory is outputs/handoff_file_inventory_v0.1.csv.

## Decision and actual status

The intended main model uses City non-cost-scaled standardized scores, plus a supplemental Priority Populations Index if its data and methods can be verified. Scores are relative evaluation inputs, not raw physical quantities. Recovering the unscaled City matrix is not required for this strategy.

The five City inputs are current_speed, unimproved_load, current_max_load, current_ridership and competitiveness. Attachment Table 1, p.6 labels four with no scaling and current ridership with Length, not Cost. No construction-cost normalization enters these five columns. This supports cost-independent evaluation, subject to confirming score orientation and baseline comparability. It does not remove technology, network, forecast-year or construction-length assumptions. City Cost-scaled, Combined and final scores remain excluded, as do equity scores whose cost processing is unresolved.

Coverage is 17, 24, 20, 20 and 17 respectively: 98 published values and 22 source missing values. All 24 rows are kept. Source N/A remains blank. Zero-filling, guessed means and dropping corridors are not used.

Priority Populations Index is registered as the sixth intended input. NO corridor-level result has been computed. Exact tract index values, complete source methodology, population weights and validated catchments have not been acquired. Full TEOZ is not interchangeable with its priority-populations component. The proposed formula is sum(P_it * I_t) / sum(P_it), using catchment population P_it and exact tract score I_t. This measures resident priority concentration, not predicted distribution of project benefits. No map-bin midpoint is substituted.

There are 43 longlisted concepts and 1,032 unresolved raw master cells. Raw-data gaps differ from standardized-input coverage. Current model_ready is false: selected inputs still need admission/interpretation review, four City columns have missing values, and the supplemental equity calculation is absent. No final admission is asserted merely to make validation pass.

## Files and authority

- data/corridor_master_v0.1.csv: 24 metadata records and raw indicator_* placeholders. Standardized scores never enter these columns.
- data/city_standardized_scores_v0.1.csv: unchanged City score values from Tables 6-7, with source missingness preserved.
- data/supplemental_model_inputs_v0.1.csv: separate derived inputs; Priority Populations Index is currently blank for all 24 corridors.
- data/model_input_selection_v0.1.json: six intended inputs; all must meet readiness conditions. A single complete column cannot make the planned model ready.
- data/model_input_coverage_v0.1.csv: measured coverage and missing IDs.
- data/workbook_records_v0.1.json: authoritative dictionary/admission records. Edit JSON and regenerate Excel; Excel-only changes do not affect validation.
- data/data_dictionary_v0.1.xlsx and data/indicator_admission_v0.1.xlsx: generated review workbooks including input_file, input_column and input_value_type.
- data/candidate_indicator_longlist_v0.1.csv: candidate concepts, not admitted criteria.
- data/city_2024_indicator_index_v0.1.csv: 30 source indicator definitions/locations, with no corridor values.
- data/source_log_v0.1.csv, indicator_observations_v0.1.csv, data_gap_register_v0.1.csv, acquisition_log_v0.1.csv and corridor_geometry_review_v0.1.csv: source and raw-gap records.
- evidence/city_2024_published_scores_NOT_RAW_v0.1.csv: source-score archive, including excluded fields; not a raw master.
- evidence/tech_evidence_v0.1.csv and part2_sources_v0.1.csv: header-only Part 2 templates.
- outputs/validation_v0.1.json: current validation. outputs/model_input_review_v0.1.html: current input review. Earlier inventory_review_v0.1.html is a pre-strategy snapshot, not current readiness evidence.

## Validation rules

raw_value_available=standardized_score_available is a compatibility status for processed input, not a claim that raw values exist. It requires input_value_type=city_standardized_score and explicit file/column mapping to a verified non-cost City field. Source values and missingness must match the archive; arbitrary replacements are rejected.

Coverage_count and missing_corridor_ids are checked against actual input files, not trusted. Every dataset retains exactly 24 unique corridor IDs. Selected inputs require final admission, no cost dependence, complete values, documented direction, and confirmed definitions, units and temporal/spatial/baseline comparability before model_ready=true. Unselected raw longlist gaps do not block a valid score model.

Allowed cost-independent labels are no, none and cost_independent. These labels require evidence. Allowed direction values are higher_is_better, lower_is_better, higher, lower and target. For a City score, higher_is_better refers to the source evaluation, not automatically the underlying speed or time ratio. A rationale belongs in notes. Target-based scoring remains blocked until an explicit target/scoring contract is implemented.

## Commands

```bash
python -B code/validate_data.py --output outputs/validation_v0.1.json
python -B code/simulation_template.py
node code/build_workbooks.mjs
```

Python uses the standard library. Workbook regeneration requires the Codex artifact-tool runtime; set ARTIFACT_NODE_MODULES to the installed node_modules path. The simulation interface is a template requiring validated inputs and supported assumptions; it does not automatically select an input dataset.

## Sources

City attachment: https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243172.pdf

Page references use its standalone 13-page sequence. Definitions: p.6; corridors: p.7; score details: pp.11-13; equity methods: p.3. Main report and priority-populations map have separate source IDs. Network/search failure is not proof that underlying data do not exist.

## Sheppard West geometry pilot

outputs/sheppard_west_pilot contains a map, a QGIS project and GeoJSON centreline, endpoints and a 500 m corridor buffer for corridor 01. The road proxy is 4.407067 km long and the buffer is 5.192196 km2. See its README for source provenance, limitations, software setup and rebuild instructions. This pilot does not fill population or equity indicators and does not change model readiness. All 24 corridor rows remain in the project.
