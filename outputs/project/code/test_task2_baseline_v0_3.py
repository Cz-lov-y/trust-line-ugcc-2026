"""Checks for units, preference switches, normalization and conditional admission."""
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import json
import tempfile
import unittest
import numpy as np

from run_task2_baseline_v0_3 import (validate_inputs,raw_criteria,normalize,score,winner,
    efficiency_weight_switch,uniform_simplex_brt_share,run)

ROOT=Path(__file__).resolve().parents[1]


def read(name):
    with (ROOT/'outputs/task2_v0.3'/name).open(newline='') as f:return list(csv.DictReader(f))


class Task2BaselineTests(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'data/task2_baseline_assumptions_v0.3.json').read_text())
        self.base=self.config['baseline'];self.ceiling=self.config['capital_ceiling_cad']

    def test_baseline_units_are_indices_and_minutes_not_fabricated_counts(self):
        rows=read('baseline_inputs.csv');brt,lrt=rows
        self.assertAlmostEqual(float(brt['cost_cad_per_km']),49.28883255879454e6)
        self.assertAlmostEqual(float(lrt['cost_cad_per_km']),133.7839740881566e6)
        self.assertEqual(float(brt['ridership_index']),1);self.assertEqual(float(lrt['ridership_index']),1.2)
        self.assertEqual(float(brt['implied_seconds_saved_per_signal']),10)
        self.assertEqual(float(lrt['implied_seconds_saved_per_signal']),14)
        for r in rows:
            self.assertEqual(r['absolute_daily_ridership'],'')
            self.assertEqual(r['cost_is_complete_capital_estimate'],'False')
            self.assertEqual(r['implementation_feasibility_certified'],'False')
            self.assertEqual(r['value_status'],'user_assumption_only')

    def test_invalid_cost_demand_or_saving_and_budget_breaches_rejected(self):
        for key,value in [('brt_cost_cad',0),('lrt_cost_cad',float('inf')),
                ('lrt_to_brt_ridership_ratio',-1),('brt_time_saving_min',-1),
                ('lrt_time_saving_min',float('nan')),('brt_cost_cad',True),('lrt_cost_cad',self.ceiling+1)]:
            values=dict(self.base,**{key:value})
            with self.assertRaises(ValueError,msg=key):validate_inputs(values,self.ceiling)
        validate_inputs(dict(self.base,lrt_cost_cad=self.ceiling),self.ceiling)

    def test_normalization_preserves_ratios_and_handles_zero_information(self):
        raw=raw_criteria(self.base);u=normalize(raw)
        np.testing.assert_allclose(u,[[1,1/1.2,2.5/3.5],[1.2*.35/.95,1,1]])
        np.testing.assert_allclose(normalize(raw*np.array([1000,500,.01])),u)
        equal=np.array([[1,1,0],[1,1,0]],float)
        self.assertEqual(winner(score(normalize(equal),[1/3]*3)),'tie')
        self.assertEqual(winner(score(normalize(equal,'minmax'),[1/3]*3)),'tie')
        self.assertTrue(np.isfinite(normalize(equal)).all())

    def test_standardization_changes_the_equal_weight_winner(self):
        raw=raw_criteria(self.base)
        ratio=score(normalize(raw),[1/3]*3);minmax=score(normalize(raw,'minmax'),[1/3]*3)
        self.assertEqual(winner(ratio),'BRT');self.assertEqual(winner(minmax),'LRT')
        np.testing.assert_allclose(ratio,[.8492063492063493,.8140350877192982])
        np.testing.assert_allclose(minmax,[1/3,2/3])
        for weights in ([1,1,1],[-.1,.5,.6],[float('nan'),0,1]):
            with self.assertRaises(ValueError):score(normalize(raw),weights)

    def test_analytic_weight_switch_is_a_tie_and_changes_winner(self):
        u=normalize(raw_criteria(self.base));root=efficiency_weight_switch(u)
        self.assertAlmostEqual(root,.28847690586543073)
        for weight,expected in [(root,'tie'),(root-.01,'LRT'),(root+.01,'BRT')]:
            self.assertEqual(winner(score(u,[weight,(1-weight)/2,(1-weight)/2])),expected)
        self.assertAlmostEqual(efficiency_weight_switch(normalize(raw_criteria(self.base),'minmax')),.5)

    def test_fixed_seed_weight_draws_match_independent_area_check(self):
        draws=read('weight_draws.csv')
        matrix=np.array([[float(r[k]) for k in ('efficiency_weight','ridership_weight','time_weight')] for r in draws])
        expected=np.random.Generator(np.random.PCG64(self.config['weight_seed'])).dirichlet(np.ones(3),size=10000)
        np.testing.assert_allclose(matrix,expected,atol=1e-15,rtol=0)
        u=normalize(raw_criteria(self.base));winners=matrix@(u[0]-u[1])>0
        share=np.mean(winners);exact=uniform_simplex_brt_share(u)
        self.assertAlmostEqual(exact,.5091996737061543)
        self.assertLess(abs(share-exact),.02)
        row=next(r for r in read('weight_support.csv') if r['normalization']=='ratio_to_best' and r['efficiency_definition']=='ridership_index_per_cost_billion')
        self.assertAlmostEqual(float(row['brt_weight_share']),share)

    def test_exact_midpoint_and_equal_priority_stresses_are_executed(self):
        stresses={s['scenario_id']:s['overrides'] for s in self.config['stress_scenarios']}
        self.assertEqual(stresses['exact_previous_midpoints']['brt_cost_cad'],(.29+.4)/2*1e9)
        self.assertEqual(stresses['exact_previous_midpoints']['lrt_cost_cad'],(.77+1.2)/2*1e9)
        rows=read('scenario_scores.csv');self.assertEqual(len(rows),192)
        self.assertEqual(len({r['scenario_id'] for r in rows}),8)
        for r in rows:
            self.assertTrue(np.isfinite(float(r['score'])))
        zero=[r for r in rows if r['scenario_id']=='zero_TSP_benefit' and r['normalization']=='ratio_to_best']
        self.assertTrue(all(float(r['utility_time'])==0 for r in zero))

    def test_efficiency_overlap_sensitivity_has_one_cost_criterion(self):
        self.assertEqual(self.config['criteria'],['cost_effectiveness','ridership','time_saving'])
        raw=raw_criteria(self.base,'inverse_cost_billion')
        np.testing.assert_allclose(raw[:,0],[1/.35,1/.95])
        equal_demand=dict(self.base,lrt_to_brt_ridership_ratio=1)
        np.testing.assert_allclose(raw_criteria(equal_demand),raw_criteria(equal_demand,'inverse_cost_billion'))

    def test_verified_failure_still_blocks_the_assumption_model(self):
        policy_config=json.loads((ROOT/self.config['policy_file']).read_text())
        strict_inputs=json.loads((ROOT/policy_config['strict_input_file']).read_text())
        strict_inputs[0]['capital']=dict(evidence_role='corridor_estimate',evidence_ids=['SYNTHETIC_TEST'],
            currency='CAD',undiscounted_initial_capital=True,consultants_excluded=True,
            complete_project_scope=True,comparable_to_budget_price_basis=True,lower_cad=17e9,upper_cad=18e9)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for rel in ('data/task2_baseline_assumptions_v0.3.json',self.config['policy_file'],policy_config['strict_policy_file']):
                target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/rel).read_bytes())
            (root/policy_config['strict_input_file']).write_text(json.dumps(strict_inputs))
            with self.assertRaises(ValueError):run(root)

    def test_prior_policy_artifacts_unchanged_and_final_choice_not_forged(self):
        manifest=json.loads((ROOT/'outputs/task2_v0.2/artifact_manifest.json').read_text())
        for rel,digest in manifest.items():self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),digest,rel)
        summary=json.loads((ROOT/'outputs/task2_v0.3/model_summary.json').read_text())
        self.assertTrue(summary['assumption_model_ready']);self.assertFalse(summary['implementation_feasibility_certified'])
        self.assertFalse(summary['complete_capital_estimates']);self.assertFalse(summary['task2_complete'])
        self.assertFalse(summary['robust_winner_across_declared_methods']);self.assertIsNone(summary['selected_technology'])


if __name__=='__main__':unittest.main()
