# Technology evidence dictionary (Task 2 v0.1)

`tech_evidence_v0.1.csv` is a long-format inventory, not a model matrix. `corridor_id=23` identifies the decision context; it does not mean a reference project's value was measured on Finch East.

| Field | Meaning |
|---|---|
| `evidence_id` | Stable record identifier within this version. `T2_REF_*` is reference evidence; `T2_TARGET_*` is an explicitly missing target estimate. |
| `technology_id` | BRT, LRT or SUBWAY. A reference technology association is not a feasibility endorsement. |
| `criterion_id`, `value`, `unit` | Exact type of fact and its unit. Value may be a number, date, year or place. Blank is unknown, never zero. Capacity, passengers/day and passengers/hour/direction are different quantities. |
| `value_status` | `reference_fact` or `pending_evidence` in this version; neither is an admitted target input. |
| `reference_year` | Reference forecast horizon when explicitly stated; otherwise publication or event year as explained in notes. Do not infer a forecast horizon from publication year. |
| `price_year`, `currency` | Monetary basis where supported. Blank means unresolved; a contract publication year is not proof of a constant-dollar price year. |
| `scenario_id` | Reference-only or target-estimate-required context. |
| `lower_bound`, `upper_bound`, `uncertainty_basis` | Published cost scope/range when available; not a statistical confidence interval. Different options or policies are separate records. |
| `source_id`, `source_locator` | Source registry ID and physical PDF page/table or HTML locator. |
| `source_url`, `source_file`, `source_sha256` | Public source URL, preserved local archive and byte hash. Acquired page shells are not automatically substantive evidence. |
| `notes` | Scope, comparisons, exclusions, unresolved assumptions and transfer restrictions. |
| `evidence_role` | `reference_only` or `target_required`. Future corridor estimates require a documented transfer method and explicit admission. |
| `reference_project`, `reference_length_km` | Actual source project and same-scope length when supported. Blank prevents an unsupported per-km calculation. |
| `target_transfer_status`, `use_in_optimization` | All current records remain outside scoring. Do not change these labels without completing the target basis and hard-constraint review. |

Capital checks use undiscounted initial capital with consistent price/cash-flow basis. Exclude consultants per case; exclude operating and lifecycle expenditure from the capital ceiling. Professional-and-agency combined categories cannot simply be relabelled as consultant-only fees. Do not mix present-value economic costs, DBFM contract totals, construction-only components and full project budgets.

Delivery means operational opening after testing, not civil substantial completion. A source construction-to-opening duration may already include testing. Elapsed duration follows the critical path, not an unqualified sum of overlapping stages.

The main screening inputs live in `data/technology_screen_inputs_v0.1.json`. Null capital/schedule objects deliberately block admission. Engineering `reviewed=false` prevents a planned ROW or a reference depot from becoming a passed design. A partial estimate must remain unknown even if its arithmetic is below the ceiling.
