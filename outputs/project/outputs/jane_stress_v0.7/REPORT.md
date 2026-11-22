# Jane length audit and leave-current_ridership-out stress test (v0.7)

## Current decision

Apply the user-authorized switch to **corridor 23, Finch Ave E, Yonge St to Victoria Park Ave**, as the provisional Task 1 primary. The five-criterion stress model keeps the prior 16 common-baseline candidates; the eight dependency corridors remain separately assessed. The six-criterion v0.6 model and all source/analysis scores are preserved as the paired baseline.

This is a primary decision after one important indicator test, not a declaration that all of Task 1, Part 2, project feasibility or competition submission clearance is complete. `data/task1_decision_v0.7.json` records the decision and remaining work. The active five-criterion selection is `data/model_input_selection_v0.7.json`; the legacy `model_input_selection_v0.1.json` intentionally remains the six-criterion baseline mapping so its frozen validation contract and outputs remain reproducible.

## 1. What the official source confirms

Official evaluation attachment: <https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243172.pdf>, physical **p.7 Table 2**. This is the evaluation attachment, not p.7 of the separate main report. Its column is **“Assumed Length (km)”**. Section 2.2 on physical p.1 defines length scaling as dividing benefits by **length of construction**. Table 1 on physical p.6 labels **current ridership = Length**.

| Row | Defined corridor | Reported assumed construction length | Base | Measured named-road proxy |
| --- | --- | ---: | --- | ---: |
| 11 | Jane: Bloor St → Eglinton Ave | 11.269 km | after 12 | 4.075 km |
| 12 | Jane: Eglinton Ave → Pioneer Village Station | 4.076 km | 0 | 11.181 km |

The 4.076 km number is **assigned to the evaluated corridor's assumed construction length**. It is not identified as a single side, one-way track mileage, or a partial extension segment. Corridor 12 has Base 0, while corridor 11 extends from 12. No Jane-specific reduced-length footnote is supplied. Footnote 6 about existing grade-separated track belongs to **corridor 3**, not corridor 12.

This does **not** establish that 4.076 km is the true physical full alignment length. Construction length can differ from a full corridor length, and the supplied table does not explain a reduction for this Jane row. The two reported lengths resemble the opposite named-road subsection lengths, suggesting a possible transposition. The proxy paths are not verified future transit alignments, so this remains a hypothesis rather than an authorized correction.

The main report repeats these assignments in **physical p.25 Table 1**: <https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243162.pdf>. Repetition does not independently validate the physical lengths. Both official PDFs were freshly downloaded and match the archived SHA256 hashes byte-for-byte. Visual inspection of the evaluation table confirms this is not merely a text-extraction row alignment error.

Within the documented bounded official-source review, no Jane-specific explanation or official erratum was located. No raw calculation workbook establishes which length was actually used inside the published ridership score. A possibly erroneous table entry therefore does not by itself prove the standardized score used that entry as its denominator.

Source extracts, the original table rendering, fresh-download hashes and the bounded search review are in `evidence/jane_audit_v0.7/`. The structured audit explicitly sets `physical_full_length_4_076_confirmed=false`, `internal_score_denominator_confirmed=false` and `official_erratum_located=false`.

## 2. Paired five-criterion design

The disputed `current_ridership` column is physically excluded from the scored matrix, rather than filled, rescaled or merely renamed. Five retained inputs:

1. current_speed
2. unimproved_load
3. current_max_load
4. competitiveness
5. low_income_population_share_500m

There is **no transfer-connectivity indicator** in either model. Stability cannot be attributed to a transfer metric that was never included. The remaining load measures may still correlate with one another; this test does not resolve every redundancy or definition issue.

Keep the same 16 main-tier candidates, two City substitution methods, frozen nominal equity z-score calibration, PCG64 seed **20261121**, and **all 10,000 exact method/profile selectors** from v0.6. The six distinct cases are also exhaustively evaluated. Delete the disputed coefficient from each weight profile and proportionally normalize the surviving weights to sum to one:

| Profile identity | Speed | Forecast load | Current max load | Competitiveness | Equity |
| --- | ---: | ---: | ---: | ---: | ---: |
| Equal | .200000 | .200000 | .200000 | .200000 | .200000 |
| Remaining-demand priority | .133333 | .266667 | .333333 | .133333 | .133333 |
| Equity priority | .111111 | .111111 | .111111 | .111111 | .555556 |

The stored key `ridership_priority` retains the baseline scenario identity for paired draws; after exclusion it weights the remaining demand/load measures, not the omitted current-ridership input. Weights were not fitted to create a preferred winner. For every corridor/case, the following removal identity is checked:

`five_score = (baseline_score - excluded_weight × original_ridership_z) / (1 - excluded_weight)`.

Original City standard scores and original reported construction lengths are unchanged. The model does not swap the Jane lengths, divide the standardized score by a guessed new length, or reconstruct unobserved raw ridership. A z score cannot be corrected by multiplying a length ratio without the relevant raw values and normalization constants; the source does not provide them.

## 3. Results: the source dispute changes the primary

| Corridor | Baseline rank range | Five-criterion rank range | Baseline top-five frequency | Five-criterion top-five | Five-criterion top-three |
| --- | --- | --- | ---: | ---: | ---: |
| 12: Jane St | 1–1 | 2–9 | 100% | **66.59%** | **33.66%** |
| 23: Finch Ave E | 2–4 | 1–2 | 100% | **100%** | **100%** |

Exact six-case top-five rates are 4/6 for Jane and 6/6 for Finch East. Monte Carlo frequencies differ slightly because the 10,000 uniform draws contain finite sampling variation. These are declared-scenario frequencies, not statistical confidence or population probabilities.

| Scenario | Jane baseline → five criteria | Finch East baseline → five criteria |
| --- | --- | --- |
| Minimum, equal | 1 → 4 | 4 → 2 |
| Mean, equal | 1 → 4 | 4 → 2 |
| Minimum, remaining-demand priority | 1 → 8 | 3 → 1 |
| Mean, remaining-demand priority | 1 → 9 | 3 → 1 |
| Minimum, equity priority | 1 → 2 | 2 → 1 |
| Mean, equity priority | 1 → 2 | 2 → 1 |

Jane does not collapse in every setting: it remains second under equity priority and fourth under equal weights. It nevertheless loses its all-scenario top-five status, drops as far as ninth, and never ranks first in the five-criterion cases. Its previous first-place stability materially depends on inclusion of the disputed length-scaled ridership score. **Corridor 23 is the only candidate exceeding 90% top-five inclusion in both models.** Under the user's decision rule, this supports switching the provisional primary to 23. The five-criterion shortlist is 23,9,20.

A numerical caution: under equal weights Jane's fifth-model score is extremely close to Wilson's (roughly 0.000032 score units separate third and fourth). Two-decimal published City scores and other input uncertainty do not justify treating that near-tie as precise. The demand-profile drop to eighth/ninth and Finch's first/second ranks are the more substantive findings.

The score-component ledger is provided for Jane and Finch. For example, Jane's source current-ridership z score is 3.26 and contributes +0.5433 units to its equal-weight six-criterion score. These are standardized score addends, not measured ridership counts or shares of real transport benefit.

## 4. What the test does and does not settle

The pressure test supports a more defensible primary candidate **without altering source evidence**. It does not show that the Jane length issue is harmless; it shows that the choice is sensitive to inclusion of the associated metric. Nor does it establish whether the official table, the score denominator, or both contain an error.

The current source/definition issue remains flagged. Other limitations remain: only six discrete combinations are explored; weights are illustrative, not stakeholder-elicited; road buffers differ from future station catchments; uniform CT allocation and Census suppression estimates are assumptions; City and Census vintages differ; and the three guiding principles plus correlation/redundancy still require a complete final argument. The newly selected primary has not yet been through Part 2 technology, cost and schedule analysis.

## 5. Files, validation and reproduction

- `data/jane_stress_policy_v0.7.json`: exclusion, proportional weights, paired design and decision rule.
- `data/model_input_selection_v0.7.json`: actual five scored fields and explicit baseline mapping.
- `data/task1_decision_v0.7.json`: corridor 23 primary and remaining Task 1 work.
- `outputs/jane_stress_v0.7/five_indicator_inputs.csv`: five-column scored input grid; omitted field absent.
- `paired_scenario_comparison.csv`: all 96 paired case/corridor scores and ranks.
- `monte_carlo_draws.csv`: all 10,000 paired selectors and resulting ranks.
- `rank_acceptability_comparison.csv`, `jane_finch_score_components.csv`, `renormalized_weights.csv`.
- `jane_finch_rank_stress.{png,svg,pdf}`, `top5_before_after.{png,svg,pdf}`.
- `outputs/validation_v0.7.json`: independent five-score/draw/decision replay.
- `outputs/tests_v0.7.txt`: **40 passing tests**; includes exclusion non-leakage, removal identity, paired selectors, actual rank loss, source-audit limits and forged-result rejection.
- `slides/jane_length_stress_v0.7_review_draft.pptx`: current five-slide review draft, explicitly switching the primary and retaining source/AI-policy limitations.

From the project root, after installing `code/requirements_gis.txt`:

```sh
python code/audit_jane_lengths_v0_7.py
python -B code/run_jane_stress_v0_7.py
python code/finalize_jane_stress_v0_7.py
python code/validate_jane_stress_v0_7.py --output outputs/validation_v0.7.json
python -B -m unittest discover -s code -p 'test_*.py' -v
python code/build_jane_stress_slides_v0_7.py
```

`audit_jane_lengths_v0_7.py` reads the archived official documents; `source_recheck.json` records the separate fresh official fetch. The baseline v0.6 is left intact and still passes its own limited-scope readiness validation. `stress_model_ready=true` means the five-criterion stress calculation is reproducible; `part1_complete=false` and `length_issue_resolved=false` remain explicit. A separate current selection file avoids silently rewriting the old six-criterion baseline contract.

The review deck discloses AI assistance. The supplied full competition guideline p.22 restricts substantive AI uses; any exception's applicability remains unestablished. These results and this deck are analytical review artifacts, not a certification of competition submission compliance.
