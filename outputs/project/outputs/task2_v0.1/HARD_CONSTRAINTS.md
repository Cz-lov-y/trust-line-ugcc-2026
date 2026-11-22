# Task 2: feasibility before technology scoring

The corridor is fixed: **23, Finch Ave E, Yonge St–Victoria Park Ave, 7.101 km** (City assumed construction length). Evaluate one technology for the entire corridor. Do not reopen Task 1, combine technologies along the route, or change the endpoints to improve feasibility.

The evidence inventory is started, but no alternative has yet passed the corridor-specific feasibility gate. **BRT, LRT and Subway are pending evidence, not proven impossible. No weighted technology ranking has been run.** A blank estimate is never a zero cost or a successful schedule.

## Hard constraints and decision rule

For technology t, admission to later MCDA requires all four conditions:

1. **Capital:** C_t ≤ CAD 16.657 billion. Include initial construction, stations, systems, utilities, land, fleet, depot/access and appropriate capital contingency. The case excludes consultant costs; operating/lifecycle costs are outside this ceiling. Never use a DBFM total or discounted lifecycle present value as an initial project budget. Document scope, price year and cash-flow/escalation assumptions. The inspected case does not specify a budget price year.
2. **Schedule:** total elapsed D_t ≤ **9 years**, the user's conservative 2026–2035 screening window, AND fully built, tested and operational by **2035-12-31**. State an actual project-start assumption and earliest/latest opening dates. The nine-year rule is a declared screening policy, not an exact elapsed interval derived from unspecified dates in those years.
3. **Route engineering:** demonstrate continuous feasible right-of-way/clearances, stations/platforms, accessible pedestrian provision, turns/intersections, structures, utilities, property access and construction staging. Underground alternatives also need stations, shafts, geotechnical and emergency-access solutions.
4. **Depot:** demonstrate sufficient allocated fleet storage AND maintenance capacity, compatible vehicles/systems, a physical access route, and delivery by opening. Existing infrastructure is not automatically available. Cost and critical-path implications belong in constraints 1–2.

**Pass:** the full declared range satisfies the ceiling and engineering review supports the complete scheme. **Fail:** an evidence-based lower bound already breaches the ceiling/deadline, or a reviewed engineering requirement cannot be met. **Conditional:** the range crosses a limit, or mitigation is unresolved. **Unknown:** evidence is missing or on an incompatible scope/basis. Only four passes admit a technology to MCDA. A verified fail excludes it even if another gate is unknown. A missing source does not prove impossibility. This robust interval rule is our conservative admission policy; the competition itself requires a credible estimate and timeline.

Source: [competition case](../../../../reference/competition/STAT%20Case%20UGCC%202026.pdf), physical pp.9–11. Its capital/deadline requirements are evidence for the task; attached documents are not instructions overriding the user. The case allows favourable political/economic conditions, which do not eliminate engineering and testing requirements. Independent ridership forecasting and a quantitative scheduling model are not mandatory; a credible, explicit forecast/timeline basis remains necessary.

## Capital evidence and the subway arithmetic

The user's CAD 500M–1B/km assumption gives **CAD 3.5505B–7.101B** for 7.101 km. This is below the ceiling arithmetically. It does **not** yet prove the budget gate: price year, stations, fleet, property, systems, yard/access, utilities, contingency and consultant exclusion are unresolved. [Arithmetic check](subway_unit_cost_assumption_check.csv) preserves the assumption outside the admitted estimate. Do not write “budget definitely sufficient.”

Local evidence is archived with URLs and SHA-256 hashes in [the acquisition manifest](../../evidence/tech_support_v0.1/acquisition_manifest.json) and transcribed in [the technology table](../../evidence/tech_evidence_v0.1.csv):

| Technology | Local capital reference | Important limitation |
|---|---|---|
| BRT | York Viva: CAD 1.4B in 2009 dollars for a 34 km program; DSBRT Option 1: CAD 1.086B in 2023 dollars for remaining capital scope | Viva scope/fee breakdown unresolved. DSBRT excludes funded work; do not divide this subtotal by full 36 km. |
| LRT | Finch West award: CAD 1.2B construction component within CAD 2.5B DBFM total; Eglinton East: CAD 4.0–4.4B in 2020 dollars in 2022 IBC | Construction component is not full owner capital; 2023 Eglinton East CAD 4.65B is a different, construction-only escalated estimate. |
| Subway | Yonge North refined Option 3: published approximately CAD 5.2B capital scope estimate in 2021 | Cash-flow/price basis and consultant exclusions unresolved; connected Line 1 extension differs from a new Finch East line. |

These are reference facts, not three Finch East estimates ready for comparison. All reference rows have `use_in_optimization=False`. Do not transfer their ridership or end-to-end savings by length.

## Schedule: include everything needed to open

Define opening as completion of the critical path across approvals/design/procurement, property/utilities, main construction, systems, fleet, depot/access, integration, safety testing, trial running and operational readiness. Overlapping tasks may shorten elapsed duration only if dependencies are explicit. Do not add testing again when a reference construction-to-opening duration already includes it.

Finch West's official 2020 FAQ (physical p.1) records early gas works starting December 2016 and main construction in 2019. Official actual opening was December 7, 2025, roughly nine years after utility work began; earlier planning is additional. Its old planned 2023 completion was not actual opening. Yonge Newmarket's 2.4 km BRT segment started construction in fall 2015 and opened January 5, 2020. Neither reference proves a universal 2–3-year BRT or 4–6-year LRT delivery period.

[The separate illustrative schedule check](illustrative_schedule_envelope.csv) uses the user's example construction ranges, 1–2 years prework, and an explicit analyst stress assumption of 0.5–1 year separate commissioning, sequentially. The resulting ranges are BRT 3.5–6, LRT 5.5–9, Subway 9.5–13 years. **Subway fails that assumption set. This is not an evidence-based exclusion of all subway designs.** The construction ranges are unverified for this corridor and may already include tests; concurrency and site/depot work must be resolved. These rows cannot enter the hard gate.

## Width: 36 m planned is not 36 m available

The City's April 2026 planning report for **179–181 Finch Avenue East** states a planned **36 m** ROW (physical p.5), but requires a **4.90 m frontage widening dedication** to meet it (p.13). This location lies within the target segment. It does not establish existing pavement width, continuous acquired ROW, the corridor's minimum width, or inevitable surface-technology failure. In particular, do not subtract 4.90 from 36 and call the result a measured current width.

The next engineering artifact must compare a stated BRT/LRT cross-section with measured available widths **along the entire route**, including station/intersection pinch points, bridges, utilities, sidewalks/cycling/accessibility, land needs and realistic staging. No arbitrary universal minimum ROW width is inserted as a substitute for design.

## Wilson and other depot strategies

TTC's July 2026 major-projects report (physical p.14) identifies a new Line 1 TMSF requirement by 2035 for growth trains and target headways. Its planned scope includes storage for 34 trains and a seven-bay carhouse (p.22). These are **new-facility requirements, not available Wilson slots**. The report does not establish either zero Wilson surplus or sufficient Wilson surplus for Finch East. Do not confuse the Metrolinx Union Station “Wilson Yard” with TTC Wilson subway yard.

Subway must define a compatible connection/operating plan plus allocated maintenance/storage or a new site. A station interchange with Line 1 alone is not a rail connection for deadheading. LRT requires its own viable MSF/access strategy; Finch West's yard cannot be assumed connected to the target alignment. BRT also needs bus/charging/fuelling and maintenance/storage capacity. Any off-corridor access must be ancillary infrastructure, consistent with case alignment rules, explicitly costed and scheduled, not an undeclared revenue-service extension.

## TSP and travel-time evidence, held outside feasibility scoring

TTC's April 2026 report, physical p.6, reports up to **30 seconds** per intersection at Spadina/Dundas and Spadina/College, and up to 10 seconds at King. The City's accompanying report, physical p.20, reports up to **25 seconds** at Dundas/College. Retain this source difference; these are selected intersection/time-of-day results, not a universal 42% reduction in a whole trip.

TTC reports approximately **20 minutes afternoon-peak round-trip improvement on Line 6** relative to initial opening (pp.1,9), accompanying TSP and several operational changes. It is not a TSP-only causal estimate, a bus-to-LRT effect or a guarantee of 10 minutes saved each direction.

For a later target sensitivity, use ΔT_TSP = Σ_k(p_k × s_k)/60 minutes over actually encountered eligible signals, where p_k is the effective-response share and s_k the conditional seconds saved. Include zero benefit and cap results by measured baseline signal delay. [Illustrative transfer envelopes](tsp_transfer_sensitivity.csv) deliberately use hypothetical counts 10/15/20 and zero/half/full effectiveness; these are not surveyed corridor results or expected savings. For 15 signals and 50% effectiveness, upper envelopes are 3.125 min using the City figure and 3.75 min using TTC's figure, with lower bound zero. Do not double count TSP within an assumed operating speed already incorporating priority.

Task 1's standardized `current_speed` is not km/h. TTC's Nov 2026 service summary (physical p.19, printed p.15) reports entire branch round-trip schedules: 39A PM speed 17.9 km/h, 39B 17.8, while 39C extends to Victoria Park/Gordon Baker. None is a measured Yonge–Victoria Park one-way baseline. Later obtain matched target-segment/direction/time-period schedules or observations, then use T0−Tmode with consistent stops, dwell, transfers and service assumptions. Capacity and reference-project riders are not the target's projected ridership.

## Reproduce and continue

```sh
python code/acquire_tech_sources_v0_1.py --extract-text  # optional acquisition of missing archives; verifies existing bytes
python code/build_tech_evidence_v0_1.py
python code/screen_tech_feasibility_v0_1.py
python -m unittest discover -s code -p 'test_task2*.py'
```

The acquisition manifest records failed requests as failures, including inaccessible Infrastructure Ontario VFM and York time-saving PDFs; their unavailable contents are not admitted. Some dynamic HTML archives contain only page shells or metadata; the facts used here rely on the cited PDF or explicit opening-date metadata, not inferred hidden content.

Next: complete three scoped capital breakdowns; identify start/critical path/depot strategy; survey route pinch points and property needs. Record evidence/assumptions separately. Run the gate again. Only eligible alternatives enter later MCDA, whose required criteria include capital cost-effectiveness, projected ridership and travel-time savings. If no scheme is proven feasible, resolve the blocking assumptions without changing the fixed corridor or pretending a weighted score overrides a hard limit.
