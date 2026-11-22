# TRUST-Line v0.6: tiered comparison and rank stability

This is an executable **tiered proxy-scenario model**, not an unrestricted forecast model or a cleared competition submission. The user explicitly authorized this scope and the readiness contract below. All 24 alternatives remain in the assessment; 16 share the main comparison baseline and eight are evaluated conditionally.

## Decision result

The declared shortlist rule selects **12 (Jane St), 23 (Finch Ave E), and 20 (Wilson Ave W)**. Only **12 and 23** meet the strictly-above-90% top-five criterion: both are top-five in all 10,000 sampled draws and in all six distinct scenarios. Corridor 20 enters the top five in **66.34%** of draws (exact six-scenario rate **66.67%**) and is a weight-sensitive third candidate, not a third high-confidence candidate. No single final Part 1 winner has been fixed.

Corridor 12 is first in all six cases. This does not validate its source geography or length normalization. The previously documented disagreement between City construction-length assignments and the two Jane road-proxy subsection lengths remains material, particularly because current ridership is length-scaled. Source scores were preserved; no speculative rescaling or source-value swap was performed.

## Tier isolation and conditional pairs

Main tier (`CITY_BASE_0`): **1,2,4,5,7,8,9,10,12,15,18,19,20,21,22,23**. Here “common base” means the City's case base network, which includes funded/under-construction projects; it does not mean no existing infrastructure.

Conditional reserve tier: **3,6,11,13,14,16,17,24**. The main plot therefore ranks **1–16**. It does not assign artificial 17–24 ranks to conditional projects. There is no pooled absolute ranking across the tiers, nor across different conditional bases.

**Conditional-baseline corridors do not enter an unanchored absolute ranking. We assess them as reserves for future network expansion.** Each reserve is evaluated with its complete source prerequisite closure. Examples: 6 requires 5; 13 requires the chain 12 → 11; 17 requires 15 → 16.

`conditional_pair_analysis.csv` reports prerequisite union coverage, the union with the extension and additional covered residents/low-income residents. Catchment overlaps are counted once. These are geometric population estimates under uniform CT density, not causal ridership/benefit effects, common-baseline forecasts or verified project feasibility. Published City z scores are not additive across corridors and are never summed into a bundle score. Tiering controls the scope of comparison; it does not reconstruct unobserved independent benefits.

## Normalization and declared weights

The five City inputs remain published standardized scores (with separately flagged minimum or mean substitutions). Equity is transformed before aggregation:

`equity_z = (equity_fraction - 0.13716878222779566) / 0.02473132688714528`.

The mean and population SD are fitted on the 16 main-tier nominal equity fractions and frozen across missing-value, weighting, suppression and endpoint stress comparisons. City columns are not restandardized after imputation; their original standardization population differs from the new equity reference. Equal criterion weights are therefore declared score weights, not a guarantee of equal within-tier variance or independent information. An all-24 equity-reference sensitivity is exported separately.

| Profile | Speed | Forecast load | Current max load | Current ridership | Competitiveness | Equity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Equal | 1/6 | 1/6 | 1/6 | 1/6 | 1/6 | 1/6 |
| Ridership priority | .10 | .20 | .25 | .25 | .10 | .10 |
| Equity priority | .10 | .10 | .10 | .10 | .10 | .50 |

These are explicitly declared analytical stress profiles, not fitted stakeholder preferences. Demand indicators can be correlated; the 70% combined demand allocation may double count demand. No costs, budget constraints or cost-bearing City combined scores enter this Part 1 calculation.

## Monte Carlo and exact verification

Seed **20261121**, NumPy **PCG64**, **10,000** draws. Each draw independently samples one of the two City methods and one of the three weight profiles with uniform probabilities. There are **six distinct score/rank cases**, not 10,000 unique weight vectors. The six cases are also exhaustively evaluated. The saved selector/rank table permits exact replay of every draw.

Original observed City cells are preserved. Only source blanks use the method's observed-column minimum or mean. The Census suppressed-CT median method is fixed in the main six cases; its mean alternative is tested separately. No missing-value tag permits an absent or arbitrary value through validation.

Ranks use tied rank intervals with tolerance 1e-12. A tied corridor counts as guaranteed top-k only if its worst tied rank is at most k. No random tie breaking is used. The high-confidence label requires both simulated and exact top-five frequencies strictly above .90. It means stability **under this declared scenario distribution**, not a statistical confidence level, a population probability of being best, or comprehensive uncertainty coverage.

The three-item shortlist uses exact top-five frequency, exact top-three frequency, exact mean midpoint rank, worst rank, then corridor ID. This prevents Monte Carlo noise from choosing among genuinely equal exact top-five rates. Corridor 20 wins the secondary criterion among the exact two-thirds top-five group; its worst rank is 13 under equity weighting. Other preference choices can support corridors 9,21 or 22.

The main Bump Chart shows corridors with at least 50% top-five inclusion. A separate frequent-top-ten chart is provided. The label “Robust Frontier” describes this requested rank-stability graphic; it is not a claim that a Pareto-efficient frontier has been computed.

## Woodbine: actual sensitivity, not a label change

The shared Woodbine anchor was perturbed at nominal plus eight bearings on a **250 m radius**, in EPSG:2952. Both corridors 5 and 6 use the same perturbed anchor. All **18** source-road shortest paths, 500 m buffers and CT allocations were rebuilt. No new Census downloads were needed; archived profiles covered these cases. The nominal results reproduce v0.5.

| Corridor | Equity fraction range, shown as percent | Route length range |
| --- | --- | --- |
| 5 | 9.21518%–9.32441% | 2.61247–4.52006 km |
| 6 | 10.44862%–10.57249% | 3.72516–4.69625 km |

Maximum absolute share change from the nominal point is approximately 0.0834 and 0.0837 percentage points respectively. The shortlist set is unchanged across these local endpoint cases, using the frozen equity calibration. The large route-length change for corridor 5 remains an important geometry limitation. Small share change is not evidence that the path or official station location is correct.

The dictionary and geometry review now use `proxy_with_sensitivity_check` for the Woodbine-related records, with actual evidence paths. Other endpoints are only declared proxies. Woodbine remains an approximate secondary coordinate cross-referenced to the official planning area, not a surveyed official point. Eight sampled bearings are a local stress test, not an exhaustive uncertainty envelope. Future transit alignments, station catchments, source road vintages, coastline support and uniform CT density remain limitations.

## Readiness contract

Current validation reports:

```text
valid_structure = true
core_ready = true
limitations_ready = true
model_ready = true
limitations_flagged = true
unrestricted_model_ready = false
admitted_indicator_count = 6
admission_status = admitted_with_limitations
```

`core_ready` requires the complete source-replayed 144-input scenario matrix. `limitations_ready` means that the limited scope is explicitly declared **and actually enforced**: correct 16/8 tier membership, complete dependency pair coverage, replayed six-case scores and 10,000 draw ranks, source/output fingerprints, declared proxies and completed Woodbine endpoint checks. It does not mean the limitations have disappeared. A missing/mismatched source, fake confidence flag, invalid draw rank, wrongly admitted dependency or undeclared geometry fails the contract.

The former unrestricted readiness issues are retained under `unrestricted_readiness_issues`. This is an explicit user-authorized change in what `model_ready` means, not an assertion that the old unrestricted model passed. Official geometry, harmonized independent forecasts, final corridor/technology decisions and competition submission clearance are not certified by this flag.

## Files and reproduction

Key outputs in this directory:

- `rank_acceptability.csv`, `six_scenario_scores.csv`, `normalized_main_tier_inputs.csv`
- `monte_carlo_draws.csv`, `scenario_sampling_frequency.csv`, `tiered_model_summary.json`
- `bump_top5.{png,svg,pdf}`, `bump_top10.{png,svg,pdf}`, `top5_acceptability.{png,svg,pdf}`
- `conditional_pair_analysis.csv`, `conditional_bundle_buffers.geojson`
- `woodbine_anchor_sensitivity.csv`, `woodbine_CT_allocations.csv`, `woodbine_route_audit.json`, `woodbine_rank_sensitivity.csv`
- `supplementary_sensitivity.csv` (CT mean and all-24 equity calibration)
- `run_manifest.json` (source/output fingerprints)

From `outputs/project`, after installing `code/requirements_gis.txt`:

```sh
python -B code/woodbine_sensitivity_v0_6.py
python -B code/analyze_extension_pairs_v0_6.py
python -B code/register_v0_6_inputs.py
python -B code/run_tiered_model_v0_6.py
python -B code/finalize_tiered_run_v0_6.py
python -B code/validate_data.py --output outputs/validation_v0.6.json
python -B -m unittest discover -s code -p 'test_*.py' -v
python code/build_tiered_slides_v0_6.py
```

Registration updates metadata and admission scope; rerun the finalizer after changing model sources or artifacts, then validate. The finalizer fingerprints outputs but does not replace numerical replay. Do not run old v0.4/v0.5 registration scripts to restore the current mapping. Rebuild Excel through `code/build_workbooks.mjs` with the artifact-tool dependency path, as described in the project README. Original v0.5 input values, raw source blanks and historical v0.5 outputs remain intact.

The seven-slide `slides/tiered_robustness_v0.6_review_draft.pptx` contains the tier rule, declared weights, both main figures, conditional pairs, readiness limitations and an AI Use Disclosure. It is an analytical review draft. The full supplied guideline p.22 restricts substantive AI uses and requires disclosure; the applicability of any designated-case exception has not been established. This file is not a cleared competition submission.

**34 tests pass**, including source preservation, independent CT replay, tier/dependency isolation, tied-boundary handling, seed reproducibility, exact/simulated acceptance replay and rejection of forged flags/ranks even after their local hashes are refreshed. No final Part 2 technology analysis or single-corridor decision has been completed.
