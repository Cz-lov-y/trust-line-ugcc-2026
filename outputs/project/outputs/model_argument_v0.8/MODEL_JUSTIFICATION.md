# Formal model justification: need-priority, redundancy, values and conditional corridors

**Current recommendation:** corridor **23, Finch Ave E (Yonge St–Victoria Park Ave)** remains the provisional first choice under the declared transport-service/equity model. The model argument and EDA are now documented; source values, the nominal five-criterion model and its historical six-criterion comparison have not been rewritten. The current argument-stage decision record is `data/task1_decision_v0.8.json`; the v0.7 selection and decision remain historical, reproducible evidence. This document does not claim complete empirical measurement of all three RTEF principles, an unconditional optimum across mixed baselines, or immunity to every preference and indicator change.

## 1. Decision question and mathematical construction

The case requires a quantitative assessment of all 24 corridors and one corridor recommendation without construction costs, budgets or cost-normalized scores (case physical pp.8–9). It permits mathematically and contextually justified variable selection. We construct a **relative need-priority index**, not a causal estimate of transport benefits or a benefit/cost analysis.

The five active inputs are:

| Input | Interpretation in this study | Important boundary |
| --- | --- | --- |
| current_speed | Published City experience/priority score for current service conditions | Not raw km/h; higher priority-score orientation does not mean faster raw service should be prioritized. |
| unimproved_load | Projected pressure on the unimproved corridor in the City's forecast framework | A forecast-context measure, not observed present demand; base-network context must be retained. |
| current_max_load | Published current on-board load score; a demand-use proxy | Does not directly measure future ridership, operating efficiency, jobs or economic benefit. |
| competitiveness | Published current transit/auto travel-time comparison score | No transfer-connectivity or employment-accessibility measure has been computed. |
| low_income_population_share_500m | Custom concentration of low-income residents around a road proxy | CT uniform-density allocation; LIM numerator / all-resident population, not official private-household LIM prevalence or realized equity benefit. |

The source City fields are standardized, non-cost-scaled scores; the disputed length-scaled current_ridership measure is excluded from the active model. Source Table 1 (evaluation attachment physical p.6) identifies these scaling rules. No City category composite or cost-bearing population/access/development score is imported to fill a gap.

For corridor i, City substitution scenario m and declared weight vector w:

`S_i(m,w) = sum_j w_j × z_ij(m)`, with `w_j >= 0` and `sum_j w_j = 1`.

The four retained City scores keep their source values and declared minimum/mean substitutions. Equity is transformed using the fixed 16-corridor reference: mean **0.13716878222779566**, population SD **0.02473132688714528**. Its z score is `(fraction - mean) / SD`. This reference is frozen across stress comparisons. Published City normalization uses its own source reference, so “equal criterion weight” is not a guarantee of equal within-tier variance or independent information.

Ranking uses tied rank intervals; a corridor is guaranteed top-k only when its worst tied rank is at most k. The provisional recommendation is selected by the previously declared stability screen across the original six-criterion and five-criterion models, not by pretending one corridor maximizes every weighted sum. Corridor 23 is the only main-tier candidate above 90% top-five inclusion in both original paired supports. Each support consists of six distinct method/profile combinations, resampled 10,000 times with common selectors. Those frequencies are not population confidence levels.

## 2. EDA: relationships, missingness and what they imply

The main decision cohort has 16 candidates. We report four correlation views, each for both Pearson and average-tie Spearman:

1. **Pairwise source-available:** retain only original observed City cells for each pair, and omit equity estimates involving suppressed-CT count substitution for correlations with equity. Pair-specific n is **11–14**.
2. **Joint source-complete:** 11 corridors with all five source inputs available under that rule (1,2,7,9,12,15,18,19,20,22,23). This is a diagnostic subset only.
3. **Minimum-substituted:** all 16 candidates under the declared observed-column-minimum scenario.
4. **Mean-substituted:** all 16 under the alternative observed-column-mean scenario.

All 16 are retained in every decision ranking; the source-complete subset never becomes a way to drop difficult alternatives. “Source available” still does not make a CT spatial estimate an exact measured catchment count.

| Indicator pair | Source-available Pearson (n) | Source-available Spearman | Minimum scenario Pearson | Mean scenario Pearson |
| --- | ---: | ---: | ---: | ---: |
| Forecast load / current maximum load | **0.151 (13)** | 0.198 | −0.094 | 0.056 |
| Current speed score / competitiveness | **−0.171 (12)** | −0.259 | 0.318 | −0.179 |

Across all indicator pairs, methods and populations, none triggers the predeclared exploratory `|correlation| >= 0.7` screen. The largest absolute source-pair Pearson relationship is current maximum load versus competitiveness, **−0.564 (n=12)**; it is a trade-off in this cohort, not a same-direction duplicate.

These results do **not** prove independence or absence of redundancy. Forecast and current load have different time/context meanings, and their low observed correlation argues against deleting one merely because both are called demand. Meanwhile, counting multiple measures of a concept can still overallocate normative importance even when the measures are not highly linearly correlated.

The changes in sign/magnitude between source-only, minimum and mean views show why relationships estimated after filling structurally unavailable cells should not be presented as pristine empirical facts. Missing current-service data are not assumed missing at random. No p values, causal claims or population-sampling inference are asserted: the sample is small, corridors can overlap spatially, and the set is a selected finite candidate list.

`descriptive_statistics.csv` reports n, mean, population SD, quartiles and range for each view. Equity source-only summaries use raw proportions; model-complete summaries use the frozen equity z score. Original City units are standardized score units, not physical counts or speeds. Pearson and Spearman heatmaps are exported as PNG/SVG/PDF with per-cell n.

**Model implication:** retain the distinct indicators provisionally, declare conceptual budgets, inspect missing-policy dependence, and stress the recommendation under indicator removal and wider weights. A correlation threshold is a screen, not an automatic variable-selection rule.

## 3. Repeated weighting: control concepts, not just columns

We define three internal scoring blocks for this diagnostic:

- Service/choice need: current_speed and competitiveness.
- Load pressure: unimproved_load and current_max_load.
- Equity need: low_income_population_share_500m.

**These three blocks are not the RTEF's three guiding principles.** Their purpose is to expose how correlated or conceptually overlapping indicators share a weight budget.

The existing five-variable profiles have the following effective conceptual budgets:

| Existing profile | Service/choice block | Load block | Equity block |
| --- | ---: | ---: | ---: |
| Equal five columns | 40.00% | 40.00% | 20.00% |
| Remaining-demand priority | 26.67% | 60.00% | 13.33% |
| Equity priority | 22.22% | 22.22% | 55.56% |

Thus “equal columns” is not equal concepts, and the demand profile intentionally gives 60% to the two load measures. This is a value choice, not something validated by the correlation matrix.

We implement a hierarchical stress model `S_i = sum_g W_g × mean(z_ij for j in group g)`. Four explicit block budgets are tested: equal thirds; service priority (50/25/25); load priority (25/50/25); equity priority (25/25/50). A block budget is split equally among its members. This prevents the mere presence of two indicators from doubling that block's allocation. It does not eliminate every cross-block relationship or establish the correct social values.

We also delete one member of the two multi-indicator blocks at a time **while keeping each block's total budget fixed**. Separately, all five current inputs are each omitted under the original profiles, with proportional renormalization; that broader catalogue has 30 cases. These catalogues have different normative meanings and are not pooled into one artificial probability.

| Stress catalogue | Cases | Corridor 23 top-three share | Top-five share | Rank range |
| --- | ---: | ---: | ---: | --- |
| Four explicit concept budgets × two methods | 8 | 100% | **100%** | 1–3 |
| Fixed-budget block-member deletion | 8 | 75% | **75%** | 1–6 |
| Each active input omitted × three profiles × two methods | 30 | 73.33% | **93.33%** | 1–6 |

In particular, deleting competitiveness and transferring its within-block budget to speed places 23 sixth under both City methods. Two broader ablations without equity also place it sixth. These are concrete limits on any “100% immunity to indicator changes” slogan. They do not erase the useful result that 23 survives the specified disputed-ridership exclusion, or that it remains top-three under all four stated conceptual budgets.

## 4. Weight rationale: transparent assumptions, not invented preferences

The City attachment (physical pp.3–4, Section 2.5) averages measures within RTEF criteria and initially weights criteria equally. Our selected subset is different. **The City did not endorse equal weight for our five columns**, and we do not claim that it did.

The retained profiles have a traceable origin:

- Equal weights are an auditable reference when no defensible preference differences have been elicited, not a theorem of value-neutrality.
- The demand profile intentionally tests a preference for demand/pressure. Its five-variable numbers are inherited by deleting the disputed coefficient from the earlier six-variable vector and proportionally renormalizing, not by fitting a desired winner.
- The equity profile intentionally prioritizes resident equity concentration. It reflects a declared distributional preference, not a claim that this proxy measures actual equity benefits.
- Concept-block profiles test a different hierarchy so that the number of columns does not silently determine a concept's total budget.

No stakeholder survey, expert AHP matrix or agency preference elicitation has taken place. We do not invent one. Data-derived entropy/PCA/variance weights would measure distributional features of this small, partially substituted dataset; they cannot by themselves supply the policy value of equity, growth or service need. We therefore make normative choices explicit and test them instead of branding them objectively optimal.

### Wider preference test and an explicit counterexample

A separate run draws **10,000** three-block budgets from **Dirichlet(1,1,1)** (PCG64 seed **20261122**), independently sampling the two City methods and splitting each block equally among its members. This prior is uniform over the block-weight simplex, not an empirical distribution of public preferences. We additionally report the **3,707** draws in the predeclared illustrative region where every block receives 10%–60%; that region is not a stakeholder-validated acceptance set.

| Preference domain | Draws | Corridor 23 top-five inclusion | Rank range |
| --- | ---: | ---: | --- |
| Full declared block-weight prior | 10,000 | **81.82%** | 1–14 |
| Illustrative 10%–60% block-budget region | 3,707 | **97.63%** | 1–8 |

The deterministic 0.05-step simplex grid supplies a concrete counterexample: with service/choice 80%, load 15%, equity 5%, and mean substitution, corridor 23 ranks **14th** and corridor 9 ranks first. This demonstrates preference dependence. It does not claim that this extreme preference is the appropriate mandate.

Accordingly, corridor 23 remains the current first choice **under the declared service/equity agenda and original stability rule**, with evidence of stability under several balanced concepts. It is not uniquely best for every admissible preference vector. The final decision maker should review the value trade-offs and the unmeasured principles rather than accept a numerical weight vector as fact.

## 5. Coverage of the three guiding principles

The authoritative RTEF mapping is City Figure 1 (attachment physical p.2) and measure Table 1 (p.6). It is mapped explicitly below rather than attaching all five indicators to every principle.

| Principle | Actually scored | Legitimate interpretation | Not measured |
| --- | --- | --- | --- |
| **Serve People** | Speed, forecast load, competitiveness, custom equity concentration | Service/choice pressure and distributional need proxies | Realized travel-time gains, reliability, transfers, station access and distribution of benefits. |
| **Strengthen Places** | **No direct scored outcome** | Existing residential intensity is supplied as unscored spatial context for all 24 | Additional housing, development potential, future place growth, neighbourhood improvement and environmental outcomes. |
| **Support Prosperity** | Current maximum load, placed by the City in its Affordability category | A non-cost demand/use proxy under that source classification | Jobs/access to employment, productivity, forecast economic growth and actual financial efficiency. |

The current maximum-load score is not relabelled as measured economic benefit merely because the source places it under Affordability. Competitiveness may have an indirect economic pathway, but no employment-access calculation was performed. Low-income resident concentration is not evidence of housing construction or land-use potential.

To inform place context without silently changing the model, `unscored_residential_intensity_context.csv` derives existing residential density from the already acquired 2021 area-weighted population divided by CT-supported land area in the road catchment. All 24 values are provided and **none enters the score**. This is current settlement intensity, not future housing/growth evidence. Coastline gaps and the uniform-CT allocation remain limitations.

Why not insert the missing City growth/housing/access scores? The published measures are cost-scaled and the reviewed source does not supply the necessary unscaled inputs. Importing them would violate Part 1's cost-independence requirement. This is a reason for exclusion and a coverage limitation, not a reason to pretend five need proxies fully represent the RTEF.

**Conclusion on scope:** the variable-selection argument is now explicit, but empirical three-principle coverage is partial. A fully balanced place/prosperity claim would require additional cost-independent, operationally defined public evidence or a consciously accepted narrower mandate. The model cannot guarantee the same corridor would win after adding such evidence. The case permits justified selection; this document does not certify a judge's acceptance of every scope choice.

## 6. All 24 are quantitatively assessed; eight are not assigned fabricated common-base ranks

The case explicitly requires quantitative assessment of all 24, so we do not describe eight as excluded from assessment. The new coverage ledger contains one row per corridor, and `all24_contextual_scores.csv` evaluates **all five selected fields for every corridor under all six method/profile combinations: 144 score rows**. Conditional values retain their own baseline labels and every City/Census substitution flag. Their displayed equity z score uses the frozen main-tier reference for consistent units; that does not harmonize forecast baselines or justify pooled ranks.

Let `B_i` denote the source's evaluation baseline and `B_0` its base forecast network. Define main-rank eligibility `a_i = 1[B_i = B_0]`. The 16 eligible candidates can be compared for one evaluated addition in that source context. The other eight are reported with a contextual need index and complete prerequisite closure, but **no cross-baseline absolute rank**. This is a stated study decision policy, not a claim that the case waived eight candidates or that engineering prohibits them.

City Section 2.5 (physical pp.3–4) states that these extension results assume a predecessor or concurrent corridor. A `CITY_BASE_AFTER_X` result does not identify what that extension's same variables would be under `CITY_BASE_0`. Treating it as an independent Base-0 result would introduce an unsupported counterfactual. Neither a good nor a bad conditional score establishes its independent priority. We do not invent a conversion factor.

Each of the eight receives:

1. The same five-variable quantitative contextual assessment in all six cases, with observed/substituted status.
2. Direct/transitive prerequisite identification checked against the source table.
3. Union coverage for the predecessor bundle and the bundle plus extension, counting overlap once.
4. Additional covered population and low-income population under the same CT allocation method.
5. An explicit next decision: reassess when predecessors are part of the decision baseline, obtain a common counterfactual, or evaluate a properly authorized multi-project bundle.

| Extension | Required sequence | Additional residents, estimated | Additional low-income residents, estimated |
| --- | --- | ---: | ---: |
| 3 | 4 -> 3 | 26,772 | 3,467 |
| 6 | 5 -> 6 | 1,020 | 108 |
| 11 | 12 -> 11 | 22,722 | 2,525 |
| 13 | 12 -> 11 -> 13 | 7,675 | 745 |
| 14 | 15 -> 14 | 11,183 | 1,173 |
| 16 | 15 -> 16 | 22,261 | 2,919 |
| 17 | 15 -> 16 -> 17 | 22,549 | 2,651 |
| 24 | 23 -> 24 | 36,917 | 4,423 |

These population additions are geometric coverage estimates, not causal additional ridership or welfare gains. Published standardized scores are not summed over the bundle. In particular, 13 requires 12→11; 17 requires 15→16. An extension cannot be called inferior merely because it is deferred from the current absolute comparison.

With corridor 23 as the current primary, corridor 24 remains an explicitly assessed 23→24 future extension. It is not silently included in the selected corridor or in Part 2's fixed-corridor technology study. Its incremental estimated coverage is approximately 36,917 residents including 4,423 low-income residents under the proxy assumptions; this is planning context, not an additional benefit credited to corridor 23's score.

**Limit of the conclusion:** all 24 have a quantitative assessment, but an unconditional optimum over 24 independent Base-0 projects is not identified by the supplied mixed-baseline data. The recommendation is conditional on the one-step common-baseline study policy. A claim of global unconditional superiority would require common-counterfactual evidence or a different bundle decision model.

## 7. The 12→23 slide is the central methodological result

Suggested slide title: **“A disputed indicator changed our recommendation.”**

Suggested slide text:

> Jane (12) led the original six-criterion model. Removing the length-scaled current-ridership input reduced its top-five inclusion from 100% to 66.59%, with a worst rank of ninth. We retained the published source scores and changed the recommendation rather than inventing a corrected score. Finch East (23) is the only corridor passing the specified top-five stability screen in both models; in the paired five-criterion cases it ranks first or second.

Suggested source note:

> Official Jane length assignments appear inconsistent with the opposite subsection proxies. A transposition is suspected, not officially confirmed; the internal score denominator is unknown. The sensitivity test isolates dependence on the disputed input, not every possible effect of a length error.

Do **not** write “absolute robustness”, “100% immunity to missing data and indicator changes”, or “confirmed official data error”. The exact supported 100% figure belongs to the original six-case paired supports. Wider tests above provide explicit counterexamples. Jane is removed from the current primary recommendation, not deleted from the evaluated alternatives or declared intrinsically worthless.

## 8. Reproducibility and deliverable status

The pre-run analytical configuration is `data/model_argument_policy_v0.8.json`; it is not represented as external study preregistration. All original values and nominal v0.6/v0.7 policies remain unchanged.

```sh
python -B code/analyze_model_argument_v0_8.py
python -B code/assess_all_corridors_v0_8.py
python code/build_model_argument_slides_v0_8.py
python code/finalize_model_argument_v0_8.py
python -B code/validate_model_argument_v0_8.py --output outputs/validation_v0.8.json
python -B -m unittest discover -s code -p 'test_*.py' -v
```

Use the GIS environment and `code/requirements_gis.txt`. Source/output fingerprints are stored in `run_manifest.json`. Existing v0.6 and v0.7 source-replay validators still pass. The full suite has **47 passing tests**, including correlation sample/tie handling, fixed block budgets, preference counterexamples, preservation of the previous main scores, all-24 contextual coverage, density units and rejection of an unsupported immunity claim even after refreshing its output hash.

The model argument, EDA and coverage explanation are documented. `three_principles_fully_measured=false`, `absolute_immunity_supported=false` and `part1_complete=false` remain explicit. Remaining work is team review of the coverage/values scope, any additional direct place/prosperity evidence chosen, final Task 1 deliverable review and then Part 2. The supplied competition AI policy and disclosure obligations remain an independent submission issue; generated analysis and this deck are review drafts, not a clearance to submit.
