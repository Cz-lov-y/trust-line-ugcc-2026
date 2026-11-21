"""Populate an evidence inventory, without scoring, imputation or simulation."""
from pathlib import Path
import csv,json,hashlib,shutil
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'outputs/project'
inv=json.loads((ROOT/'work/inventory_data.json').read_text(encoding='utf-8'))
def write(name,rows,headers=None):
    path=P/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=headers or list(rows[0]));w.writeheader();w.writerows(rows)
    return path
general_types=['observed_summary','forecast_change','forecast_level','derived_forecast_coverage','forecast_accessibility_change','derived_spatial_potential','forecast_change','forecast_share_change','derived_forecast_coverage','forecast_accessibility_change','derived_spatial_potential','observed_summary','observed_count','forecast_change','observed_ratio']
units=['km/h; main report Figure 17 context','time benefit; aggregation unit not specified','passengers; loading period not specified','persons','weighted accessibility; unit not specified','not specified','vehicle-km; period not specified','share change; percent or percentage-point convention not specified','jobs','weighted accessibility; unit not specified','not specified','passengers; loading period not specified','riders; exact aggregation not specified','additional riders; period not specified','ratio; numerator convention requires verification']
overlaps=['competitiveness;travel_time_savings','access_employment;access_population;new_riders','current_max_load;current_ridership','residential_potential;access_population;current_ridership','employment;travel_time_savings','population;approved_residential_units','auto_mode_share;new_riders','auto_vkt;new_riders','employment_potential;access_employment','population;travel_time_savings','employment;approved_nonresidential_floor_area','unimproved_load;current_ridership','current_max_load;population;new_riders','current_ridership;auto_mode_share;auto_vkt','current_speed;travel_time_savings']
principles=['Serve People','Support Prosperity','Serve People','Serve People','Support Prosperity','Strengthen Places','Strengthen Places','Strengthen Places','Serve People','Support Prosperity','Strengthen Places','Serve People','Serve People','Serve People','Serve People']
long=[]
for j,m in enumerate(inv[1]['rows']):
    key=m[0]; equity=j>=15
    d=dict(indicator_id=key,indicator_name=m[2],primary_principle='Serve People' if equity else principles[j],city_rtef_category=m[1],definition=m[3],unit='dimensionless raw Palma ratio; full formula not published' if equity else units[j],spatial_scope='City corridor evaluation scope; exact aggregation requires verification',population_scope='Relevant equity group and its comparison population' if equity else 'As defined by the source measure',reference_year='2021 and forecast scenario' if equity else ('2022' if j in [0,12,14] else '2051' if j in [1,3,8] else 'requires_verification'),measurement_period='not fully specified',value_type='derived_equity_ratio' if equity else general_types[j],technology_dependence='forecast service assumptions' if equity or j in [1,4,6,7,9,13] else 'station layout may affect coverage' if j in [3,5,8,10] else 'existing or baseline conditions',cost_dependence='not_explicitly_stated_for_equity' if equity else 'published_score_cost_scaled; raw_benefit_not_intrinsically_cost_based' if m[7]=='Cost' else 'no_explicit_cost_scaling',potential_overlap='overall benefit measure; other equity groups; group membership overlaps' if equity else overlaps[j],data_availability='raw_value_not_published',source_id='CITY2024_ATTACHMENT',notes='Candidate only. Published standardized score must not populate the raw master.',master_column='indicator_'+key,source_locator=m[14].replace('；','; '),direction='requires_verification' if equity or j in [0,14] else 'higher_represents_more_demand_or_benefit',city_scaling=m[7] if not equity else 'not_stated',admission_status='pending_evidence',definition_status='source_defined_but_incomplete_implementation',raw_source_status='not_published')
    if equity:
        parts=key.removeprefix('equity_')
        benefit='relative distribution of travel-time savings' if key.endswith('_tts') else 'relative distribution of employment-accessibility improvement' if key.endswith('_access_employment') else 'relative distribution of population served within 500 m of proposed stops'
        d['definition']=m[2]+': '+benefit+'. Source describes a Palma ratio; its exact numerator, denominator and scoring reversal are not fully specified.'
        if 'low_income' in key:d['notes']+=' Main report p.16 uses LIM-AT.'
        if 'racialized' in key:d['notes']+=' Main report p.16 footnote 10 refers to Total Visible Minority and excludes Indigenous population.'
        if 'recent_immigrants' in key:d['notes']+=' Main report p.17 includes immigrants arriving in 2016-2021 and non-permanent residents.'
        if 'long_commute' in key:d['notes']+=' Main report p.18 defines commute of one hour or more.'
        d['source_id']+=';CITY2024_MAIN'
    if key=='current_speed':
        d['measurement_period']='Fall 2022, 3-7 PM map context'
        d['notes']+=' Main report p.21 reports km/h bands, using express routes where available; no exact corridor aggregate was inferred.'
        d['source_id']+=';CITY2024_MAIN'
    long.append(d)
supp=[
('population_coverage_2021','Existing population coverage','Serve People','Residents in the union of 500 m buffers around an explicitly documented stop set; overlapping buffers counted once.','persons','CENSUS_NEIGHBOURHOODS','population;existing_population_density','2021'),
('employment_coverage_2021','Existing employment coverage','Serve People','Jobs in the same documented catchment, using a consistent employment-survey year and spatial allocation.','jobs','TES_SUMMARY','employment;employment_growth','2021 target; availability unverified'),
('transfer_connections','Transfer connections','Serve People','Distinct transit route or line connections within a documented pedestrian transfer distance of proposed stops; avoid counting route variants as separate lines.','connections','TTC_GTFS','service_frequency;economic_centre_accessibility','common network snapshot required'),
('service_frequency','Existing service frequency','Serve People','Scheduled departures per hour at agreed representative corridor stops, with a fixed weekday peak period, direction and aggregation rule.','departures/hour','TTC_GTFS','current_ridership;transfer_connections','common timetable snapshot required'),
('reliability_buffer_time','Travel-time reliability buffer','Serve People','95th-percentile minus median observed end-to-end travel time, using a common weekday period and direction.','minutes','CITY2024_MAIN','current_speed;travel_time_savings','Fall 2022 target'),
('existing_population_density','Existing population density','Strengthen Places','Population divided by land area in the common catchment; water and overlapping catchments handled consistently.','persons/km2','CENSUS_NEIGHBOURHOODS','population_coverage_2021;population','2021'),
('community_facility_count','Community facility coverage','Strengthen Places','Unique public libraries, recreation centres and health-service facilities within the common catchment; maintain separate facility-type counts before any aggregation.','facilities','SOURCE_NOT_YET_IDENTIFIED','population_coverage_2021;access_population','snapshot required'),
('approved_residential_units','Approved residential pipeline','Strengthen Places','Approved but unbuilt dwelling units within the common catchment at a fixed snapshot; deduplicate project revisions and phases.','dwelling units','DEVELOPMENT_APPLICATIONS','residential_potential;population','snapshot required'),
('approved_nonresidential_floor_area','Approved non-residential pipeline','Strengthen Places','Approved but unbuilt non-residential gross floor area within the common catchment; deduplicate amendments and phases.','m2','DEVELOPMENT_APPLICATIONS','employment_potential;employment_growth','snapshot required'),
('ksi_collision_count','Existing severe collision burden','Strengthen Places','Unique fatal or serious-injury collision events within a defined road corridor buffer over a fixed multi-year window; distinguish events from persons.','collision events','KSI_DATA','current_speed;population_coverage_2021','fixed multi-year window required'),
('employment_growth','Observed employment growth','Support Prosperity','Absolute change in jobs between two specified comparable survey years in a fixed catchment; not attributed to the proposed transit project.','jobs gained or lost','TES_SUMMARY','employment;employment_potential','two comparable years required'),
('economic_centre_accessibility','Economic-centre accessibility','Support Prosperity','Change in transit travel time or reachable employment at designated centres under a common service scenario; destination set and aggregation must be fixed before calculation.','unit pending operational definition','TTC_GTFS','access_employment;travel_time_savings','common baseline and project horizon required')]
for key,name,principle,definition,unit,source,overlap,year in supp:
    long.append(dict(indicator_id=key,indicator_name=name,primary_principle=principle,city_rtef_category='supplemental_candidate',definition=definition,unit=unit,spatial_scope='Common stop catchment or validated corridor geometry; not yet available',population_scope='Defined in the proposed operational definition',reference_year=year,measurement_period='requires_specification',value_type='proposed_derived_measure',technology_dependence='station/service scenario dependence requires control',cost_dependence='no_cost_in_proposed_definition',potential_overlap=overlap,data_availability='pending_collection',source_id=source,notes='Proposed definition, not a measure already supplied by the City attachment. Geometry, snapshot and aggregation must be documented before values can be entered.',master_column='indicator_'+key,source_locator='supplemental source; see source register',direction='higher_need' if key in ['ksi_collision_count','reliability_buffer_time'] else 'requires_policy_interpretation',city_scaling='not_applicable',admission_status='pending_evidence',definition_status='proposed_requires_operationalization',raw_source_status='pending_collection'))

def populate():
    write('data/candidate_indicator_longlist_v0.1.csv',long)
    master=[]
    base={r[0]:r[7] for r in inv[2]['rows']}
    for r in inv[2]['rows']:
        i=r[0];chain=[];b=base[i]
        while b:chain.append(b);b=base[b]
        note='Metadata transcribed from Attachment Table 2, p.7. Candidate raw values are unavailable or pending; see observations. Length is the City assumed construction length, not verified full alignment length.'
        if i==3:note+=' Length is 3 km with superscript footnote 6, reduced for existing grade-separated track.'
        if i in [11,12]:note+=' Preserve reported length; endpoint-length pairing requires independent geographic verification.'
        if i==16:note+=' Source Relative Cost is printed as 87; retained only in separate source archive, excluded from this master.'
        if chain:note+=' Benefits depend on preceding corridor scenario(s).'
        d=dict(corridor_id=i,corridor_name=r[1],endpoint_a=r[2],endpoint_b=r[3],length_km=r[5],length_basis='city_assumed_construction_length',city_assumed_technology=r[4],baseline_scenario_id='CITY_BASE_0' if not r[7] else 'CITY_BASE_AFTER_'+str(r[7]),prerequisite_corridor_ids=';'.join(map(str,chain)))
        d.update({m['master_column']:'' for m in long});d.update(source_id='CITY2024_ATTACHMENT',notes=note);master.append(d)
    write('data/corridor_master_v0.1.csv',master)
    obs=[]
    for c in master:
        for m in long:
            obs.append(dict(corridor_id=c['corridor_id'],indicator_id=m['indicator_id'],value='',value_status='not_published' if m['raw_source_status']=='not_published' else 'pending_collection',source_id=m['source_id'],source_locator=m['source_locator'],reference_year=m['reference_year'],scenario_id=c['baseline_scenario_id'] if m['technology_dependence']=='forecast service assumptions' else 'requires_verification',transformation_id='',notes='No raw corridor value was entered. '+('Published standardized score exists separately; cannot invert without scale parameters.' if m['raw_source_status']=='not_published' else 'Requires source acquisition and documented corridor/stop matching.')))
    write('data/indicator_observations_v0.1.csv',obs)
    # Archive reported scores, explicitly not a raw-input master.
    scores=[]
    for r in inv[7]['rows']:
        scores.append(dict(table_number=r[0],pdf_page=r[1],corridor_id=r[2],field_id=r[3],reported_value='' if r[4] is None else r[4],printed_token=r[5],value_type='published_score_or_quintile',source_id='CITY2024_ATTACHMENT',part1_usage='not_admitted; raw evidence review required',notes='N/A is not zero. Source scores have not been recalculated.'))
    write('evidence/city_2024_published_scores_NOT_RAW_v0.1.csv',scores)
    summaries=[]
    for m in long:summaries.append(dict(indicator_id=m['indicator_id'],nonmissing_corridors=0,missing_corridors=24,status=m['raw_source_status'],next_action='Obtain unscaled corridor values and computation metadata' if m['raw_source_status']=='not_published' else 'Fix operational definition, acquire source and validate spatial/temporal match'))
    write('data/data_gap_register_v0.1.csv',summaries)
    (ROOT/'work/longlist_english.json').write_text(json.dumps(long,indent=2),encoding='utf-8')
    schema=json.loads((P/'data/schema_v0.1.json').read_text(encoding='utf-8'))
    dictionary_keys='indicator_id indicator_name primary_principle definition unit spatial_scope population_scope reference_year measurement_period value_type technology_dependence cost_dependence potential_overlap data_availability source_id source_locator master_column notes'.split()
    dictionary=[{k:m[k] for k in dictionary_keys} for m in long]
    admissions=[]
    for m in long:
        admissions.append(dict(indicator_id=m['indicator_id'],indicator_name=m['indicator_name'],primary_principle=m['primary_principle'],admission_status='pending_evidence',cost_dependence=m['cost_dependence'],raw_value_available='no',definition_clear='partial' if m['definition_status'].startswith('source') else 'proposed',unit_clear='no' if 'not specified' in m['unit'] or 'pending' in m['unit'] else 'partial',direction=m['direction'],temporal_comparability='not_established',spatial_comparability='not_established',baseline_comparability='not_established',coverage_count=0,missing_corridor_ids=';'.join(map(str,range(1,25))),potential_overlap=m['potential_overlap'],decision_reason='Retained on longlist. No final admission decision. Published Cost-scaled versions are ineligible for Part 1.',source_id=m['source_id'],reviewer='Agent A',review_date='2026-11-21',notes='No model run. Need comparable raw values across all 24 alternatives before quantitative review.'))
    (P/'data/workbook_records_v0.1.json').write_text(json.dumps(dict(data_dictionary=dictionary,indicator_admission=admissions),indent=2),encoding='utf-8')
    sources=[
    ('CITY2024_ATTACHMENT','Prioritization of Higher-Order Transit: Corridor Evaluation Procedure','City of Toronto','2024-02-12','https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243172.pdf','reviewed_pdf','Tables 1-8; PDF pp.1-13','24 candidate corridors','Reviewed and extracted. Detailed tables publish scores, not raw quantities.'),
    ('CITY2024_MAIN','Prioritization of Planned Higher-Order Transit Projects','City of Toronto','2024-02-12','https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243162.pdf','reviewed_pdf','Figures 9-13 pp.16-18; Figures 16-17 p.21; corridor tables pp.24-25','Context and definitions','Relevant text reviewed. Maps use bands; no exact corridor values inferred. Recent immigrants include non-permanent residents.'),
    ('CENSUS_NEIGHBOURHOODS','Neighbourhood Profiles','City of Toronto','','https://open.toronto.ca/dataset/neighbourhood-profiles/','source_prospect','2021 Census resources','Neighbourhoods, not corridor catchments','Landing page located; underlying resources not acquired. Neighbourhood totals cannot be assigned directly to 500 m stop buffers; finer census geography is needed.'),
    ('TES_SUMMARY','Toronto Employment Survey Summary Tables','City of Toronto','','https://open.toronto.ca/dataset/toronto-employment-survey-summary-tables/','source_prospect','Survey summary tables','Published aggregation areas','Landing page located. Availability of consistent small-area 2021 data not verified; cannot allocate summary totals to corridors without a method.'),
    ('TTC_GTFS','TTC Routes and Schedules','TTC / City of Toronto','','https://open.toronto.ca/dataset/ttc-routes-and-schedules/','source_prospect','GTFS resources','Existing transit network','Landing page located. Archived snapshot and planned stop geometry still needed. Existing stops are not the approved future station set.'),
    ('DEVELOPMENT_APPLICATIONS','Development Applications','City of Toronto','','https://open.toronto.ca/dataset/development-applications/','source_prospect','Application records','Development projects','Catalogue identified. Status fields, units, snapshot, deduplication and geocoding require verification; no corridor count extracted.'),
    ('KSI_DATA','Motor Vehicle Collisions Involving Killed or Seriously Injured Persons','City of Toronto / Toronto Police Service','','https://open.toronto.ca/dataset/motor-vehicle-collisions-involving-killed-or-seriously-injured-persons/','source_prospect','Collision event resources','Toronto road network','Catalogue identified through official metadata. Event-level deduplication, time window and corridor buffer required.'),
    ('SOURCE_NOT_YET_IDENTIFIED','Community facility and other missing operational datasets','Not yet identified','','','unidentified','Not available','Candidate data acquisition','Placeholder status only, not an evidence citation. No data claimed.'),
    ('TTC_RIDERSHIP2022','Annual streetcar boardings by route, 2022 ridership section','Toronto Transit Commission','','https://pw.ttc.ca/-/media/Project/TTC/DevProto/Documents/Home/Transparency-and-accountability/2022-Ridership-Section-Update.pdf','source_prospect','Annual route-level ridership tables','Whole TTC routes','Official search result located. Annual route boardings differ from Fall 2022 corridor demand and cannot be substituted without mapping and period reconciliation.')]
    sr=[]
    for sid,title,pub,date,url,typ,loc,scope,note in sources:sr.append(dict(source_id=sid,title=title,publisher=pub,publication_date=date,retrieval_date='2026-11-21',url=url,source_type=typ,source_locator=loc,scope=scope,notes=note))
    write('data/source_log_v0.1.csv',sr)
    archive=P/'evidence/source_documents';archive.mkdir(exist_ok=True)
    for name in ['city_2024_corridor_evaluation.pdf','city_2024_main_report.pdf']:shutil.copy2(ROOT/'work'/name,archive/name)
    hashes=[dict(filename=x.name,sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in archive.glob('*.pdf')]
    write('evidence/source_document_checksums.csv',hashes)
    print('Wrote 24 corridor rows, 42 candidates and 1008 explicit missing observations. No values imputed.')
if __name__=='__main__':populate()

