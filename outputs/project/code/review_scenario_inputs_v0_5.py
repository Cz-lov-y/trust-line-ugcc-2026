"""Baseline dependency audit and explicitly exploratory six-criterion diagnostics."""
from pathlib import Path
import csv,json,statistics,math
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/corridor_batch_v0.5'
FIELDS=['current_speed','unimproved_load','current_max_load','current_ridership','competitiveness']
def read(p):
 with Path(p).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(p,rows):
 with Path(p).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run():
 master=read(ROOT/'data/corridor_master_v0.1.csv');minimum=read(ROOT/'data/city_analysis_inputs_v0.4.csv');means=read(ROOT/'data/city_mean_sensitivity_v0.4.csv');source=read(ROOT/'data/city_standardized_scores_v0.1.csv');equity=read(ROOT/'data/supplemental_model_inputs_v0.5.csv')
 expected={str(i) for i in range(1,25)}
 for dataset in [master,minimum,means,source,equity]:
  if len(dataset)!=24 or {r['corridor_id'] for r in dataset}!=expected:raise ValueError('Unique 24-corridor source join required')
  dataset.sort(key=lambda r:int(r['corridor_id']))
 matrix=[dict(corridor_id=i+1,**{f:minimum[i][f] for f in FIELDS},low_income_population_share_500m=equity[i]['low_income_population_share_500m'],City_imputed_indicator_ids=minimum[i]['imputed_indicator_ids'],equity_value_status=equity[i]['value_status'],equity_imputed_CTUIDs=equity[i]['imputed_CTUIDs']) for i in range(24)]
 write(ROOT/'data/model_matrix_v0.5.csv',matrix)
 graph={r['corridor_id']:[p for p in r['prerequisite_corridor_ids'].split(';') if p] for r in master}
 def visit(cid,stack=()):
  if cid in stack:raise ValueError('Cyclic baseline dependency')
  for p in graph[cid]:
   if p not in graph:raise ValueError('Unknown baseline prerequisite')
   visit(p,(*stack,cid))
 for cid in graph:visit(cid)
 audit=[]
 for m,s in zip(master,source):
  missing=[f for f in FIELDS if s[f]=='']
  audit.append(dict(corridor_id=m['corridor_id'],corridor_name=m['corridor_name'],baseline_scenario_id=m['baseline_scenario_id'],prerequisite_corridor_ids=m['prerequisite_corridor_ids'],source_missing_fields=';'.join(missing),source_missing_count=len(missing),baseline_ID_reconciled='yes',dependency_DAG_valid='yes',observed_TTC_fields='current_speed;current_max_load;current_ridership;competitiveness',observed_reference='Fall 2022 where specified in City Table 1; current maximum load has no separate explicit year',forecast_field='unimproved_load',forecast_reference='2051 forecast framework; unimproved corridor',conditional_forecast_review='requires_common_baseline_counterfactual' if graph[m['corridor_id']] else 'CITY_BASE_0_retained',geographic_scope_review='pending_road_proxy_vs_City_corridor',review_status='documented_not_harmonized',evidence='CITY2024_ATTACHMENT physical pp.3-4 Section 2.5, p.6 Table 1, p.7 Table 2',notes='Minimum substitution changes the missing input, not the forecast baseline. Range overlap is descriptive and cannot establish counterfactual equivalence. Equity is 2020 income / 2021 population under historical geography.'))
 write(O/'baseline_comparability_audit.csv',audit)
 observed_range={f:(min(float(r[f]) for r in source if r[f]!=''),max(float(r[f]) for r in source if r[f]!='')) for f in FIELDS}
 ref=[float(r['unimproved_load']) for r in source if all(r[f]!='' for f in FIELDS)]
 for a,m in zip(audit,minimum):
  a['unimproved_load_analysis_score']=m['unimproved_load'];a['within_complete_corridor_unimproved_load_range']=min(ref)<=float(m['unimproved_load'])<=max(ref)
 write(O/'baseline_comparability_audit.csv',audit)
 def zscores(values):
  mean=statistics.fmean(values);sd=statistics.pstdev(values)
  if sd==0:raise ValueError('Constant equity cannot be standardized')
  return [(v-mean)/sd for v in values]
 raw=[float(r['low_income_population_share_500m']) for r in equity]
 alternate=[float(r['mean_sensitivity_share']) for r in equity]
 scenarios={};rows=[]
 for name,city,eq,drop,dynamic in [('city_min_CT_median',minimum,raw,False,False),('city_min_CT_mean',minimum,alternate,False,False),('city_mean_CT_median',means,raw,False,False),('available_case_CT_median',source,raw,False,True),('exclude_forecast_load',minimum,raw,True,False)]:
  z=zscores(eq);scores=[]
  for i,r in enumerate(city):
   values=[float(r[f]) for f in FIELDS if (not drop or f!='unimproved_load') and r[f]!='']+[z[i]]
   scores.append(statistics.fmean(values))
  ranks={i+1:1+sum(v>scores[i] for v in scores) for i in range(24)}
  scenarios[name]=dict(scores=scores,ranks=ranks,top3=sorted(sorted(ranks,key=lambda k:(ranks[k],k))[:3]))
 for i in range(24):
  row=dict(corridor_id=i+1)
  for name,s in scenarios.items():row[name+'_score']=s['scores'][i];row[name+'_rank']=s['ranks'][i+1]
  rows.append(row)
 write(O/'six_criterion_policy_diagnostic.csv',rows)
 base=scenarios['city_min_CT_median'];summary={}
 for name,s in scenarios.items():summary[name]=dict(top3=s['top3'],maximum_rank_change_from_primary=max(abs(s['ranks'][i]-base['ranks'][i]) for i in range(1,25)))
 result=dict(data_matrix_ready=True,scenario_computation_ready=True,model_ready=False,final_recommendation_ready=False,selected_indicator_count=6,input_cells=144,City_observed_cells=98,City_scenario_substitutions=22,equity_estimate_count=24,conditional_baseline_corridors=[int(r['corridor_id']) for r in audit if r['prerequisite_corridor_ids']],baseline_dependency_DAG_valid=True,common_baseline_equivalence_established=False,all_geographic_reviews_pending=True,diagnostic_only=True,diagnostic_method='Equal criterion weights; retain published City z scores; equity standardized across all 24 with population SD separately in each scenario; competition ranks; available-case proportional reweighting for missing City cells',scenarios=summary,limitations=['No common-baseline counterfactual data to harmonize conditional City forecasts','Road buffers differ from station catchments; seven general shortest paths differ from seventeen named-road proxies','Observed-minimum substitution is not a theoretical worst-case bound or proof of robust ordering','Historical income/population and City observation/forecast vintages differ'])
 (O/'scenario_review_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
