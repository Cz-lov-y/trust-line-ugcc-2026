# Task 2 v0.4: proportional costs, milestones, TSP evidence and policy choice

**The four requested tasks are complete at competition scope:** a source-based cost composition check inside the existing totals, four assumed delivery milestones, citations to existing TTC/City TSP evidence, and a fixed-formula policy-weight decision. No independent ridership forecasting, new route-time collection, detailed construction schedule or engineering certification is introduced as a requirement.

The corridor remains **23: Finch East, Yonge–Victoria Park, 7.101 km**. BRT/LRT remain conditional alternatives; Subway remains outside the conservative base-case shortlist by the v0.2 policy. Source data, the CAD350M/CAD950M user cost points, R index 1/1.2, T savings 2.5/3.5 minutes and v0.3 scoring formula are unchanged.

## 1. Cost proportions: an accounting check inside fixed assumed totals

**Source:** Metrolinx, *Eglinton Crosstown West Extension Initial Business Case*, February 2020, Table 19, **physical p.79 / printed p.71**, with assumptions on physical p.78 / printed p.70. [Official PDF](https://assets.metrolinx.com/image/upload/v1668540646/Images/Metrolinx/2020-02-28_ECWE_IBC.pdf) · [Archived PDF](../../evidence/tech_support_v0.4/ecwe_ibc_2020.pdf).

Option 1 is used because it is the reference's mostly surface-running LRT option, rather than the selected final underground project. It still includes an airport segment and is not a Finch East scheme. Its financial capital table is nominal year-of-expenditure expenditure, not a current constant-dollar target estimate. Here only **dimensionless composition shares** are transferred; the cost levels are not transferred or inflation-adjusted.

| Category | Published amount, CAD million | Share of reported 2,935M | Share after professional-services exclusion proxy |
|---|---:|---:|---:|
| Property acquisition | 31 | 1.06% | **1.23%** |
| Vehicles | 410 | 13.97% | **16.32%** |
| Systems | 218 | 7.43% | **8.67%** |
| Contingency | 677 | 23.07% | **26.94%** |
| Other capital / indirect / tax / reconciliation | 1,177 | 40.10% | **46.84%** |
| Professional services | 422 | 14.38% | **0%** |
| Total | 2,935 | 100% | 100% |

The case excludes consultant costs. For this illustrative composition, remove the whole separately reported professional-services allowance and renormalize the rest to **2,935−422 = 2,513M**. This is a declared proxy, not a consultant-only cost audit: professional services includes design/procurement/construction support, and the separate indirect-cost row may contain unidentified fee elements. No claim of exact consultant exclusion is made.

The eleven published line items sum to **2,933M**, versus the published total 2,935M. Preserve the **2M unresolved reconciliation** in the other bucket; rounding is plausible but not officially established. The other bucket includes guideway, stations/stops, MSF, sitework, indirect costs, tax and reconciliation. It is neither an omitted add-on nor a demonstrated consultant-free subtotal.

Applying the normalized shares **within**, rather than on top of, the user's fixed totals gives:

| Category | Allocation share | BRT, CAD million | LRT, CAD million |
|---|---:|---:|---:|
| Property | 1.23% | 4.32 | 11.72 |
| Vehicles | 16.32% | 57.10 | 154.99 |
| Systems | 8.67% | 30.36 | 82.41 |
| Contingency | 26.94% | 94.29 | 255.93 |
| Other capital / indirect / tax / reconciliation | 46.84% | 163.93 | 444.95 |
| **Total, unchanged** | **100%** | **350.00** | **950.00** |

These figures demonstrate an internally balanced allocation, **not independent validation that 350M/950M covers the full project**. They do not turn the earlier construction-component reference into a full capital estimate. No category is charged twice. Both assumed totals remain numerically below CAD16.657B, subject to their declared scope/price limitations.

Two important transfer limits remain visible: (1) the source assumes private property acquisition only in its airport segment, so the low land share does not establish Finch East land needs; (2) applying an LRT composition to BRT is the requested cross-technology approximation, not evidence of actual BRT vehicle/system/land proportions. The table is a proportion check, not a new bill of quantities.

## 2. Four milestones, not a quantitative construction schedule

**User duration assumptions:** 1–2 years planning/approvals, 1–2 years property/utilities, 3–4 years core construction, 1 year tests. Sequential range: **6–9 years**. Illustrative programme start: **January 1, 2027**. The calendar below uses the upper case, **2+2+4+1=9 years**, without relying on overlapping stages:

| Milestone | Assumed phase duration | Illustrative upper-case completion |
|---|---|---|
| Planning and approvals | 1–2 years | December 31, 2028 |
| Property and utility enabling works | 1–2 years | December 31, 2030 |
| Core construction and systems | 3–4 years | December 31, 2034 |
| Testing, commissioning and operational readiness | 1 year | **December 31, 2035** |

Procurement decisions are included in planning; fleet manufacture, depot/access, stations and systems must be delivered within the construction milestone. These are not uncounted fifth/sixth phases after the deadline. The upper case has **zero additional delay buffer**, and unresolved property, utility or depot issues remain delivery risks.

The calendar is an explicitly assumed milestone scenario for both conditional alternatives, not an agency forecast, critical-path analysis or proof that both schemes will open. Existing local context remains relevant: Newmarket's construction-to-opening interval was roughly four years; Finch West's utilities-to-opening interval was roughly nine, excluding earlier planning. The proposed LRT core/test durations are assumptions, not durations validated by the longer Finch West actual history. No Gantt chart, day-level estimate or independent construction-scheduling model is needed for this package.

The case's physical p.10 asks for a **credible development timeline for the recommended project**, while explicitly not requiring quantitative construction scheduling, independent ridership forecasting or formal hypothesis tests. Milestone evidence and assumptions should be judged on that scope, without substituting engineering certification for the competition task.

## 3. Existing TSP citations and the assumed benefits

| Existing official evidence | Correct interpretation | Target use |
|---|---|---|
| TTC April 2026 *Improving LRT and Streetcar Speed and Reliability*, physical p.6: selected Spadina intersections up to **30 sec**, King up to **10 sec** | Selected intersections and time-of-day results; not a whole-route reduction rate | Context for testing user assumptions |
| City's 2026 congestion-plan attachments, physical p.20: selected Dundas/College results up to **25 sec** | Preserve the source difference; do not average 25 and 30 or call either an expected target saving | Same context, not a forecast |
| TTC report pp.1,9: Line 6 approximately **20 min afternoon-peak round-trip improvement** since opening | TSP plus other operational changes; not a TSP-only causal effect or a bus-to-LRT saving | Supporting operational context only |

Source URLs, locators and unchanged notes appear in [the citation table](TSP_citation_table.csv). No new actual runtime is collected. At the **assumed** 15 signals, 2.5/3.5 minutes correspond to 10/14 seconds per signal if each contributes equally. Those equivalents are below selected-pilot maxima but are **not empirically calibrated Finch East averages**. A pilot maximum gives no positive lower bound for another corridor or technology. Both savings remain explicit user assumptions on a common hypothetical before-trip baseline; neither is guaranteed by LRT capacity or grade separation. Existing equal/zero TSP sensitivity remains in v0.3. Avoid adding savings to a speed already incorporating TSP.

## 4. Fixed scoring and policy-weight switch

The existing formula is frozen: **E=R/C**, primary normalization **ratio to best**, S=w_Eu_E+w_Ru_R+w_Tu_T. Cost/km is diagnostic, not another scored criterion. No new formula or normalization is introduced, and no old score is edited. The cases below are copied exactly from the v0.3 baseline results:

| Declared analytical priority | E / R / T weights | BRT | LRT | Conditional preference |
|---|---|---:|---:|---|
| Equal baseline | 1/3 / 1/3 / 1/3 | 0.849206 | 0.814035 | **BRT** |
| Capital-efficiency priority | 0.50 / 0.25 / 0.25 | 0.886905 | 0.721053 | **BRT** |
| Service-benefit priority | 0.20 / 0.40 / 0.40 | 0.819048 | 0.888421 | **LRT** |

When the remaining demand/time weights are equal, **28.8477% efficiency weight** is the baseline tie. Above it BRT wins; below it LRT wins. This is a decision boundary under the fixed assumptions, not a universally optimal technology threshold.

**E and R still share ridership information.** Policy-weight switching makes the chosen priorities explicit; it does not mathematically eliminate that overlap. We disclose it instead of claiming independence or introducing a new formula. The profiles are analyst value choices, not official Toronto policy, surveyed public preferences or empirically estimated weights. The prior normalization sensitivity is retained in v0.3 rather than hidden, but the current decision page uses the already declared primary method consistently.

Suggested closing slide text:

> Under our equal or capital-efficiency priorities and declared scenario inputs, BRT is the preferred conditional option for Finch East. A service-benefit priority instead selects LRT. Cost composition, TSP evidence and the four milestone scenario support transparent review of the assumptions; they do not certify final engineering feasibility. The preference is a policy choice with a visible switching boundary.

## Deliverables and status

[Cost allocation](cost_ratio_allocation.csv) · [Four milestones](delivery_milestones.csv) · [TSP citations](TSP_citation_table.csv) · [Unchanged policy scores](fixed_policy_scores.csv) · [Four-slide review deck](../../slides/task2_competition_v0.4_review_draft.pptx).

`requested_four_deliverables_complete=true` and `competition_scope_analysis_package_ready=true`. This is a competition-level analytical package, not an engineering certification. Reference ratios do not independently establish complete target capital or exact consultant exclusions. Final presentation/submission status and the project's existing AI-use disclosures remain separate. All earlier source and analysis artifacts remain unchanged.

```sh
python code/build_task2_competition_pack_v0_4.py
python code/build_task2_competition_slides_v0_4.py
python -m unittest discover -s code -p 'test_task2*.py'
```
