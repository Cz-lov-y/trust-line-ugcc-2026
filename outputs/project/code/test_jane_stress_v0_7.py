"""Leave-one-out isolation, paired design and primary-switch regression checks."""
import copy,json,math,shutil,tempfile,unittest
from pathlib import Path
import numpy as np
from tiered_common import ROOT,read,sha,write
from run_tiered_model_v0_6 import load_model,case_results,scenario_draws
from run_jane_stress_v0_7 import five_cases,O
from validate_jane_stress_v0_7 import validate
from validate_data import validate as validate_baseline
class JaneStressTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.config=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text())
  cls.base,_,cls.ids,_,_,minimum,means,equity,mu,sd=load_model();cls.old,cls.matrices=case_results(cls.base,cls.ids,minimum,means,equity,mu,sd);cls.new,cls.five=five_cases(cls.config,cls.base,cls.matrices)
 def test_proportional_weights_and_removal_identity(self):
  excluded=self.base['fields'].index('current_ridership')
  for old,new in zip(self.old,self.new):
   w=self.base['weight_profiles'][old['weight_profile']][excluded];x=self.matrices[old['city_method']][:,excluded]
   self.assertTrue(np.allclose(new['scores'],(old['scores']-w*x)/(1-w),atol=1e-12,rtol=0))
  self.assertNotIn('current_ridership',self.config['fields']);self.assertTrue(all(m.shape==(16,5) for m in self.five.values()))
 def test_excluded_column_cannot_leak_into_five_scores(self):
  modified={method:matrix.copy() for method,matrix in self.matrices.items()}
  for matrix in modified.values():matrix[:,self.base['fields'].index('current_ridership')]=np.arange(16)*1e9
  altered,_=five_cases(self.config,self.base,modified)
  for before,after in zip(self.new,altered):self.assertTrue(np.array_equal(before['scores'],after['scores']))
 def test_seed_and_every_selector_match_baseline(self):
  expected=scenario_draws(self.base).tolist();rows=read(O/'monte_carlo_draws.csv')
  self.assertEqual(len(rows),10000);self.assertEqual([int(r['case_id']) for r in rows],expected)
 def test_actual_rank_loss_triggers_finch_primary(self):
  jane=[int(c['rank_high'][self.ids.index(12)]) for c in self.new];finch=[int(c['rank_high'][self.ids.index(23)]) for c in self.new]
  self.assertEqual(jane,[4,8,2,4,9,2]);self.assertEqual(finch,[2,1,1,2,1,1])
  summary=json.loads((O/'jane_stress_summary.json').read_text());self.assertEqual(summary['jane_12']['five_top5_frequency'],.6659);self.assertEqual(summary['finch_23']['five_top5_frequency'],1);self.assertTrue(summary['switch_to_23_triggered']);self.assertEqual(summary['primary_corridor_id'],23);self.assertFalse(summary['length_issue_resolved'])
 def test_source_audit_and_baseline_still_validate(self):
  audit=json.loads((ROOT/'evidence/jane_audit_v0.7/jane_length_audit.json').read_text());self.assertEqual(audit['rows'][1]['reported_assumed_construction_length_km'],4.076);self.assertFalse(audit['internal_score_denominator_confirmed']);self.assertFalse(audit['physical_full_length_4_076_confirmed']);self.assertTrue(validate_baseline(ROOT)['model_ready']);self.assertTrue(validate(ROOT)['stress_model_ready'])
 def test_forged_stress_rank_is_rejected_after_hash_refresh(self):
  manifest=json.loads((O/'run_manifest.json').read_text())
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   for rel in set(manifest['source_files'])|set(manifest['output_files'])|{'outputs/jane_stress_v0.7/run_manifest.json'}:
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,p)
   file=root/'outputs/jane_stress_v0.7/paired_scenario_comparison.csv';rows=read(file)
   next(r for r in rows if r['case_id']=='1' and r['corridor_id']=='12')['five_rank_worst']='1';write(file,rows)
   rel=str(file.relative_to(root));manifest['output_files'][rel]=sha(file);(root/'outputs/jane_stress_v0.7/run_manifest.json').write_text(json.dumps(manifest))
   result=validate(root);self.assertFalse(result['stress_model_ready']);self.assertTrue(any('replay failed' in e for e in result['errors']))
if __name__=='__main__':unittest.main()
