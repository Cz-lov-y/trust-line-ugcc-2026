"""Tier-isolated six-scenario ranking, 10000 seeded draws, and exportable figures."""
import itertools,json,math
import numpy as np
from tiered_common import ROOT,O,read,write,dump,sha,policy,tiers,rank_intervals

def load_model(root=ROOT):
 config=policy(root);master=read(root/'data/corridor_master_v0.1.csv');byid,main,conditional,closure=tiers(master,config)
 source={int(r['corridor_id']):r for r in read(root/'data/city_standardized_scores_v0.1.csv')}
 minimum={int(r['corridor_id']):r for r in read(root/'data/city_analysis_inputs_v0.4.csv')}
 means={int(r['corridor_id']):r for r in read(root/'data/city_mean_sensitivity_v0.4.csv')}
 equity={int(r['corridor_id']):r for r in read(root/'data/supplemental_model_inputs_v0.5.csv')}
 for table in [source,minimum,means,equity]:
  if set(table)!=set(range(1,25)):raise ValueError('Unique complete 24-corridor mapping required')
 # Independently recompute both methods against original City cells.
 for method,table in [('imputed_conservative_min',minimum),('imputed_observed_mean',means)]:
  for f in config['fields'][:5]:
   vals=[float(r[f]) for r in source.values() if r[f]!=''];replacement=min(vals) if method=='imputed_conservative_min' else float(np.mean(vals))
   for cid,r in table.items():
    expected=float(source[cid][f]) if source[cid][f]!='' else replacement
    expected_flag='source_observed' if source[cid][f]!='' else method
    if not math.isclose(float(r[f]),expected,abs_tol=1e-12) or r[f+'_value_status']!=expected_flag:raise ValueError('City scenario differs from source/statistic')
 eq=np.array([float(equity[cid][config['fields'][5]]) for cid in main]);mu=float(eq.mean());sd=float(eq.std(ddof=0))
 if not np.isfinite(eq).all() or sd<=0:raise ValueError('Equity calibration must be finite and nonconstant')
 for weights in config['weight_profiles'].values():
  if len(weights)!=6 or not np.isfinite(weights).all() or min(weights)<0 or not math.isclose(sum(weights),1,abs_tol=1e-12):raise ValueError('Invalid nonnegative normalized weights')
 return config,byid,main,conditional,closure,minimum,means,equity,mu,sd

def case_results(config,main,minimum,means,equity,mu,sd,equity_override=None):
 matrices={}
 for method,table in zip(config['city_methods'],[minimum,means]):
  matrices[method]=np.array([[*[float(table[cid][f]) for f in config['fields'][:5]],((equity_override or {}).get(cid,float(equity[cid][config['fields'][5]]))-mu)/sd] for cid in main])
  if not np.isfinite(matrices[method]).all():raise ValueError('Nonfinite main-tier matrix')
 cases=[]
 for method,profile in itertools.product(config['city_methods'],config['weight_profiles']):
  scores=matrices[method]@np.asarray(config['weight_profiles'][profile]);low,high=rank_intervals(scores.tolist())
  cases.append(dict(case_id=len(cases),city_method=method,weight_profile=profile,scores=scores,rank_low=np.asarray(low),rank_high=np.asarray(high)))
 return cases,matrices

def scenario_draws(config):
 rng=np.random.Generator(np.random.PCG64(config['seed']));n=config['draws']
 mi=rng.integers(0,len(config['city_methods']),size=n);wi=rng.integers(0,len(config['weight_profiles']),size=n)
 return mi*len(config['weight_profiles'])+wi

def run():
 O.mkdir(parents=True,exist_ok=True)
 config,master,main,conditional,closure,minimum,means,equity,mu,sd=load_model()
 tierrows=[dict(corridor_id=cid,corridor_name=master[cid]['corridor_name'],tier='main_common_baseline' if cid in main else 'conditional_extension_reserve',baseline_scenario_id=master[cid]['baseline_scenario_id'],main_rank_eligible=cid in main,prerequisite_closure=';'.join(map(str,closure[cid])),dependency_sequence=' -> '.join(map(str,[*closure[cid],cid])),pooled_absolute_rank='not_computed') for cid in range(1,25)]
 write(ROOT/'data/corridor_tiers_v0.6.csv',tierrows)
 cases,matrices=case_results(config,main,minimum,means,equity,mu,sd)
 normrows=[]
 for method,matrix in matrices.items():
  for cid,values in zip(main,matrix):normrows.append(dict(corridor_id=cid,city_method=method,**dict(zip(config['fields'],values)),equity_zscore_reference_mean=mu,equity_zscore_reference_population_SD=sd,reference_tier='16_CITY_BASE_0_corridors'))
 write(O/'normalized_main_tier_inputs.csv',normrows)
 scores=[]
 for case in cases:
  for i,cid in enumerate(main):scores.append(dict(case_id=case['case_id'],city_method=case['city_method'],weight_profile=case['weight_profile'],corridor_id=cid,score=case['scores'][i],rank_best=int(case['rank_low'][i]),rank_worst=int(case['rank_high'][i]),top5_guaranteed=case['rank_high'][i]<=5))
 write(O/'six_scenario_scores.csv',scores)
 selectors=scenario_draws(config)
 weights=np.bincount(selectors,minlength=len(cases))/config['draws']
 exactweights=np.ones(len(cases))/len(cases)
 lows=np.stack([c['rank_low'] for c in cases]);highs=np.stack([c['rank_high'] for c in cases]);mids=(lows+highs)/2
 summary=[]
 for i,cid in enumerate(main):
  top5=float(np.mean(highs[selectors,i]<=5));exact5=float(np.mean(highs[:,i]<=5))
  summary.append(dict(corridor_id=cid,corridor_name=master[cid]['corridor_name'],top1_frequency=float(np.mean(highs[selectors,i]<=1)),top3_frequency=float(np.mean(highs[selectors,i]<=3)),exact_top3_frequency=float(np.mean(highs[:,i]<=3)),exact_mean_midpoint_rank=float(np.mean(mids[:,i])),top5_frequency=top5,top10_frequency=float(np.mean(highs[selectors,i]<=10)),exact_top5_frequency=exact5,exact_top10_frequency=float(np.mean(highs[:,i]<=10)),mean_midpoint_rank=float(weights@mids[:,i]),best_rank=int(lows[:,i].min()),worst_rank=int(highs[:,i].max()),high_confidence_candidate=top5>config['high_confidence_top5_threshold'] and exact5>config['high_confidence_top5_threshold'],interpretation='Declared scenario frequency, not a statistical confidence level'))
 ordered=sorted(summary,key=lambda r:(-r['exact_top5_frequency'],-r['exact_top3_frequency'],r['exact_mean_midpoint_rank'],r['worst_rank'],r['corridor_id']))
 shortlist=[r['corridor_id'] for r in ordered[:3]]
 for r in summary:r['main_shortlist']=r['corridor_id'] in shortlist
 write(O/'rank_acceptability.csv',ordered)
 drawrows=[]
 for i,selector in enumerate(selectors):
  case=cases[selector];drawrows.append(dict(draw_id=i+1,case_id=int(selector),city_method=case['city_method'],weight_profile=case['weight_profile'],**{f'corridor_{cid}_rank_worst':int(highs[selector,j]) for j,cid in enumerate(main)}))
 write(O/'monte_carlo_draws.csv',drawrows)
 casefreq=[dict(case_id=c['case_id'],city_method=c['city_method'],weight_profile=c['weight_profile'],draw_count=int((selectors==c['case_id']).sum()),simulated_frequency=weights[c['case_id']],exact_frequency=1/len(cases)) for c in cases]
 write(O/'scenario_sampling_frequency.csv',casefreq)
 # Endpoint stress: shared Woodbine perturbation changes only affected corridor inputs,
 # using the frozen nominal main-tier equity calibration (not a moving normalization).
 endpoint=read(O/'woodbine_anchor_sensitivity.csv');anchorcases=sorted({r['anchor_case'] for r in endpoint})
 stress=[];shortlist_sets=[]
 for anchor in anchorcases:
  overrides={int(r['corridor_id']):float(r['low_income_population_share_500m']) for r in endpoint if r['anchor_case']==anchor}
  alternative,_=case_results(config,main,minimum,means,equity,mu,sd,overrides)
  high=np.stack([c['rank_high'] for c in alternative]);low=np.stack([c['rank_low'] for c in alternative]);ranking=[]
  for j,cid in enumerate(main):
   item=dict(anchor_case=anchor,corridor_id=cid,exact_top5_frequency=float(np.mean(high[:,j]<=5)),exact_top3_frequency=float(np.mean(high[:,j]<=3)),mean_midpoint_rank=float(np.mean((high[:,j]+low[:,j])/2)),best_rank=int(low[:,j].min()),worst_rank=int(high[:,j].max()))
   stress.append(item);ranking.append(item)
  ranking.sort(key=lambda r:(-r['exact_top5_frequency'],-r['exact_top3_frequency'],r['mean_midpoint_rank'],r['worst_rank'],r['corridor_id']))
  shortlist_sets.append(set(r['corridor_id'] for r in ranking[:3]))
 write(O/'woodbine_rank_sensitivity.csv',stress)
 # Additional deterministic CT mean and all-24 calibration checks, outside the MC support.
 checks=[]
 alleq=np.array([float(equity[cid][config['fields'][5]]) for cid in range(1,25)])
 for name,mm,ss,override in [('CT_mean',mu,sd,{cid:float(equity[cid]['mean_sensitivity_share']) for cid in main}),('equity_zscore_reference_24',float(alleq.mean()),float(alleq.std(ddof=0)),None)]:
  alternative,_=case_results(config,main,minimum,means,equity,mm,ss,override)
  for j,cid in enumerate(main):checks.append(dict(check=name,corridor_id=cid,exact_top5_frequency=float(np.mean([c['rank_high'][j]<=5 for c in alternative])),best_rank=min(int(c['rank_low'][j]) for c in alternative),worst_rank=max(int(c['rank_high'][j]) for c in alternative)))
 write(O/'supplementary_sensitivity.csv',checks)
 highconfidence=[r['corridor_id'] for r in ordered if r['high_confidence_candidate']]
 result=dict(version='v0.6',seed=config['seed'],draws=config['draws'],distinct_base_scenarios=len(cases),main_tier_corridor_ids=main,conditional_tier_corridor_ids=conditional,main_shortlist=shortlist,high_confidence_top5_candidates=highconfidence,threshold_strictly_greater_than=0.9,exact_enumeration_agrees_with_simulation_candidate_set=highconfidence==[r['corridor_id'] for r in ordered if r['exact_top5_frequency']>0.9],equity_calibration=dict(reference_ids=main,mean=mu,population_SD=sd),woodbine_shortlist_set_unchanged=all(s==set(shortlist) for s in shortlist_sets),high_confidence_claim='Above 90% top-five inclusion under six declared discrete scenarios; not population confidence or comprehensive uncertainty',single_corridor_final_recommendation=None,model_scope=config['readiness_scope'],limitations=config['limitations'])
 dump(O/'tiered_model_summary.json',result)
 sourcepaths=[ROOT/'data/tiered_model_policy_v0.6.json',ROOT/'data/corridor_master_v0.1.csv',ROOT/'data/city_standardized_scores_v0.1.csv',ROOT/'data/city_analysis_inputs_v0.4.csv',ROOT/'data/city_mean_sensitivity_v0.4.csv',ROOT/'data/supplemental_model_inputs_v0.5.csv',O/'woodbine_anchor_sensitivity.csv']
 dump(O/'model_input_manifest.json',{str(p.relative_to(ROOT)):sha(p) for p in sourcepaths})
 plot(cases,main,ordered,shortlist,config)
 print(json.dumps(result,indent=2));return result

def plot(cases,main,summary,shortlist,config):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.ticker import PercentFormatter
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'})
 colors=plt.get_cmap('tab20');color={cid:colors(i%20) for i,cid in enumerate(main)}
 color.update({12:'#146c78',23:'#d49324',20:'#7952a1',9:'#cd5847',22:'#54687a',21:'#bd83a7'})
 # Main bump chart: frequent top-five lines. Supplement shows frequent top-ten lines.
 for k in [5,10]:
  chosen=[r for r in summary if r[f'top{k}_frequency']>=config['frequent_line_threshold']]
  order=[0,3,1,4,2,5];labels=['Minimum\nEqual','Mean\nEqual','Minimum\nRidership','Mean\nRidership','Minimum\nEquity','Mean\nEquity']
  fig,ax=plt.subplots(figsize=(12,7))
  for r in chosen:
   cid=r['corridor_id'];j=main.index(cid);y=[(cases[i]['rank_low'][j]+cases[i]['rank_high'][j])/2 for i in order]
   ax.plot(range(6),y,marker='o',lw=2.8 if cid in shortlist else 1.5,color=color[cid],alpha=1 if cid in shortlist else .65,label=f'{cid}: {r["corridor_name"]}')
  ax.set_xticks(range(6),labels);ax.set_ylim(16.6,.4);ax.set_yticks(range(1,17));ax.grid(axis='y',alpha=.18);ax.set_ylabel('Rank among 16 common-baseline corridors (1 = best)')
  ax.set_title(f'Robust Frontier diagnostic | frequent top-{k} corridors',loc='left',fontweight='bold',fontsize=15)
  ax.legend(loc='upper left',bbox_to_anchor=(1.01,1),frameon=False,fontsize=9)
  fig.text(.08,.025,'Six discrete scenarios; lines shown when top-'+str(k)+' frequency ≥ 50%. Conditional extensions are assessed separately.\n10,000 seeded draws resample these scenarios; inclusion rates are assumption-dependent, not statistical confidence.',fontsize=9,color='#465766')
  fig.subplots_adjust(right=.71,bottom=.17,top=.90)
  for ext in ['png','svg','pdf']:fig.savefig(O/f'bump_top{k}.{ext}',dpi=220)
  plt.close(fig)
 fig,ax=plt.subplots(figsize=(11,7));ranked=summary[::-1]
 y=np.arange(len(ranked));rates=[r['top5_frequency'] for r in ranked]
 ax.barh(y,rates,color=['#146c78' if r['high_confidence_candidate'] else '#a4b4be' for r in ranked]);ax.axvline(.9,color='#b85038',ls='--',lw=1.4,label='90% threshold')
 ax.set_yticks(y,[str(r['corridor_id'])+': '+r['corridor_name'] for r in ranked]);ax.set_xlim(0,1.13);ax.xaxis.set_major_formatter(PercentFormatter(1))
 for i,r in enumerate(ranked):ax.text(r['top5_frequency']+.015,i,f'{100*r["top5_frequency"]:.1f}%',va='center',fontsize=9)
 ax.set_title('Top-five rank acceptability | 16 common-baseline corridors',loc='left',fontweight='bold');ax.set_xlabel('Share of 10,000 draws from six declared scenarios');ax.legend(frameon=False,loc='lower right');ax.grid(axis='x',alpha=.15)
 fig.text(.32,.015,'Conditional on declared weights, missing-data policies and provisional road buffers.',fontsize=8,color='#465766');fig.tight_layout(rect=[0,.03,1,1])
 for ext in ['png','svg','pdf']:fig.savefig(O/f'top5_acceptability.{ext}',dpi=220)
 plt.close(fig)
if __name__=='__main__':run()
