"""Paired five-criterion rerun that physically excludes the disputed input column."""
from pathlib import Path
import json,math,itertools
import numpy as np
from tiered_common import ROOT,read,write,dump,sha,rank_intervals
from run_tiered_model_v0_6 import load_model,case_results,scenario_draws
O=ROOT/'outputs/jane_stress_v0.7'

def five_cases(config,baseline_config,matrices):
 keep=[baseline_config['fields'].index(f) for f in config['fields']]
 if len(keep)!=5 or 'current_ridership' in config['fields']:raise ValueError('The excluded field must not enter the five-column matrix')
 result=[];five_matrices={method:matrix[:,keep] for method,matrix in matrices.items()}
 for method,profile in itertools.product(config['city_methods'],config['weight_profiles']):
  weights=np.asarray(config['weight_profiles'][profile]);expected=np.asarray(baseline_config['weight_profiles'][profile])[keep];expected=expected/expected.sum()
  if len(weights)!=5 or not np.allclose(weights,expected,atol=1e-14,rtol=0):raise ValueError('Surviving weights must be proportionally renormalized')
  scores=five_matrices[method]@weights;low,high=rank_intervals(scores.tolist())
  result.append(dict(case_id=len(result),city_method=method,weight_profile=profile,scores=scores,rank_low=np.asarray(low),rank_high=np.asarray(high)))
 return result,five_matrices

def run():
 O.mkdir(parents=True,exist_ok=True);config=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text())
 base,master,ids,conditional,closure,minimum,means,equity,mu,sd=load_model()
 baseline,matrices=case_results(base,ids,minimum,means,equity,mu,sd);stress,five=five_cases(config,base,matrices)
 selectors=scenario_draws(base)
 old_draws=read(ROOT/'outputs/tiered_v0.6/monte_carlo_draws.csv')
 if selectors.tolist()!=[int(r['case_id']) for r in old_draws]:raise ValueError('Paired selectors do not match baseline')
 norm=[]
 for method,matrix in five.items():
  for cid,row in zip(ids,matrix):norm.append(dict(corridor_id=cid,city_method=method,**dict(zip(config['fields'],row))))
 write(O/'five_indicator_inputs.csv',norm)
 rows=[];components=[]
 omitted=base['fields'].index('current_ridership')
 for old,new in zip(baseline,stress):
  weights=base['weight_profiles'][old['weight_profile']];w=weights[omitted]
  for i,cid in enumerate(ids):
   contribution=w*matrices[old['city_method']][i,omitted]
   identity=(old['scores'][i]-contribution)/(1-w)
   if not math.isclose(float(new['scores'][i]),float(identity),abs_tol=1e-12):raise ValueError('Removal identity failed')
   rows.append(dict(case_id=new['case_id'],city_method=new['city_method'],weight_profile=new['weight_profile'],corridor_id=cid,corridor_name=master[cid]['corridor_name'],baseline_score=old['scores'][i],baseline_rank_best=int(old['rank_low'][i]),baseline_rank_worst=int(old['rank_high'][i]),five_score=new['scores'][i],five_rank_best=int(new['rank_low'][i]),five_rank_worst=int(new['rank_high'][i]),rank_change_worst=int(new['rank_high'][i]-old['rank_high'][i]),five_top3=new['rank_high'][i]<=3,five_top5=new['rank_high'][i]<=5))
   if cid in [12,23]:
    for field,coefficient,value in zip(base['fields'],weights,matrices[old['city_method']][i]):components.append(dict(case_id=old['case_id'],corridor_id=cid,city_method=old['city_method'],weight_profile=old['weight_profile'],field=field,original_standardized_value=value,baseline_weight=coefficient,baseline_weighted_addend=coefficient*value,excluded_in_five_model=field=='current_ridership',five_weight=0 if field=='current_ridership' else coefficient/(1-w)))
 write(O/'paired_scenario_comparison.csv',rows);write(O/'jane_finch_score_components.csv',components)
 oldhigh=np.stack([c['rank_high'] for c in baseline]);high=np.stack([c['rank_high'] for c in stress]);low=np.stack([c['rank_low'] for c in stress]);mid=(high+low)/2
 acceptance=[]
 for i,cid in enumerate(ids):
  record=dict(corridor_id=cid,corridor_name=master[cid]['corridor_name'],baseline_top1_frequency=float(np.mean(oldhigh[selectors,i]<=1)),baseline_top3_frequency=float(np.mean(oldhigh[selectors,i]<=3)),baseline_top5_frequency=float(np.mean(oldhigh[selectors,i]<=5)),five_top1_frequency=float(np.mean(high[selectors,i]<=1)),five_top3_frequency=float(np.mean(high[selectors,i]<=3)),five_top5_frequency=float(np.mean(high[selectors,i]<=5)),five_exact_top1_frequency=float(np.mean(high[:,i]<=1)),five_exact_top3_frequency=float(np.mean(high[:,i]<=3)),five_exact_top5_frequency=float(np.mean(high[:,i]<=5)),five_exact_mean_rank=float(np.mean(mid[:,i])),five_best_rank=int(low[:,i].min()),five_worst_rank=int(high[:,i].max()),baseline_best_rank=int(oldhigh[:,i].min()),baseline_worst_rank=int(oldhigh[:,i].max()),max_rank_drop=int(np.max(high[:,i]-oldhigh[:,i])))
  record['stable_top5_in_both_models']=record['baseline_top5_frequency']>.9 and record['five_top5_frequency']>.9 and record['five_exact_top5_frequency']>.9
  acceptance.append(record)
 acceptance.sort(key=lambda r:(-r['five_exact_top5_frequency'],-r['five_exact_top3_frequency'],r['five_exact_mean_rank'],r['five_worst_rank'],r['corridor_id']))
 write(O/'rank_acceptability_comparison.csv',acceptance)
 drawrows=[dict(draw_id=i+1,case_id=int(k),city_method=stress[k]['city_method'],weight_profile=stress[k]['weight_profile'],**{f'corridor_{cid}_rank_worst':int(high[k,j]) for j,cid in enumerate(ids)}) for i,k in enumerate(selectors)]
 write(O/'monte_carlo_draws.csv',drawrows)
 write(O/'renormalized_weights.csv',[dict(profile=name,**dict(zip(config['fields'],weights)),excluded_indicator='current_ridership') for name,weights in config['weight_profiles'].items()])
 byid={r['corridor_id']:r for r in acceptance};jane=byid[12];finch=byid[23]
 trigger=jane['five_top5_frequency']<=.9 and finch['stable_top5_in_both_models']
 primary=23 if trigger else (12 if jane['stable_top5_in_both_models'] else None)
 summary=dict(version='v0.7',comparison='six-criterion baseline versus five-criterion current_ridership exclusion',draws=10000,seed=base['seed'],distinct_scenarios=6,paired_selectors_identical=True,active_stress_fields=config['fields'],equity_calibration_frozen=dict(mean=mu,population_SD=sd,reference_ids=ids),jane_12=jane,finch_23=finch,stable_top5_in_both_models=[r['corridor_id'] for r in acceptance if r['stable_top5_in_both_models']],five_model_shortlist=[r['corridor_id'] for r in acceptance[:3]],switch_to_23_triggered=trigger,primary_corridor_id=primary,source_scores_modified=False,length_issue_resolved=False,conclusion='Corridor 12 loses its all-scenario top-five status and falls to ranks 8–9 under the remaining-demand profile; corridor 23 stays at ranks 1–2. Apply the user-authorized switch to corridor 23 as provisional Task 1 primary.' if trigger else 'Inspect the documented decision rule before selecting a primary.',interpretation='Sensitivity to excluding one disputed input, not proof of a corrected length, raw-score error, statistical confidence, or complete robustness. No transfer-connectivity indicator is included.')
 dump(O/'jane_stress_summary.json',summary)
 selection=dict(version='v0.7',role='Active five-criterion Task 1 stress model and decision basis; six-criterion v0.6 preserved as paired baseline',selected_indicator_ids=config['fields'],excluded_indicator_ids=['current_ridership'],policy_file='data/jane_stress_policy_v0.7.json',normalized_inputs_file='outputs/jane_stress_v0.7/five_indicator_inputs.csv',baseline_selection_file='data/model_input_selection_v0.1.json',baseline_policy_file='data/tiered_model_policy_v0.6.json',main_tier_ids=ids,conditional_tier_ids=conditional,source_scores_modified=False)
 dump(ROOT/'data/model_input_selection_v0.7.json',selection)
 decision=dict(version='v0.7',primary_corridor_id=primary,primary_corridor_name=master[primary]['corridor_name'] if primary else None,primary_endpoints=[master[primary]['endpoint_a'],master[primary]['endpoint_b']] if primary else None,decision_status='provisional_primary_after_predeclared_indicator_exclusion',previous_top_ranked_corridor=12,reason=summary['conclusion'],evidence_file='outputs/jane_stress_v0.7/jane_stress_summary.json',active_model_selection='data/model_input_selection_v0.7.json',costs_used_in_Part1=False,part1_complete=False,length_issue_resolved=False,remaining_work=['Resolve or clearly retain the official Jane length ambiguity','Complete correlation/redundancy, weight rationale and coverage of three guiding principles','Finalize single-corridor argument and Task 1 deliverables','Confirm competition AI policy applicability and disclosure; Part 2 not yet completed'])
 dump(ROOT/'data/task1_decision_v0.7.json',decision)
 plot(rows,acceptance)
 print(json.dumps(summary,indent=2));return summary

def plot(rows,acceptance):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','font.size':10})
 order=[0,3,1,4,2,5];labels=['Minimum\nEqual','Mean\nEqual','Minimum\nDemand','Mean\nDemand','Minimum\nEquity','Mean\nEquity']
 fig,axes=plt.subplots(1,2,figsize=(12,5.5),sharey=True)
 for ax,cid in zip(axes,[12,23]):
  lookup={int(r['case_id']):r for r in rows if int(r['corridor_id'])==cid}
  ax.plot(range(6),[lookup[k]['baseline_rank_worst'] for k in order],color='#8395a4',marker='o',ls='--',label='Six criteria: baseline')
  ax.plot(range(6),[lookup[k]['five_rank_worst'] for k in order],color='#b45737' if cid==12 else '#146c78',marker='o',lw=2.6,label='Five criteria: ridership removed')
  ax.axhspan(.5,5.5,color='#d9eceb',alpha=.45);ax.set_xticks(range(6),labels,fontsize=8);ax.set_ylim(16.5,.5);ax.set_yticks(range(1,17));ax.grid(axis='y',alpha=.18);ax.set_title(f'{cid}: '+('Jane St' if cid==12 else 'Finch Ave E'),loc='left',fontweight='bold');ax.legend(fontsize=8,loc='lower left')
 axes[0].set_ylabel('Rank among 16 common-baseline corridors');fig.suptitle('Length-scaled ridership exclusion: paired stress test',fontweight='bold',x=.07,ha='left')
 fig.text(.07,.025,'Same seed, selectors and equity calibration; surviving weights proportionally renormalized.\nShading: top five. Six exact cases resampled 10,000 times; not statistical confidence.',fontsize=9,color='#465766');fig.tight_layout(rect=[0,.10,1,.95])
 for ext in ['png','svg','pdf']:
  target=O/f'jane_finch_rank_stress.{ext}';fig.savefig(target,dpi=220)
  if ext=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,4.8));byid={r['corridor_id']:r for r in acceptance};x=np.arange(2)
 ax.bar(x-.17,[100*byid[i]['baseline_top5_frequency'] for i in [12,23]],width=.34,color='#8395a4',label='Six criteria')
 vals=[100*byid[i]['five_top5_frequency'] for i in [12,23]];ax.bar(x+.17,vals,width=.34,color=['#b45737','#146c78'],label='Five criteria')
 for i,v in enumerate(vals):ax.text(i+.17,v+1,f'{v:.2f}%',ha='center')
 ax.set_xticks(x,['12: Jane St','23: Finch Ave E']);ax.set_ylim(0,112);ax.set_ylabel('Top-five inclusion in paired draws (%)');ax.axhline(90,color='#bd7b22',ls='--',lw=1);ax.set_title('Removing the disputed indicator changes the primary choice',loc='left',fontweight='bold');ax.legend(frameon=False,loc='lower right');fig.text(.12,.02,'Assumption-dependent scenario frequency, not population confidence. Jane length remains unresolved.',fontsize=9);fig.tight_layout(rect=[0,.06,1,1])
 for ext in ['png','svg','pdf']:
  target=O/f'top5_before_after.{ext}';fig.savefig(target,dpi=220)
  if ext=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
 plt.close(fig)
if __name__=='__main__':run()
