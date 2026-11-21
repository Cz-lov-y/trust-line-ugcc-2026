"""Build the handoff catalogue only; do not mutate model inputs or admission records."""
from pathlib import Path
import csv,json,hashlib,zipfile

ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'outputs/project'
DOC=P/'HANDOFF_v0.1.md'
CAT=P/'outputs/handoff_file_inventory_v0.1.csv'
PURPOSE={
'README.md':('Current data strategy, authority, validation commands and pilot pointer','Current; read before editing'),
'HANDOFF_v0.1.md':('Complete structured successor-assistant handoff','Current handoff; generated catalogue appended'),
'data/acquisition_log_v0.1.csv':('Five acquisition attempts/prospects and evidence gaps','Historical acquisition notes; supplement for new downloads'),
'data/candidate_indicator_longlist_v0.1.csv':('43 candidate indicator concepts and provenance/interpretation','Longlist, not admitted model criteria'),
'data/city_2024_indicator_index_v0.1.csv':('30 City indicator definitions, table/page references, units, direction, cost and overlap','Index only; not corridor observations'),
'data/city_standardized_scores_v0.1.csv':('Separate 24-row matrix of five non-cost City processed score columns','98 values; 22 source blanks; no imputation'),
'data/corridor_geometry_review_v0.1.csv':('24-row alignment, endpoint, length, station/catchment review','ID 1 road proxy only; IDs 2-24 not digitized'),
'data/corridor_master_v0.1.csv':('24 eligible corridor metadata records and 43 raw indicator placeholders','1032 raw blanks; no processed City scores in indicator_*'),
'data/data_dictionary_v0.1.xlsx':('Generated indicator dictionary workbook','Review view; JSON is authoritative'),
'data/data_dictionary_v0.1.xlsx.inspect.ndjson':('Dictionary workbook inspection dump','Generated inspection artifact; not authoritative'),
'data/data_gap_register_v0.1.csv':('43 raw-indicator acquisition gaps','Raw gaps; do not confuse with processed-score coverage'),
'data/indicator_admission_v0.1.xlsx':('Generated indicator admission review workbook','No indicators admitted; edit JSON then regenerate'),
'data/indicator_admission_v0.1.xlsx.inspect.ndjson':('Admission workbook inspection dump','Generated inspection artifact; not authoritative'),
'data/indicator_observations_v0.1.csv':('24 x 43 raw observation/status/source grid','1032 blank values with statuses; synchronized with raw master'),
'data/model_input_coverage_v0.1.csv':('Measured coverage/missing IDs for six selected input candidates','Current 17/24/20/20/17/0 coverage'),
'data/model_input_selection_v0.1.json':('Selected six IDs, processed strategy, no-cost/no-imputation configuration','Authoritative intended model-input selection'),
'data/review_issues_v0.1.csv':('12 source/methodological findings','Historical references to 42 candidates are stale; now 43'),
'data/schema_v0.1.json':('Column schemas for datasets, dictionary/admission workbooks and templates','Current schema; update deliberately with records/code'),
'data/source_log_v0.1.csv':('12 source IDs, URLs, locators and acquisition/prospect distinctions','Current register includes official City centreline'),
'data/supplemental_model_inputs_v0.1.csv':('Separate 24-row derived PPI model-input file','All 24 PPI values blank; not computed'),
'data/workbook_records_v0.1.json':('Authoritative dictionary and admission records read by validator/workbook builder','Edit here for admission; XLSX-only edits are ineffective'),
'evidence/city_2024_published_scores_NOT_RAW_v0.1.csv':('1248 long-form City published score/archive records including excluded fields','Preserve as evidence; cost-bearing fields not model inputs'),
'evidence/part2_sources_v0.1.csv':('Part 2 source evidence template','Header only; no data'),
'evidence/source_document_checksums.csv':('Checksums for two archived City source PDFs','Source-integrity record'),
'evidence/tech_evidence_v0.1.csv':('Part 2 technology evidence template','Header only; no estimates'),
'evidence/source_documents/city_2024_corridor_evaluation.pdf':('Official City 2024 13-page evaluation attachment','Archived source; main definition/table page references use this sequence'),
'evidence/source_documents/city_2024_main_report.pdf':('Official City 2024 context/definitions report','Archived source; separate page sequence'),
'evidence/gis/centreline_metadata.json':('City ArcGIS layer schema and metadata snapshot','Archived current road service metadata, not a 2024 alignment'),
'evidence/gis/sheppard_roads.geojson':('284 queried Sheppard/Yonge road features used by pilot graph','Archived input; pilot selects 33 named Sheppard segments'),
'evidence/gis/sheppard_background.geojson':('Bounded official road background features for static map','Archived offline map context'),
'evidence/gis/sheppard_overpass_query.txt':('OSM Overpass query attempted for Sheppard geometry','Query text only; no OSM geometry acquired'),
'code/build_workbooks.mjs':('Generate dictionary/admission XLSX files from JSON/schema and preview renders','Requires current Codex artifact-tool Node dependencies'),
'code/build_sheppard_pilot.py':('Rebuild pilot GeoJSON, map, HTML and numerical summary from archived road inputs','Successfully rerun; no census overlay/PPI; no QGZ generation'),
'code/requirements_gis.txt':('GIS pilot dependency minimum versions','Not an exact lockfile; runtime environments remain separate'),
'code/simulation_template.py':('Fixed-24 simulation callback interface and metadata safeguards','Template only; no uncertainty model or processed-input adapter'),
'code/validate_data.py':('Validate schema, fixed 24 IDs, missingness, cost/admission/input mapping and archive agreement','Standard-library script; true structure, false readiness'),
'code/__pycache__/validate_data.cpython-312.pyc':('Python-generated validator bytecode','Disposable cache; excluded from ZIP'),
'outputs/delivery_checks_v0.1.json':('Earlier delivery/language/count audit snapshot','98 City scores, zero PPI, model_ready false; not a full GIS/handoff audit'),
'outputs/inventory_review_v0.1.html':('Initial evidence-inventory review page','Historical pre-strategy snapshot; not current readiness authority'),
'outputs/model_input_review_v0.1.html':('Processed-input strategy/coverage review page','Current input review; no model results'),
'outputs/validation_v0.1.json':('Latest validator result','valid_structure true, model_ready false; no errors/warnings'),
'outputs/handoff_file_inventory_v0.1.csv':('Machine-readable file purposes, status, sizes, row counts and checksums','Handoff snapshot; excludes its own row/checksum'),
'outputs/sheppard_west_pilot/README.md':('Pilot source, method, measurements, setup, rebuild and limitations','Current pilot explanation'),
'outputs/sheppard_west_pilot/corridor_01_boundary_pilot.png':('English static boundary map','Visually checked; offline background is official City roads'),
'outputs/sheppard_west_pilot/corridor_01_boundary_pilot.svg':('Vector version of static boundary map','Exported from same plot'),
'outputs/sheppard_west_pilot/corridor_01_buffer_500m.geojson':('500 m round-cap corridor proximity polygon','Valid; 5.192196 km2; EPSG:4326 export'),
'outputs/sheppard_west_pilot/corridor_01_centerline.geojson':('Joined official road-centreline proxy','4.407067 km; not approved transit alignment'),
'outputs/sheppard_west_pilot/corridor_01_endpoints.geojson':('Two road-junction endpoint proxies','Not exact station/platform centres'),
'outputs/sheppard_west_pilot/corridor_01_interactive_map.html':('Interactive geometry viewer with OSM background tiles','Needs network for external libraries/tiles; not an OSM centreline download'),
'outputs/sheppard_west_pilot/corridor_01_pilot.qgz':('Styled QGIS project, three relative-path GeoJSON layers','Opened successfully; no census/PPI layers'),
'outputs/sheppard_west_pilot/pilot_summary.json':('Exact length, buffer area, source segment IDs, CRS and limitations','ready_for_final_population_estimation false'),
'outputs/sheppard_west_pilot/qgis_setup_status.json':('Software/provider/GUI/network verification record','12 algorithms loaded; no successful OSM query'),
'outputs/sheppard_west_pilot/source_centerline_segments.geojson':('33 original City centreline features with source IDs','Preserved pilot source subset')
}
WORK_PURPOSE={
'scaffold_b.py':'Historical Agent B scaffolding; do not rerun blindly',
'fill_project.py':'Historical data/record population generator; may overwrite current data',
'build_inventory.py':'Earlier City inventory extraction/generation helper',
'build_inventory.mjs':'Earlier inventory workbook generator',
'finalize_project.py':'Historical project documentation/packaging generator',
'adopt_standardized.py':'Migration to separate processed City score inputs; historical state writer',
'finish_standardized.py':'Historical standardized-strategy delivery updater; may overwrite outputs',
'check_standardized.py':'Processed-score consistency/admission spot checks',
'check_project_b.py':'Earlier scaffolding consistency check',
'project_audit.py':'Earlier file/language/schema audit helper',
'prepare_gis.py':'QGIS/plugin acquisition setup helper',
'extract_qgis.py':'MSI cabinet/manifest extraction helper; expensive historical setup',
'get_sheppard.py':'City road acquisition helper',
'fetch_osm.py':'Overpass acquisition attempts; failed HTTP 406',
'build_sheppard_pilot.py':'Original workspace pilot script; canonical reusable copy is in project/code',
'qgis_finish.py':'PyQGIS project builder/provider check; overwrites project/setup status',
'qgis_local_setup.cmd':'Generate local QGIS runtime environment via --postinstall',
'finalize_gis_pilot.py':'Pilot docs/archive updater; copies older script into project/code; review before reuse',
'audit_handoff.py':'Read-only dataset/environment audit and local case text extraction',
'build_handoff_catalogue.py':'Build handoff appendices/file inventory and refresh ZIP; no model-input edits',
'qgis_file_manifest.json':'37270-file installer reconstruction manifest; vendor paths indexed here',
'QGIS-OSGeo4W-3.44.15-2.msi':'Official signed installer; normal installation failed',
'qgis_application.cab':'Application cabinet extracted from official MSI',
'QuickOSM-2.6.0.zip':'Official plugin file archive used for workspace profile',
'stat_case_handoff_reference.txt':'Local case text extraction for requirement/page verification',
'qgis_install.log':'Windows Installer failure evidence',
'qgis_expand.log':'Vendor cabinet extraction log',
'qgis_gui_error.log':'GUI-launch diagnostic log',
'qgis_gui_out.log':'GUI-launch diagnostic log',
'inventory_data.json':'Historical inventory/workbook generation intermediate',
'longlist_english.json':'English candidate-longlist intermediate'
}

def csv_count(path):
    if path.suffix.lower()!='.csv':return ''
    try:
        with path.open(encoding='utf-8-sig',newline='') as f:return len(list(csv.DictReader(f)))
    except Exception:return 'unreadable'

def metadata(path,scope,purpose,status):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return dict(path=path.relative_to(ROOT).as_posix(),scope=scope,bytes=path.stat().st_size,csv_data_rows=csv_count(path),purpose=purpose,status=status,sha256=h.hexdigest())

files=sorted(f for f in P.rglob('*') if f.is_file() and f!=CAT)
unknown=[f.relative_to(P).as_posix() for f in files if f.relative_to(P).as_posix() not in PURPOSE]
if unknown:raise RuntimeError('Missing catalogue descriptions: '+str(unknown))

lines=['\n### Appendix A. Canonical project file tree\n','```text','project/']
def tree(folder,prefix=''):
    children=sorted(folder.iterdir(),key=lambda p:(not p.is_dir(),p.name.lower()))
    for i,ch in enumerate(children):
        last=i==len(children)-1
        lines.append(prefix+('`-- ' if last else '|-- ')+ch.name+('/' if ch.is_dir() else ''))
        if ch.is_dir():tree(ch,prefix+('    ' if last else '|   '))
tree(P)
if not CAT.exists():lines.append('    [handoff_file_inventory_v0.1.csv is generated in outputs by this handoff]')
lines+=['```','\n`slides/` exists and is empty. The Python bytecode cache is disposable and excluded from the delivery ZIP.\n','### Appendix B. Canonical file purposes and status\n','| File | Purpose | Current status |','| --- | --- | --- |']
for rel in sorted(PURPOSE):
    purpose,status=PURPOSE[rel]
    lines.append(f'| `{rel}` | {purpose} | {status} |')

lines+=['\n### Appendix C. Outer delivery folder and historical copies\n','| Workspace-relative path | Meaning and status |','| --- | --- |']
outer=[]
for path in sorted((ROOT/'outputs').iterdir()):
    if path==P:continue
    rel=path.relative_to(ROOT).as_posix()
    if path.is_dir():
        desc='Older extracted project copy; not the working project'
    elif path.name=='TRUST_Line_project_v0.1.zip':
        desc='Current delivery archive, refreshed with this handoff; excludes work/runtime and bytecode'
    elif path.name=='Open_Sheppard_West_QGIS.cmd':
        desc='Local runtime/profile/project launcher; requires adjacent workspace work directory'
    else:desc='Earlier standalone inventory export; historical, not current model-input authority'
    lines.append(f'| `{rel}` | {desc} |')
    if path.is_file() and path.suffix!='.zip':outer.append((path,desc))

lines+=['\n### Appendix D. Workspace setup and historical helper files\n','These are outside the portable project ZIP. They are not a second data authority. Older generation helpers can overwrite newer files.\n','| Workspace-relative file | Role/status |','| --- | --- |']
workfiles=sorted(f for f in (ROOT/'work').iterdir() if f.is_file())
for f in workfiles:
    desc=WORK_PURPOSE.get(f.name)
    if desc is None:
        if f.suffix in {'.png','.ndjson'}:desc='Historical source render, workbook preview or inspection dump; diagnostic only'
        elif f.suffix=='.geojson':desc='GIS source/query intermediate; canonical pilot evidence subset is archived in project/evidence/gis'
        elif f.suffix=='.pdf':desc='Working source PDF copy; canonical City copies are under project/evidence/source_documents'
        elif f.suffix in {'.txt','.html'}:desc='Source extraction/page/query intermediate; not a model-input dataset'
        else:desc='Workspace acquisition/setup intermediate; inspect before reuse'
    WORK_PURPOSE[f.name]=desc
    lines.append(f'| `work/{f.name}` | {desc} |')
lines+=['\nDependency directories (vendor files grouped, not individually described):\n','- `work/tools/QGIS/`: reconstructed local QGIS runtime; `work/qgis_file_manifest.json` indexes installer files.','- `work/gis_pydeps/`: separate pip target, including Shapely/pyproj/folium/NumPy and dependencies.','- `work/qgis_profiles/`: QGIS settings and installed QuickOSM package; runtime caches and user-profile state are mutable.','- Other `work` extraction/cache directories, if present, are setup intermediates rather than project evidence.','\n### Appendix E. All 24 corridor identities\n','Lengths are the City source assumptions from the master, not all GIS-verified full alignment lengths. Prerequisites are source scenario metadata, not permission to drop alternatives.\n','| ID | Corridor | Endpoint A | Endpoint B | Source length (km) | Prerequisite IDs |','| ---: | --- | --- | --- | ---: | --- |']
with (P/'data/corridor_master_v0.1.csv').open(encoding='utf-8-sig',newline='') as f:
    for row in csv.DictReader(f):
        lines.append('| '+' | '.join(row[k] or 'None' for k in ['corridor_id','corridor_name','endpoint_a','endpoint_b','length_km','prerequisite_corridor_ids'])+' |')
lines+=['\n### Appendix F. City source page map\n','| Source | Reference locations |','| --- | --- |','| `CITY2024_ATTACHMENT` | 13-page attachment: equity method p.3; definitions/scaling Table 1 p.6; 24-corridor list p.7; detailed scores pp.11-13 (Tables 6-8). |','| `CITY2024_MAIN` | Equity definitions/figures pp.16-18; operational map bands p.21; corridor tables pp.24-25. Separate PDF sequence. |','| `CITY2024_PRIORITY_MAP` | One-page May 2024 priority-populations map/prospect; exact tract index values and complete construction not acquired. |','\nSource URLs and notes are in `data/source_log_v0.1.csv`. Do not reverse cost-scaled z-scores into raw values without the original scaling/standardization parameters. The source anomaly where corridor 16 Relative Cost is printed as 87 was preserved as evidence, not silently corrected; cost remains excluded from Part 1.\n']

prefix=DOC.read_text(encoding='utf-8').split('<!-- GENERATED_CATALOGUE -->')[0]
DOC.write_text(prefix+'<!-- GENERATED_CATALOGUE -->\n'+'\n'.join(lines)+'\n',encoding='utf-8')

records=[]
for f in files:
    rel=f.relative_to(P).as_posix()
    records.append(metadata(f,'canonical_project',*PURPOSE[rel]))
for f,desc in outer:
    records.append(metadata(f,'outer_delivery_or_legacy',desc,'See handoff; not the canonical project data directory'))
old=ROOT/'outputs/TRUST_Line_project_v0.1'
if old.exists():
    for f in sorted(old.rglob('*')):
        if f.is_file():records.append(metadata(f,'legacy_extracted_copy','Historical extracted project artifact','Not current; edit canonical outputs/project instead'))
for f in workfiles:
    records.append(metadata(f,'workspace_intermediate',WORK_PURPOSE[f.name],'Outside portable project; inspect before reuse'))
with CAT.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['path','scope','bytes','csv_data_rows','purpose','status','sha256'])
    writer.writeheader();writer.writerows(records)

# Repackage only canonical project deliverables; leave the historical extracted copy alone.
with zipfile.ZipFile(ROOT/'outputs/TRUST_Line_project_v0.1.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(P.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts:z.write(f,f.relative_to(P.parent))
print(json.dumps({'handoff':str(DOC),'inventory_rows':len(records),'canonical_file_count':len(files)+1,'zip_refreshed':True,'model_inputs_modified':False},indent=2))
