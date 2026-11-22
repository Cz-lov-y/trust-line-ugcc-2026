"""Descriptive correlations, transparent block budgets and unfitted weight stresses."""
import itertools,json,math
from pathlib import Path
import numpy as np
from tiered_common import ROOT,read,write,dump,sha,rank_intervals
from run_tiered_model_v0_6 import load_model,case_results
from run_jane_stress_v0_7 import five_cases
O=ROOT/'outputs/model_argument_v0.8'

def average_ranks(values):
 a=np.asarray(values,dtype=float);order=np.argsort(a,kind='stable');out=np.empty(len(a));start=0
 while start<len(a):
  end=start+1
  while end<len(a) and a[order[end]]==a[order[start]]:end+=1
  out[order[start:end]]=(start+1+end)/2;start=end
 return out

def correlation(x,y,method):
 x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
 if len(x)<3 or x.std()==0 or y.std()==0:return None
 if method=='Spearman_average_ties':x,y=average_ranks(x),average_ranks(y)
 return float(np.corrcoef(x,y)[0,1])

def block_feature_weights(config,fields,block_weights,deleted=None):
 weights=np.zeros(len(fields))
 for name,budget in zip(config['blocks'],block_weights):
  members=[f for f in config['blocks'][name] if f!=deleted]
  if not members:raise ValueError('Cannot delete the sole member of a retained block')
  for f in members:weights[fields.index(f)]=budget/len(members)
 if not np.isclose(weights.sum(),1):raise ValueError('Invalid block budget')
 return weights

def worst_ranks(score_matrix):
 s=np.asarray(score_matrix);return (s[:,None,:]>=s[:,:,None]-1e-12).sum(axis=2)

def run():
 O.mkdir(parents=True,exist_ok=True);config=json.loads((ROOT/'data/model_argument_policy_v0.8.json').read_text());active=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text());fields=active['fields']
 base,master,ids,conditional,closure,minimum,means,equity,mu,sd=load_model();_,six=case_results(base,ids,minimum,means,equity,mu,sd);_,matrices=five_cases(active,base,six)
 source={int(r['corridor_id']):r for r in read(ROOT/'data/city_standardized_scores_v0.1.csv')}
 observed={}
 for cid in ids:
  observed[cid]={}
  for f in fields:
   if f==fields[-1]:observed[cid][f]=float(equity[cid][f]) if equity[cid]['value_status']!='suppressed_CT_imputed' else None
   else:observed[cid][f]=float(source[cid][f]) if source[cid][f]!='' else None
 complete=[cid for cid in ids if all(observed[cid][f] is not None for f in fields)]
 correlations=[];descriptive=[]
 def process(label,lookup,joint=False):
  for f in fields:
   vals=[lookup[cid][f] for cid in ids if lookup[cid][f] is not None and (not joint or cid in complete)]
   descriptive.append(dict(population=label,field=f,n=len(vals),mean=float(np.mean(vals)),population_SD=float(np.std(vals)),minimum=min(vals),q25=float(np.quantile(vals,.25)),median=float(np.median(vals)),q75=float(np.quantile(vals,.75)),maximum=max(vals),unit='raw equity fraction' if label.startswith(('pairwise','joint')) and f==fields[-1] else 'dimensionless model/source score'))
  for f,g in itertools.combinations(fields,2):
   eligible=[cid for cid in ids if lookup[cid][f] is not None and lookup[cid][g] is not None and (not joint or cid in complete)]
   for method in config['correlation_methods']:
    value=correlation([lookup[c][f] for c in eligible],[lookup[c][g] for c in eligible],method)
    correlations.append(dict(population=label,method=method,field_x=f,field_y=g,n=len(eligible),corr=value if value is not None else '',absolute_screen_flag=value is not None and abs(value)>=config['high_correlation_screen'],corridor_ids=';'.join(map(str,eligible)),interpretation='Descriptive candidate relationship; no independence, causality or significance claim'))
 process('pairwise_source_available_main_tier',observed)
 process('joint_complete_source_main_tier',observed,True)
 for name,matrix in matrices.items():process('minimum_substituted_main_tier' if 'conservative' in name else 'mean_substituted_main_tier',{cid:dict(zip(fields,row)) for cid,row in zip(ids,matrix)})
 write(O/'indicator_correlations.csv',correlations);write(O/'descriptive_statistics.csv',descriptive)
 write(O/'source_missingness_main_tier.csv',[dict(corridor_id=cid,**{f+'_source_available':observed[cid][f] is not None for f in fields},joint_complete=cid in complete) for cid in ids])
 budgets=[]
 for name,w in active['weight_profiles'].items():budgets.append(dict(profile='nominal_'+name,**{block:sum(w[fields.index(f)] for f in members) for block,members in config['blocks'].items()},**dict(zip(fields,w)),basis='Declared v0.7 criterion weights, not stakeholder elicitation'))
 deterministic=[]
 for method,matrix in matrices.items():
  for name,bw in config['block_weight_profiles'].items():
   weights=block_feature_weights(config,fields,bw);scores=matrix@weights;lo,hi=rank_intervals(scores.tolist())
   if method==list(matrices)[0]:budgets.append(dict(profile=name,**dict(zip(config['blocks'],bw)),**dict(zip(fields,weights)),basis='Illustrative fixed concept budgets; equal split inside blocks'))
   for i,cid in enumerate(ids):deterministic.append(dict(stress='concept_block_profiles',case=name,city_method=method,corridor_id=cid,score=scores[i],rank_best=lo[i],rank_worst=hi[i],deleted_indicator=''))
  for deleted in config['duplicate_indicator_deletions']:
   w=block_feature_weights(config,fields,config['block_weight_profiles']['block_equal'],deleted);scores=matrix@w;lo,hi=rank_intervals(scores.tolist())
   for i,cid in enumerate(ids):deterministic.append(dict(stress='fixed_block_member_deletion',case='delete_'+deleted,city_method=method,corridor_id=cid,score=scores[i],rank_best=lo[i],rank_worst=hi[i],deleted_indicator=deleted))
  for deleted in fields:
   keep=[j for j,f in enumerate(fields) if f!=deleted]
   for name,original in active['weight_profiles'].items():
    w=np.asarray(original)[keep];w=w/w.sum();scores=matrix[:,keep]@w;lo,hi=rank_intervals(scores.tolist())
    for i,cid in enumerate(ids):deterministic.append(dict(stress='all_indicator_leave_one_out',case=name+'__delete_'+deleted,city_method=method,corridor_id=cid,score=scores[i],rank_best=lo[i],rank_worst=hi[i],deleted_indicator=deleted))
 write(O/'concept_weight_budgets.csv',budgets);write(O/'redundancy_and_ablation_scores.csv',deterministic)
 # Broader preference sensitivity is a separate, predeclared prior; it does not replace nominal weights.
 rng=np.random.Generator(np.random.PCG64(config['continuous_seed']));n=config['continuous_group_weight_draws'];methods=rng.integers(0,2,n);bw=rng.dirichlet(np.ones(3),n)
 group_indices=[[fields.index(f) for f in members] for members in config['blocks'].values()]
 group_scores=np.stack([np.column_stack([m[:,ix].mean(axis=1) for ix in group_indices]) for m in matrices.values()])
 scores=np.einsum('nk,njk->nj',bw,group_scores[methods]);ranks=worst_ranks(scores)
 region=config['balanced_region'];balanced=(bw.min(axis=1)>=region['minimum_each_block'])&(bw.max(axis=1)<=region['maximum_each_block'])
 drawrows=[]
 for j in range(n):drawrows.append(dict(draw_id=j+1,city_method=list(matrices)[methods[j]],**dict(zip(config['blocks'],bw[j])),inside_illustrative_balanced_region=bool(balanced[j]),**{f'corridor_{cid}_rank_worst':int(ranks[j,i]) for i,cid in enumerate(ids)}))
 write(O/'continuous_block_weight_draws.csv',drawrows)
 preference=[]
 for name,mask in [('full_Dirichlet_simplex',np.ones(n,dtype=bool)),('illustrative_balanced_region',balanced)]:
  if not mask.any():raise ValueError('No draws in declared weight region')
  for i,cid in enumerate(ids):preference.append(dict(weight_region=name,corridor_id=cid,draws=int(mask.sum()),top1_frequency=float(np.mean(ranks[mask,i]<=1)),top3_frequency=float(np.mean(ranks[mask,i]<=3)),top5_frequency=float(np.mean(ranks[mask,i]<=5)),best_rank=int(ranks[mask,i].min()),worst_rank=int(ranks[mask,i].max()),interpretation='Prior-dependent preference sensitivity, not statistical confidence'))
 write(O/'continuous_rank_acceptability.csv',preference)
 grid=[]
 for method,m in zip(matrices,group_scores):
  for a in range(21):
   for b in range(21-a):
    w=np.array([a,b,20-a-b])/20;s=m@w;lo,hi=rank_intervals(s.tolist());i=ids.index(23)
    grid.append(dict(city_method=method,**dict(zip(config['blocks'],w)),corridor_23_rank_best=lo[i],corridor_23_rank_worst=hi[i],best_corridor_ids=';'.join(str(ids[j]) for j,r in enumerate(lo) if r==1)))
 write(O/'preference_simplex_grid.csv',grid)
 summaries=[]
 for category in ['concept_block_profiles','fixed_block_member_deletion','all_indicator_leave_one_out']:
  for cid in ids:
   subset=[x for x in deterministic if x['stress']==category and x['corridor_id']==cid]
   summaries.append(dict(stress=category,corridor_id=cid,distinct_cases=len(subset),top1_fraction=sum(x['rank_worst']<=1 for x in subset)/len(subset),top3_fraction=sum(x['rank_worst']<=3 for x in subset)/len(subset),top5_fraction=sum(x['rank_worst']<=5 for x in subset)/len(subset),best_rank=min(x['rank_best'] for x in subset),worst_rank=max(x['rank_worst'] for x in subset)))
 write(O/'redundancy_stress_summary.csv',summaries)
 flagged=[x for x in correlations if x['absolute_screen_flag']]
 counter=max(grid,key=lambda x:x['corridor_23_rank_worst'])
 result=dict(version='v0.8',fields=fields,main_tier_ids=ids,joint_complete_source_ids=complete,correlation_screen=.7,flagged_correlations=flagged,conceptual_blocks=config['blocks'],corridor_23_deterministic=[x for x in summaries if x['corridor_id']==23],corridor_23_continuous=[x for x in preference if x['corridor_id']==23],continuous_seed=config['continuous_seed'],broad_weight_draws=n,balanced_region_draws=int(balanced.sum()),grid_counterexample=counter,absolute_immunity_supported=False,nominal_primary_changed=False,nominal_primary_corridor_id=23,three_principles_fully_measured=False,limitations=['Five scored measures do not directly measure all three RTEF principles','Non-random missingness and uniform spatial allocation affect observed associations','Illustrative profiles and priors are not elicited social values','All-24 unconditional optimality is not identified by mixed-baseline inputs'])
 dump(O/'argument_analysis_summary.json',result)
 plot(correlations,preference)
 print(json.dumps(result,indent=2));return result

def plot(correlations,preference):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 labels=['Speed\nscore','Projected\nload','Current\nmax load','Choice\nscore','Equity\nproxy'];fields=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text())['fields']
 populations=['pairwise_source_available_main_tier','joint_complete_source_main_tier','minimum_substituted_main_tier','mean_substituted_main_tier'];titles=['Source-available pairs','Joint source-complete cases','Minimum substitutions','Mean substitutions']
 for method,tag in [('Pearson','pearson'),('Spearman_average_ties','spearman')]:
  fig,axes=plt.subplots(2,2,figsize=(11,10))
  for ax,pop,title in zip(axes.flat,populations,titles):
   matrix=np.eye(5);n=np.zeros((5,5),dtype=int)
   rows=[r for r in correlations if r['population']==pop and r['method']==method]
   for r in rows:
    i,j=fields.index(r['field_x']),fields.index(r['field_y']);matrix[i,j]=matrix[j,i]=float(r['corr']);n[i,j]=n[j,i]=r['n']
   image=ax.imshow(matrix,vmin=-1,vmax=1,cmap='RdBu_r')
   for i in range(5):
    for j in range(5):ax.text(j,i,'1.00' if i==j else f'{matrix[i,j]:.2f}\nn={n[i,j]}',ha='center',va='center',fontsize=9,color='white' if abs(matrix[i,j])>.65 else '#203d55')
   ax.set_xticks(range(5),labels,fontsize=8);ax.set_yticks(range(5),labels,fontsize=8);ax.set_title(title,fontweight='bold')
  fig.subplots_adjust(left=.10,right=.88,bottom=.10,top=.90,wspace=.35,hspace=.37);bar=fig.add_axes([.91,.2,.02,.6]);fig.colorbar(image,cax=bar);fig.suptitle(f'{method.split("_")[0]} relationships | five active indicators',fontsize=16,fontweight='bold');fig.text(.1,.025,'Source-available equity omits suppressed-CT imputations for correlation only. All 16 candidates remain ranked.\nDescriptive relationships; no causal, significance or missing-at-random claim.',fontsize=9)
  save(fig,'correlation_'+tag);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(12,6),sharex=True)
 for ax,region,title in zip(axes,['full_Dirichlet_simplex','illustrative_balanced_region'],['Broad group-weight simplex','Illustrative balanced region']):
  rows=sorted([r for r in preference if r['weight_region']==region],key=lambda r:r['top5_frequency']);y=np.arange(len(rows));ax.barh(y,[r['top5_frequency'] for r in rows],color=['#146c78' if r['corridor_id']==23 else '#a8b7c2' for r in rows]);ax.set_yticks(y,[str(r['corridor_id']) for r in rows]);ax.set_xlim(0,1);ax.set_title(title,fontweight='bold');ax.set_xlabel('Top-five inclusion under declared preference prior');ax.grid(axis='x',alpha=.2)
  for i,r in enumerate(rows):
   if r['corridor_id']==23:ax.text(min(.95,r['top5_frequency']+.01),i,f' 23: {100*r["top5_frequency"]:.1f}%',va='center',ha='right' if r['top5_frequency']>.8 else 'left',fontweight='bold')
 axes[0].set_ylabel('Corridor ID (main tier)');fig.suptitle('Weight sensitivity tests the limits of “100% immunity”',fontweight='bold');fig.text(.09,.025,'Dirichlet(1,1,1) group budgets; equal member split; two imputation methods.\nBalanced subset: every group 10%–60%. This region is illustrative, not stakeholder-elicited.',fontsize=9);fig.tight_layout(rect=[0,.10,1,.94]);save(fig,'preference_prior_sensitivity');plt.close(fig)

def save(fig,name):
 for ext in ['png','svg','pdf']:
  p=O/(name+'.'+ext);fig.savefig(p,dpi=210)
  if ext=='svg':p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
if __name__=='__main__':run()
