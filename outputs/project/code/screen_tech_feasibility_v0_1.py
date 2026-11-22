"""Task 2 admission gate. Unknown evidence never becomes a feasible alternative.

No technology scores or ranks are computed here. Costs are undiscounted project
capital, excluding consultants; timelines end after testing and operational readiness.
"""
from pathlib import Path
from datetime import date
import csv
import json
import math

ROOT = Path(__file__).resolve().parents[1]


def interval_status(lower, upper, ceiling):
    values = (lower, upper, ceiling)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or
           not math.isfinite(x) or x < 0 for x in values):
        raise ValueError('Bounds and ceiling must be finite nonnegative numbers')
    if lower > upper:
        raise ValueError('Reversed interval')
    if lower > ceiling:
        return 'fail'
    if upper <= ceiling:
        return 'pass'
    return 'conditional'


def cost_gate(cost, policy):
    if not cost or cost.get('evidence_role') != 'corridor_estimate' or not cost.get('evidence_ids'):
        return 'unknown'
    required = ('undiscounted_initial_capital', 'consultants_excluded',
                'complete_project_scope', 'comparable_to_budget_price_basis')
    if cost.get('currency') != 'CAD' or any(cost.get(k) is not True for k in required):
        return 'unknown'
    return interval_status(cost['lower_cad'], cost['upper_cad'], policy['capital_ceiling_cad'])


def schedule_gate(schedule, policy):
    if not schedule or schedule.get('evidence_role') != 'corridor_estimate' or not schedule.get('evidence_ids'):
        return 'unknown'
    required = ('includes_approvals_design_procurement', 'includes_utilities_and_property',
                'includes_fleet_and_depot', 'includes_testing_and_operational_readiness',
                'dependencies_and_overlap_declared')
    if any(schedule.get(k) is not True for k in required):
        return 'unknown'
    duration = interval_status(schedule['elapsed_years_lower'], schedule['elapsed_years_upper'],
                               policy['planning_window_years'])
    earliest = date.fromisoformat(schedule['earliest_operational_date'])
    latest = date.fromisoformat(schedule['latest_operational_date'])
    start = date.fromisoformat(schedule['project_start_date'])
    if not start <= earliest <= latest:
        raise ValueError('Invalid schedule dates')
    # Reject a short claimed duration paired with dates spanning more than the window.
    if abs((earliest - start).days / 365.2425 - schedule['elapsed_years_lower']) > .02 or \
       abs((latest - start).days / 365.2425 - schedule['elapsed_years_upper']) > .02:
        raise ValueError('Calendar dates disagree with elapsed duration')
    deadline = date.fromisoformat(policy['operational_deadline'])
    calendar = 'fail' if earliest > deadline else ('pass' if latest <= deadline else 'conditional')
    if 'fail' in (duration, calendar):
        return 'fail'
    return 'conditional' if 'conditional' in (duration, calendar) else 'pass'


def engineering_gate(review):
    if not review or review.get('reviewed') is not True or not review.get('evidence_ids') or not review.get('reason'):
        return 'unknown'
    result = review.get('assessment')
    if result not in ('pass', 'fail', 'conditional', 'unknown'):
        raise ValueError('Invalid engineering assessment')
    return result


def screen(alternative, policy):
    if alternative['corridor_id'] != 23 or alternative['length_km'] != 7.101 or \
       alternative.get('whole_corridor_single_technology') is not True:
        raise ValueError('Task 2 corridor and single-technology scope are locked')
    gates = dict(budget=cost_gate(alternative.get('capital'), policy),
                 schedule=schedule_gate(alternative.get('schedule'), policy),
                 route_engineering=engineering_gate(alternative.get('route_engineering')),
                 depot=engineering_gate(alternative.get('depot')))
    status = ('excluded' if 'fail' in gates.values() else
              'eligible_for_mcda' if all(v == 'pass' for v in gates.values()) else
              'pending_evidence')
    return dict(technology_id=alternative['technology_id'], **gates, screening_status=status)


def run(root=ROOT):
    policy = json.loads((root / 'data/task2_hard_constraints_v0.1.json').read_text())
    alternatives = json.loads((root / 'data/technology_screen_inputs_v0.1.json').read_text())
    if {a['technology_id'] for a in alternatives} != {'BRT', 'LRT', 'SUBWAY'} or len(alternatives) != 3:
        raise ValueError('Exactly three distinct technology dossiers are required')
    results = [screen(a, policy) for a in alternatives]
    out = root / 'outputs/task2_v0.1'
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'hard_constraint_screen.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    summary = dict(corridor_id=23, length_km=7.101, capital_ceiling_cad=policy['capital_ceiling_cad'],
                   operational_deadline=policy['operational_deadline'],
                   eligible_technologies=[r['technology_id'] for r in results if r['screening_status'] == 'eligible_for_mcda'],
                   excluded_technologies=[r['technology_id'] for r in results if r['screening_status'] == 'excluded'],
                   pending_technologies=[r['technology_id'] for r in results if r['screening_status'] == 'pending_evidence'],
                   scoring_performed=False, selected_technology=None,
                   task2_complete=False, no_feasible_technology_proven=not any(r['screening_status'] == 'eligible_for_mcda' for r in results),
                   all_technologies_proven_impossible=all(r['screening_status'] == 'excluded' for r in results))
    (out / 'screening_summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    return summary


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
