from pathlib import Path
import csv,json,html,zipfile,re
R=Path(__file__).resolve().parent.parent;P=R/'outputs/project'
def read(f):
 with (P/f).open(encoding='utf-8-sig',newline='') as s:return list(csv.DictReader(s))
e=lambda x:html.escape(str(x))
def table(rows,cols):return '<table><tr>'+''.join('<th>'+e(k)+'</th>' for k in cols)+'</tr>'+''.join('<tr>'+''.join('<td>'+e(r.get(k,'') or 'Unavailable')+'</td>' for k in cols)+'</tr>' for r in rows)+'</table>'
coverage=read('data/model_input_coverage_v0.1.csv');scores=read('data/city_standardized_scores_v0.1.csv');v=json.loads((P/'outputs/validation_v0.1.json').read_text())
page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Model input review</title><style>body{font:15px/1.6 Arial;color:#203b51;margin:30px auto;max-width:1450px;padding:20px}table{border-collapse:collapse;width:100%;margin-bottom:24px}th{background:#203b51;color:white}td,th{padding:9px;border-bottom:1px solid #d9e2e9;text-align:left}tr:nth-child(even){background:#f0f4f8}.status{padding:18px;background:#fff1cf}</style><h1>Model input review v0.1</h1><p class="status">City non-cost-scaled score strategy adopted. All 24 corridors retained. Structure valid; MODEL READY: FALSE. There are 98 unchanged City scores, 22 source missing values and no computed corridor-level Priority Populations Index. No imputation or ranking performed.</p><h2>Coverage and admission</h2>'''
page+=table(coverage,list(coverage[0]))+'<h2>Published City score values</h2>'+table(scores,['corridor_id','current_speed','unimproved_load','current_max_load','current_ridership','competitiveness'])
page+='<h2>Priority Populations Index</h2><p>Proposed formula: sum(P_it * I_t) / sum(P_it). Exact tract index values and catchment population estimates are required. These have not been acquired or calculated. No values have been entered. The full TEOZ index must not be substituted.</p><h2>Validation blockers</h2><ul>'+''.join('<li>'+e(x)+'</li>' for x in v['readiness_issues'])+'</ul></html>'
(P/'outputs/model_input_review_v0.1.html').write_text(page,encoding='utf-8')
for p in P.rglob('*'):
 if p.is_file() and p.suffix in ['.csv','.json','.py','.mjs','.md','.html']:assert not re.search('[\u4e00-\u9fff]',p.read_text(encoding='utf-8-sig')),p
(P/'outputs/delivery_checks_v0.1.json').write_text(json.dumps(dict(language_audit='passed',corridor_count=24,candidate_count=43,selected_inputs=6,published_city_score_count=98,missing_city_score_count=22,ppi_values_computed=0,model_ready=False),indent=2),encoding='utf-8')
# Retain the previous overview as a clearly labelled historical snapshot.
old=P/'outputs/inventory_review_v0.1.html'
txt=old.read_text(encoding='utf-8')
if 'PRE-STRATEGY SNAPSHOT' not in txt:old.write_text(txt.replace('<h1>','<p><strong>PRE-STRATEGY SNAPSHOT:</strong> See <a href="model_input_review_v0.1.html">current model input review</a> for updated selection, counts and readiness.</p><h1>',1),encoding='utf-8')
with zipfile.ZipFile(R/'outputs/TRUST_Line_project_v0.1.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in P.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.inspect.ndjson'):z.write(p,Path('project')/p.relative_to(P))
 for d in ['slides','outputs']:z.writestr('project/'+d+'/',b'')
print('Updated English review, checks and project archive.')
