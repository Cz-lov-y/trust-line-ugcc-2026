"""Checks for policy/evidence separation and hard-limit precedence."""
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import json
import tempfile
import unittest

from screen_tech_policy_v0_2 import classify,run

ROOT=Path(__file__).resolve().parents[1]


class Task2PolicyTests(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'data/task2_screening_policy_v0.2.json').read_text())
        self.policy=json.loads((ROOT/self.config['strict_policy_file']).read_text())
        self.alts=json.loads((ROOT/self.config['strict_input_file']).read_text())
        self.declarations={a['technology_id']:a for a in self.config['alternatives']}

    def test_requested_shortlist_is_not_engineering_certification(self):
        results=[classify(a,self.policy,self.declarations[a['technology_id']]) for a in self.alts]
        self.assertEqual([r['policy_decision'] for r in results],['conditional_pass','conditional_pass','policy_fail'])
        self.assertEqual([r['provisional_shortlisted'] for r in results],[True,True,False])
        for r in results:
            self.assertFalse(r['verified_feasible']);self.assertFalse(r['demonstrated_hard_failure'])
            self.assertFalse(r['implementation_feasibility_certified'])
            self.assertEqual(r['strict_schedule'],'unknown')

    def test_proven_budget_failure_overrides_conditional_pass(self):
        alt=deepcopy(self.alts[0])
        alt['capital']=dict(evidence_role='corridor_estimate',evidence_ids=['SYNTHETIC_TEST'],
            currency='CAD',undiscounted_initial_capital=True,consultants_excluded=True,
            complete_project_scope=True,comparable_to_budget_price_basis=True,
            lower_cad=17e9,upper_cad=18e9)
        result=classify(alt,self.policy,self.declarations['BRT'])
        self.assertEqual(result['policy_decision'],'verified_fail')
        self.assertFalse(result['provisional_shortlisted']);self.assertTrue(result['demonstrated_hard_failure'])

    def test_subway_can_reopen_if_all_original_gates_pass(self):
        alt=deepcopy(self.alts[2])
        alt['capital']=dict(evidence_role='corridor_estimate',evidence_ids=['SYNTHETIC_TEST'],currency='CAD',
            undiscounted_initial_capital=True,consultants_excluded=True,complete_project_scope=True,
            comparable_to_budget_price_basis=True,lower_cad=5e9,upper_cad=8e9)
        alt['schedule']=dict(evidence_role='corridor_estimate',evidence_ids=['SYNTHETIC_TEST'],
            includes_approvals_design_procurement=True,includes_utilities_and_property=True,
            includes_fleet_and_depot=True,includes_testing_and_operational_readiness=True,
            dependencies_and_overlap_declared=True,project_start_date='2027-01-01',
            earliest_operational_date='2033-01-01',latest_operational_date='2035-01-01',
            elapsed_years_lower=6,elapsed_years_upper=8)
        for key in ('route_engineering','depot'):
            alt[key]=dict(reviewed=True,evidence_ids=['SYNTHETIC_TEST'],assessment='pass',reason='Synthetic complete scheme')
        result=classify(alt,self.policy,self.declarations['SUBWAY'])
        self.assertEqual(result['policy_decision'],'verified_pass')
        self.assertTrue(result['provisional_shortlisted']);self.assertTrue(result['verified_feasible'])

    def test_unknown_policy_and_missing_conditions_rejected(self):
        declaration=deepcopy(self.declarations['BRT']);declaration['requested_decision']='pretend_pass'
        with self.assertRaises(ValueError):classify(self.alts[0],self.policy,declaration)
        declaration['requested_decision']='conditional_pass';declaration['required_condition_ids'].remove('DEPOT')
        with self.assertRaises(ValueError):classify(self.alts[0],self.policy,declaration)

    def test_original_v01_sources_and_artifacts_unchanged(self):
        manifest=json.loads((ROOT/'outputs/task2_v0.1/run_manifest.json').read_text())
        for name,digest in manifest['source_and_artifact_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)

    def test_partial_costs_are_not_admitted_as_full_capital(self):
        with (ROOT/'outputs/task2_v0.2/partial_cost_assumptions.csv').open() as f:rows=list(csv.DictReader(f))
        costs={r['technology_id']:r for r in rows}
        self.assertAlmostEqual(float(costs['BRT']['exact_unadjusted_reference_transfer_cad']),1.4e9/34*7.101)
        self.assertAlmostEqual(float(costs['LRT']['exact_unadjusted_reference_transfer_cad']),1.2e9/11*7.101)
        for r in rows:
            self.assertEqual(r['full_capital_estimate'],'False')
            self.assertEqual(r['budget_verified'],'False');self.assertEqual(r['use_as_mcda_cost'],'False')
            self.assertIn('not',r['bound_provenance'])

    def test_policy_cannot_relax_original_numerical_constraints(self):
        for key,value in [('capital_ceiling_cad',20e9),('planning_window_years',12),
                          ('operational_deadline','2040-12-31'),('corridor_id',24),('length_km',9.514)]:
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);(root/'data').mkdir()
                config=deepcopy(self.config);config[key]=value
                (root/'data/task2_screening_policy_v0.2.json').write_text(json.dumps(config))
                for rel in (config['strict_policy_file'],config['strict_input_file']):
                    (root/rel).write_bytes((ROOT/rel).read_bytes())
                with self.assertRaises(ValueError,msg=key):run(root)

    def test_output_enables_scenarios_without_claiming_a_winner(self):
        out=ROOT/'outputs/task2_v0.2';summary=json.loads((out/'policy_summary.json').read_text())
        self.assertTrue(summary['scenario_development_ready']);self.assertFalse(summary['comparable_numeric_mcda_inputs_ready'])
        self.assertEqual(summary['conditional_shortlist'],['BRT','LRT']);self.assertEqual(summary['policy_excluded'],['SUBWAY'])
        self.assertEqual(summary['verified_failures'],[]);self.assertEqual(summary['verified_feasible'],[])
        self.assertFalse(summary['technology_ranking_performed']);self.assertFalse(summary['task2_complete'])
        self.assertIsNone(summary['selected_technology'])
        with (out/'conditions_register.csv').open() as f:conditions=list(csv.DictReader(f))
        self.assertEqual(len(conditions),12);self.assertTrue(all(r['condition_status']=='open' for r in conditions))


if __name__=='__main__':
    unittest.main()
