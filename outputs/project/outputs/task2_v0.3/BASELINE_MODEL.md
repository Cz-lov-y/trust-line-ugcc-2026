# Task 2 v0.3: executable user-assumption baseline

**The user-specified inputs now produce an executable, provisional two-technology model. BRT wins the equal-weight ratio-normalized baseline, 0.849 versus 0.814. LRT wins under the declared service-priority weights or min–max normalization. There is no method-invariant final technology recommendation.**

The fixed decision remains corridor **23, Finch East, Yonge–Victoria Park, 7.101 km**. BRT and LRT are conditionally admitted under v0.2; Subway remains outside the conservative base-case shortlist by policy. Original reference evidence and all four final feasibility conditions are preserved.

## Inputs and their status

| Quantity | BRT | LRT | Status |
|---|---:|---:|---|
| Hypothetical cost point, CAD | 350,000,000 | 950,000,000 | User-selected scenario values; not complete capital estimates |
| Cost / 7.101 km | CAD49.289M/km | CAD133.784M/km | Diagnostic arithmetic, not a fourth scored criterion |
| Relative ridership index R | 1.0 | 1.2 | User demand-premium hypothesis; no absolute daily count invented |
| Assumed one-way end-to-end saving T | 2.5 min | 3.5 min | User hypothesis on a common hypothetical before-trip baseline |
| Assumed eligible signals | 15 | 15 | Not a surveyed signal count |
| Equal-contribution equivalent saving / signal | 10 sec | 14 sec | Arithmetic implication if all 15 contribute; not an observation |
| E = R / cost in CAD billions | 2.857 | 1.263 | Relative-demand capital-effectiveness proxy; not passengers per dollar |

The cost points are **rounded user choices**, not the exact midpoints of the previous ranges. BRT [0.29,0.40]B has midpoint **0.345B**; LRT [0.77,1.20]B has midpoint **0.985B**. An exact-midpoint sensitivity is included rather than silently changing the requested baseline. A two-endpoint range does not establish a probability distribution or statistical median.

The user now authorizes these cost points for hypothetical scoring. Their common monetary comparability is itself an assumption: no inflation index, complete initial scope or price year has been established. This is not a conversion of Viva's 2009 programme dollars and Finch West's 2018 construction component into comparable complete project capital. Both point values are arithmetically below CAD16.657B; that does not certify the final budget condition. Original partial-cost flags remain false for full-capital admission.

Surface LRT can have a reserved guideway while still crossing road intersections. Neither complete grade separation nor greater demand follows automatically from the technology name or vehicle capacity. The LRT/BRT ratio **1.2** is a scenario hypothesis, not an agency forecast or a capacity-to-ridership conversion. No day/peak forecast horizon is fabricated. If later absolute BRT demand R0 is sourced consistently, the current hypothesis would imply LRT demand 1.2R0; until then only relative indices are used.

## TSP evidence supports testing an assumption, not claiming a forecast

The 2.5/3.5 minutes are assumed **one-way end-to-end trip** improvements, not average passenger-trip savings or a measured bus-to-LRT effect. A matched observed target baseline and passenger trip-length distribution remain absent.

TTC's 2026 pilot reports up to 30 seconds at selected Spadina intersections; the City's report describes up to 25 seconds (references T2_REF_017–018). The target's assumed 10/14 second equal-contribution equivalents are below those maxima, but a pilot maximum is not evidence for the target's average or even a positive lower bound. TTC's approximately 20-minute Finch West round-trip improvement also includes several operational changes (T2_REF_019); it is not a TSP-only estimate or a transferable 10-minute one-way saving.

Do not add the assumed savings to a mode operating speed that already includes signal priority. Treat both technologies' TSP and service assumptions consistently. Equal-benefit and zero-benefit cases are explicitly run, so LRT is not guaranteed a priority advantage by definition.

## Transparent three-criterion computation

For t in {BRT,LRT}, compute E_t = R_t / C_t, using C in hypothetical CAD billions, and benefits x_t = (E_t,R_t,T_t). Primary utilities are u_tj = x_tj / max_t(x_tj). Scores S_t = w_Eu_tE + w_Ru_tR + w_Tu_tT, with nonnegative weights summing to one. The optimizer selects the larger score **within the already conditionally admitted pair**. A verified hard failure still blocks admission; a score cannot override it.

Primary normalization preserves the relative magnitude of the assumed advantages and disadvantages. It is a value/model choice, not an empirically estimated utility function. With two alternatives, min–max normalization converts each nonconstant criterion into 0/1 and makes a small demand advantage as decisive as a large efficiency difference. That is a materially different interpretation, so it is shown explicitly as sensitivity. No winner-driven standard-score edits are made.

If both time savings are zero, ratio utilities for that column are both zero: the unchanged time weight gives neither alternative a ranking advantage. Min–max assigns an equal 0.5 to constant columns. These common offsets do not change their within-scenario ordering. Scores from different normalization methods or input scenarios are not cardinal welfare estimates and should not be compared as benefit totals.

| Criterion | BRT primary utility | LRT primary utility |
|---|---:|---:|
| Capital effectiveness E | 1.000000 | 0.442105 |
| Relative demand R | 0.833333 | 1.000000 |
| Time saving T | 0.714286 | 1.000000 |

**Overlap control:** E already includes R, while R also enters explicitly to meet the case's distinct demand consideration. These criteria are conceptually dependent. We do not claim independence or score raw cost/per-km cost as another criterion. A separate inverse-cost efficiency view E'=1/C removes demand from the efficiency column and retains demand and time separately. It gives the same qualitative baseline winner here but is an alternative cost-intensity proxy, not independently measured passenger cost-effectiveness. No stakeholder preference elicitation or survey has occurred.

## Declared weight profiles and outcomes

| Profile | E / R / T weights | BRT score | LRT score | Scenario winner |
|---|---|---:|---:|---|
| Equal | 1/3 / 1/3 / 1/3 | 0.849206 | 0.814035 | BRT |
| Capital-efficiency priority | 0.50 / 0.25 / 0.25 | 0.886905 | 0.721053 | BRT |
| Service-benefit priority | 0.20 / 0.40 / 0.40 | 0.819048 | 0.888421 | LRT |

Holding demand/time weights equal at (1−w_E)/2, the baseline tie occurs at **w_E = 28.8477%**. Above this share BRT wins; below it LRT wins, conditional on the fixed input and normalization assumptions. With min–max the corresponding boundary is 50%, and equal weights select LRT (BRT 0.333333, LRT 0.666667).

## Stress tests and 10,000 preference draws

Eight input cases are run: requested baseline; exact previous midpoints; equal demand; equal TSP benefit; zero TSP benefit; LRT demand ratio 1.5; doubled BRT cost; doubled LRT cost. Each is evaluated with three profiles, two normalizations and two efficiency definitions: **192 technology score rows**. Stress choices are analyst assumptions, not evidence-based uncertainty distributions or complete cost forecasts. See [all scores](scenario_scores.csv).

The 10,000 fixed-input weight draws use PCG64 seed **20261122**, Dirichlet(1,1,1). The same weight vectors are reused across method views. They explore an illustrative uniform weight simplex; costs, ridership and savings are held fixed. There is no sampling model for project success or empirical demand, and these proportions are not statistical confidence.

| Efficiency / normalization | BRT weight-draw support | Exact uniform-simplex area |
|---|---:|---:|
| R/C, ratio to best | 51.45% | 50.9200% |
| R/C, min–max | 25.36% | 25.0000% |
| 1/C, ratio to best | 54.95% | 54.4767% |
| 1/C, min–max | 25.36% | 25.0000% |

The analytic area provides an independent check of the numerical draws; Monte Carlo frequencies need not equal their limiting areas. Support is sensitive to the assumed preference prior, criteria and normalization. The baseline does not establish a high-confidence universal BRT winner.

[Decision sensitivity figure](baseline_decision_sensitivity.png) · [Baseline inputs](baseline_inputs.csv) · [Preference support](weight_support.csv) · [Four-slide review deck](../../slides/task2_baseline_v0.3_review_draft.pptx)

## Readiness and continuation

`assumption_model_ready=true`: the specified conditional comparison is executable. `complete_capital_estimates=false`, `implementation_feasibility_certified=false`, and `task2_complete=false`. There is a baseline scenario winner, not a final technology selection. The nine-year window, operational deadline, capital ceiling, complete route fit and allocated depot/access requirements are unchanged. All original evidence and v0.1/v0.2 artifacts remain preserved.

Next substantive evidence work: reconcile complete initial capital/price basis and delivery plans, establish matched demand/travel assumptions, and resolve the route/depot conditions. The team can now test these changes in the existing model rather than inventing a new scoring method after seeing a preferred result.

```sh
python code/run_task2_baseline_v0_3.py
MPLCONFIGDIR=/tmp/trust_line_mpl python code/build_task2_baseline_slides_v0_3.py
python -m unittest discover -s code -p 'test_task2*.py'
```

All numeric inputs in this version are identified as user or analyst assumptions. The evidence inventory is not relabelled as observed target data. Competition-use and AI disclosure limitations remain as documented in the existing handoff; these are analytical review artifacts, not submission clearance.
