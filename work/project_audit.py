from pathlib import Path
import csv,json,html,re
P=Path(__file__).resolve().parent.parent/'outputs/project'
def read(name):
 with (P/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def tab(rows,cols):
 e=lambda v:html.escape(str(v))
 return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+e(c.replace('_',' '))+'</th>' for c in cols)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(r.get(c,''))+'</td>' for c in cols)+'</tr>' for r in rows)+'</tbody></table></div>'
issues=[
 {'issue':'Raw-value availability','finding':'The 13-page attachment does not publish the unscaled 24-corridor indicator matrix. All 42 candidate raw columns remain blank. This is an evidence inventory, not a complete modelling dataset.','action':'Acquire the underlying model outputs or reconstruct comparable measures with documented methods.'},
 {'issue':'Cost contamination','finding':'Ten general measures are Cost-scaled before standardization. Multiplying z-scores by relative cost cannot recover raw benefits.','action':'Retain the benefit concepts but exclude the published cost-scaled versions from Part 1.'},
 {'issue':'Construction length','finding':'ID 3 is 3 km with footnote 6, reduced for existing infrastructure. IDs 11 and 12 retain the original lengths pending geographic verification.','action':'Do not interpret the master length as verified full alignment length. Keep length_basis.'},
 {'issue':'Source anomaly','finding':'ID 16 Relative Cost is printed as 87. No silent correction was made.','action':'Cost is excluded from the raw master and preserved as a documented source issue.'},
 {'issue':'Baseline dependency','finding':'Eight alternatives depend on other evaluated corridors. Transitive dependencies are retained.','action':'Resolve standalone versus extension benefit comparability before modelling.'},
 {'issue':'Forecast horizon','finding':'Several indicators refer to 2051, whereas the case requires operation by 2035.','action':'Keep original years; do not relabel forecasts.'},
 {'issue':'Equity definitions','finding':'Main report p.16 identifies LIM-AT and Census visible-minority concept; p.17 recent immigrants includes 2016-2021 arrivals and non-permanent residents; p.18 long commute is one hour or more.','action':'Use the actual source populations. Preserve differences between household and person measures.'},
 {'issue':'Equity ratios','finding':'Table 8 contains standardized scores, not the original Palma ratios. The complete transformation formula is not supplied.','action':'Do not apply a threshold of 1 to standardized scores or infer group counts.'},
 {'issue':'Maps and route data','finding':'Main report p.21 uses mapped ridership/speed bands. External TTC annual route boardings are not equivalent to segment demand in Fall 2022.','action':'No midpoint substitutions or whole-route totals were assigned to candidate segments.'},
 {'issue':'Geometry and facilities','finding':'Endpoints alone do not specify an exact alignment or future station set. Supplementary indicators need catchment definitions.','action':'Record line geometry, stop set, buffer union, source geography and reference date before spatial aggregation.'},
 {'issue':'Principle assignment','finding':'The candidate longlist uses the requested user-facing principles; the City RTEF category is retained separately.','action':'Do not present the candidate grouping as an unchanged City hierarchy.'},
 {'issue':'Pending admission','finding':'All 42 candidate concepts remain pending evidence. A longlist is not a selection of 42 model criteria.','action':'Later review should address redundancy, coverage and policy meaning; no weighting performed.'}]
with (P/'data/review_issues_v0.1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(issues[0]));w.writeheader();w.writerows(issues)
head='''<!doctype html><html lang="en"><meta charset="utf-8"><title>TRUST-Line Evidence Inventory v0.1</title><style>body{font:16px/1.6 Arial,sans-serif;color:#1c3448;max-width:1500px;margin:35px auto;padding:0 24px}h1{font-size:29px}h2{font-size:22px;margin-top:32px}.notice{background:#fff2d8;padding:18px;border-left:5px solid #ba7b1c}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #dae2e8;vertical-align:top;text-align:left}th{background:#223d54;color:white}tr:nth-child(even){background:#f1f5f8}.scroll{overflow:auto}a{color:#1b609d}</style><h1>TRUST-Line Evidence Inventory v0.1</h1><p>Source review and candidate registration. No model, ranking, imputation or simulation was run.</p><div class="notice"><strong>Status: structurally populated, raw evidence incomplete.</strong><br>24 corridor records; 42 candidate indicators; 1,008 unresolved raw observations. 720 refer to raw measures not published in the City attachment; 288 require supplemental collection. The published scores are archived separately and never substituted for raw measurements.</div><p><a href="../data/corridor_master_v0.1.csv">Corridor master</a> | <a href="../data/data_dictionary_v0.1.xlsx">Data dictionary</a> | <a href="../data/indicator_admission_v0.1.xlsx">Admission review</a> | <a href="../data/source_log_v0.1.csv">Source register</a></p>'''
sections=[('Candidate indicator longlist',read('data/candidate_indicator_longlist_v0.1.csv'),['indicator_id','indicator_name','primary_principle','definition','unit','cost_dependence','potential_overlap','data_availability']),('City 2024 index: no corridor values',read('data/city_2024_indicator_index_v0.1.csv'),['indicator_name','definition_page','value_table','value_page','underlying_value_type','published_value_type','unit','cost_dependence']),('Fixed corridor inventory',read('data/corridor_master_v0.1.csv'),['corridor_id','corridor_name','endpoint_a','endpoint_b','length_km','length_basis','baseline_scenario_id','prerequisite_corridor_ids','notes']),('Review findings',issues,['issue','finding','action']),('Source register',read('data/source_log_v0.1.csv'),['source_id','title','source_type','source_locator','notes'])]
out=head+''.join('<h2>'+title+'</h2>'+tab(rows,cols) for title,rows,cols in sections)+'</html>'
(P/'outputs/inventory_review_v0.1.html').write_text(out,encoding='utf-8')
schema=json.loads((P/'data/schema_v0.1.json').read_text())
schema['corridor_master']=list(read('data/corridor_master_v0.1.csv')[0])
schema['candidate_indicator_longlist']=list(read('data/candidate_indicator_longlist_v0.1.csv')[0])
schema['indicator_prefix']='indicator_'
(P/'data/schema_v0.1.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
bad=[]
for p in P.rglob('*'):
 if p.is_file() and p.suffix in ['.csv','.json','.py','.mjs','.md','.html']:
  if re.search('[\u4e00-\u9fff]',p.read_text(encoding='utf-8-sig')):bad.append(str(p.relative_to(P)))
print('English-content audit:',bad or 'no Chinese text in project text files')
