"""Quantitatively assess all 24 in their declared contexts, without pooled ranks."""
import json,itertools
import numpy as np
import geopandas as gpd
from tiered_common import ROOT,read,write,dump,tiers
from run_tiered_model_v0_6 import load_model
O=ROOT/'outputs/model_argument_v0.8'
def run():
 config=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text());base,master,main,conditional,closure,minimum,means,equity,mu,sd=load_model();fields=config['fields']
 source={int(r['corridor_id']):r for r in read(ROOT/'data/city_standardized_scores_v0.1.csv')};pairs={int(r['corridor_id']):r for r in read(ROOT/'outputs/tiered_v0.6/conditional_pair_analysis.csv')}
 contextual=[]
 for method,table in zip(config['city_methods'],[minimum,means]):
  for profile,weights in config['weight_profiles'].items():
   for cid in range(1,25):
    values=[float(table[cid][f]) if f!=fields[-1] else (float(equity[cid][f])-mu)/sd for f in fields]
    row=dict(corridor_id=cid,corridor_name=master[cid]['corridor_name'],baseline_scenario_id=master[cid]['baseline_scenario_id'],tier='common_baseline_main' if cid in main else 'conditional_extension',city_method=method,weight_profile=profile,**dict(zip(fields,values)),contextual_priority_index=sum(v*w for v,w in zip(values,weights)),cross_baseline_rank='not_computed',imputed_City_fields=';'.join(f for f in fields[:-1] if source[cid][f]==''),equity_value_status=equity[cid]['value_status'],interpretation='Need-priority score in stated baseline context, not comparable causal benefit across different baseline networks')
    contextual.append(row)
 write(O/'all24_contextual_scores.csv',contextual)
 ledger=[];conditional_details=[]
 for cid in range(1,25):
  missing=[f for f in fields[:-1] if source[cid][f]==''];eqimputed=equity[cid]['value_status']=='suppressed_CT_imputed'
  ledger.append(dict(corridor_id=cid,corridor_name=master[cid]['corridor_name'],baseline_scenario_id=master[cid]['baseline_scenario_id'],quantitatively_assessed=True,selected_field_count=5,declared_method_profile_cases=6,main_rank_eligible=cid in main,eligibility_basis='Common City Base 0 source context' if cid in main else 'Source forecast context assumes additional evaluated predecessor corridor(s); unanchored Base 0 counterpart unavailable',required_predecessors=';'.join(map(str,closure[cid])),source_City_values_available=4-len(missing),source_City_values_missing=len(missing),imputed_City_fields=';'.join(missing),equity_count_imputation_involved=eqimputed,conditional_pair_assessed=cid in conditional,underlying_source_replaced=False,cross_baseline_rank='not_computed'))
  if cid in conditional:
   scores=[float(r['contextual_priority_index']) for r in contextual if r['corridor_id']==cid]
   p=pairs[cid];conditional_details.append(dict(corridor_id=cid,corridor_name=master[cid]['corridor_name'],baseline_scenario_id=master[cid]['baseline_scenario_id'],required_predecessors=';'.join(map(str,closure[cid])),required_sequence=' -> '.join(map(str,[*closure[cid],cid])),all5_selected_fields_evaluated=True,method_profile_cases=6,contextual_index_minimum=min(scores),contextual_index_maximum=max(scores),unanchored_absolute_rank='not_identified',incremental_population_estimate=p['incremental_population_estimate'],incremental_low_income_estimate=p['incremental_low_income_estimate'],with_extension_union_population=p['with_extension_population_estimate'],with_extension_union_low_income_share=p['with_extension_custom_low_income_share'],imputed_City_fields=';'.join(missing),imputed_CTUIDs=p['imputed_CTUIDs'],next_decision='Reassess against common counterfactual when predecessors are committed/in baseline, or model explicit bundles under a separate mandate',limitations='Conditional need index is not additive across projects; geometric extra coverage is not ridership or causal transport benefit. No evidence this corridor is intrinsically inferior.'))
 write(O/'all24_evaluation_coverage.csv',ledger);write(O/'conditional_assessment_detail.csv',conditional_details)
 # Unscored land-use context from already acquired sources; do not call current residents future growth.
 buffers=gpd.read_file(ROOT/'outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson').to_crs(2952);areas={int(r.corridor_id):r.geometry.area for r in buffers.itertuples()}
 density=[]
 for cid in range(1,25):
  row=equity[cid];support=areas[cid]-float(row['area_outside_CT_cartographic_frame_m2'])
  if support<=0:raise ValueError('Nonpositive CT land support')
  population=float(row['total_population_estimate'])
  density.append(dict(corridor_id=cid,covered_population_estimate=population,CT_cartographic_land_support_km2=support/1e6,existing_residential_density_persons_per_km2=population/(support/1e6),scored_in_main_model=False,reference='2021 population/geography; current-road proxy catchment',principle_context='Strengthen Places: current residential intensity only',does_not_measure='Housing supply, development potential, future population growth, station access or environmental benefits'))
 write(O/'unscored_residential_intensity_context.csv',density)
 coverage=[dict(principle='Serve People',scored_fields='current_speed;unimproved_load;competitiveness;low_income_population_share_500m',direct_measurement='Existing/forecast service-pressure and relative choice scores; concentration of low-income residents',indirect_pathway='Potential service and distributional need, not realized benefit or transport access gain',unscored_context='',unmeasured_outcomes='Realized travel time gains, reliability, transfer integration, station accessibility and distribution of benefits',coverage_status='Scored need proxies; benefit interpretation limited',evidence='City attachment physical pp.1-3 Figure 1/Table 1; custom Census definition'),dict(principle='Strengthen Places',scored_fields='',direct_measurement='No direct scored housing/development/environment outcome',indirect_pathway='Equitable resident catchments may inform place planning, but are not a development outcome',unscored_context='2021 residential intensity in CT-supported proxy catchments (all 24)',unmeasured_outcomes='Additional housing, land-use development potential, neighbourhood quality, emissions and forecast place growth',coverage_status='Context only; direct scored coverage gap disclosed',evidence='City Figure 1 physical p.2 and Table 1 p.6; Census/CT proxy density is separately unscored'),dict(principle='Support Prosperity',scored_fields='current_max_load',direct_measurement='City places current maximum load in Affordability; this is a non-cost demand proxy, not measured financial efficiency',indirect_pathway='Demand/service use may support economic activity; competitiveness may affect journey choice but no job access is computed',unscored_context='',unmeasured_outcomes='Employment catchments, access to jobs, productivity, forecast economic growth and actual affordability/cost effectiveness',coverage_status='Partial City-category proxy; growth/economic outcomes unmeasured',evidence='City Figure 1 physical p.2; Table 1 physical p.6; Part 1 cost prohibition prevents cost-based substitutes')]
 write(O/'three_principle_coverage.csv',coverage)
 result=dict(all24_assessed=len(ledger)==24,quantitative_context_score_rows=len(contextual),main_rank_count=16,conditional_corridor_count=8,conditional_selected_fields=5,conditional_cases_each=6,conditional_pair_count=len(conditional_details),all24_unconditional_optimum_identified=False,main_decision_scope='One evaluated corridor addition compared against City Base 0, with explicit rank eligibility; not a physical infeasibility declaration or source-case waiver',all_three_principles_directly_scored=False,residential_context_scored=False)
 dump(O/'coverage_summary.json',result);print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
