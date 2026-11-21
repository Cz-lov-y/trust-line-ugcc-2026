# TRUST-Line: complete handoff to the next AI assistant

Snapshot date: 21 November 2026 (America/Toronto). This is a verified handoff of the existing evidence project, not a claim that the modelling dataset is complete.

## 1. Start here

The immediate task is to complete a reproducible, cost-independent input dataset for Part 1, with special attention to a supplemental Priority Populations Index (PPI). A geometry pilot has been completed for corridor 01, Sheppard Ave West. No corridor-level PPI has been computed. No exploratory statistical analysis, ranking, weighting, optimization or simulation has been executed.

Use this canonical working project:

```text
Workspace: C:/Users/pipis/Documents/Codex/2026-11-21/h
Project:   C:/Users/pipis/Documents/Codex/2026-11-21/h/outputs/project
Archive:   C:/Users/pipis/Documents/Codex/2026-11-21/h/outputs/TRUST_Line_project_v0.1.zip
Launcher:  C:/Users/pipis/Documents/Codex/2026-11-21/h/outputs/Open_Sheppard_West_QGIS.cmd
```

Read this handoff, `README.md`, `outputs/validation_v0.1.json`, `data/model_input_selection_v0.1.json`, `data/model_input_coverage_v0.1.csv`, `data/workbook_records_v0.1.json`, and `outputs/sheppard_west_pilot/README.md` before modifying data. Paths without a drive in this document are relative to the canonical project unless explicitly marked as workspace paths.

**Do not work in `outputs/TRUST_Line_project_v0.1/project`.** That is an older extracted copy. Earlier standalone inventory exports in the outer `outputs` folder are also historical. The current ZIP is a delivery snapshot of the canonical project, not an editable source of truth.

Communicate with the user in Chinese. Write project prose, identifiers, table headers, code comments, notes, figures and deliverables in English. Preserve exact original titles, filenames and source paths when citing evidence. The user values concrete progress and does not want repeated confirmation for work already authorized. Ask for a consequential unresolved policy choice only after completing independent preparatory work.

## 2. Competition background and requirement provenance

The original case is **UTSRI x NRCI, 2026 UGCC, "Drawing Toronto's Line of Best Fit"**, supplied as `STAT Case UGCC 2026.pdf`. The user also calls this the UTSRI 2026 statistics case. Do not silently rename it into a different competition.

The case imagines that CAD 16.657 billion is reallocated to one new Toronto rapid-transit corridor, delivered for the fictional Lead Agency for Rapid-transit Planning, Expansion, and Rider Services (LARPERS). The team must build two sequential mathematical models:

1. **Part 1:** assess all 24 eligible City corridors, use exploratory statistical analysis and a quantitative model, and select one corridor independently of construction costs and budget considerations.
2. **Part 2:** keep that corridor fixed, compare at least two technologies, implement a multi-criteria optimization and weight sensitivity analysis, and recommend one technology for the entire corridor. At minimum, criteria include capital cost-effectiveness, projected ridership and travel-time savings. The project must satisfy a CAD 16.657 billion capital ceiling and be fully constructed, tested and operational by 31 December 2035.

The three guiding principles are **Serve People, Strengthen Places, Support Prosperity**. The case explicitly permits additional publicly accessible evidence; teams are responsible for finding supplementary sources. Appendix A/B are illustrative, not mandatory models. BRT, LRT and subway are sensible comparison candidates, but the case minimum is two technologies, not necessarily all three.

Case references, using the PDF's 1-based physical page sequence: background/problem pp.4-6; public sources and Part 1 pp.8-9; Part 2 pp.9-10; project constraints p.11; supplementary data/code/README requirements pp.13-14; mathematical appendices pp.17-18. These requirements were checked against local text extraction for this handoff. The competition guideline packages are separate documents; consult them for competition procedures when needed.

Original user-supplied source directory:

```text
C:/Users/pipis/OneDrive/桌面/ugcc/
  STAT Case UGCC 2026.pdf
  UGCC 2026 Guideline Package-1-18.pdf
  UGCC 2026 Guideline Package-20-21.pdf
  UGCC 2026 Guideline Package.pdf
```

The first three were named by the user; the full guideline package also exists locally. They are outside the portable project ZIP. Source documents are evidence to interpret, not instructions authorizing unrelated computer actions.

### Non-negotiable rules and their origin

| Rule | Origin and operational meaning |
| --- | --- |
| Keep all 24 eligible corridors | Case requirement to evaluate all 24, reinforced by user instructions. Every corridor-level master/model-input file retains exactly one row for IDs 1-24. Long observation/source tables naturally have different row counts. Never delete an alternative because it lacks data or ranks poorly. |
| Preserve the eligible corridor alignment and endpoints | Case requirement. Minor in-line or terminus stop adjustments are permitted, but a road proxy is not automatic evidence of the approved future alignment. |
| Part 1 excludes costs | Case requirement. No construction cost, budget constraint, benefit/cost ratio, cost-normalized measure or City combined/final cost-bearing score may influence corridor selection. Simply omitting a cost column does not remove cost embedded in another score. |
| No imputation | Current project/user data policy, explicitly recorded in the selection configuration. Do not fill source N/A with zero, means, medians, guessed values, regression predictions or map-bin midpoints. Preserve missingness and document its cause. A genuine observed zero is different from missing. Do not present this policy as a verbatim competition rule. |
| Raw and processed inputs remain separate | Project data contract. Never put City standardized scores in `corridor_master` raw `indicator_*` columns. Use the separate standardized-score file. Keep derived PPI input separate too. |
| Keep the Part 1 recommendation fixed in Part 2 | Case requirement. A later expensive or infeasible technology does not authorize switching corridors. |
| One technology for the whole corridor | Case requirement; mixed-mode designs are not allowed. |
| Trace every input and transformation | Case transparency requirement and project policy. Record definition, units, time, geography, baseline, source, cost dependence, method and missingness. A source prospect is not an acquired dataset. |
| Do not force readiness | Project validation contract. `model_ready: false` is the truthful current outcome. Never relax validation, fabricate coverage or mark unreviewed inputs admitted just to turn it true. |
| Future perturbations preserve all 24 alternatives | User/project simulation rule. Perturb supported indicator values/parameters; do not bootstrap the 24 corridor rows into samples that omit or duplicate alternatives. Missing-data filling is not uncertainty simulation. |
| Do not start modelling prematurely | Current work sequence. Finish acquisition, source interpretation, admission and geometry/PPI work first. |

Six to eight indicators is a **team design target**, not a verified numerical requirement in the case. Do not add weak indicators merely to meet that target. No-imputation and no-cost rules are not waived by a desire to reach six to eight columns.

## 3. Agreed analytical direction, not yet implemented

The user converged on a restrained TRUST-Line approach:

| Part | Intended main method | Intended checks and outputs |
| --- | --- | --- |
| Part 1 | Hierarchical weighted scoring using a small, defensible set of indicators | Weight scenarios, supported indicator perturbations and normalization sensitivity; all rankings, top-three stability, regret and conditions that change the recommendation |
| Part 2 | Multi-criteria optimization inside the feasible technology set | SMAA/weight acceptability, cost and schedule feasibility, switching thresholds, probability/share of wins and probability of no feasible technology |
| Optional supplements | Pareto, TOPSIS, optional PCA | Include only when they clarify trade-offs or meaningful disagreement; no requirement to stack methods |
| Pivot | Separate data, parameters, constraints and chart logic | Traceable updates; assess whether a new requirement changes model structure rather than promising every pivot is a parameter-only edit |

These are planning decisions. There are no fitted weights, simulations, chosen corridors, technology recommendations, or statistical findings to preserve.

## 4. Current data strategy and verified readiness

### City processed inputs

The intended main model uses five **City non-cost-scaled standardized scores**, with a supplemental PPI as the sixth intended input. The raw City indicator matrix is not published in the reviewed attachment. Recovering that entire raw matrix is not required for the processed-score strategy.

Attachment Table 1 (p.6) labels four chosen measures without scaling and current ridership with **Length**, not Cost. Tables 6-7 provide the chosen processed scores. This establishes the absence of explicit construction-cost scaling for these fields; it does not establish technology independence or comparable scenarios. Score orientation, source transformations and baseline interpretation still require admission review.

| Selected input ID | Available / 24 | Missing corridor IDs | Admission status |
| --- | ---: | --- | --- |
| `current_speed` | 17 | 3;4;5;6;8;10;13 | `pending_missing_data` |
| `unimproved_load` | 24 | None | `pending_baseline_review` |
| `current_max_load` | 20 | 4;6;8;10 | `pending_missing_data` |
| `current_ridership` | 20 | 4;6;8;10 | `pending_missing_data` |
| `competitiveness` | 17 | 3;4;5;6;8;10;13 | `pending_missing_data` |
| `priority_populations_index` | 0 | All 1-24 | `pending_evidence` |

There are **98 published City values and 22 source missing values** in the five-column standardized matrix. Scores can be negative; they are dimensionless processed scores, not physical counts or speeds. Preserve their exact source values and blanks. A missing existing-service score can be structurally unavailable for a proposed corridor; investigate before assuming it is an acquisition failure.

`city_standardized_scores_v0.1.csv` columns:

```text
corridor_id,current_speed,unimproved_load,current_max_load,current_ridership,competitiveness,source_id,notes
```

`supplemental_model_inputs_v0.1.csv` columns:

```text
corridor_id,priority_populations_index,source_id,notes
```

Both have 24 rows. PPI is blank for every row. `corridor_master_v0.1.csv` has 24 metadata records, 43 raw `indicator_*` columns and 1,032 blank raw indicator cells. It is an evidence inventory, not a complete raw modelling matrix. Construction length in this master is the City source quantity; it is not automatically full route length or a verified GIS measurement.

### Latest validation snapshot

```json
{
  "valid_structure": true,
  "corridor_count": 24,
  "indicator_count": 43,
  "missing_indicator_cells": 1032,
  "selected_indicator_count": 6,
  "admitted_indicator_count": 0,
  "model_ready": false,
  "errors": [],
  "warnings": []
}
```

Structural validity is different from modelling readiness. Current blockers are non-admission of all six selected criteria, the 22 missing City scores, absence of PPI, and unresolved interpretation/comparability. Completing PPI alone will **not** make this model ready. Missing raw longlist columns do not by themselves block a valid processed-score model if those raw columns are not selected.

### Admission and validation contract

`data/workbook_records_v0.1.json` is the authoritative editable dictionary/admission record. XLSX files are generated review views. Excel-only edits are not read by the validator. Update JSON, synchronize other affected records and regenerate workbooks.

- Canonical final status: `admission_status=admitted`. The validator's selected-input check expects that literal status; do not depend on aliases accepted elsewhere.
- Accepted admitted `direction`: `higher_is_better`, `lower_is_better`, `target`, `higher`, `lower`. Target-based scoring remains blocked until an explicit target/scoring contract exists. Prefer explicit higher/lower labels.
- Accepted admitted `cost_dependence`: `none`, `no`, `cost_independent`. These are evidence-backed conclusions, not labels to assign mechanically.
- `raw_value_available=standardized_score_available` is supported **only as a compatibility label for processed City input**, with `input_value_type=city_standardized_score` and explicit file/column mapping. It does not mean raw values exist.
- Other availability states accepted as complete are `yes`, `true`, `confirmed`, `complete`; evidence and input type must still be truthful for a derived PPI.
- Definition, units and temporal/spatial/baseline comparability must be confirmed. The validator accepts affirmative states such as `yes`, `true`, `confirmed`, `comparable`, `verified`, `complete` for these fields.
- `coverage_count` and `missing_corridor_ids` must match actual files. Final admission normally requires 24 finite values, no missing IDs, complete interpretation and documented provenance.
- The validator cross-checks City values/missingness against the source-score archive and recognizes only the five whitelisted non-cost City fields. It prevents arbitrary replacements disguised as original City scores.
- Detailed direction rationale belongs in `notes`. Higher source evaluation score does not automatically mean higher raw speed or a higher underlying time ratio. Demand pressure and current service quality have different policy interpretations.

Existing `equity_*` City fields were not admitted: cost processing is unresolved (`not_explicitly_stated_for_equity` or unresolved records). Do not recode them to `none` without source evidence. Full TEOZ is also not interchangeable with its priority-populations component.

## 5. Completed work and the Sheppard West geometry pilot

### Earlier evidence work

The project has a 24-corridor master, a 30-item City indicator index, a 43-concept longlist, source and gap registers, source-score archive, admission/dictionary workbooks and validation/simulation interfaces. Public-data acquisition failures and source mismatches were recorded rather than covered with invented values. The five processed inputs were separated from raw placeholders. PPI was added as a candidate and separate intended input, without fabricated results.

### Corridor 01 result

| Item | Verified pilot result |
| --- | --- |
| Eligible corridor | ID 1, Sheppard Ave West; report endpoints `Sheppard W Stn.` to `Sheppard Stn.` (Sheppard-Yonge area) |
| Geometry source | Official City of Toronto Centreline, ArcGIS FeatureServer layer 2; retrieved 21 November 2026 |
| Source URL | https://gis.toronto.ca/arcgis/rest/services/cot_geospatial/FeatureServer/2 |
| Method | Shortest connected path restricted to named `Sheppard Ave W` road segments |
| Endpoint proxies | City road node 13450458 at Allen Rd / Sheppard, and 13448689 at Yonge St / Sheppard |
| Joined source segments | 33; individual `CENTRELINE_ID` values preserved in summary/source GeoJSON |
| Measured road length | **4.407067432 km**, approximately **4.407 km** |
| City assumed construction length | **4.404 km**, unchanged in the raw master |
| Length difference | **3.067 m**; agreement is a sanity check, not alignment proof |
| Trial boundary | **500 m Euclidean buffer on each side**, round end caps |
| Buffer area | **5.192196496 km2**, approximately **5.192 km2** |
| Measurement CRS | **EPSG:2952**, NAD83(CSRS) / MTM zone 10, metres |
| Delivered GeoJSON CRS | **EPSG:4326**, longitude/latitude |
| Geometry checks | Simple connected line, valid polygon, consecutive joins <1 m, merged length within 0.1 m of graph path length |
| Visual check | PNG inspected; QGIS project opened with three valid, styled layers |
| Population/PPI status | No census overlay, population total, tract allocation or PPI aggregation performed |

Pilot files are in `outputs/sheppard_west_pilot/`. The QGIS project uses relative GeoJSON layer paths. The static PNG/SVG uses archived City road background. The interactive HTML uses OSM background tiles and external Leaflet resources; that is not evidence that OSM supplied the road centreline.

The geometry register still has all 24 rows. Only ID 1 is `road_proxy_digitized_pending_endpoint_review`; its station set is `not_defined`. IDs 2-24 are not digitized. ID 1 is not selected as the winning corridor; it was chosen only as an easy geometry test.

### What the pilot does not establish

- Current road geometry is not the proposed 2024 transit alignment or tunnel footprint.
- Road intersections are station-area proxies, not exact station/platform centres or approved termini.
- A continuous road buffer includes areas between stations where boarding may be impossible. It is not a union of station buffers or a walking-network catchment. The City population definition uses station buffers; do not call the trial method equivalent.
- No municipal/land clipping was applied to the polygon.
- The source snapshot is 2026, while proposed supplemental census data are from 2021 and the City report is from 2024. Disclose and review that temporal mismatch.
- A single pilot does not establish a reliable minutes-per-corridor estimate. Setup/source discovery were substantial one-time overhead; branch, terminus and off-road cases still need manual review.

## 6. PPI: what is missing and how to complete it correctly

### Intended construct

PPI is intended to add an equity dimension to Part 1: concentration of residents from priority populations around a corridor. It belongs to Serve People. The proposed corridor statistic is:

```text
I_t   = exact, verified PPI for Census Tract t
P_it  = documented estimate/count of residents in catchment i intersecting tract t
PPI_i = sum_t(P_it * I_t) / sum_t(P_it)
```

This is a population-weighted mean of tract scores. It measures priority-population concentration, not the distribution of future travel-time benefits, and not total people served. It is also an ecological, area-level measure; do not infer an individual resident's identity or need from a tract mean. An accompanying population coverage measure would represent a different construct and needs separate overlap review.

The desired source prospect is the City map **Transportation Equity: Priority Populations**, May 2024, registered as `CITY2024_PRIORITY_MAP`:

https://www.toronto.ca/wp-content/uploads/2024/07/8efd-Equity-PriorityPop.pdf

The map/prospect is identified; **exact tract-level scores and complete index construction are not acquired**. Its map classes cannot produce exact values. The University of Toronto Mobilizing Justice Dashboard was suggested by the user as an alternative prospect; a downloadable, methodology-verified dataset from it is not present in this project. Do not conflate differently constructed indices under one PPI label.

### Required acquisition and decisions

1. Locate exact tract-level PPI and its authoritative metadata/formula, including census vintage, tract identifiers, scale, component definitions, denominators, transformations, weights and missing/suppression handling. Confirm the component list from the actual source, not only from earlier user descriptions.
2. If exact scores are public, use and cite them. If reconstructing tract PPI from 2021 Census, obtain all required component inputs and the complete published construction method first. Do not invent weights, use map-bin midpoints or substitute full TEOZ. A newly designed index must be explicitly labelled as a new index and reviewed as a methodological change.
3. Acquire matching Census Tract boundary geometry and population data for the same vintage/geographic universe. Obtain DA/dissemination-block or better population support where needed for partial-tract intersections. Preserve IDs such as `CTUID`/`DGUID` as strings; do not convert identifiers to numbers and lose formatting.
4. Confirm the exact eligible corridor geometry and adopt a consistent catchment method for all 24. The current 500 m road buffer is a pilot choice, not a final decision. Record whether using line buffers, station-buffer unions or network walksheds. Do not choose whichever boundary increases a corridor's score.
5. Define `P_it` transparently. Entire intersecting-tract populations cannot simply be counted as fully inside the buffer. Area weighting assumes uniform density and is not population weighting. If spatial allocation is required, document it as an estimator with assumptions and sensitivity; never silently introduce it as a missing-value fill. Prefer population support that reduces allocation assumptions. Respect the strict no-imputation policy when source counts or PPI components are unavailable.
6. Reproject all geometries to a suitable metric CRS, validate/repair geometries with logged changes, dissolve overlaps within each catchment, intersect/index against tracts and population support, compute the population-weighted numerator/denominator, and flag missing/zero denominators. No valid estimate means a blank plus a recorded reason, not zero.

### Recommended implementation contracts (not yet created)

Implement a script such as `code/calculate_corridor_ppi.py` using PyQGIS or a deliberate Python GIS environment. QGIS has the needed geometry/overlay functionality; QuickOSM is not required for census overlay. Use corridor 01 to test the entire chain before scaling to 24.

Suggested new evidence/intermediate outputs:

| Proposed artifact | Minimum contents |
| --- | --- |
| Exact tract PPI source archive | Original source file, source ID/URL, retrieval date, checksum and source methodology |
| `census_tract_ppi_v0.1.csv` | Tract string ID, exact or explicitly reconstructed index, vintage, units, methodology/source ID, missing/suppression status |
| Tract/population geometries | CRS, geographic vintage, unit IDs, population/count definitions, archive/checksum |
| `corridor_tract_population_weights_v0.1.csv` | `corridor_id`, tract ID, overlap/allocation method, estimated covered population `P_it`, relevant fractions, source IDs and QA flags |
| `corridor_ppi_audit_v0.1.csv` | Numerator, denominator, tract counts, covered/missing population, completeness, buffer definition, geometry status and source references |
| Run/config metadata | Parameters, source snapshots, package versions, geographic method, exclusions/repairs, reproducible command and run timestamp |

These names are suggestions, not existing files. Never imply that they already contain results.

### QA and integration

- Verify unique tract keys and one-to-one score joins; investigate every unmatched tract and boundary-vintage mismatch.
- Intersections must not create duplicate population through overlapping catchment fragments. Each corridor's catchment should be a union before aggregation.
- Check finite nonnegative population weights, completeness, denominator >0 and independently reconciled population totals where possible. A complete weighted mean must lie within the min/max of contributing finite source scores.
- Missing tract index/population cannot simply be dropped from the denominator to manufacture a complete result. Report data coverage and keep the corridor estimate unavailable unless a separately justified method is agreed.
- Assess catchment/boundary sensitivity and whether the population allocation is credible. Do not perturb missing source data into existence.
- Retain **24 corridor output rows** throughout development. Until a corridor is computed, keep its value blank with status notes. The first pilot result does not authorize `coverage_count=24`.
- Put the final model-facing derived index in `data/supplemental_model_inputs_v0.1.csv`. Do not overwrite City standardized values. The existing raw master placeholder does not authorize calling a composite index a raw observation. Any later integration there must explicitly identify the derived value type and keep `indicator_observations` synchronized.
- Update source/acquisition/gap logs, geometry review, dictionary/admission JSON and coverage. Only after the exact source/method, direction, cost independence and comparability are established and all 24 inputs exist should PPI be marked admitted and the workbooks regenerated.

## 7. Other blockers that remain after PPI

1. **Missing City scores:** four of the five City columns lack values. No-imputation and fixed-24 rules jointly mean the current six-input matrix cannot yet be scored as complete. Seek genuinely comparable public evidence or explicitly review the selected criterion set/method. Any independent replacement measure needs its own definition, file and provenance; do not edit the preserved City score column and pass it off as the original.
2. **Scenario and technology dependence:** some City benefits are conditional on prerequisite corridors, and City assumed technologies are not binding in the case. Eight alternatives have recorded prerequisites. Confirm standalone versus extension comparability; cost-free does not mean scenario-free.
3. **Forecast horizon:** several City measures use 2051, while the case requires opening by 2035. Preserve the original forecast year and explain its role rather than relabelling it 2035.
4. **Lengths/endpoints:** ID 3 has a source construction-length adjustment; Jane corridor IDs 11/12 retain source lengths pending geographic review. Do not swap seemingly inconsistent values without evidence or use construction length as a substitute for route geometry.
5. **Direction and overlap:** `current_speed`, `competitiveness`, load and ridership need explicit policy interpretation and redundancy review. The five scores heavily emphasize existing operations/demand; adding equity alone does not establish balanced coverage of Strengthen Places or Support Prosperity. Review construct coverage before final selection.
6. **City equity fields:** source scores are not raw Palma ratios. A threshold of 1 for a raw ratio cannot be applied to its standardized score. Cost processing is unresolved, so these are not admitted shortcuts.
7. **Historical inventory text:** `review_issues_v0.1.csv` still contains earlier references to 42 candidates; the current verified count is 43 after adding PPI. Treat the register as useful historical findings, not current count authority. `inventory_review_v0.1.html` is also pre-strategy. `model_input_review_v0.1.html` and current validation describe the present selection.
8. **Part 2:** `tech_evidence` and `part2_sources` are header-only templates. No technology cost estimate, capacity study, ridership forecast, schedule or optimization has been completed. The project is still on Part 1 data readiness.

## 8. Tooling, dependencies and environment

### Windows and workspace

- Operating workflow: Windows, PowerShell. Client timezone: America/Toronto.
- Current writable workspace is under `C:/Users/pipis/Documents/Codex`. User PDFs under OneDrive are available as read sources. New sessions may have different filesystem/network permissions; grants from an earlier turn are not permanent evidence of access.
- Use `rg` for targeted content/path searches. Avoid recursively dumping the QGIS distribution or dependency directories; they contain tens of thousands of vendor files.
- Keep deliverables in `outputs`; installation artifacts and scratch files in workspace `work`. Do not put the multi-gigabyte QGIS runtime inside the project ZIP.

### Python environments

The shell's current default Python is:

```text
C:/Users/pipis/AppData/Local/Programs/Python/Python312/python.exe
Python 3.12.8
```

`validate_data.py` and `simulation_template.py` use the standard library. Default Python currently has matplotlib 3.11.0 and pandas 2.3.3. It did not have GeoPandas, pypdf, pdfplumber or PyMuPDF at this audit; do not assume them installed.

GIS packages installed in the separate workspace target `work/gis_pydeps` include Shapely 2.2.0, pyproj 3.8.0, folium 1.0.0, NumPy 2.5.5 and requests 2.34.2, with their dependencies. That directory is not automatically on the default Python path. `code/requirements_gis.txt` lists broad minimum versions, not an exact lockfile. The pilot also uses default matplotlib. Shapely emitted deprecation warnings for `shapely.ops.transform`; the successful run had no geometry failures. Modernize deliberately and verify equal geometry if changing APIs.

QGIS has a separate bundled **Python 3.12.15** and bundled GIS/native dependencies. Use its `bin/python-qgis-ltr.bat` environment for PyQGIS. A normal `import qgis` in default Python is not expected to work. Avoid mixing the external target's NumPy/GDAL/Qt binaries into QGIS's environment. Choose either PyQGIS or a separately managed GIS environment for the next script, and record that choice.

The current Codex bundle can be located with `mcp__codex_app__load_workspace_dependencies`. At handoff, bundle version is `26.1119.11507`, with Node/Python under:

```text
C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1119-907-0_26.1119.907.0_x64__3k8sg7r9htsxt/dependencies/
```

This location is version-specific. Re-query it rather than hardcoding it for future sessions. `build_workbooks.mjs` contains an older fallback runtime path; explicitly set `ARTIFACT_NODE_MODULES` to the current bundled Node `node_modules` directory when regenerating workbooks. It imports `@oai/artifact-tool`. It also writes workbook preview PNGs to workspace `work`. Do not rerun workbook generation merely to read these files.

For PDF text extraction, `pdftotext` is available at `D:/texlive/2026/bin/windows/pdftotext.exe`. The City layout text and page renders are already in `work`. Use source PDFs/page images to resolve table layout; text extraction alone can merge columns incorrectly.

### QGIS and QuickOSM status

- Official installer: `work/QGIS-OSGeo4W-3.44.15-2.msi`, signature verified as valid, Open Source Geospatial Foundation.
- Normal MSI installation failed with Windows Installer exit 1601 and access error `0x80070005`. QGIS is **not registered as a normal Windows installation**.
- A local standalone runtime was reconstructed from that signed installer at `work/tools/QGIS` and post-install environment generation was run. Version: **QGIS 3.44.15-Solothurn**. The QGIS GUI successfully opened the three-layer pilot project.
- Executable: `work/tools/QGIS/bin/qgis-ltr-bin.exe`. Its generated `.env` has absolute/Windows short paths and `QGIS_CUSTOM_CONFIG_PATH` pointing to the workspace profile. Moving the runtime or workspace may require regeneration; it is not a fully relocation-proof portable distribution.
- QuickOSM **2.6.0** is in `work/qgis_profiles/profiles/default/python/plugins/QuickOSM`. A separate workspace profile enables it. The Processing provider registered and enumerated **12 algorithms**. A new GUI session showed its toolbar and copyright prompt.
- Default-profile plugin-manager interaction became unresponsive; acknowledging the new-profile copyright prompt timed out. No GUI Overpass query completed. Do not claim a successful end-to-end QuickOSM download.
- Three Overpass POST endpoints and one status GET returned HTTP 406. Earlier open.toronto.ca/CKAN requests also had DNS/download failures. Failures are logged environment/service observations, not proof the public datasets do not exist. Try a valid official resource/API when appropriate; do not indefinitely repeat the same failed request.
- No TTC GTFS archive or extracted `shapes.txt` was acquired. A bus shape is not inherently more accurate for an eligible corridor: route direction, branches, terminal loops, snapshot and segment mapping require review.
- The outer `outputs/Open_Sheppard_West_QGIS.cmd` is a **local convenience launcher** using this workspace's runtime/profile. It is not inside the project ZIP and requires the adjacent workspace `work` directory. The QGZ/GeoJSON themselves can be opened in another installed QGIS.

If controlling Windows UI in Codex, read the available computer-use skill first. The preceding session used `@oai/sky` through Node REPL for UI observations/actions. Old window handles and accessibility indexes must be refreshed. No current GUI is guaranteed responsive. Headless PyQGIS/scripted overlays are preferable for reproducibility once inputs are verified.

### Commands with known scope

From the canonical project directory:

```powershell
python -B code\validate_data.py --output outputs\validation_v0.1.json
python -B code\simulation_template.py
```

The first checks structure and readiness. A successful process exit can coexist with `model_ready=false`; read the JSON. The second prints that it is only a template and performs no simulation. The template currently permits mutation of raw-style `indicator_*` fields; it does not yet provide a processed City/PPI modelling adapter. A future model must explicitly select/join the processed inputs by corridor ID rather than quietly feeding the empty raw master.

To rebuild the geometry/map from its archived City input files in a suitably provisioned Python environment:

```powershell
python -B code\build_sheppard_pilot.py
```

An equivalent successful command in the current workspace used the separate target dependencies:

```powershell
# Run from the workspace, not the project directory.
python -B -c "import sys,runpy; sys.path.insert(0,'work/gis_pydeps'); runpy.run_path('outputs/project/code/build_sheppard_pilot.py',run_name='__main__')"
```

This script rebuilds GeoJSON, PNG/SVG, interactive HTML and the numerical summary. It does **not** rebuild the QGIS `.qgz`; its current generation/check is in workspace `work/qgis_finish.py`. That helper also overwrites setup status, so do not casually rerun it and lose the richer GUI/network status record.

Workbook regeneration, after intentional JSON/schema changes:

```powershell
# Replace this placeholder with the current dependency path returned by the runtime tool.
$env:ARTIFACT_NODE_MODULES = '<current bundled Node node_modules directory>'
node code\build_workbooks.mjs
```

Never blindly rerun older `work/scaffold_b.py`, `fill_project.py`, `adopt_standardized.py`, `finalize_project.py`, `finish_standardized.py` or other historical generation scripts: several overwrite current project files using earlier assumptions. Read them before reuse. The canonical `code` folder is the preferred starting point. `work/finalize_gis_pilot.py` rebuilds documentation/archive and copies its older pilot script into `code`; it must be reviewed before future use to avoid undoing changes.

## 9. Recommended next work sequence and acceptance criteria

1. Reconfirm canonical paths and run/read validation; preserve the initial snapshot. Do not start scoring.
2. Acquire exact PPI methodology/tract data and matching census geography/population support. Record every resource and checksum. This is presently an evidence gap as well as a GIS gap.
3. Review corridor 01's station-area endpoints and the catchment definition. Implement an auditable single-corridor population-overlay/PPI pipeline, keeping an output row for every corridor even while only one is computed.
4. Check tract joins, population accounting, source completeness and sensitivity; inspect the pilot geometry/overlay visually. Distinguish exact data from spatial estimates.
5. Reuse the reviewed pipeline for the remaining 23 eligible corridors while preserving original geometry/endpoints and separately reviewing extensions, branches and length anomalies.
6. Integrate derived PPI with honest coverage metadata; update logs and authoritative admission/dictionary JSON; regenerate review workbooks when evidence warrants it.
7. In parallel or afterwards, resolve the missing/non-comparable City inputs and the final criterion set across the three principles. The fixed-24/no-imputation conflict cannot be resolved by silently dropping alternatives or renormalizing over whichever values happen to exist.
8. Only when all selected inputs genuinely pass the readiness contract should `model_ready` become true. Then begin the agreed Part 1 exploratory analysis and scoring. Part 2 follows after a defensible corridor recommendation.

The next milestone is not "a nonblank PPI column". It is a **traceable corridor equity dataset with exact or explicitly reconstructed tract scores, verified population weights and a consistent geographic method**, together with an honest report of all unresolved gaps.

## 10. File catalogue and corridor register

The following appendices are generated from the current filesystem. They enumerate every canonical project file and explain its role/status, followed by historical workspace artifacts and the 24-row source corridor register. Vendor QGIS/Python library files are grouped as dependencies rather than individually described. `outputs/handoff_file_inventory_v0.1.csv` provides a machine-readable inventory and checksums for canonical files, outer historical exports, the old extracted copy and top-level workspace intermediates. It excludes itself and the delivery ZIP to avoid self-reference; nested vendor/runtime/profile files are grouped rather than individually hashed.

<!-- GENERATED_CATALOGUE -->

### Appendix A. Canonical project file tree

```text
project/
|-- code/
|   |-- __pycache__/
|   |   `-- validate_data.cpython-312.pyc
|   |-- build_sheppard_pilot.py
|   |-- build_workbooks.mjs
|   |-- requirements_gis.txt
|   |-- simulation_template.py
|   `-- validate_data.py
|-- data/
|   |-- acquisition_log_v0.1.csv
|   |-- candidate_indicator_longlist_v0.1.csv
|   |-- city_2024_indicator_index_v0.1.csv
|   |-- city_standardized_scores_v0.1.csv
|   |-- corridor_geometry_review_v0.1.csv
|   |-- corridor_master_v0.1.csv
|   |-- data_dictionary_v0.1.xlsx
|   |-- data_dictionary_v0.1.xlsx.inspect.ndjson
|   |-- data_gap_register_v0.1.csv
|   |-- indicator_admission_v0.1.xlsx
|   |-- indicator_admission_v0.1.xlsx.inspect.ndjson
|   |-- indicator_observations_v0.1.csv
|   |-- model_input_coverage_v0.1.csv
|   |-- model_input_selection_v0.1.json
|   |-- review_issues_v0.1.csv
|   |-- schema_v0.1.json
|   |-- source_log_v0.1.csv
|   |-- supplemental_model_inputs_v0.1.csv
|   `-- workbook_records_v0.1.json
|-- evidence/
|   |-- gis/
|   |   |-- centreline_metadata.json
|   |   |-- sheppard_background.geojson
|   |   |-- sheppard_overpass_query.txt
|   |   `-- sheppard_roads.geojson
|   |-- source_documents/
|   |   |-- city_2024_corridor_evaluation.pdf
|   |   `-- city_2024_main_report.pdf
|   |-- city_2024_published_scores_NOT_RAW_v0.1.csv
|   |-- part2_sources_v0.1.csv
|   |-- source_document_checksums.csv
|   `-- tech_evidence_v0.1.csv
|-- outputs/
|   |-- sheppard_west_pilot/
|   |   |-- corridor_01_boundary_pilot.png
|   |   |-- corridor_01_boundary_pilot.svg
|   |   |-- corridor_01_buffer_500m.geojson
|   |   |-- corridor_01_centerline.geojson
|   |   |-- corridor_01_endpoints.geojson
|   |   |-- corridor_01_interactive_map.html
|   |   |-- corridor_01_pilot.qgz
|   |   |-- pilot_summary.json
|   |   |-- qgis_setup_status.json
|   |   |-- README.md
|   |   `-- source_centerline_segments.geojson
|   |-- delivery_checks_v0.1.json
|   |-- handoff_file_inventory_v0.1.csv
|   |-- inventory_review_v0.1.html
|   |-- model_input_review_v0.1.html
|   `-- validation_v0.1.json
|-- slides/
|-- HANDOFF_v0.1.md
`-- README.md
```

`slides/` exists and is empty. The Python bytecode cache is disposable and excluded from the delivery ZIP.

### Appendix B. Canonical file purposes and status

| File | Purpose | Current status |
| --- | --- | --- |
| `HANDOFF_v0.1.md` | Complete structured successor-assistant handoff | Current handoff; generated catalogue appended |
| `README.md` | Current data strategy, authority, validation commands and pilot pointer | Current; read before editing |
| `code/__pycache__/validate_data.cpython-312.pyc` | Python-generated validator bytecode | Disposable cache; excluded from ZIP |
| `code/build_sheppard_pilot.py` | Rebuild pilot GeoJSON, map, HTML and numerical summary from archived road inputs | Successfully rerun; no census overlay/PPI; no QGZ generation |
| `code/build_workbooks.mjs` | Generate dictionary/admission XLSX files from JSON/schema and preview renders | Requires current Codex artifact-tool Node dependencies |
| `code/requirements_gis.txt` | GIS pilot dependency minimum versions | Not an exact lockfile; runtime environments remain separate |
| `code/simulation_template.py` | Fixed-24 simulation callback interface and metadata safeguards | Template only; no uncertainty model or processed-input adapter |
| `code/validate_data.py` | Validate schema, fixed 24 IDs, missingness, cost/admission/input mapping and archive agreement | Standard-library script; true structure, false readiness |
| `data/acquisition_log_v0.1.csv` | Five acquisition attempts/prospects and evidence gaps | Historical acquisition notes; supplement for new downloads |
| `data/candidate_indicator_longlist_v0.1.csv` | 43 candidate indicator concepts and provenance/interpretation | Longlist, not admitted model criteria |
| `data/city_2024_indicator_index_v0.1.csv` | 30 City indicator definitions, table/page references, units, direction, cost and overlap | Index only; not corridor observations |
| `data/city_standardized_scores_v0.1.csv` | Separate 24-row matrix of five non-cost City processed score columns | 98 values; 22 source blanks; no imputation |
| `data/corridor_geometry_review_v0.1.csv` | 24-row alignment, endpoint, length, station/catchment review | ID 1 road proxy only; IDs 2-24 not digitized |
| `data/corridor_master_v0.1.csv` | 24 eligible corridor metadata records and 43 raw indicator placeholders | 1032 raw blanks; no processed City scores in indicator_* |
| `data/data_dictionary_v0.1.xlsx` | Generated indicator dictionary workbook | Review view; JSON is authoritative |
| `data/data_dictionary_v0.1.xlsx.inspect.ndjson` | Dictionary workbook inspection dump | Generated inspection artifact; not authoritative |
| `data/data_gap_register_v0.1.csv` | 43 raw-indicator acquisition gaps | Raw gaps; do not confuse with processed-score coverage |
| `data/indicator_admission_v0.1.xlsx` | Generated indicator admission review workbook | No indicators admitted; edit JSON then regenerate |
| `data/indicator_admission_v0.1.xlsx.inspect.ndjson` | Admission workbook inspection dump | Generated inspection artifact; not authoritative |
| `data/indicator_observations_v0.1.csv` | 24 x 43 raw observation/status/source grid | 1032 blank values with statuses; synchronized with raw master |
| `data/model_input_coverage_v0.1.csv` | Measured coverage/missing IDs for six selected input candidates | Current 17/24/20/20/17/0 coverage |
| `data/model_input_selection_v0.1.json` | Selected six IDs, processed strategy, no-cost/no-imputation configuration | Authoritative intended model-input selection |
| `data/review_issues_v0.1.csv` | 12 source/methodological findings | Historical references to 42 candidates are stale; now 43 |
| `data/schema_v0.1.json` | Column schemas for datasets, dictionary/admission workbooks and templates | Current schema; update deliberately with records/code |
| `data/source_log_v0.1.csv` | 12 source IDs, URLs, locators and acquisition/prospect distinctions | Current register includes official City centreline |
| `data/supplemental_model_inputs_v0.1.csv` | Separate 24-row derived PPI model-input file | All 24 PPI values blank; not computed |
| `data/workbook_records_v0.1.json` | Authoritative dictionary and admission records read by validator/workbook builder | Edit here for admission; XLSX-only edits are ineffective |
| `evidence/city_2024_published_scores_NOT_RAW_v0.1.csv` | 1248 long-form City published score/archive records including excluded fields | Preserve as evidence; cost-bearing fields not model inputs |
| `evidence/gis/centreline_metadata.json` | City ArcGIS layer schema and metadata snapshot | Archived current road service metadata, not a 2024 alignment |
| `evidence/gis/sheppard_background.geojson` | Bounded official road background features for static map | Archived offline map context |
| `evidence/gis/sheppard_overpass_query.txt` | OSM Overpass query attempted for Sheppard geometry | Query text only; no OSM geometry acquired |
| `evidence/gis/sheppard_roads.geojson` | 284 queried Sheppard/Yonge road features used by pilot graph | Archived input; pilot selects 33 named Sheppard segments |
| `evidence/part2_sources_v0.1.csv` | Part 2 source evidence template | Header only; no data |
| `evidence/source_document_checksums.csv` | Checksums for two archived City source PDFs | Source-integrity record |
| `evidence/source_documents/city_2024_corridor_evaluation.pdf` | Official City 2024 13-page evaluation attachment | Archived source; main definition/table page references use this sequence |
| `evidence/source_documents/city_2024_main_report.pdf` | Official City 2024 context/definitions report | Archived source; separate page sequence |
| `evidence/tech_evidence_v0.1.csv` | Part 2 technology evidence template | Header only; no estimates |
| `outputs/delivery_checks_v0.1.json` | Earlier delivery/language/count audit snapshot | 98 City scores, zero PPI, model_ready false; not a full GIS/handoff audit |
| `outputs/handoff_file_inventory_v0.1.csv` | Machine-readable file purposes, status, sizes, row counts and checksums | Handoff snapshot; excludes its own row/checksum |
| `outputs/inventory_review_v0.1.html` | Initial evidence-inventory review page | Historical pre-strategy snapshot; not current readiness authority |
| `outputs/model_input_review_v0.1.html` | Processed-input strategy/coverage review page | Current input review; no model results |
| `outputs/sheppard_west_pilot/README.md` | Pilot source, method, measurements, setup, rebuild and limitations | Current pilot explanation |
| `outputs/sheppard_west_pilot/corridor_01_boundary_pilot.png` | English static boundary map | Visually checked; offline background is official City roads |
| `outputs/sheppard_west_pilot/corridor_01_boundary_pilot.svg` | Vector version of static boundary map | Exported from same plot |
| `outputs/sheppard_west_pilot/corridor_01_buffer_500m.geojson` | 500 m round-cap corridor proximity polygon | Valid; 5.192196 km2; EPSG:4326 export |
| `outputs/sheppard_west_pilot/corridor_01_centerline.geojson` | Joined official road-centreline proxy | 4.407067 km; not approved transit alignment |
| `outputs/sheppard_west_pilot/corridor_01_endpoints.geojson` | Two road-junction endpoint proxies | Not exact station/platform centres |
| `outputs/sheppard_west_pilot/corridor_01_interactive_map.html` | Interactive geometry viewer with OSM background tiles | Needs network for external libraries/tiles; not an OSM centreline download |
| `outputs/sheppard_west_pilot/corridor_01_pilot.qgz` | Styled QGIS project, three relative-path GeoJSON layers | Opened successfully; no census/PPI layers |
| `outputs/sheppard_west_pilot/pilot_summary.json` | Exact length, buffer area, source segment IDs, CRS and limitations | ready_for_final_population_estimation false |
| `outputs/sheppard_west_pilot/qgis_setup_status.json` | Software/provider/GUI/network verification record | 12 algorithms loaded; no successful OSM query |
| `outputs/sheppard_west_pilot/source_centerline_segments.geojson` | 33 original City centreline features with source IDs | Preserved pilot source subset |
| `outputs/validation_v0.1.json` | Latest validator result | valid_structure true, model_ready false; no errors/warnings |

### Appendix C. Outer delivery folder and historical copies

| Workspace-relative path | Meaning and status |
| --- | --- |
| `outputs/city_2024_corridors.csv` | Earlier standalone inventory export; historical, not current model-input authority |
| `outputs/city_2024_metrics.csv` | Earlier standalone inventory export; historical, not current model-input authority |
| `outputs/city_2024_report_scores_NOT_RAW.csv` | Earlier standalone inventory export; historical, not current model-input authority |
| `outputs/City_2024_指标与走廊审阅.xlsx` | Earlier standalone inventory export; historical, not current model-input authority |
| `outputs/City_2024_指标定位与审阅.html` | Earlier standalone inventory export; historical, not current model-input authority |
| `outputs/Open_Sheppard_West_QGIS.cmd` | Local runtime/profile/project launcher; requires adjacent workspace work directory |
| `outputs/TRUST_Line_project_v0.1` | Older extracted project copy; not the working project |
| `outputs/TRUST_Line_project_v0.1.zip` | Current delivery archive, refreshed with this handoff; excludes work/runtime and bytecode |

### Appendix D. Workspace setup and historical helper files

These are outside the portable project ZIP. They are not a second data authority. Older generation helpers can overwrite newer files.

| Workspace-relative file | Role/status |
| --- | --- |
| `work/admission_final.inspect.ndjson` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/admission_template.inspect.ndjson` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/adopt_standardized.py` | Migration to separate processed City score inputs; historical state writer |
| `work/allen_roads.geojson` | GIS source/query intermediate; canonical pilot evidence subset is archived in project/evidence/gis |
| `work/audit_handoff.py` | Read-only dataset/environment audit and local case text extraction |
| `work/build_handoff_catalogue.py` | Build handoff appendices/file inventory and refresh ZIP; no model-input edits |
| `work/build_inventory.mjs` | Earlier inventory workbook generator |
| `work/build_inventory.py` | Earlier City inventory extraction/generation helper |
| `work/build_sheppard_pilot.py` | Original workspace pilot script; canonical reusable copy is in project/code |
| `work/centreline_metadata.json` | Workspace acquisition/setup intermediate; inspect before reuse |
| `work/check_project_b.py` | Earlier scaffolding consistency check |
| `work/check_standardized.py` | Processed-score consistency/admission spot checks |
| `work/city-01.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-02.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-03.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-04.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-05.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-06.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-07.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-08.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-09.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-10.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-11.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-12.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city-13.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/city_2024_corridor_evaluation.pdf` | Working source PDF copy; canonical City copies are under project/evidence/source_documents |
| `work/city_2024_layout.txt` | Source extraction/page/query intermediate; not a model-input dataset |
| `work/city_2024_main_report.pdf` | Working source PDF copy; canonical City copies are under project/evidence/source_documents |
| `work/city_2024_main_report.txt` | Source extraction/page/query intermediate; not a model-input dataset |
| `work/city_bbox.html` | Source extraction/page/query intermediate; not a model-input dataset |
| `work/data_dictionary_preview.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/dictionary_final.inspect.ndjson` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/dictionary_template.inspect.ndjson` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/extract_qgis.py` | MSI cabinet/manifest extraction helper; expensive historical setup |
| `work/fetch_osm.py` | Overpass acquisition attempts; failed HTTP 406 |
| `work/fill_project.py` | Historical data/record population generator; may overwrite current data |
| `work/finalize_gis_pilot.py` | Pilot docs/archive updater; copies older script into project/code; review before reuse |
| `work/finalize_project.py` | Historical project documentation/packaging generator |
| `work/finish_standardized.py` | Historical standardized-strategy delivery updater; may overwrite outputs |
| `work/get_sheppard.py` | City road acquisition helper |
| `work/indicator_admission_preview.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/inventory.inspect.ndjson` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/inventory_data.json` | Historical inventory/workbook generation intermediate |
| `work/inventory_final.inspect.ndjson` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/longlist_english.json` | English candidate-longlist intermediate |
| `work/prepare_gis.py` | QGIS/plugin acquisition setup helper |
| `work/project_audit.py` | Earlier file/language/schema audit helper |
| `work/QGIS-OSGeo4W-3.44.15-2.msi` | Official signed installer; normal installation failed |
| `work/qgis_application.cab` | Application cabinet extracted from official MSI |
| `work/qgis_expand.log` | Vendor cabinet extraction log |
| `work/qgis_file_manifest.json` | 37270-file installer reconstruction manifest; vendor paths indexed here |
| `work/qgis_finish.py` | PyQGIS project builder/provider check; overwrites project/setup status |
| `work/qgis_gui_error.log` | GUI-launch diagnostic log |
| `work/qgis_gui_out.log` | GUI-launch diagnostic log |
| `work/qgis_install.log` | Windows Installer failure evidence |
| `work/qgis_local_setup.cmd` | Generate local QGIS runtime environment via --postinstall |
| `work/QuickOSM-2.6.0.zip` | Official plugin file archive used for workspace profile |
| `work/quickosm_page.html` | Source extraction/page/query intermediate; not a model-input dataset |
| `work/scaffold_b.py` | Historical Agent B scaffolding; do not rerun blindly |
| `work/sheet_1.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheet_2.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheet_3.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheet_4.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheet_5.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheet_6.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheet_7.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheet_8.png` | Historical source render, workbook preview or inspection dump; diagnostic only |
| `work/sheppard_background.geojson` | GIS source/query intermediate; canonical pilot evidence subset is archived in project/evidence/gis |
| `work/sheppard_overpass_query.txt` | Source extraction/page/query intermediate; not a model-input dataset |
| `work/sheppard_roads.geojson` | GIS source/query intermediate; canonical pilot evidence subset is archived in project/evidence/gis |
| `work/stat_case_handoff_reference.txt` | Local case text extraction for requirement/page verification |
| `work/west_crossroads.geojson` | GIS source/query intermediate; canonical pilot evidence subset is archived in project/evidence/gis |

Dependency directories (vendor files grouped, not individually described):

- `work/tools/QGIS/`: reconstructed local QGIS runtime; `work/qgis_file_manifest.json` indexes installer files.
- `work/gis_pydeps/`: separate pip target, including Shapely/pyproj/folium/NumPy and dependencies.
- `work/qgis_profiles/`: QGIS settings and installed QuickOSM package; runtime caches and user-profile state are mutable.
- Other `work` extraction/cache directories, if present, are setup intermediates rather than project evidence.

### Appendix E. All 24 corridor identities

Lengths are the City source assumptions from the master, not all GIS-verified full alignment lengths. Prerequisites are source scenario metadata, not permission to drop alternatives.

| ID | Corridor | Endpoint A | Endpoint B | Source length (km) | Prerequisite IDs |
| ---: | --- | --- | --- | ---: | --- |
| 1 | Sheppard Ave West | Sheppard W Stn. | Sheppard Stn. | 4.404 | None |
| 2 | Sheppard Ave East | Don Mills Stn. | McCowan Rd | 7.387 | None |
| 3 | Waterfront West LRT #1 | Long Branch | Park Lawn | 3 | 4 |
| 4 | Waterfront West LRT #2 | Park Lawn | Union Station | 9.3 | None |
| 5 | Finch West LRT Extension #1 | Humber College | Woodbine GO | 3.3 | None |
| 6 | Finch West LRT Extension #2 | Woodbine GO | Pearson Airport | 2.8 | 5 |
| 7 | Finch Ave West | Finch West Stn. | Finch Station | 6.344 | None |
| 8 | Ontario Line West extension | Ontario Place | Dundas West Stn. | 4 | None |
| 9 | Ontario Line North extension | Eglinton Ave E | Steeles Ave | 10.57 | None |
| 10 | Line 2 west extension | Kipling Station | Sherway Gardens | 4.3 | None |
| 11 | Jane St | Bloor St | Eglinton Ave | 11.269 | 12 |
| 12 | Jane St | Eglinton Ave | Pioneer Village Stn. | 4.076 | None |
| 13 | St Clair Ave W | Weston Rd | Jane St | 2.04 | 11;12 |
| 14 | Steeles | Pioneer Village Stn. | Bathurst St | 5.34 | 15 |
| 15 | Steeles | Bathurst St | Bayview Ave | 4.316 | None |
| 16 | Steeles | Bayview Ave | Milliken Go Stn. | 8.367 | 15 |
| 17 | Steeles | Milliken Go Stn. | Morningside Ave | 4.123 | 16;15 |
| 18 | Kingston Rd E | Victoria Park Stn. | Eglinton | 8.851 | None |
| 19 | McCowan | Sheppard Ave E | Markham Centre | 4.85 | None |
| 20 | Wilson Ave W | Weston Rd | Wilson Stn. | 7.398 | None |
| 21 | Dufferin St | Dufferin Gate Loop | Eglinton Ave W | 7.04 | None |
| 22 | Lawrence Ave W | Weston Rd | Lawrence Ave W Stn. | 6.055 | None |
| 23 | Finch Ave E | Yonge St | Victoria Park Ave | 7.101 | None |
| 24 | Finch Ave E | Victoria Park Ave | Morningside Ave. | 9.514 | 23 |

### Appendix F. City source page map

| Source | Reference locations |
| --- | --- |
| `CITY2024_ATTACHMENT` | 13-page attachment: equity method p.3; definitions/scaling Table 1 p.6; 24-corridor list p.7; detailed scores pp.11-13 (Tables 6-8). |
| `CITY2024_MAIN` | Equity definitions/figures pp.16-18; operational map bands p.21; corridor tables pp.24-25. Separate PDF sequence. |
| `CITY2024_PRIORITY_MAP` | One-page May 2024 priority-populations map/prospect; exact tract index values and complete construction not acquired. |

Source URLs and notes are in `data/source_log_v0.1.csv`. Do not reverse cost-scaled z-scores into raw values without the original scaling/standardization parameters. The source anomaly where corridor 16 Relative Cost is printed as 87 was preserved as evidence, not silently corrected; cost remains excluded from Part 1.

