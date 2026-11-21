# TRUST-Line - UGCC 2026

## v0.5: complete declared proxy scenario (current)

Current handoff: `CONTINUATION_v0.5.json`. Validation: `outputs/validation_v0.5.json`. Review: `outputs/review_v0.5.html`. All earlier version sections below are historical snapshots; v0.5 supersedes their current-coverage and no-Census-imputation statements. Project artifacts use English; user status reports use Chinese.

The six selected analysis columns now contain 144 finite inputs for all 24 corridors. The joined analysis matrix is `data/model_matrix_v0.5.csv`; City columns retain published-score units and equity retains a raw fraction, so apply the documented diagnostic standardization before aggregation. The five City columns retain 98 original published scores and 22 separately flagged observed-column-minimum substitutions (`imputed_conservative_min`). The original source table and 1,056-cell raw inventory remain unchanged. Equity has 24/24 **scenario estimates**, of which 21 catchments use fully observed CT counts and three contain estimated contributions from suppressed CTs. This is not 24 fully observed measurements.

### Seven additional road proxies

`code/batch_endpoint_road_buffers.py` uses GeoPandas, an official Statistics Canada 2021 Road Network File extract covering the GTA, an undirected source-endpoint graph, and sourced longitude/latitude input pairs for corridors **4,5,6,8,9,10,19**. It snaps points to source road edges, computes shortest paths and buffers them by 500 m in EPSG:2952. `--acquire-roads` queries an endpoint-driven geographic envelope with a routing margin; the acquisition manifest records exact bounds, URLs and hashes. No missing graph link is invented; internal planar crossings do not automatically become network junctions. Node coordinates are rounded to 0.01 m. This cartographic network is not a turn-restricted driving router.

The endpoint table is `data/corridor_endpoint_coordinates_v0.5.csv`; full provenance and assumptions are in the adjacent JSON and `evidence/corridor_batch_v0.5/endpoint_reference_review.json`. TTC/GO/UP official GTFS supplies operating-stop coordinates. Ontario Place uses the City centreline node at the operator-described west entrance. **Future Woodbine GO has no surveyed coordinate in the reviewed official page: its numeric anchor is an explicitly secondary approximate coordinate, cross-referenced to Metrolinx's Highway 27 rail-corridor location.** Markham Centre is represented by Unionville GO mobility hub; Pearson by Terminal 1 UP Express; the northern Ontario Line proxy assumes Don Mills Road/Steeles. These choices were authorized as provisional endpoint assumptions and still require review. Woodbine anchor uncertainty (about 250 m), future station sites and route branches have not been resolved by the count-imputation sensitivity test.

All seven routes are current-road geometry scenarios, not approved future transit alignments. Their path lengths are 9.532, 2.892, 4.300, 4.701, 10.560, 4.514 and 9.917 km respectively. They are combined with the prior 17 named-road proxies, preserving those geometries. The two path-building methods and 2021 RNF versus prior current City-road vintages are a comparability limitation. City assumed construction lengths are preserved and are not substituted for full path length. Station catchments, grade connectivity, coastlines and the Jane subsection length anomalies remain under review.

### CT allocation and suppression

Official profiles cover **305 intersecting CTs**. The same uniform within-CT area allocation applies everywhere:

`sum(CT intersection area / CT polygon area * analysis LIM count) / sum(CT intersection area / CT polygon area * total population)`.

LIM count is Census characteristic 326; total population is characteristic 1. Income reference is 2020 and population/geography is 2021. This custom all-resident denominator differs from the official private-household LIM universe (characteristic 321); the result is a resident-concentration proxy, not official LIM prevalence or a transit-benefit measure. Cartographic polygon support and uncovered area are reported without inventing residents outside the source land frame. The corridor 1 pilot remains 15.9119216%.

CT **5350205.00** (population 144) and **5350006.00** (population 119) both suppress LIM counts. The complete CT-to-DA membership check finds one DA per CT (35204701 and 35201461 respectively); their populations reconcile, and both DA LIM cells are also suppressed. A partial DA sum cannot be used as a complete CT count.

The user authorized the fallback: acquire every Toronto CT profile, retain the **583 complete positive-population CTs** from 585 municipal CTs, compute the unweighted median of each CT's `LIM count / total population`, then multiply by the suppressed CT's total population. The median rate is **0.1147842056932966**; the mean sensitivity rate is **0.12657021072488234**. Constructed CT counts are 16.52892562 and 13.65932048 respectively. These are model scenario estimates, never newly observed source counts. CT municipality membership is checked against the archived GAF crosswalk; its earlier third-party-mirror/official-checksum limitation remains documented in v0.2.

`data/census_ct_batch_v0.5.csv` retains original blank source counts and flag 6. The separate analysis table, allocation ledger and `suppression_imputation_trace.csv` identify `suppressed_CT_imputed`, formula, donor pool, source flags and mean alternative. **Corridors 3,8,21** intersect these CTs; corridor 8 is newly exposed by the batch geometry. Both original and estimated counts remain distinguishable.

### Baseline review and readiness

`baseline_comparability_audit.csv` reconciles all 24 baseline IDs and checks the prerequisite graph for missing IDs and cycles. Eight corridors (3,6,11,13,14,16,17,24) have conditional baselines. City Attachment Section 2.5 (physical pp.3-4) explicitly describes benefits conditional on prior corridors. The four current TTC measures use existing observations (Fall 2022 where specified; no separate year stated for current maximum load), whereas unimproved load belongs to the projected forecast framework. Filling a missing score does not create a common-baseline forecast counterfactual. Numeric range overlap is recorded only descriptively; corridor 10's forecast score lies outside the range of corridors with all five source scores. No arbitrary acceptance threshold or baseline equivalence is asserted.

The validator now replays Census median/mean replacements from archived official profiles, checks complete DA membership/population, verifies source hashes and flags, and reconciles CT weighted totals to every corridor input. It continues to verify the 22 City substitutions against the source statistics. **A notes label never waives an absent or arbitrary value.** Final admission still requires actual geographic and comparability reviews. Both workbooks expose a separate `scenario_admission_status=admitted_for_declared_proxy_scenario` for the six complete analysis inputs; final `admission_status=pending_comparability_review` remains explicit.

Current results: `valid_structure=true`, `data_matrix_ready=true`, `scenario_computation_ready=true`, `model_ready=false`. The remaining final-readiness reasons are review/evidence gaps, not missing selected values. This preserves the original final-model gate while permitting the fully specified scenario calculation.

### Sensitivity and verification

The six-criterion equal-weight diagnostic retains published City z scores and standardizes the equity proxy across all 24 corridors using population SD. It is exploratory, not a final ranking recommendation. Changing Census median to mean shifts equity by at most **0.00335 percentage points** and changes no ranks in this diagnostic. Changing City minimum substitutions to means moves an individual rank by up to **8**, and available-case dynamic weighting by up to **12**; dropping projected unimproved load moves one by up to **5** and changes the top-three set. The first two City missing-data alternatives retain the diagnostic top-three set but do not make all individual ranks robust. Full outputs are in `six_criterion_policy_diagnostic.csv` and `scenario_review_summary.json`.

All **26 tests pass**, including independent GeoPandas CT replay for the seven new corridors, pilot regression, source suppression preservation, invalid-value/flag rejection and disconnected crossing behavior. Workbooks and input metadata are current. No new competition slides or final recommendation are asserted.

Offline reproduction after installing `code/requirements_gis.txt`:

```sh
python -B code/prepare_endpoint_inputs_v0_5.py
python -B code/batch_endpoint_road_buffers.py
python -B code/calculate_equity_v0_5.py
python -B code/register_v0_5_inputs.py
python -B code/review_scenario_inputs_v0_5.py
python -B code/validate_data.py
python -B -m unittest discover -s code -p 'test_*.py' -v
```

Official RNF source pages are losslessly packed in `evidence/corridor_batch_v0.5/official_RNF_source_pages.zip`, with ID reconciliation, URL and hash manifests. The script reads them directly for offline runs. Fresh acquisition: `python code/acquire_endpoint_stops_v0_5.py`; `python code/batch_endpoint_road_buffers.py --acquire-roads`; then `python -c 'import sys; sys.path.insert(0,"code"); from batch_corridor_equity import acquire; acquire(version="v0.5")'` for matching geometry/profile inputs. `python code/acquire_v0_5_support.py profiles` refreshes the official municipal/DA profiles. Fresh downloads can change source vintages; review manifests and rerun calculations/validation. Rebuild Excel with `node code/build_workbooks.mjs` using the local artifact-tool dependency path as configured in that script.

Evidence, reproducible data preparation and modelling-readiness review for the UTSRI x NRCI 2026 UGCC statistics case, "Drawing Toronto's Line of Best Fit".

## Start here

- [Latest v0.4 continuation](outputs/project/CONTINUATION_v0.4.json)
- [Missingness and batch equity review](outputs/project/outputs/review_v0.4.html)
- [Current project instructions](outputs/project/README.md)
- [Input coverage](outputs/project/data/model_input_coverage_v0.1.csv)
- [Validation](outputs/project/outputs/validation_v0.4.json)
- [Original handoff (historical)](outputs/project/HANDOFF_v0.1.md)
- [Repository setup and upload scope](REPOSITORY_SETUP.md)

## City missingness: pattern B

The preserved source has 98 observed values and 22 blanks across five selected columns. All gaps occur in seven corridors:

| Corridor IDs | Missing columns | Cells |
| --- | --- | ---: |
| 4, 6, 8, 10 | current_speed, current_max_load, current_ridership, competitiveness | 16 |
| 3, 5, 13 | current_speed, competitiveness | 6 |

The other 17 corridors are complete; no corridor has all five columns missing. Column missing counts are 7, 0, 4, 4, 7. Repeated missingness is not treated as random or automatically equivalent to absent benefits.

The user-authorized [analysis scenario](outputs/project/data/city_analysis_inputs_v0.4.csv) retains every observed score and substitutes the observed column minimum only in the 22 originally blank cells. Per-cell `imputed_conservative_min` flags and a [trace](outputs/project/outputs/missingness_v0.4/imputation_trace.csv) identify every substitution. The original score file and source archive are unchanged. Observed minima are not verified theoretical lower bounds; this scenario can penalize new/extension corridors with unavailable existing-service measures.

Observed-mean and available-case dynamic-weight diagnostics were computed across all 24 corridors using five equal City weights. Relative to the minimum scenario, ranks move by up to **14** and **16** places, respectively, and the top-three sets change. The policy is **not robust** in these diagnostics. These results exclude equity and are not a final recommendation.

## Batch equity progress

PPI remains withdrawn. The selected equity proxy is the user-approved CT area-weighted LIM-AT population share in a 500 m continuous corridor buffer, under uniform within-CT density. The numerator's income reference year is 2020, Census population/geography are 2021, and current road geometry is from 2026. The all-resident denominator makes this a custom share, not official LIM prevalence.

The batch pipeline uses official road and Census sources, retains all 24 output rows, and produces:

- **17** current-road proxies with source segment IDs, endpoint evidence and topology checks;
- official Census profiles for **249** intersecting CTs;
- **15/24** complete provisional equity estimates;
- **7** unresolved future alignments/endpoints: IDs 4, 5, 6, 8, 9, 10, 19;
- **2** additional Census-suppressed cases: ID 3 (CT 5350205.00, population 144) and ID 21 (CT 5350006.00, population 119).

The two suppressed income counts remain missing; no zero fill is inferred from positive population. Conditional suppression-only intervals are reported separately. The named-road proxies and station-area endpoints all require geographic review. Areas outside the CT cartographic frame and source-versus-road length discrepancies are logged. The measured Jane subsections do not agree with their source construction-length assignments; original lengths and scores are preserved for review.

Corridor 01 reproduces its earlier **15.9119%** custom share. Its CT area-weighted population is 30,491.28 and low-income count 4,851.75. The separate LIM-applicable-population comparison is 16.0012%. The population-bound midpoint 32,679.5 remains a denominator-only stress scenario, not an area-weighted estimator.

## Readiness and validation

**model_ready remains false.** The active City analysis scenario is complete (120 values, including 22 declared substitutions), but the source is still only 98 observed values. Nine equity values remain unavailable, and baseline/admission/geographic reviews are unresolved. The validator verifies actual statistics, preserved observations and per-cell flags; a notes string cannot bypass missing data. Unselected raw inventory blanks do not block this processed strategy.

From `outputs/project`, in the isolated environment described by `code/requirements_census_v0.2.txt`:

```sh
python -B code/analyze_city_missingness.py
python -B code/build_corridor_road_proxies.py
python -B code/batch_corridor_equity.py
python -B code/register_v0_4_inputs.py
python -B -m unittest discover -s code -p 'test_*.py' -v
python -B code/validate_data.py --output outputs/validation_v0.4.json
```

Archived sources suffice for offline reproduction. `batch_corridor_equity.py --acquire` explicitly refreshes public Census downloads. Current dictionary/admission JSON and Excel views distinguish source coverage from scenario coverage. Workbook generation supports `SKIP_WORKBOOK_PREVIEWS=1` to avoid new preview figures.

## Repository layout and history

```text
outputs/project/       Current canonical project
outputs/*.zip          Historical delivery archives
reference/competition/ Original case and guideline PDFs
work/                  Historical helpers/intermediates; read before reuse
```

Old registrations and work generators can restore earlier mappings; use the v0.4 instructions for the current state. Original Windows paths are historical. Runtime/vendor trees, the 93 MB full centreline download and scratch assets are excluded. `UPLOAD_MANIFEST_v0.4.csv` describes this upload; earlier manifests and review pages remain historical. The participation-rule AI-use issue recorded in v0.2 remains unresolved.
