# TRUST-Line - UGCC 2026

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
