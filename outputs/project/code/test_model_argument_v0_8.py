"""Numerical EDA, duplicate-budget, coverage and claim-boundary verification."""
import copy,json,math,shutil,tempfile,unittest
from pathlib import Path
import numpy as np
from tiered_common import ROOT,read,write,sha,rank_intervals
from analyze_model_argument_v0_8 import average_ranks,correlation,block_feature_weights,worst_ranks
from validate_model_argument_v0_8 import validate
O=ROOT/'outputs/model_argument_v0.8'
class ModelArgumentTests(unittest.TestCase):
 def test_spearman_ties_and_source_pair_counts(self):
  self.assertTrue(np.array_equal(average_ranks([4,1,1,2]),[4,1.5,1.5,3]));self.assertAlmostEqual(correlation([1,1,2,3],[9,9,4,0],'Spearman_average_ties'),-1)
  rows=read(O/'indicator_correlations.csv');self.assertEqual(len(rows),80)
  source={int(r['corridor_id']):r for r in read(ROOT/'data/city_standardized_scores_v0.1.csv')};ids=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text())['main_tier_ids']
  pairs=[(float(source[c]['unimproved_load']),float(source[c]['current_max_load'])) for c in ids if source[c]['current_max_load']!='']
  stored=next(r for r in rows if r['population']=='pairwise_source_available_main_tier' and r['method']=='Pearson' and r['field_x']=='unimproved_load' and r['field_y']=='current_max_load')
  self.assertEqual(int(stored['n']),len(pairs));self.assertAlmostEqual(float(stored['corr']),float(np.corrcoef(np.array(pairs).T)[0,1]),places=12)
  self.assertFalse(any(r['absolute_screen_flag']=='True' for r in rows))
 def test_fixed_block_deletion_preserves_group_budget(self):
  config=json.loads((ROOT/'data/model_argument_policy_v0.8.json').read_text());fields=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text())['fields'];budgets=[1/3]*3
  w=block_feature_weights(config,fields,budgets,'competitiveness');self.assertAlmostEqual(w[fields.index('current_speed')],1/3);self.assertEqual(w[fields.index('competitiveness')],0)
  for block,budget in zip(config['blocks'].values(),budgets):self.assertAlmostEqual(sum(w[fields.index(f)] for f in block),budget)
  with self.assertRaises(ValueError):block_feature_weights(config,fields,budgets,fields[-1])
 def test_vector_ranks_and_preference_counterexample(self):
  values=[[10,9,8,7,6,6],[2,4,1,4,8,3]]
  for row,ranks in zip(values,worst_ranks(values)):
   self.assertEqual(ranks.tolist(),rank_intervals(row)[1])
  summary=json.loads((O/'argument_analysis_summary.json').read_text());self.assertFalse(summary['absolute_immunity_supported']);self.assertEqual(summary['grid_counterexample']['corridor_23_rank_worst'],14)
  rows=read(O/'continuous_rank_acceptability.csv');full=next(r for r in rows if r['corridor_id']=='23' and r['weight_region']=='full_Dirichlet_simplex');balanced=next(r for r in rows if r['corridor_id']=='23' and r['weight_region']=='illustrative_balanced_region')
  self.assertAlmostEqual(float(full['top5_frequency']),.8182);self.assertEqual(int(balanced['draws']),3707);self.assertAlmostEqual(float(balanced['top5_frequency']),3619/3707)
 def test_main_scores_match_prior_five_model_and_all24_are_assessed(self):
  contextual=read(O/'all24_contextual_scores.csv');self.assertEqual(len(contextual),144);self.assertEqual({int(r['corridor_id']) for r in contextual},set(range(1,25)))
  old={(r['city_method'],r['weight_profile'],r['corridor_id']):float(r['five_score']) for r in read(ROOT/'outputs/jane_stress_v0.7/paired_scenario_comparison.csv')}
  for r in contextual:
   key=(r['city_method'],r['weight_profile'],r['corridor_id'])
   if key in old:self.assertAlmostEqual(float(r['contextual_priority_index']),old[key],places=12)
   self.assertEqual(r['cross_baseline_rank'],'not_computed')
  conditional=read(O/'conditional_assessment_detail.csv');self.assertEqual(len(conditional),8);self.assertTrue(all(r['all5_selected_fields_evaluated']=='True' and r['unanchored_absolute_rank']=='not_identified' for r in conditional))
 def test_principle_gap_is_disclosed_and_context_is_not_scored(self):
  coverage=read(O/'three_principle_coverage.csv');self.assertEqual(len(coverage),3);place=next(r for r in coverage if r['principle']=='Strengthen Places');self.assertEqual(place['scored_fields'],'');self.assertIn('gap',place['coverage_status'])
  for r in read(O/'unscored_residential_intensity_context.csv'):
   self.assertEqual(r['scored_in_main_model'],'False');self.assertAlmostEqual(float(r['covered_population_estimate']),float(r['CT_cartographic_land_support_km2'])*float(r['existing_residential_density_persons_per_km2']),places=6)
  self.assertFalse(json.loads((O/'coverage_summary.json').read_text())['all_three_principles_directly_scored'])
 def test_full_argument_and_prior_models_validate(self):
  result=validate(ROOT);self.assertTrue(result['argument_artifacts_valid'],result['errors']);self.assertFalse(result['part1_complete'])
 def test_absolute_immunity_or_pooled_rank_cannot_be_forged(self):
  manifest=json.loads((O/'run_manifest.json').read_text())
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'repo/outputs/project';root.mkdir(parents=True)
   for rel in set(manifest['source_files'])|set(manifest['output_files'])|{'outputs/model_argument_v0.8/run_manifest.json'}:
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
   for rel in manifest['repository_source_files']:
    p=root.parent.parent/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT.parent.parent/rel,p)
   self.assertTrue(validate(root,check_history=False)['argument_artifacts_valid'])
   file=root/'outputs/model_argument_v0.8/argument_analysis_summary.json';data=json.loads(file.read_text());data['absolute_immunity_supported']=True;file.write_text(json.dumps(data));manifest['output_files'][str(file.relative_to(root))]=sha(file);(root/'outputs/model_argument_v0.8/run_manifest.json').write_text(json.dumps(manifest))
   result=validate(root,check_history=False);self.assertFalse(result['argument_artifacts_valid']);self.assertTrue(any('Unsupported' in s for s in result['errors']))
if __name__=='__main__':unittest.main()
