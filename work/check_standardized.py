from pathlib import Path
import sys,tempfile,shutil,json,csv
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'outputs/project'
sys.path.insert(0,str(P/'code'))
from validate_data import validate

def save(p,rows):
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

with tempfile.TemporaryDirectory(prefix='trust_line_standardized_') as tmp:
 p=Path(tmp)/'project';shutil.copytree(P,p,ignore=shutil.ignore_patterns('__pycache__','*.inspect.ndjson'))
 records_path=p/'data/workbook_records_v0.1.json'
 original=json.loads(records_path.read_text())
 cfg=p/'data/model_input_selection_v0.1.json'
 cfg.write_text(json.dumps({'selected_indicator_ids':['unimproved_load']}))
 fixture=json.loads(json.dumps(original));a=next(a for a in fixture['indicator_admission'] if a['indicator_id']=='unimproved_load')
 a.update(admission_status='admitted',definition_clear='confirmed',unit_clear='confirmed',temporal_comparability='confirmed',spatial_comparability='confirmed',baseline_comparability='confirmed')
 records_path.write_text(json.dumps(fixture))
 assert validate(p)['model_ready'],validate(p)
 a['cost_dependence']='cost_scaled';records_path.write_text(json.dumps(fixture))
 assert any('cost dependence' in e for e in validate(p)['errors'])
 a['cost_dependence']='no';a['coverage_count']=23;records_path.write_text(json.dumps(fixture))
 assert any('coverage' in e for e in validate(p)['errors'])
 records_path.write_text(json.dumps(original));cfg.write_text(json.dumps({'selected_indicator_ids':['current_speed']}))
 scores_path=p/'data/city_standardized_scores_v0.1.csv';scores=read(scores_path)
 # Report N/A cannot be hidden by invented zero values.
 blank=next(r for r in scores if r['current_speed']=='');blank['current_speed']='0'
 save(scores_path,scores)
 assert any('differs from source' in e for e in validate(p)['errors'])
 save(scores_path,scores[:-1]);assert any('24 unique' in e for e in validate(p)['errors'])
 # The real project is neither admitted nor complete.
 assert validate(P)['valid_structure'] and not validate(P)['model_ready']
print('Passed: valid standardized-score routing, cost exclusion, coverage integrity, source missingness integrity, 24-ID retention, real-project readiness gate.')
