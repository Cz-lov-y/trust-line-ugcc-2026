"""Register complete proxy-scenario inputs while retaining final review gates."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
FIELDS={'current_speed','unimproved_load','current_max_load','current_ridership','competitiveness'}
def read(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:
  r=csv.DictReader(f);return r.fieldnames,list(r)
def write(p,fields,rows):
 with Path(p).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def js(p,obj):Path(p).write_bytes(json.dumps(obj,indent=2).replace('\n','\r\n').encode())
def register():
 d=ROOT/'data';p=d/'workbook_records_v0.1.json';records=json.loads(p.read_text())
 for section,rows in records.items():
  for r in rows:
   key=r['indicator_id']
   if key not in FIELDS|{'low_income_population_share_500m'}:continue
   if key in FIELDS:
    r['notes']='Higher is interpreted as a more favourable published City evaluation score (Attachment pp.2,4), not a raw speed or time ratio. Table 1 has no cost scaling for this input; current ridership is length-scaled. Original source cells are preserved. Analysis file substitutes only original blanks using observed-column minima and per-cell imputed_conservative_min flags. This is a penalty assumption, not a theoretical worst-case bound. v0.5: All 24 analysis inputs available. Conditional forecast dependencies documented in baseline_comparability_audit.csv; substitution does not harmonize CITY_BASE_AFTER_X. Original observation and forecast vintages retained; geographic/counterfactual comparability unresolved.'
   else:
    r.update(input_file='data/supplemental_model_inputs_v0.5.csv',input_column=key,input_value_type='area_weighted_census_imputation_scenario',published_source_coverage_count=21,scenario_substitution_count=3,missing_data_policy='Complete DA sum, otherwise same-CSD complete CT rate median; suppressed_CT_imputed; mean sensitivity')
    r['notes']='v0.5: 24/24 provisional CT area-weighted estimates. Custom LIM characteristic 326 / all residents characteristic 1; income reference 2020, geography/population 2021; not official LIM prevalence. Uniform within-CT density. Two positive-population CTs (5350205.00, 5350006.00) and all their DAs have suppressed LIM counts. User-authorized same-Toronto complete CT rate median (583 peers) times CT population supplies separate scenario counts; mean sensitivity retained. Original suppressed source cells stay blank. Corridors 3,8,21 include these replacements. Source-complete catchments: 21; constructed scenario coverage: 24. Seven 2021 RNF shortest-road proxies plus seventeen prior named-road proxies; no approved future alignment or station catchment claim. Geographic, vintage and baseline reviews remain pending.'
   r['scenario_admission_status']='admitted_for_declared_proxy_scenario'
   if section=='indicator_admission':
    r.update(coverage_count=24,missing_corridor_ids='',admission_status='pending_comparability_review',decision_reason='Complete replay-validated proxy scenario available; final geography and common-baseline equivalence not established.')
    if key=='low_income_population_share_500m':r.update(raw_value_available='scenario_input_available',spatial_comparability='consistent_CT_allocation; mixed_road_proxy_methods_pending_review',temporal_comparability='historical_income_population_and_City_vintages_disclosed',baseline_comparability='not_established_across_24')
 js(p,records)
 p=d/'model_input_selection_v0.1.json';s=json.loads(p.read_text());s.update(strategy='Six-criterion declared proxy scenario: City observed-minimum and CT area-weighted equity with municipal peer-rate fallback',supplemental_inputs_file='data/supplemental_model_inputs_v0.5.csv',missing_data_policy='Preserve all source blanks. City: observed-column minimum in separate scenario. Census: complete DA sum when possible, otherwise authorized municipal CT-rate median with mean sensitivity. No arbitrary missing-value waiver.',equity_suppression_policy='data/equity_proxy_method_v0.5.json');js(p,s)
 method=dict(indicator_id='low_income_population_share_500m',allocation_method='ct_area_fraction_uniform_density',numerator='sum(intersection_area / CT_area * CT_analysis_LIM_count)',denominator='sum(intersection_area / CT_area * CT_total_population)',source_characteristics={'population_2021':1,'LIM_applicable_population':321,'LIM_low_income_count':326},primary_suppression_method='complete DA sum; if any member DA LIM count missing, unweighted median of all complete positive-population CT LIM/all-population ratios in same CSD times suppressed CT population',sensitivity_method='unweighted mean of same complete municipal CT ratios',fallback_CSDUID='3520005',fallback_peer_CT_count=583,flag='suppressed_CT_imputed',source_preservation='Suppressed source cells remain blank; only analysis counts are constructed',geographic_review='pending',income_reference_year=2020,population_geography_year=2021,scope='resident concentration around road proxy, not official prevalence or benefit distribution',new_endpoint_policy='data/corridor_endpoint_coordinates_v0.5.json',provenance_validation='code/validate_equity_scenario.py')
 js(d/'equity_proxy_method_v0.5.json',method)
 fields,rows=read(d/'model_input_coverage_v0.1.csv')
 for r in rows:
  if r['indicator_id']=='low_income_population_share_500m':r.update(input_file='data/supplemental_model_inputs_v0.5.csv',coverage_count='24',missing_corridor_ids='',published_source_coverage_count='21',scenario_substitution_count='3')
  if r['indicator_id'] in FIELDS|{'low_income_population_share_500m'}:r['admission_status']='pending_comparability_review'
 write(d/'model_input_coverage_v0.1.csv',fields,rows)
 fields,rows=read(d/'corridor_geometry_review_v0.1.csv');audit={str(r['corridor_id']):r for r in json.loads((ROOT/'outputs/corridor_batch_v0.5/endpoint_route_audit.json').read_text())}
 for r in rows:
  if r['corridor_id'] in audit:
   a=audit[r['corridor_id']];r.update(alignment_geometry_status='shortest_road_proxy_pending_review',station_set_status='not_defined',catchment_status='500m_road_buffer_pending_review',full_alignment_length_km=a['measured_route_length_km'],geometry_source_id='RNF2021_ENDPOINT_PROXY',next_action='Review provisional endpoint choice, cartographic topology and road path against future transit scope.',notes=a['limitations'])
 write(d/'corridor_geometry_review_v0.1.csv',fields,rows)
 fields,gaps=read(d/'data_gap_register_v0.1.csv')
 for gap in gaps:
  if gap['indicator_id']=='low_income_population_share_500m':gap.update(status='raw_placeholder_empty; derived_scenario_separate',next_action='Raw source inventory remains blank. Separate v0.5 scenario has 24/24 estimates (21 source-complete catchments; 3 include suppressed_CT_imputed). Complete final geography/baseline reviews.')
 write(d/'data_gap_register_v0.1.csv',fields,gaps)
 fields,rows=read(d/'source_log_v0.1.csv')
 new=[dict(source_id='RNF2021_ENDPOINT_PROXY',title='2021 Road Network File and provisional endpoint references',publisher='Statistics Canada; TTC; Metrolinx; Ontario Place; coordinate supplement Wikipedia',publication_date='2021',retrieval_date='2026-11-21',url='https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Road_Network_File/MapServer',source_type='official_cartographic_roads_with_declared_endpoint_assumptions',source_locator='evidence/corridor_batch_v0.5/official_RNF_source_pages.zip; data/corridor_endpoint_coordinates_v0.5.json',scope='Seven current-road proxy paths; all GTA road ranks queried with ID reconciliation',notes='Operator GTFS coordinates wherever available. Ontario Place entrance uses City intersection node. Future Woodbine GO uses a secondary approximate coordinate cross-referenced to official Highway 27 planning location; not surveyed. Undirected cartographic proxies.'),dict(source_id='CENSUS_SUPPRESSION_POLICY_V05',title='User-authorized Census CT suppression scenario policy',publisher='Team analytical configuration; Statistics Canada profiles',publication_date='2026-11-21',retrieval_date='2026-11-21',url='',source_type='declared_analysis_method',source_locator='data/equity_proxy_method_v0.5.json; outputs/corridor_batch_v0.5/suppression_imputation_trace.csv',scope='Two Toronto CT source cells affecting three corridor estimates',notes='All member DA LIM cells are suppressed. Median of 583 complete municipal CT rates times suppressed CT total population; mean sensitivity. No source overwrite.')]
 for r in new:
  if r['source_id'] not in {x['source_id'] for x in rows}:rows.append(r)
 write(d/'source_log_v0.1.csv',fields,rows)
 fields,rows=read(d/'acquisition_log_v0.1.csv')
 if 'ACQ_V05_PROXY_COMPLETE' not in {r['acquisition_id'] for r in rows}:rows.append(dict(acquisition_id='ACQ_V05_PROXY_COMPLETE',indicator_scope='24/24 proxy equity and six-criterion matrix',source_id='RNF2021_ENDPOINT_PROXY;CENSUS_SUPPRESSION_POLICY_V05;STATCAN2021_LIM_PROFILE',status='scenario_complete_24; final_review_pending',last_checked='2026-11-21',evidence='Seven sourced endpoint road paths; profiles for 305 intersecting CTs and 585 Toronto peer CTs; 583 eligible peers. Two DA cells also suppressed. Matrix complete, source blanks retained.',required_input='Common-baseline counterfactuals and reviewed future transit geography',next_action='Use declared scenario for exploratory computation; review geography/conditional baselines; do not claim full source observation or final robustness.'))
 write(d/'acquisition_log_v0.1.csv',fields,rows)
 schema_path=d/'schema_v0.1.json';schema=json.loads(schema_path.read_text());
 for key in ['data_dictionary','indicator_admission']:
  if 'scenario_admission_status' not in schema[key]:schema[key].append('scenario_admission_status')
 schema['v0_5_analysis_scenarios']={'equity_input_type':'area_weighted_census_imputation_scenario','source_complete_corridor_count':21,'scenario_coverage':24,'scenario_admission_status':'admitted_for_declared_proxy_scenario','notes':'Final admission retains comparability gates; scenario readiness differs from model_ready.'};js(schema_path,schema)
if __name__=='__main__':register()
