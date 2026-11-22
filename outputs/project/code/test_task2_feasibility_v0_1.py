"""Meaningful failure-mode checks for the pre-MCDA gate; synthetic fixtures only."""
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import json
import unittest

from screen_tech_feasibility_v0_1 import interval_status, cost_gate, schedule_gate, screen

ROOT = Path(__file__).resolve().parents[1]


class Task2FeasibilityTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads((ROOT / 'data/task2_hard_constraints_v0.1.json').read_text())
        self.alt = dict(technology_id='BRT', corridor_id=23, length_km=7.101,
            whole_corridor_single_technology=True,
            capital=dict(evidence_role='corridor_estimate', evidence_ids=['SYNTHETIC_TEST'],
                currency='CAD', undiscounted_initial_capital=True, consultants_excluded=True,
                complete_project_scope=True, comparable_to_budget_price_basis=True,
                lower_cad=1e9, upper_cad=2e9),
            schedule=dict(evidence_role='corridor_estimate', evidence_ids=['SYNTHETIC_TEST'],
                includes_approvals_design_procurement=True, includes_utilities_and_property=True,
                includes_fleet_and_depot=True, includes_testing_and_operational_readiness=True,
                dependencies_and_overlap_declared=True, project_start_date='2027-01-01',
                earliest_operational_date='2031-01-01', latest_operational_date='2032-01-01',
                elapsed_years_lower=4, elapsed_years_upper=5),
            route_engineering=dict(reviewed=True, evidence_ids=['SYNTHETIC_TEST'], assessment='pass', reason='Synthetic reviewed design'),
            depot=dict(reviewed=True, evidence_ids=['SYNTHETIC_TEST'], assessment='pass', reason='Synthetic allocated capacity'))

    def test_inclusive_limits_and_crossing_ranges(self):
        self.assertEqual(interval_status(10, 10, 10), 'pass')
        self.assertEqual(interval_status(9, 11, 10), 'conditional')
        self.assertEqual(interval_status(10.01, 11, 10), 'fail')
        for lo, hi in [(2,1), (float('nan'),2), (1,float('inf')), (-1,2), (True,2)]:
            with self.assertRaises(ValueError):
                interval_status(lo,hi,10)

    def test_only_all_pass_enters_scoring_pool(self):
        self.assertEqual(screen(self.alt,self.policy)['screening_status'],'eligible_for_mcda')
        for field in ('capital','schedule','route_engineering','depot'):
            alt=deepcopy(self.alt);alt[field]=None
            self.assertEqual(screen(alt,self.policy)['screening_status'],'pending_evidence')

    def test_reference_pv_lifecycle_or_partial_cost_cannot_pass(self):
        mutations = [('evidence_role','reference_only'), ('currency','USD'),
            ('undiscounted_initial_capital',False),('consultants_excluded',False),
            ('complete_project_scope',False),('comparable_to_budget_price_basis',False),
            ('evidence_ids',[])]
        for key, value in mutations:
            cost=deepcopy(self.alt['capital']);cost[key]=value
            self.assertEqual(cost_gate(cost,self.policy),'unknown',key)

    def test_cost_fail_excludes_even_if_engineering_unknown(self):
        alt=deepcopy(self.alt);alt['capital']['lower_cad']=17e9;alt['capital']['upper_cad']=18e9
        alt['depot']=None
        self.assertEqual(screen(alt,self.policy)['screening_status'],'excluded')

    def test_budget_straddling_not_eligible(self):
        alt=deepcopy(self.alt);alt['capital']['upper_cad']=17e9
        result=screen(alt,self.policy)
        self.assertEqual(result['budget'],'conditional')
        self.assertEqual(result['screening_status'],'pending_evidence')

    def test_construction_without_testing_depot_or_prework_is_not_full_delivery(self):
        for key in ('includes_approvals_design_procurement','includes_testing_and_operational_readiness',
                    'includes_fleet_and_depot','includes_utilities_and_property','dependencies_and_overlap_declared'):
            schedule=deepcopy(self.alt['schedule']);schedule[key]=False
            self.assertEqual(schedule_gate(schedule,self.policy),'unknown',key)

    def test_calendar_deadline_and_duration_are_both_enforced(self):
        schedule=deepcopy(self.alt['schedule'])
        schedule.update(project_start_date='2032-01-01', earliest_operational_date='2036-01-01', latest_operational_date='2037-01-01')
        self.assertEqual(schedule_gate(schedule,self.policy),'fail')
        # Entire project is after the deadline although its duration is just 4–5 years.
        schedule=deepcopy(self.alt['schedule'])
        schedule.update(project_start_date='2020-01-01', earliest_operational_date='2030-01-01',
                        latest_operational_date='2031-01-01', elapsed_years_lower=10, elapsed_years_upper=11)
        self.assertEqual(schedule_gate(schedule,self.policy),'fail')
        # Opening before deadline alone does not satisfy the user's nine-year rule.

    def test_inconsistent_calendar_durations_rejected(self):
        schedule=deepcopy(self.alt['schedule']);schedule['elapsed_years_upper']=3
        with self.assertRaises(ValueError):
            schedule_gate(schedule,self.policy)

    def test_depot_is_hard_requirement_and_unreviewed_width_is_not_pass(self):
        for field in ('depot','route_engineering'):
            alt=deepcopy(self.alt);alt[field]['reviewed']=False
            self.assertEqual(screen(alt,self.policy)[field],'unknown')
            alt[field]['reviewed']=True;alt[field]['assessment']='fail'
            self.assertEqual(screen(alt,self.policy)['screening_status'],'excluded')

    def test_corridor_scope_and_single_mode_cannot_change(self):
        for key,value in [('corridor_id',24),('length_km',9.514),('whole_corridor_single_technology',False)]:
            alt=deepcopy(self.alt);alt[key]=value
            with self.assertRaises(ValueError):
                screen(alt,self.policy)

    def test_actual_outputs_preserve_unknown_and_no_ranking(self):
        result=json.loads((ROOT/'outputs/task2_v0.1/screening_summary.json').read_text())
        self.assertEqual(result['eligible_technologies'],[])
        self.assertEqual(result['excluded_technologies'],[])
        self.assertEqual(set(result['pending_technologies']),{'BRT','LRT','SUBWAY'})
        self.assertFalse(result['all_technologies_proven_impossible'])
        self.assertFalse(result['scoring_performed'])
        self.assertIsNone(result['selected_technology'])

    def test_reference_table_has_integrity_and_explicit_target_gaps(self):
        with (ROOT/'evidence/tech_evidence_v0.1.csv').open(newline='') as f:
            rows=list(csv.DictReader(f))
        refs=[r for r in rows if r['evidence_role']=='reference_only']
        targets=[r for r in rows if r['evidence_role']=='target_required']
        self.assertEqual(len(refs),29);self.assertEqual(len(targets),12)
        for r in refs:
            self.assertEqual(hashlib.sha256((ROOT/r['source_file']).read_bytes()).hexdigest(),r['source_sha256'])
            self.assertTrue(r['source_url'].startswith('https://'))
        for r in targets:
            self.assertEqual(r['value'],'');self.assertEqual(r['value_status'],'pending_evidence')
        self.assertTrue(all(r['use_in_optimization']=='False' for r in rows))
        ids={r['evidence_id'] for r in rows}
        for alt in json.loads((ROOT/'data/technology_screen_inputs_v0.1.json').read_text()):
            for key in ('route_engineering','depot'):
                self.assertTrue(set(alt[key]['evidence_ids'])<=ids)


if __name__ == '__main__':
    unittest.main()
