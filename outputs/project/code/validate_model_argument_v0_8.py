"""Check argument outputs, preference replay, all-corridor coverage and claim limits."""
import json,math
from pathlib import Path
import numpy as np
from tiered_common import ROOT,read,sha
from analyze_model_argument_v0_8 import worst_ranks
from validate_data import validate as validate_base
from validate_jane_stress_v0_7 import validate as validate_stress

def validate(root=ROOT,check_history=True):
 root=Path(root);o=root/'outputs/model_argument_v0.8';errors=[]
 try:
  if check_history and (not validate_base(root)['model_ready'] or not validate_stress(root)['stress_model_ready']):raise ValueError('Historical model no longer validates')
  config=json.loads((root/'data/model_argument_policy_v0.8.json').read_text());active=json.loads((root/'data/jane_stress_policy_v0.7.json').read_text());fields=active['fields'];ids=active['main_tier_ids']
  manifest=json.loads((o/'run_manifest.json').read_text())
  for section in ['source_files','output_files']:
   for rel,digest in manifest[section].items():
    p=(root/rel).resolve()
    if not p.is_relative_to(root.resolve()) or not p.exists() or sha(p)!=digest:raise ValueError('Missing/changed argument artifact: '+rel)
  for rel,digest in manifest['repository_source_files'].items():
   p=(root.parent.parent/rel).resolve()
   if not p.is_relative_to(root.parent.parent.resolve()) or sha(p)!=digest:raise ValueError('Repository source mismatch')
  ledger=read(o/'all24_evaluation_coverage.csv');context=read(o/'all24_contextual_scores.csv')
  if len(ledger)!=24 or {int(r['corridor_id']) for r in ledger}!=set(range(1,25)) or len(context)!=144 or len({(r['corridor_id'],r['city_method'],r['weight_profile']) for r in context})!=144:raise ValueError('All-24 evaluation grid incomplete')
  master={int(r['corridor_id']):r for r in read(root/'data/corridor_master_v0.1.csv')}
  for r in ledger:
   cid=int(r['corridor_id'])
   if r['quantitatively_assessed']!='True' or r['selected_field_count']!='5' or r['declared_method_profile_cases']!='6' or r['main_rank_eligible']!=str(cid in ids) or r['baseline_scenario_id']!=master[cid]['baseline_scenario_id']:raise ValueError('Incorrect tier/coverage claim')
  city_tables={method:{int(r['corridor_id']):r for r in read(root/path)} for method,path in zip(active['city_methods'],['data/city_analysis_inputs_v0.4.csv','data/city_mean_sensitivity_v0.4.csv'])}
  equity={int(r['corridor_id']):float(r[fields[-1]]) for r in read(root/'data/supplemental_model_inputs_v0.5.csv')}
  reference=np.array([equity[cid] for cid in ids]);mu,sd=float(reference.mean()),float(reference.std(ddof=0))
  for r in context:
   cid=int(r['corridor_id'])
   for f in fields:
    expected=(equity[cid]-mu)/sd if f==fields[-1] else float(city_tables[r['city_method']][cid][f])
    if not math.isclose(float(r[f]),expected,abs_tol=1e-12):raise ValueError('Context input differs from source/declared calibration')
   if r['cross_baseline_rank']!='not_computed' or r['baseline_scenario_id']!=master[int(r['corridor_id'])]['baseline_scenario_id']:raise ValueError('Context was pooled across baselines')
   weights=active['weight_profiles'][r['weight_profile']];expected=sum(float(r[f])*w for f,w in zip(fields,weights))
   if not math.isclose(float(r['contextual_priority_index']),expected,abs_tol=1e-10):raise ValueError('Context score formula mismatch')
  pairs=read(o/'conditional_assessment_detail.csv')
  if len(pairs)!=8 or {int(r['corridor_id']) for r in pairs}!=set(active['conditional_tier_ids']) or any(r['all5_selected_fields_evaluated']!='True' or r['unanchored_absolute_rank']!='not_identified' for r in pairs):raise ValueError('Conditional assessment incomplete or ranked without common base')
  norm=read(root/'outputs/jane_stress_v0.7/five_indicator_inputs.csv');matrices=[]
  for method in active['city_methods']:
   byid={int(r['corridor_id']):r for r in norm if r['city_method']==method};matrices.append(np.array([[float(byid[cid][f]) for f in fields] for cid in ids]))
  index=[[fields.index(f) for f in members] for members in config['blocks'].values()];group=np.stack([np.column_stack([m[:,ix].mean(axis=1) for ix in index]) for m in matrices])
  rng=np.random.Generator(np.random.PCG64(config['continuous_seed']));n=config['continuous_group_weight_draws'];methods=rng.integers(0,2,n);budgets=rng.dirichlet(np.ones(3),n)
  scores=np.einsum('nk,njk->nj',budgets,group[methods]);ranks=worst_ranks(scores);draws=read(o/'continuous_block_weight_draws.csv')
  if len(draws)!=10000:raise ValueError('Broader weight draws incomplete')
  region=config['balanced_region'];mask=(budgets.min(axis=1)>=region['minimum_each_block'])&(budgets.max(axis=1)<=region['maximum_each_block'])
  for i,r in enumerate(draws):
   if int(r['draw_id'])!=i+1 or r['city_method']!=active['city_methods'][methods[i]] or r['inside_illustrative_balanced_region']!=str(bool(mask[i])):raise ValueError('Preference selector metadata mismatch')
   if not np.allclose([float(r[b]) for b in config['blocks']],budgets[i],atol=1e-13,rtol=0):raise ValueError('Continuous preferences not reproducible')
   if any(int(r[f'corridor_{cid}_rank_worst'])!=ranks[i,j] for j,cid in enumerate(ids)):raise ValueError('Preference ranks not reproducible')
  coverage=json.loads((o/'coverage_summary.json').read_text());summary=json.loads((o/'argument_analysis_summary.json').read_text())
  if coverage['all_three_principles_directly_scored'] or coverage['all24_unconditional_optimum_identified'] or summary['absolute_immunity_supported'] or summary['three_principles_fully_measured']:raise ValueError('Unsupported completeness/robustness claim')
  context=read(o/'unscored_residential_intensity_context.csv')
  if len(context)!=24 or any(r['scored_in_main_model']!='False' for r in context):raise ValueError('Unscored context was silently admitted')
  for r in context:
   if not math.isclose(float(r['existing_residential_density_persons_per_km2'])*float(r['CT_cartographic_land_support_km2']),float(r['covered_population_estimate']),abs_tol=1e-6):raise ValueError('Residential density unit mismatch')
 except (OSError,ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as e:errors.append(str(e))
 return dict(argument_artifacts_valid=not errors,model_argument_documented=not errors,nominal_primary_corridor_id=23,all24_quantitatively_assessed=not errors,absolute_immunity_supported=False,three_principles_fully_measured=False,part1_complete=False,source_values_modified=False,errors=errors)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();r=validate();s=json.dumps(r,indent=2);print(s)
 if a.output:a.output.write_text(s+'\n')
 raise SystemExit(0 if r['argument_artifacts_valid'] else 1)
