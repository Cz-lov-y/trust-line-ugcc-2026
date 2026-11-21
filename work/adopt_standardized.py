from pathlib import Path
import csv,json,copy
P=Path(__file__).resolve().parent.parent/'outputs/project'
def load(f):
 with (P/f).open(encoding='utf-8-sig',newline='') as s:return list(csv.DictReader(s))
def save(f,r):
 with (P/f).open('w',encoding='utf-8-sig',newline='') as s:
  w=csv.DictWriter(s,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
keys=['current_speed','unimproved_load','current_max_load','current_ridership','competitiveness']
master=load('data/corridor_master_v0.1.csv');archive=load('evidence/city_2024_published_scores_NOT_RAW_v0.1.csv')
lookup={(r['corridor_id'],r['field_id']):r['reported_value'] for r in archive if r['table_number'] in ['6','7']}
scores=[dict(corridor_id=c['corridor_id'],**{k:lookup[(c['corridor_id'],k)] for k in keys},source_id='CITY2024_ATTACHMENT',notes='Published dimensionless scores copied without transformation; blank means source N/A. Current ridership is length-scaled, not cost-scaled.') for c in master]
save('data/city_standardized_scores_v0.1.csv',scores)
records=json.loads((P/'data/workbook_records_v0.1.json').read_text(encoding='utf-8'))
for a in records['indicator_admission']:
 if a['indicator_id'] in keys:
  k=a['indicator_id'];missing=[r['corridor_id'] for r in scores if r[k]=='']
  a.update(input_file='data/city_standardized_scores_v0.1.csv',input_column=k,input_value_type='city_standardized_score',raw_value_available='standardized_score_available',cost_dependence='no',direction='higher_is_better',coverage_count=24-len(missing),missing_corridor_ids=';'.join(missing),admission_status='pending_missing_data' if missing else 'pending_baseline_review',definition_clear='confirmed',unit_clear='confirmed',spatial_comparability='source_corridor_scope_retained',temporal_comparability='source_vintage_retained',baseline_comparability='not_established',decision_reason='Selected for the standardized-score strategy; final admission requires complete inputs and source interpretation review.',notes='Higher is interpreted as a more favourable City evaluation score, not a higher raw speed or transit/auto time ratio. Source Table 1 lists no Cost scaling for this measure. Score orientation/aggregation and baseline comparability require review. '+('Original scores are per construction length.' if k=='current_ridership' else '')+' Source N/A values remain blank; no imputation performed.')
for d in records['data_dictionary']:
 if d['indicator_id'] in keys:
  d.update(input_file='data/city_standardized_scores_v0.1.csv',input_column=d['indicator_id'],input_value_type='city_standardized_score',input_unit='dimensionless City standardized score',input_cost_dependence='no',notes=d['notes']+' Separate standardized input is now selected for review; the raw master column remains empty. No inverse standardization was performed.')

long=load('data/candidate_indicator_longlist_v0.1.csv')
if not any(r['indicator_id']=='priority_populations_index' for r in long):
 ppi=copy.deepcopy(next(r for r in long if r['indicator_id']=='population_coverage_2021'))
 ppi.update(indicator_id='priority_populations_index',indicator_name='Priority Populations Index (population-weighted corridor mean)',primary_principle='Serve People',city_rtef_category='Equity supplemental candidate',definition='Mean of exact Census Tract Priority Populations Index scores weighted by estimated residents in the corridor catchment. Formula: sum(P_it * I_t) / sum(P_it). Full TEOZ is not interchangeable with its priority-populations component.',unit='index points; source scale to be verified',reference_year='2021 Census; May 2024 City map',value_type='derived_composite_index',technology_dependence='catchment and stop assumptions only; no technology costs proposed',cost_dependence='requires_source_method_verification',potential_overlap='equity population measures; housing and manufacturing employment components',data_availability='not_computed',source_id='CITY2024_PRIORITY_MAP',notes='No corridor index has been calculated. Exact tract scores, methodology, population weights and validated corridor catchments are not yet acquired. Do not use map-class midpoints or substitute full TEOZ.',master_column='indicator_priority_populations_index',source_locator='Transportation Equity Priority Populations map, May 2024',direction='higher_is_better',city_scaling='not_verified',admission_status='pending_evidence',definition_status='proposed_requires_inputs',raw_source_status='pending_collection')
 long.append(ppi)
 dd={k:ppi.get(k,'') for k in records['data_dictionary'][0]}
 dd.update(input_file='data/supplemental_model_inputs_v0.1.csv',input_column='priority_populations_index',input_value_type='derived_composite_index',input_unit=ppi['unit'],input_cost_dependence='unresolved')
 records['data_dictionary'].append(dd)
 aa={k:'' for k in records['indicator_admission'][0]}
 aa.update(indicator_id=ppi['indicator_id'],indicator_name=ppi['indicator_name'],primary_principle='Serve People',admission_status='pending_evidence',cost_dependence='unresolved',raw_value_available='no',definition_clear='proposed',unit_clear='partial',direction='higher_is_better',temporal_comparability='not_established',spatial_comparability='not_established',baseline_comparability='not_established',coverage_count=0,missing_corridor_ids=';'.join(str(i) for i in range(1,25)),potential_overlap=ppi['potential_overlap'],decision_reason='Selected supplemental equity candidate, not admitted until calculation and provenance exist.',source_id=ppi['source_id'],reviewer='Agent A',review_date='2026-11-21',notes=ppi['notes'],input_file='data/supplemental_model_inputs_v0.1.csv',input_column='priority_populations_index',input_value_type='derived_composite_index')
 records['indicator_admission'].append(aa)
 for c in master:c['indicator_priority_populations_index']=''
 obs=load('data/indicator_observations_v0.1.csv')
 for c in master:obs.append(dict(corridor_id=c['corridor_id'],indicator_id='priority_populations_index',value='',value_status='pending_collection',source_id=ppi['source_id'],source_locator=ppi['source_locator'],reference_year=ppi['reference_year'],scenario_id='catchment_not_established',transformation_id='',notes=ppi['notes']))
 save('data/indicator_observations_v0.1.csv',obs)
save('data/candidate_indicator_longlist_v0.1.csv',long);save('data/corridor_master_v0.1.csv',master)
save('data/supplemental_model_inputs_v0.1.csv',[dict(corridor_id=c['corridor_id'],priority_populations_index='',source_id='CITY2024_PRIORITY_MAP',notes='Not computed. Source methods and exact tract scores/catchments required.') for c in master])
sources=load('data/source_log_v0.1.csv')
if not any(r['source_id']=='CITY2024_PRIORITY_MAP' for r in sources):sources.append(dict(source_id='CITY2024_PRIORITY_MAP',title='Transportation Equity: Priority Populations',publisher='City of Toronto Transportation Services',publication_date='2024-05',retrieval_date='2026-11-21',url='https://www.toronto.ca/wp-content/uploads/2024/07/8efd-Equity-PriorityPop.pdf',source_type='official_map_method_prospect',source_locator='Single-page map and explanatory note',scope='Toronto Census Tract priority-population index',notes='Public map identified; exact tract data and complete index construction not acquired. Map classes do not provide exact corridor values.'))
save('data/source_log_v0.1.csv',sources)
schema=json.loads((P/'data/schema_v0.1.json').read_text())
for section in ['data_dictionary','indicator_admission']:
 for k in ['input_file','input_column','input_value_type']:
  if k not in schema[section]:schema[section].append(k)
 for r in records[section]:
  for k in ['input_file','input_column','input_value_type']:r.setdefault(k,'')
schema['corridor_master']=list(master[0]);schema['city_standardized_scores']=list(scores[0])
(P/'data/schema_v0.1.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
(P/'data/workbook_records_v0.1.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(P/'data/model_input_selection_v0.1.json').write_text(json.dumps(dict(strategy='City non-cost-scaled standardized scores plus verified supplemental equity input',selected_indicator_ids=keys+['priority_populations_index'],cost_inputs_prohibited=True,missing_data_policy='preserve source missingness; no imputation authorized in this dataset',standardized_scores_file='data/city_standardized_scores_v0.1.csv'),indent=2),encoding='utf-8')
gap=load('data/data_gap_register_v0.1.csv')
if not any(r['indicator_id']=='priority_populations_index' for r in gap):gap.append(dict(indicator_id='priority_populations_index',nonmissing_corridors=0,missing_corridors=24,status='not_computed',next_action='Obtain exact tract index, population weights and validated catchments'))
save('data/data_gap_register_v0.1.csv',gap)
save('data/model_input_coverage_v0.1.csv',[dict(indicator_id=a['indicator_id'],input_file=a['input_file'],coverage_count=a['coverage_count'],missing_corridor_ids=a['missing_corridor_ids'],admission_status=a['admission_status']) for a in records['indicator_admission'] if a['indicator_id'] in keys+['priority_populations_index']])
print(json.dumps({k:sum(s[k]!='' for s in scores) for k in keys},indent=2))
