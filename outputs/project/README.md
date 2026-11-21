# TRUST-Line input strategy and evidence inventory

## v0.4: missingness diagnosis, explicit scenarios and batch equity

Current state: `CONTINUATION_v0.4.json`; review: `outputs/review_v0.4.html`; validation: `outputs/validation_v0.4.json`. Earlier version sections, inventories and checks below are historical. Use the v0.4 registration command for current mappings; older registration helpers reproduce their own earlier state.

The City source has 98 observed scores and 22 blanks. Gaps are concentrated in seven corridors (pattern B): IDs 4/6/8/10 each lack current speed, current maximum load, current ridership and competitiveness; IDs 3/5/13 lack current speed and competitiveness. The other 17 corridors are complete. No corridor lacks all five columns. Column missing counts are 7, 0, 4, 4, 7. This is not assumed to be random missingness or evidence that all missing services have zero benefit.

The user authorized considering conservative substitutions. `data/city_standardized_scores_v0.1.csv` and its archive remain unchanged. The separate active `data/city_analysis_inputs_v0.4.csv` contains all 120 analysis values: 98 source values and 22 `imputed_conservative_min` substitutions, with per-cell flags and a trace. The substitutions use observed column minima (-1.26 speed, -2.16 maximum load, -0.90 ridership, -1.84 competitiveness). The complete unimproved-load column needs no substitution. Observed minima are not verified theoretical lower bounds or estimates of structurally unavailable existing service. Mean substitutions are a separate sensitivity file. The prior no-source-imputation policy is changed only for these explicitly declared City analysis scenarios; Census suppression is not filled.

In the five-column equal-weight diagnostic, changing minima to observed means changes individual ranks by up to 14 positions; available-case dynamic weighting changes them by up to 16. Tied-top-three sets also change: minimum scenario {12,20,21}; mean/dynamic diagnostics {10,12,20}. These are missing-policy diagnostics, not a final recommendation, a six-criterion model, or evidence of robustness. Original source coverage is displayed separately from complete scenario coverage in dictionary/admission records and Excel.

The validator checks actual substitutions against recomputed source statistics, preserves observed values, cross-checks the published archive, and requires correct per-cell flags. A notes tag alone cannot authorize a missing or arbitrary value. Coverage 24 for each City analysis column describes that constructed scenario, not 24 genuine observations. Baseline, orientation and scenario comparability remain under review; no final `admitted` status is asserted.

Batch geometry uses a reproducible named-road graph and 500 m buffers in EPSG:2952, with exact source segment/node IDs and per-corridor endpoint evidence. The archived source subset retains 3,270 original features from the official 64,384-feature City download. Seventeen road proxies are available; IDs 4/5/6/8/9/10/19 still need future alignments/endpoints. No straight-line surrogate or missing-link bridge is introduced. Pioneer Village is anchored near Northwest Gate/Steeles, Milliken near Redlea/Steeles, and Wilson's western approach uses Walsh Avenue, based on operator descriptions. Selected Allen Road endpoint splits are planar source-road crossings, not claims of grade connectivity or transfer access. Every geography remains provisional and subject to review.

Official profiles for 249 intersecting CTs produce 15 complete provisional equity estimates in `data/supplemental_model_inputs_v0.4.csv`. Corridors 3 and 21 are also missing because CTs 5350205.00 and 5350006.00 have positive total populations (144 and 119) but suppressed LIM counts. Their model values stay blank; conditional suppression-only bounds are in the batch audit. Source counts are never dropped from a denominator to manufacture completeness. Areas outside the CT cartographic land frame are reported for review (not assigned an invented population). Corridor 01 reproduces the prior 15.9119% result exactly. All 24 output rows remain present.

The City construction lengths and all original master cells are preserved. Measured road lengths for the two Jane subsections disagree substantially with the source length assignments; these are review flags, not a reason to swap source values. City current ridership is length-scaled, so the discrepancy also needs review before final interpretation. The Waterfront construction-length discount must not be mistaken for full route length.

`model_ready=false`: nine equity values are still missing (3,4,5,6,8,9,10,19,21), all geographic reviews are pending, and admission/comparability reviews remain unresolved. The 1,056 blank raw inventory cells are not what blocks the selected processed-input model. Current tests cover source/flag preservation, missing-value bypass rejection, 24-alternative retention and batch suppression handling.

Offline reproduction in the existing GIS environment:

```sh
python -B code/analyze_city_missingness.py
python -B code/build_corridor_road_proxies.py
python -B code/batch_corridor_equity.py
python -B code/register_v0_4_inputs.py
python -B -m unittest discover -s code -p 'test_*.py' -v
python -B code/validate_data.py --output outputs/validation_v0.4.json
```

The batch Census script downloads official geometry/profiles only when explicitly run with `--acquire`. The road builder uses the archived named-road subset; `--full-city-source` refreshes that subset from a separately acquired official whole-city GeoJSON. The 93 MB full download and temporary map renders are outside Git. To rebuild the current Excel views, set the available `ARTIFACT_NODE_MODULES` path and use `SKIP_WORKBOOK_PREVIEWS=1 node code/build_workbooks.mjs`.

## v0.3: PPI withdrawn; Census low-income equity proxy

The current state is `CONTINUATION_v0.3.json`, with results in `outputs/low_income_pilot_v0.3/review.html` and readiness in `outputs/validation_v0.3.json`. Earlier v0.1/v0.2 handoffs, inventories, review pages and checks are historical. The authoritative dictionary/admission JSON and its generated XLSX review views are updated for this pivot.

The selected sixth candidate is `low_income_population_share_500m`; PPI is withdrawn from selection and no longer an acquisition objective. This is a new independent Census measure, not a renamed City Palma ratio. Official Census Profile characteristics 326 (LIM-AT low-income count), 1 (total Census population) and 321 (LIM-applicable private-household population for comparison) are archived, with labels, flags, query URLs and checksums. Income is measured for 2020, population/geography for 2021, and the road-proxy snapshot for 2026.

The user approved one consistent CT area-weighting rule for the complete pilot and future corridors after a DA source suppression was found: `a_it = area(buffer_i intersect CT_t) / area(CT_t)`, then `share_i = sum(a_it * L_t) / sum(a_it * P_t)`. Total population and low-income population are assumed uniform within each CT cartographic polygon. This is an explicit spatial-estimation assumption; missing source counts are never filled. The continuous 500 m road buffer and endpoint proxies still require geographic review and are not station walksheds.

Corridor 01 intersects 14 CTs with complete counts. Estimated low-income population is 4,851.748955 and total population 30,491.282436, yielding **0.159119216 (15.9119%)**. The denominator includes all residents, while LIM applies to private households; the custom share must not be called official LIM prevalence. Dividing by the estimated LIM-applicable population of 30,321.090939 gives a separate comparison of **16.0012%**. Higher custom share is the user's chosen direction for greater priority; it measures resident concentration, not realized transit benefits.

The finer comparison uses 48 DAs; the earlier 174 features are DBs, not DAs. DA 35202414 has a suppressed LIM-AT count (FLAG 6), so the complete DA numerator and ratio remain unavailable. Its known-contribution and suppression-only bounds are separately labelled in the audit; the missing source is not replaced with a CT estimate. The user-approved CT method is applied independently to all contributing tracts. The DA population estimate, 31,150.880639, is 2.1632% above the CT estimate. Both lie within the earlier DB bounds; this checks compatibility only and does not establish that uniformity is correct.

The DB population midpoint is `(25,300 + 40,059)/2 = 32,679.5`. It is a midpoint, not an area-weighted estimate. The pilot includes `low_bound`, `midpoint_population` and `high_bound` denominator-only stress scenarios, keeping the CT numerator fixed. These are not confidence intervals or jointly estimated demographic allocations. No ranking sensitivity is asserted.

`data/supplemental_model_inputs_v0.3.csv` retains all 24 alternatives: one pilot estimate and 23 blank `pending_collection` rows. `data/equity_proxy_method_v0.3.json` records the policy. `data/workbook_records_v0.1.json` remains authoritative; the proxy is `pending_collection`, PPI is `withdrawn_from_selection`. A new blank raw placeholder and 24 observation-status rows maintain the inventory contract; the derived proxy is stored only in its mapped supplemental file. There are now 44 longlisted concepts and 1,056 empty raw cells; these unselected raw gaps do not determine processed-model readiness.

The five preserved City columns have coverage **17, 24, 20, 20, 17**, totalling **98/120** values. The 22 missing cells occur inside those selected five columns, not in 22 separate unused indicators. A complete six-column selected matrix currently lacks 45 cells (22 City plus 23 proxy). Admissions, baseline/scenario interpretation and geographic comparability remain unresolved. No zero fill, corridor removal or false `coverage_count=24` is used to obtain `model_ready=true`.

Offline reproduction in the isolated GIS environment:

```sh
python -B code/calculate_low_income_proxy.py
python -B -m unittest discover -s code -p 'test_*.py' -v
python -B code/validate_data.py --output outputs/validation_v0.3.json
```

To intentionally refresh dictionary/admission records from the calculated pilot, run `python -B code/register_low_income_proxy.py`. Rebuild their XLSX views with `ARTIFACT_NODE_MODULES` set to the available artifact-tool Node module directory and `SKIP_WORKBOOK_PREVIEWS=1 node code/build_workbooks.mjs`. This refreshes inspection dumps without producing preview figures. Source acquisition is separate: `python -B code/acquire_low_income_support.py` repeats public downloads; archived inputs suffice for offline calculation.

Next work is reviewed geometry and CT overlays for the remaining 23 corridors, and a resolution of missing/non-comparable selected City inputs. The AI-use participation-rule issue documented in v0.2 remains unresolved. The sections below preserve the historical strategies and are superseded by this v0.3 state wherever they describe PPI as selected or population estimation as absent.

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
