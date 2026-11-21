from pathlib import Path
import csv,json,re,zipfile,hashlib

ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'outputs/project'
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

master=read(P/'data/corridor_master_v0.1.csv')
geometry=[]
for c in master:
    geometry.append(dict(corridor_id=c['corridor_id'],corridor_name=c['corridor_name'],endpoint_a=c['endpoint_a'],endpoint_b=c['endpoint_b'],alignment_geometry_status='not_digitized',station_set_status='not_verified',construction_length_km=c['length_km'],full_alignment_length_km='',coordinate_reference_system='',geometry_source_id='',catchment_status='not_defined',next_action='Verify the original alignment and endpoints; document a stop set or a corridor-buffer definition before spatial aggregation.',notes='Construction length cannot substitute for full alignment geometry. Preserve all 24 alternatives.'))
write(P/'data/corridor_geometry_review_v0.1.csv',geometry)

acquisition=[
dict(acquisition_id='ACQ01',indicator_scope='City attachment raw indicators',source_id='CITY2024_ATTACHMENT',status='raw_matrix_not_located',last_checked='2026-11-21',evidence='Attachment Tables 6-8 publish processed scores. Public search did not locate a downloadable unscaled 24-corridor matrix.',required_input='Unscaled quantities; scaling means and standard deviations; direction transforms; demand aggregation; baseline scenario documentation.',next_action='Search additional project appendices or obtain public model outputs. Do not claim the data do not exist or reverse scores without scale parameters.'),
dict(acquisition_id='ACQ02',indicator_scope='Population, employment and equity catchments',source_id='CENSUS_NEIGHBOURHOODS;TES_SUMMARY',status='geometry_and_finer_geography_required',last_checked='2026-11-21',evidence='Neighbourhood and summary-area data are not the same as proposed stop catchments.',required_input='Validated corridor geometry and stop set; fine census units; boundary files; appropriate allocation method.',next_action='Complete corridor_geometry_review before computing any catchment totals.'),
dict(acquisition_id='ACQ03',indicator_scope='Public open-data acquisition',source_id='CENSUS_NEIGHBOURHOODS;TTC_GTFS',status='download_attempt_failed',last_checked='2026-11-21',evidence='Shell requests to open.toronto.ca and its CKAN API host failed DNS resolution. Web extraction returned landing-page shells, not data resources.',required_input='Accessible official resource endpoint and a dated source snapshot.',next_action='Retry official resource acquisition when the endpoint is accessible. Source prospects are not acquired evidence.'),
dict(acquisition_id='ACQ04',indicator_scope='Community facilities',source_id='TPL_BRANCHES',status='official_catalogue_located',last_checked='2026-11-21',evidence='Official Library Branch General Information catalogue was opened; underlying branch records were not downloaded.',required_input='Branch coordinates and snapshot; complementary recreation and health facility sources; common catchment.',next_action='Acquire resource files and deduplicate facilities before aggregation. Library counts alone do not represent all community facilities.'),
dict(acquisition_id='ACQ05',indicator_scope='Existing transit demand and reliability',source_id='TTC_RIDERSHIP2022;CITY2024_MAIN',status='scope_mismatch_unresolved',last_checked='2026-11-21',evidence='Available route-level annual totals and map bands do not directly provide exact segment-level Fall 2022 quantities.',required_input='Segment, direction and time-period matched observations; express/local route treatment.',next_action='Do not allocate whole-route boardings or map-band midpoints to candidate corridors without a justified method.')]
write(P/'data/acquisition_log_v0.1.csv',acquisition)
sources=read(P/'data/source_log_v0.1.csv')
if not any(s['source_id']=='TPL_BRANCHES' for s in sources):
    sources.append(dict(source_id='TPL_BRANCHES',title='Library Branch General Information',publisher='Toronto Public Library / City of Toronto',publication_date='',retrieval_date='2026-11-21',url='https://open.toronto.ca/dataset/library-branch-general-information/',source_type='official_catalogue_reviewed_resource_not_acquired',source_locator='Dataset landing page',scope='Library branch facilities, not all community facilities',notes='Official catalogue opened. Resource-level records not acquired. Counts cannot be filled before catchment geometry is fixed.'))
write(P/'data/source_log_v0.1.csv',sources)
readme=P/'README.md'
content=readme.read_text(encoding='utf-8')
extra='''
## Acquisition and geometry handoff

`data/acquisition_log_v0.1.csv` records source availability, failed download attempts and exact missing inputs. A failed search or network request is not proof that a dataset does not exist.

`data/corridor_geometry_review_v0.1.csv` retains 24 geometry-review records. No alignment or future station set has been digitized or approved in this inventory. Endpoint text and construction length alone are insufficient to calculate stop catchments. Published map bands and whole-route annual ridership have not been converted into exact corridor values.

`outputs/inventory_review_v0.1.html` is the English review view. The candidate longlist, dictionary and admission records are populated; Part 2 evidence files remain header-only templates. `outputs/validation_v0.1.json` distinguishes structural validity from model readiness. The unresolved raw-value count is a limitation, not completed data entry.
'''
if '## Acquisition and geometry handoff' not in content:readme.write_text(content+extra,encoding='utf-8')

bad=[]
for p in P.rglob('*'):
    if p.is_file() and p.suffix in ['.csv','.json','.py','.mjs','.md','.html'] and re.search('[\u4e00-\u9fff]',p.read_text(encoding='utf-8-sig')):bad.append(str(p.relative_to(P)))
assert not bad,bad
for filename in ['data_dictionary_v0.1.xlsx','indicator_admission_v0.1.xlsx']:
    with zipfile.ZipFile(P/'data'/filename) as z:
        for name in z.namelist():
            if name.endswith('.xml'):assert not re.search('[\u4e00-\u9fff]',z.read(name).decode('utf-8')),(filename,name)
checks=dict(language_audit='passed: English project content',corridor_count=len(master),unique_corridor_ids=len({r['corridor_id'] for r in master}),candidate_count=len(read(P/'data/candidate_indicator_longlist_v0.1.csv')),city_index_count=len(read(P/'data/city_2024_indicator_index_v0.1.csv')),source_count=len(sources),no_scoring_or_simulation_executed=True)
(P/'outputs/delivery_checks_v0.1.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))
