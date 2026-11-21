from pathlib import Path
import csv,json
P=Path(__file__).resolve().parent.parent/'outputs/project'
for d in ['data','evidence','code','outputs','slides']:(P/d).mkdir(parents=True,exist_ok=True)
schema={
'corridor_master':['corridor_id','corridor_name','endpoint_a','endpoint_b','length_km','length_basis','city_assumed_technology','baseline_scenario_id','prerequisite_corridor_ids','source_id','notes'],
'source_log':['source_id','title','publisher','publication_date','retrieval_date','url','source_type','source_locator','scope','notes'],
'data_dictionary':['indicator_id','indicator_name','primary_principle','definition','unit','spatial_scope','population_scope','reference_year','measurement_period','value_type','technology_dependence','cost_dependence','potential_overlap','data_availability','source_id','source_locator','master_column','notes'],
'indicator_admission':['indicator_id','indicator_name','primary_principle','admission_status','cost_dependence','raw_value_available','definition_clear','unit_clear','direction','temporal_comparability','spatial_comparability','baseline_comparability','coverage_count','missing_corridor_ids','potential_overlap','decision_reason','source_id','reviewer','review_date','notes'],
'tech_evidence':['evidence_id','corridor_id','technology_id','technology_name','criterion_id','value','unit','value_status','reference_year','price_year','currency','scenario_id','lower_bound','upper_bound','uncertainty_basis','source_id','source_locator','notes'],
'part2_sources':['source_id','title','publisher','publication_date','retrieval_date','url','source_type','source_locator','technology_scope','comparability_notes','notes'],
'indicator_observations':['corridor_id','indicator_id','value','value_status','source_id','source_locator','reference_year','scenario_id','transformation_id','notes']}
(P/'data/schema_v0.1.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
for key,folder in [('corridor_master','data'),('source_log','data'),('indicator_observations','data'),('tech_evidence','evidence'),('part2_sources','evidence')]:
 f=P/f'{folder}/{key}_v0.1.csv'
 if not f.exists():
  with f.open('w',newline='',encoding='utf-8-sig') as o:
   w=csv.writer(o);w.writerow(schema[key])
   if key=='corridor_master':
    for i in range(1,25):w.writerow([i]+['']*(len(schema[key])-1))
src=json.loads((P.parent.parent/'work/inventory_data.json').read_text(encoding='utf-8'))[1]['rows']
units=['Speed; source unit not specified','Time savings; aggregation and time unit not specified','On-board riders; peak period and direction not specified','Persons','Weighted accessibility; units not specified','Development potential; units not specified','Vehicle-kilometres; period not specified','Mode-share decrease; percent vs percentage points not specified','Jobs','Weighted accessibility; units not specified','Development potential; units not specified','On-board riders; peak period and direction not specified','Riders; measurement period not specified','Additional riders; measurement period not specified','Transit-to-auto time ratio; numerator convention requires verification']
types=['Observed summary statistic','Forecast level','Forecast level','Forecast and spatial aggregation','Scenario difference','Spatial planning measure','Scenario difference','Scenario difference','Forecast and spatial aggregation','Scenario difference','Spatial planning measure','Observed summary statistic','Observed ridership','Scenario difference','Observed ratio']
types[1]='Scenario benefit estimate'
overlap=['Competitiveness; travel-time savings','Employment accessibility; ridership; equity time savings','Current maximum load; current ridership; new riders','Population accessibility; residential potential; ridership; equity coverage','Time savings; job coverage; equity job accessibility','Population coverage; employment potential','Auto mode share; new riders','Auto VKT; new riders','Employment accessibility; employment potential; ridership','Population coverage; employment accessibility; time savings','Employment coverage; residential potential','Unimproved load; current ridership','Maximum load; population/job coverage; new riders','Current ridership; auto VKT; mode share; accessibility','Current speed; travel-time savings']
header=['indicator_id','indicator_name','rtef_category','definition','definition_page','value_table','value_page','underlying_value_type','published_value_type','unit','direction','cost_dependence','potential_overlap','source_id','notes']
rows=[]
for i,r in enumerate(src):
 if i<15:
  cost='yes: published score uses Cost scaling' if r[7]=='Cost' else 'no explicit cost scaling; Length scaling' if r[7]=='Length' else 'no explicit cost scaling'
  direction='Higher benefit is generally preferable; verify source score orientation'
  if i in [0,14]:direction='Depends on service-quality versus unmet-need objective; verify source transformation'
  elif i in [2,11,12]:direction='Higher demand/pressure, not necessarily higher project benefit'
  notes='Raw corridor quantities are not published in the attachment. Cost-scaled scores cannot enter Part 1.' if r[7]=='Cost' else 'Published score is not a raw observation. Verify missingness and direction.'
  if i in [3,8]:notes+=' Forecast uses 2021 level plus 0.8 times projected 2021-2051 growth.'
  rows.append([r[0],r[2],r[1],r[3],6,6 if i<8 else 7,11 if i<8 else 12,types[i],'Standardized score',units[i],direction,cost,overlap[i],'CITY2024_ATTACHMENT',notes])
 else:
  dim=(i-15)%3
  defs=['Relative group benefit from average travel-time savings','Relative group benefit from change in transit access to employment','Relative group benefit from population served within 500 m of proposed stops; Table 8 labels 2021 Census Distribution']
  rows.append([r[0],r[2],'Equity',defs[dim],3,8,13,'Group benefit ratio derived from forecasts or census coverage','Standardized score; not raw Palma ratio','Dimensionless','Raw Palma below 1 favours equity group; standardized direction formula not fully specified','not explicitly specified; verify implementation',['Overall travel-time savings; other equity dimensions','Overall employment accessibility; travel-time savings','Overall population coverage; overlapping equity groups'][dim],'CITY2024_ATTACHMENT','Five equity groups may overlap. Group thresholds and complete ratio formula are not supplied here.'])
with (P/'data/city_2024_indicator_index_v0.1.csv').open('w',newline='',encoding='utf-8-sig') as o:
 w=csv.writer(o);w.writerow(header);w.writerows(rows)
(P/'data/workbook_records_v0.1.json').write_text(json.dumps({'data_dictionary':[],'indicator_admission':[]},indent=2),encoding='utf-8')
print('Created schemas, empty tables, fixed 24-ID skeleton, and 30-indicator index.')
