# Task 2 v0.2: a conditional shortlist that can move forward

**BRT and LRT receive Conditional Pass for scenario development. Subway is excluded from the base-case shortlist under the user-authorized conservative delivery/depot policy.** This supersedes v0.1's provisional shortlist policy, while preserving its source facts and evidence-based feasibility checks.

Fixed scope: corridor **23, Finch Ave E, Yonge–Victoria Park, 7.101 km**. Capital ceiling **CAD16.657B**; complete development/delivery **≤9 years** under the user's policy; built, tested and operational **by 2035-12-31**. These limits have not been relaxed.

| Technology | Decision for this analysis | Basis and remaining conditions |
|---|---|---|
| BRT | **Conditional Pass** | Keep a surface busway for scenario development. Newmarket's local construction-to-opening experience supports considering it, but a complete Finch East schedule, route fit and bus-garage strategy remain conditions. |
| LRT | **Conditional Pass** | Keep surface rail with a tight delivery envelope. Finch West's roughly nine years from early utilities to opening provides caution, not proof of a complete nine-year target programme. ROW/property/utilities and MSF/access remain conditions. |
| Subway | **Conservative screen Fail / policy exclusion** | Do not carry into base-case weighted comparison while a credible nine-year full programme and allocated depot/access remain unsupported. This is a declared risk policy, not demonstrated physical infeasibility. |

## What changes, and what does not

Conditional admission does not require 100% certainty. It allows explicit assumptions, mitigations and stress scenarios to be investigated before final project design. It also does not turn a missing full capital estimate into zero cost, a planned ROW into an available cross-section, or an unallocated depot into confirmed capacity.

The primary decision field is now `policy_decision`, with BRT/LRT `conditional_pass` and Subway `policy_fail`. The old four evidence gate results remain visible in `strict_*` fields. None currently proves feasibility or a hard failure. A later **verified** budget, deadline or engineering failure overrides conditional admission. Conversely, if a fully evidenced Subway scheme satisfies all original hard constraints, the rule permits reconsideration; it is not a permanent technology ban.

This is an explicit asymmetric risk preference: the team is willing to investigate unresolved surface alternatives while excluding a newly developed underground alternative from its conservative base case. The same missing depot evidence is not being represented as a physical failure for Subway and a physical success for surface modes. The policy preference must be disclosed, and the excluded option must remain documented. No probability of completion, inevitable failure, or engineering certification is inferred from that preference.

## Capital envelopes: retain the arithmetic and its scope

| Technology | Exact unadjusted length transfer | User scenario envelope | Interpretation |
|---|---|---|---|
| BRT | 1.4B / 34 × 7.101 = **CAD0.292394B** | **CAD0.29–0.40B** | Viva's provincial programme investment, in **2009 dollars**; complete consultant/fleet/owner-scope breakdown unresolved. |
| LRT | 1.2B / 11 × 7.101 = **CAD0.774655B** | **CAD0.77–1.20B** | Finch West's **2018 published construction component**, not complete owner capital. Publication year is not proof of a constant-dollar price basis. |
| Subway | 7.101 × 0.5–1.0B/km = **CAD3.5505–7.101B** | Same arithmetic envelope | User unit-cost assumption; complete scope and price year unresolved. |

The upper bounds are user scenario choices, not official uncertainty ranges or an inflation conversion. Preserve these as **partial historical cost assumptions**, outside numeric MCDA inputs. Do not call them full capital estimates or compare them as equal-price-year budgets. Full capital must include the applicable property, utilities, vehicles, stations, systems, depot/access and contingency, while excluding consultant fees per the case. Do not add items already included in a source component. Neither “budget definitely sufficient” nor a complete-capital cost ranking is currently established.

Sources: [Viva opening release](https://www.yrrtc.ca/news_releases/2020-01-03_Viva-Bus-Rapid-Transit-Segments-Opening-in-Vaughan-and-Newmarket), [Finch West award](https://www.aecon.com/press-room/news/2018/05/07/1428-Aecon-consortium-reaches-financial-close-on-Finch-West-Light-Rail-Transit-project). Exact archives and hashes remain in [the reference table](../../evidence/tech_evidence_v0.1.csv), records T2_REF_001 and T2_REF_008.

## Delivery and depots: what existing evidence supports

- **BRT:** Newmarket's 2.4km segment began construction in fall 2015 and opened January 5, 2020 (T2_REF_006–007). Earlier development is not counted by that interval. This motivates a conditional surface option; it does not establish that an entire new programme, including a garage, is safely complete inside nine years.
- **LRT:** Finch West's early gas works started December 2016, main construction began in 2019, and actual opening was December 7, 2025 (T2_REF_014–016). Pre-2016 planning is additional. Its history is neither a duration distribution nor proof that a 7.101km project takes the same time.
- **Subway:** the LRT experience does not prove a numerical subway duration lower bound or a high probability of missing 2035. TTC identifies a new Line 1 TMSF need by 2035 (T2_REF_023–024); this neither proves zero spare Wilson capacity nor a delivery time for a new Finch East facility. Exclusion therefore rests on the declared conservative policy while these issues remain unresolved.

The illustrative sequential Subway scenario in v0.1 is 9.5–13 years, using user example construction durations and separate analyst testing assumptions. It fails that scenario's nine-year limit; it is not an independently verified target schedule. Parallel works or a duration already including tests must be handled explicitly, not double-counted.

## Engineering: conditions, not unsupported guarantees

The City describes a **planned 36m ROW**, with a **4.90m frontage widening dedication** required at 179–181 Finch Avenue East (T2_REF_025–028). This is local evidence, not a measured corridor-wide minimum. BRT may offer fleet and staging options; a blanket claim that BRT always needs less width than LRT is not established. Busway lane/platform/bypass layouts can change the comparison. Both require a continuous, stated cross-section and pinch-point review.

BRT needs an allocated compatible bus/charging/fuelling/maintenance strategy. LRT needs a connected MSF; Finch West's existing yard is not automatically connected or available to this corridor. Subway needs a suitable depot or an allocated, compatible existing facility with a real rail access route. These costs and dates belong in the capital and critical-path conditions.

## Conditions to release or reject an alternative

1. **COST:** complete comparable initial capital estimate within CAD16.657B, with scope and consultant treatment documented.
2. **OPENING:** full critical-path programme, stated start, justified overlaps and testing, ≤9 years and operational by December 31, 2035.
3. **ROW:** route/station/intersection/structure fit, utilities/property/staging mitigation inside the same capital and schedule envelope.
4. **DEPOT:** identified allocated storage and maintenance, fleet compatibility and physical access, costed and operational by opening.

All twelve technology/condition entries are tracked in [the register](conditions_register.csv), including the conditions for reconsidering Subway. A failed verified condition excludes an option regardless of its weighted benefits. For BRT/LRT, the conditions are open while scenario development proceeds.

## Slide wording

> **We retain BRT and LRT as conditional alternatives. Subway is excluded from our conservative base-case shortlist because a complete nine-year delivery programme and allocated depot/access solution have not been demonstrated. This is a screening policy, not proof that subway construction is physically impossible. Surface alternatives must still satisfy the same final capital, opening, route and depot conditions.**

[Three-slide review deck](../../slides/task2_screening_v0.2_review_draft.pptx) keeps the qualification visible. It is an analytical draft under the project's existing AI-use disclosure and submission-status caveats.

## Reproduce and next work

```sh
python code/screen_tech_policy_v0_2.py
python code/build_task2_screening_slides_v0_2.py
python -m unittest discover -s code -p 'test_task2*.py'
```

`scenario_development_ready=true`: the conditional shortlist is available to the next stage. `comparable_numeric_mcda_inputs_ready=false`: complete comparable capital inputs and matched Finch East demand/time assumptions have not yet been supplied. No technology has received a weighted score or final recommendation in this step. Complete those assumptions for BRT/LRT, test cost and schedule stress cases, then run provisional MCDA with all conditions visible. Task 1 source data and v0.1 evidence checks remain unchanged.
