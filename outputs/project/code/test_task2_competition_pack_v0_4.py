"""Check accounting, deadline limits and preservation of the existing model."""
from copy import deepcopy
from pathlib import Path
import csv
import hashlib
import json
import unittest

from build_task2_competition_pack_v0_4 import ratio_template,milestones

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    with (ROOT/path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


class Task2CompetitionPackTests(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'data/task2_competition_pack_v0.4.json').read_text())
        self.summary=json.loads((ROOT/'outputs/task2_v0.4/package_summary.json').read_text())

    def test_source_denominators_and_reconciliation_remain_visible(self):
        rows,difference,net=ratio_template(self.config)
        self.assertEqual(sum(self.config['reference_components_million'].values()),2933)
        self.assertEqual(difference,2);self.assertEqual(net,2513)
        r={r['category']:r for r in rows}
        self.assertAlmostEqual(r['property']['published_total_share'],31/2935)
        self.assertAlmostEqual(r['contingency']['professional_services_excluded_template_share'],677/2513)
        full=read('outputs/task2_v0.4/reference_cost_ratios.csv')
        self.assertAlmostEqual(sum(float(r['published_total_share']) for r in full),1)
        self.assertAlmostEqual(sum(float(r['professional_services_excluded_template_share']) for r in full),1)

    def test_allocations_sum_to_original_totals_without_addons(self):
        rows=read('outputs/task2_v0.4/cost_ratio_allocation.csv')
        self.assertEqual(len(rows),10)
        for mode,total in [('BRT',350e6),('LRT',950e6)]:
            selected=[r for r in rows if r['technology_id']==mode]
            self.assertAlmostEqual(sum(float(r['allocated_cad']) for r in selected),total,places=6)
            self.assertAlmostEqual(sum(float(r['template_share']) for r in selected),1)
            self.assertTrue(all(r['allocation_inside_total']=='True' and r['full_capital_cost_verified']=='False' for r in selected))

    def test_fee_proxy_is_not_certified_and_bad_templates_rejected(self):
        self.assertFalse(self.summary['exact_consultant_exclusion_verified'])
        self.assertFalse(self.summary['allocation_is_total_cost_validation'])
        rows=read('outputs/task2_v0.4/reference_cost_ratios.csv')
        fee=next(r for r in rows if r['category']=='professional_services_excluded')
        self.assertEqual(float(fee['reference_amount_million']),422)
        self.assertEqual(float(fee['professional_services_excluded_template_share']),0)
        bad=deepcopy(self.config);bad['reference_components_million']['Vehicles']=-1
        with self.assertRaises(ValueError):ratio_template(bad)
        bad=deepcopy(self.config);bad['allocation_buckets']['vehicles']='Professional Services'
        with self.assertRaises(ValueError):ratio_template(bad)

    def test_four_milestones_fit_the_window_with_no_upper_case_buffer(self):
        rows,lo,hi=milestones(self.config,'2035-12-31',9)
        self.assertEqual(len(rows),4);self.assertEqual((lo,hi),(6,9))
        self.assertEqual(rows[-1]['illustrative_upper_case_completion'],'2035-12-31')
        self.assertEqual(self.summary['upper_case_delay_buffer_years'],0)
        self.assertFalse(self.summary['quantitative_construction_scheduling_performed'])
        bad=deepcopy(self.config);bad['milestones'][2]['duration_upper_years']=5
        with self.assertRaises(ValueError):milestones(bad,'2035-12-31',9)
        bad=deepcopy(self.config);bad['milestones'][-1]['illustrative_completion']='2036-12-31'
        with self.assertRaises(ValueError):milestones(bad,'2035-12-31',9)

    def test_existing_TSP_sources_reused_without_new_forecast(self):
        original={r['evidence_id']:r for r in read('evidence/tech_evidence_v0.1.csv')}
        table=read('outputs/task2_v0.4/TSP_citation_table.csv')
        self.assertEqual({r['evidence_id'] for r in table},set(self.config['TSP_evidence_ids']))
        for row in table:
            for key,value in row.items():self.assertEqual(value,original[row['evidence_id']][key])
        self.assertFalse(self.summary['independent_ridership_forecasting_performed'])
        self.assertFalse(self.summary['new_runtime_data_collection_performed'])

    def test_policy_scores_are_exactly_preserved_not_new_formula(self):
        old=read('outputs/task2_v0.3/baseline_scores.csv')
        new=read('outputs/task2_v0.4/fixed_policy_scores.csv')
        self.assertEqual(new,old)
        self.assertEqual(self.summary['capital_efficiency_priority_winner'],'BRT')
        self.assertEqual(self.summary['service_benefit_priority_winner'],'LRT')
        self.assertFalse(self.summary['scoring_formula_changed'])
        self.assertFalse(self.summary['overlap_eliminated'])

    def test_prior_baseline_artifacts_remain_immutable(self):
        manifest=json.loads((ROOT/'outputs/task2_v0.3/artifact_manifest.json').read_text())
        for rel,digest in manifest.items():self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),digest,rel)

    def test_ready_package_does_not_forge_engineering_clearance(self):
        self.assertTrue(self.summary['requested_four_deliverables_complete'])
        self.assertTrue(self.summary['competition_scope_analysis_package_ready'])
        self.assertFalse(self.summary['implementation_feasibility_certified'])
        archive=json.loads((ROOT/'evidence/tech_support_v0.4/acquisition_manifest.json').read_text())[0]
        self.assertEqual(hashlib.sha256((ROOT/archive['file']).read_bytes()).hexdigest(),archive['sha256'])


if __name__=='__main__':unittest.main()
