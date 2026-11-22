# TRUST-Line input strategy and evidence inventory

## Task 2 v0.3: executable assumption baseline and sensitivity (current)

The user's rounded cost points **CAD0.35B / 0.95B**, relative ridership **1 / 1.2**, and one-way savings **2.5 / 3.5 min** now run through a provisional BRT/LRT model. Cost per km is **CAD49.29M / 133.78M**, reported without another cost weight. The main three criteria are relative demand per cost, relative demand and time savings. Source values and strict feasibility gates are unchanged.

Ratio-to-best normalization and equal weights give **BRT 0.849206 / LRT 0.814035**. The efficiency-weight tie is **28.8477%** when other weights split equally. Service-priority weights or min–max normalization select LRT. Ten thousand fixed-input Dirichlet weight draws give BRT **51.45%** support in the ratio model and **25.36%** in min–max; these are illustrative preference shares, not confidence. Eight input cases, two efficiency definitions and two normalization methods expose dependence on assumptions and conceptual overlap.

**77 tests pass.** The assumption model is executable; full capital, absolute demand, engineering/delivery certification and final Task 2 selection remain incomplete. The cost points are rounded choices rather than exact previous interval midpoints, and neither grade separation nor a measured demand/TSP advantage is attributed automatically to LRT.

[Baseline report](outputs/task2_v0.3/BASELINE_MODEL.md) · [Input table](outputs/task2_v0.3/baseline_inputs.csv) · [Decision sensitivity figure](outputs/task2_v0.3/baseline_decision_sensitivity.png) · [Four-slide review deck](slides/task2_baseline_v0.3_review_draft.pptx) · [Continuation](CONTINUATION_task2_v0.3.json)

## Task 2 v0.2: conditional shortlist (preserved policy)

**BRT and LRT: Conditional Pass. Subway: excluded from the conservative base-case shortlist by policy.** Scenario development can proceed with the two surface technologies. This changes provisional admission, not the original CAD16.657B / nine-year / 2035-12-31 / route-and-depot constraints. A verified hard failure overrides conditional admission; an evidenced scheme clearing all gates can reopen the Subway decision.

No physical-infeasibility proof or zero Wilson surplus is asserted. The user's BRT CAD0.29–0.40B and LRT CAD0.77–1.20B ranges are explicitly partial historical cost scenarios with different monetary bases, not full capital estimates ready for scoring. Twelve release/reconsideration conditions remain tracked. No weighted technology ranking or final winner is claimed. **67 tests pass**, including checks that the policy cannot relax hard limits and that v0.1 evidence/artifacts remain unchanged.

[Decision note](outputs/task2_v0.2/DECISION_NOTE.md) · [Policy screen](outputs/task2_v0.2/technology_policy_screen.csv) · [Condition register](outputs/task2_v0.2/conditions_register.csv) · [Three-slide review deck](slides/task2_screening_v0.2_review_draft.pptx) · [Continuation](CONTINUATION_task2_v0.2.json)

## Task 2 v0.1: original hard-evidence gate (historical admission policy)

The corridor is fixed at **23, Finch Ave E, Yonge–Victoria Park, 7.101 km**. The pre-MCDA gate now requires capital ≤ **CAD 16.657B**, total delivery ≤ the user-directed **nine-year window**, operational opening by **2035-12-31**, a feasible complete route and an allocated compatible depot/storage/maintenance strategy. Only four passes allow scoring. Conditional or unknown evidence stays outside the ranking; a verified failure excludes the alternative.

The technology evidence table contains **29 sourced reference records plus 12 explicit target-estimate gaps**. Reference costs, riders and journey times retain their own project scope, monetary basis and units. BRT/LRT/Subway are currently **pending evidence**, with no proven hard exclusion and no weighted technology ranking. The illustrative subway unit-cost envelope gives CAD 3.5505–7.101B, but cannot yet certify a complete capital estimate. A sequential example schedule excludes Subway only within its stated assumptions, not as a universal technology finding.

City evidence shows Finch East's planned 36m ROW still requires local frontage acquisition; this is not a measured full-route width. TTC identifies a new Line 1 TMSF requirement, not free Wilson capacity. Signal-priority evidence is recorded with its actual per-intersection/round-trip context, without turning Task 1 standardized speed into minutes. **59 tests pass**, including 12 new gate tests. Task 1 source values and existing analysis outputs are preserved.

[Hard-constraint report and evidence findings](outputs/task2_v0.1/HARD_CONSTRAINTS.md) · [Screen results](outputs/task2_v0.1/hard_constraint_screen.csv) · [Technology evidence](evidence/tech_evidence_v0.1.csv) · [Dictionary](evidence/tech_evidence_dictionary_v0.1.md) · [Continuation](CONTINUATION_task2_v0.1.json)

## v0.8: formal model argument and its boundaries (current)

The current provisional primary remains **23: Finch Ave E, Yonge–Victoria Park** under the declared five-criterion transport-service/equity model. Formal EDA, conceptual budget controls, weight rationale, three-principle coverage and quantitative assessment of all 24 are documented.

No indicator pair reaches the predeclared |correlation|≥0.7 screen. Source-available forecast/current-load Pearson r=0.151 (n=13); low sample correlation does not erase conceptual over-weighting. Corridor 23 remains top-three in all eight concept-budget cases, but wider tests disprove “100% immunity”: top-five inclusion is 81.82% under a broad block-weight prior, 97.63% in the illustrative 10%–60% budget subset, and it can rank sixth after fixed-budget removal of competitiveness. These results do not replace the original paired-support 100% figure; they bound that claim.

All 24 now have five-variable contextual scores in six cases (144 rows). Eight conditional corridors retain complete prerequisite/bundle assessments and no fabricated common-base absolute rank. Their independent Base-0 optimality is not identified.

Three-principle coverage is explicitly partial: Serve People has scored need proxies; Strengthen Places has unscored residential-intensity context but no direct housing/growth outcome; Support Prosperity has the City's current-load Affordability proxy but no measured jobs/productivity. Do not describe the five measures as a complete balanced RTEF model. **47 tests pass**, source values and nominal policies are unchanged, and Task 1 is not declared complete.

[Formal justification](outputs/model_argument_v0.8/MODEL_JUSTIFICATION.md) · [Correlations](outputs/model_argument_v0.8/correlation_pearson.png) · [All-24 coverage](outputs/model_argument_v0.8/all24_evaluation_coverage.csv) · [Updated review slides](slides/model_argument_v0.8_review_draft.pptx)

## v0.7: Jane source audit and five-criterion exclusion stress (current)

The current provisional Task 1 primary is **23: Finch Ave E, Yonge St–Victoria Park Ave**. The disputed `current_ridership` column is excluded from the active five-criterion stress model; source scores and lengths are preserved. The original v0.6 six-criterion model remains the frozen paired baseline.

Fresh official PDFs match the archives. Evaluation Table 2 (physical p.7) labels 4.076 km as Jane corridor 12's **assumed construction length**, with no one-side/one-direction/extension annotation. It does not establish the true full physical length. The 11/12 entries suggest a possible transposition; neither an official correction nor the internal standardized-score denominator has been established.

With identical 10,000 selectors (seed 20261121), retained equity calibration and proportional surviving weights, Jane 12 moves from first in all six cases to ranks **2–9**; top-five frequency falls from **100% to 66.59%**, top-three to **33.66%**. Finch East 23 remains top-five in **100%**, ranks **1–2** and is the only candidate exceeding 90% top-five inclusion in both models. Apply the user-authorized switch to 23; do not claim the length issue is resolved or harmless.

Current active selection: `data/model_input_selection_v0.7.json`; decision: `data/task1_decision_v0.7.json`. The legacy `model_input_selection_v0.1.json` still maps the preserved six-criterion baseline. **40 tests pass**. The five-criterion stress validator reports ready, while Task 1 completion and Jane length resolution remain false. Older version sections below are historical snapshots.

[Full v0.7 report](outputs/jane_stress_v0.7/REPORT.md) · [Paired rank chart](outputs/jane_stress_v0.7/jane_finch_rank_stress.png) · [Stress validation](outputs/validation_v0.7.json) · [Updated review deck](slides/jane_length_stress_v0.7_review_draft.pptx)

## v0.6: tiered comparison, 10,000 draws and limited-scope readiness (current)

The user authorized a tiered proxy-scenario model. Sixteen `CITY_BASE_0` corridors form the main ranking; eight conditional extensions are evaluated with prerequisite closures and additional union catchments, without pooled absolute ranks or summed City z scores. All 24 alternatives remain assessed.

The shortlist is **12 (Jane St), 23 (Finch Ave E), 20 (Wilson Ave W)**. Only **12 and 23** exceed 90% top-five inclusion; both score 100% in the six exact cases and 10,000 fixed-seed draws. Corridor 20 has 66.34% sampled top-five inclusion and is a weight-sensitive third candidate. No single final winner is selected. Jane length/source-score anomalies remain a material limitation.

Equity is z-scored using the 16 main-tier reference population before aggregation. Two City missing-value methods and three declared weight profiles define six distinct cases; 10,000 PCG64 draws (seed 20261121) resample these cases, with exhaustive verification. Frequencies describe these assumptions, not statistical confidence or all possible weights. Exact scenario criteria determine the shortlist so sampling noise cannot break exact ties.

Woodbine's nominal plus eight 250m anchor bearings were rebuilt for both linked corridors (18 routes/buffers/CT allocations). The shortlist set is unchanged in these local tests. Corridor 5 path lengths vary 2.612–4.520 km; completed sensitivity does not verify the official station site. Source and analysis values remain separate.

Current validation: `core_ready=true`, `limitations_ready=true`, `model_ready=true`, `limitations_flagged=true`, **`unrestricted_model_ready=false`**. Six indicators are `admitted_with_limitations`. The updated flag explicitly means an executable tiered proxy model; it does not certify the old unrestricted model, future transit geography, final project feasibility or competition submission clearance. **34 tests pass.** Earlier version sections below are historical snapshots.

[Full v0.6 report](outputs/tiered_v0.6/REPORT.md) · [Review page](outputs/review_v0.6.html) · [Validation](outputs/validation_v0.6.json) · [Draft slides](slides/tiered_robustness_v0.6_review_draft.pptx)

Account transfer: read [the current handoff](../../HANDOFF_NEXT_ACCOUNT_2026-11-21.md) before continuing from older snapshots.

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
