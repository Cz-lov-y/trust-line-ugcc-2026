"""Independent numerical replay of five-criterion scores and paired draw decisions."""
from pathlib import Path
import json,math,statistics,itertools
from tiered_common import ROOT,read,sha,rank_intervals

def validate(root=ROOT):
 root=Path(root);o=root/'outputs/jane_stress_v0.7';errors=[];summary={}
 try:
  config=json.loads((root/'data/jane_stress_policy_v0.7.json').read_text());base=json.loads((root/'data/tiered_model_policy_v0.6.json').read_text())
  if config['city_methods']!=base['city_methods'] or list(config['weight_profiles'])!=list(base['weight_profiles']) or config['seed']!=base['seed'] or config['draws']!=10000:raise ValueError('Paired scenario design changed')
  fields=[f for f in base['fields'] if f!='current_ridership'];ids=base['main_tier_ids']
  if config['fields']!=fields or len(fields)!=5:raise ValueError('Disputed field was not actually excluded')
  source={int(r['corridor_id']):r for r in read(root/'data/city_standardized_scores_v0.1.csv')};eq={int(r['corridor_id']):float(r['low_income_population_share_500m']) for r in read(root/'data/supplemental_model_inputs_v0.5.csv')}
  mu=statistics.fmean(eq[cid] for cid in ids);sd=statistics.pstdev(eq[cid] for cid in ids)
  cases=[]
  for method,profile in itertools.product(config['city_methods'],config['weight_profiles']):
   keep=[base['fields'].index(f) for f in fields];weights=[base['weight_profiles'][profile][i] for i in keep];total=sum(weights);weights=[v/total for v in weights]
   if len(config['weight_profiles'][profile])!=5:raise ValueError('Five surviving weights required')
   if any(not math.isclose(a,b,abs_tol=1e-14) for a,b in zip(weights,config['weight_profiles'][profile])):raise ValueError('Weight renormalization changed relative preferences')
   matrix=[]
   for cid in ids:
    values=[]
    for f in fields:
     if f==fields[-1]:value=(eq[cid]-mu)/sd
     elif source[cid][f]!='':value=float(source[cid][f])
     else:
      observed=[float(r[f]) for r in source.values() if r[f]!=''];value=min(observed) if method=='imputed_conservative_min' else statistics.fmean(observed)
     values.append(value)
    matrix.append(values)
   scores=[sum(v*w for v,w in zip(values,weights)) for values in matrix];lo,hi=rank_intervals(scores)
   cases.append(dict(method=method,profile=profile,scores=scores,lo=lo,hi=hi,matrix=matrix))
  normalized=read(o/'five_indicator_inputs.csv')
  if len(normalized)!=32 or 'current_ridership' in normalized[0]:raise ValueError('Five-column normalization grid invalid')
  for r in normalized:
   case=next(c for c in cases if c['method']==r['city_method']);j=ids.index(int(r['corridor_id']))
   if any(not math.isclose(float(r[f]),case['matrix'][j][i],abs_tol=1e-12) for i,f in enumerate(fields)):raise ValueError('Normalized source values changed')
  stored=read(o/'paired_scenario_comparison.csv')
  if len(stored)!=96 or len({(r['case_id'],r['corridor_id']) for r in stored})!=96:raise ValueError('Paired score grid incomplete')
  for r in stored:
   case=cases[int(r['case_id'])];j=ids.index(int(r['corridor_id']))
   if not math.isclose(float(r['five_score']),case['scores'][j],abs_tol=1e-10) or int(r['five_rank_worst'])!=case['hi'][j]:raise ValueError('Five-criterion score/rank replay failed')
  draws=read(o/'monte_carlo_draws.csv');old=read(root/'outputs/tiered_v0.6/monte_carlo_draws.csv')
  if len(draws)!=10000 or len(draws)!=len(old):raise ValueError('Missing draws')
  counts=[0]*6
  for i,(r,b) in enumerate(zip(draws,old)):
   if int(r['draw_id'])!=i+1 or r['case_id']!=b['case_id']:raise ValueError('Selectors not paired to baseline')
   k=int(r['case_id']);case=cases[k];counts[k]+=1
   if r['city_method']!=case['method'] or r['weight_profile']!=case['profile']:raise ValueError('Draw selector metadata invalid')
   if any(int(r[f'corridor_{cid}_rank_worst'])!=case['hi'][j] for j,cid in enumerate(ids)):raise ValueError('Draw rank replay failed')
  acceptance=read(o/'rank_acceptability_comparison.csv');byid={int(r['corridor_id']):r for r in acceptance}
  if len(acceptance)!=16 or set(byid)!=set(ids):raise ValueError('Wrong-tier rank acceptance')
  for cid,r in byid.items():
   j=ids.index(cid)
   for k in [1,3,5]:
    rate=sum(counts[i] for i,c in enumerate(cases) if c['hi'][j]<=k)/10000
    if not math.isclose(float(r[f'five_top{k}_frequency']),rate,abs_tol=1e-12):raise ValueError('Acceptance replay failed')
  summary=json.loads((o/'jane_stress_summary.json').read_text());decision=json.loads((root/'data/task1_decision_v0.7.json').read_text())
  trigger=float(byid[12]['five_top5_frequency'])<=.9 and float(byid[23]['five_top5_frequency'])>.9 and float(byid[23]['baseline_top5_frequency'])>.9
  if summary['switch_to_23_triggered']!=trigger or (trigger and (summary['primary_corridor_id']!=23 or decision['primary_corridor_id']!=23)):raise ValueError('Decision does not follow predeclared stress rule')
  if summary['length_issue_resolved'] or summary['source_scores_modified']:raise ValueError('Stress does not correct source lengths or scores')
  audit=json.loads((root/'evidence/jane_audit_v0.7/jane_length_audit.json').read_text())
  if audit['physical_full_length_4_076_confirmed'] or audit['internal_score_denominator_confirmed']:raise ValueError('Audit overstates source evidence')
  manifest=json.loads((o/'run_manifest.json').read_text())
  for section in ['source_files','output_files']:
   for rel,digest in manifest[section].items():
    p=(root/rel).resolve()
    if not p.is_relative_to(root.resolve()) or not p.is_file() or sha(p)!=digest:raise ValueError('Missing or changed stress evidence: '+rel)
 except (ValueError,KeyError,OSError,TypeError,IndexError,ZeroDivisionError) as e:errors.append(str(e))
 return dict(stress_model_ready=not errors,criterion_count=5,excluded_indicator='current_ridership',draw_count=10000,source_scores_modified=False,length_issue_resolved=False,primary_corridor_id=summary.get('primary_corridor_id'),limitations_flagged=True,part1_complete=False,errors=errors)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args();result=validate();payload=json.dumps(result,indent=2);print(payload)
 if args.output:args.output.write_text(payload+'\n')
 raise SystemExit(0 if result['stress_model_ready'] else 1)
