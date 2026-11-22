"""Meaningful tier-isolation, numerical replay and readiness rejection checks."""
from pathlib import Path
import copy,json,math,csv,shutil,tempfile,unittest
import numpy as np
from tiered_common import ROOT,O,read,write,sha,policy,tiers,rank_intervals
from run_tiered_model_v0_6 import load_model,case_results,scenario_draws
from validate_tiered_contract import validate_tiered_contract
from validate_data import validate
class TieredModelTests(unittest.TestCase):
 def test_dependencies_and_no_pooled_ranking(self):
  _,main,conditional,closure=tiers(read(ROOT/'data/corridor_master_v0.1.csv'),policy())
  self.assertEqual((len(main),len(conditional)),(16,8));self.assertEqual(closure[13],[12,11]);self.assertEqual(closure[17],[15,16])
  scores=read(O/'six_scenario_scores.csv');self.assertEqual({int(r['corridor_id']) for r in scores},set(main));self.assertTrue(all(int(r['rank_worst'])<=16 for r in scores))
  bad=copy.deepcopy(policy());bad['main_tier_ids'].append(3)
  with self.assertRaises(ValueError):tiers(read(ROOT/'data/corridor_master_v0.1.csv'),bad)
 def test_normalization_and_source_preservation(self):
  config,_,main,_,_,minimum,means,equity,mu,sd=load_model();cases,matrices=case_results(config,main,minimum,means,equity,mu,sd)
  z=matrices[config['city_methods'][0]][:,-1];self.assertAlmostEqual(float(z.mean()),0,places=12);self.assertAlmostEqual(float(z.std(ddof=0)),1,places=12)
  for method,table in zip(config['city_methods'],[minimum,means]):
   for i,cid in enumerate(main):self.assertAlmostEqual(matrices[method][i,0],float(table[cid]['current_speed']))
  self.assertTrue(all(np.isfinite(case['scores']).all() for case in cases))
 def test_fixed_seed_matches_all_stored_draws(self):
  draws=scenario_draws(policy());self.assertTrue(np.array_equal(draws,scenario_draws(policy())))
  self.assertEqual(draws.tolist(),[int(r['case_id']) for r in read(O/'monte_carlo_draws.csv')]);self.assertEqual(len(draws),10000)
  self.assertEqual(set(draws),set(range(6)))
 def test_exact_support_and_simulated_top5_reproduce_candidates(self):
  config,_,main,_,_,minimum,means,equity,mu,sd=load_model();cases,_=case_results(config,main,minimum,means,equity,mu,sd);draws=scenario_draws(config)
  rows={int(r['corridor_id']):r for r in read(O/'rank_acceptability.csv')}
  for i,cid in enumerate(main):
   self.assertAlmostEqual(float(rows[cid]['exact_top5_frequency']),sum(c['rank_high'][i]<=5 for c in cases)/6)
   self.assertAlmostEqual(float(rows[cid]['top5_frequency']),sum(cases[k]['rank_high'][i]<=5 for k in draws)/10000)
  result=json.loads((O/'tiered_model_summary.json').read_text());self.assertEqual(set(result['high_confidence_top5_candidates']),{12,23});self.assertEqual(result['main_shortlist'],[12,23,20])
 def test_tied_boundary_does_not_manufacture_top5_stability(self):
  low,high=rank_intervals([10,9,8,7,6,6]);self.assertEqual(low[-2:],[5,5]);self.assertEqual(high[-2:],[6,6]);self.assertTrue(all(v>5 for v in high[-2:]))
 def test_conditional_union_catchments_add_up_without_summed_scores(self):
  rows=read(O/'conditional_pair_analysis.csv');self.assertEqual(len(rows),8)
  for r in rows:
   self.assertAlmostEqual(float(r['with_extension_population_estimate']),float(r['base_population_estimate'])+float(r['incremental_population_estimate']),places=5)
   self.assertEqual(r['main_absolute_rank'],'not_applicable');self.assertEqual(r['City_score_bundle_total'],'not_additive_not_computed')
 def test_real_endpoint_checks_and_limited_readiness(self):
  rows=read(O/'woodbine_anchor_sensitivity.csv');self.assertEqual(len(rows),18)
  for r in rows:
   radius=math.hypot(float(r['dx_m']),float(r['dy_m']));self.assertTrue(radius<1e-9 or abs(radius-250)<1e-9)
  report=validate(ROOT);self.assertTrue(report['model_ready']);self.assertTrue(report['core_ready']);self.assertTrue(report['limitations_ready']);self.assertTrue(report['limitations_flagged']);self.assertFalse(report['unrestricted_model_ready']);self.assertEqual(report['admitted_indicator_count'],6)
  self.assertFalse(validate_tiered_contract(ROOT,False)['model_ready'])
 def test_unsupported_flags_and_ranks_fail_even_with_refreshed_hash(self):
  manifest=json.loads((O/'run_manifest.json').read_text())
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   paths=set(manifest['source_files'])|set(manifest['output_files'])|{'outputs/tiered_v0.6/run_manifest.json'}
   for rel in paths:
    dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dest)
   self.assertTrue(validate_tiered_contract(root,True)['model_ready'])
   mutations=[('data/corridor_tiers_v0.6.csv','source_files',lambda r:r.update(main_rank_eligible='True') if r['corridor_id']=='13' else None),('data/geometry_declarations_v0.6.csv','source_files',lambda r:r.update(proxy_declared='False') if r['corridor_id']=='5' else None),('outputs/tiered_v0.6/rank_acceptability.csv','output_files',lambda r:r.update(high_confidence_candidate='True') if r['corridor_id']=='9' else None),('outputs/tiered_v0.6/monte_carlo_draws.csv','output_files',lambda r:r.update(corridor_12_rank_worst='16') if r['draw_id']=='1' else None)]
   for rel,section,mutate in mutations:
    p=root/rel;original=p.read_bytes();rows=read(p)
    for r in rows:mutate(r)
    write(p,rows);changed=copy.deepcopy(manifest);changed[section][rel]=sha(p);(root/'outputs/tiered_v0.6/run_manifest.json').write_text(json.dumps(changed))
    result=validate_tiered_contract(root,True);self.assertFalse(result['model_ready'],rel);self.assertTrue(result['readiness_issues'])
    p.write_bytes(original);(root/'outputs/tiered_v0.6/run_manifest.json').write_text(json.dumps(manifest))
if __name__=='__main__':unittest.main()
