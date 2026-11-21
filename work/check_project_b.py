from pathlib import Path
import csv, json, shutil, sys, tempfile
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent.parent/'outputs/project'
sys.path.insert(0,str(root/'code'))
from validate_data import validate

def save(path,fields,rows):
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

base=validate(root)
assert base['valid_structure'] and not base['model_ready']
with tempfile.TemporaryDirectory(prefix='trust_line_validation_') as tmp:
 p=Path(tmp);shutil.copytree(root/'data',p/'data')
 master=p/'data/corridor_master_v0.1.csv'
 with master.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
 save(master,fields,rows[:-1]);assert not validate(p)['valid_structure']
 save(master,fields,rows[:-1]+[rows[0]]);assert not validate(p)['valid_structure']
 original=rows[0]['source_id'];rows[0]['source_id']='NONEXISTENT_SOURCE';save(master,fields,rows)
 assert any('Unknown master source' in e for e in validate(p)['errors'])
 rows[0]['source_id']=original;save(master,fields,rows)
 obs=p/'data/indicator_observations_v0.1.csv'
 with obs.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f);of=reader.fieldnames;orr=list(reader)
 orr[0]['value']='123';save(obs,of,orr)
 assert any('disagreement' in e for e in validate(p)['errors'])
 orr[0]['value']='';save(obs,of,orr)
 f=p/'data/workbook_records_v0.1.json';records=json.loads(f.read_text())
 records['indicator_admission'][1]['admission_status']='admitted';f.write_text(json.dumps(records))
 assert any('cost dependence' in e for e in validate(p)['errors'])
print('Checks passed: baseline valid/not ready; deleted and duplicate IDs rejected; unknown provenance rejected; observation mismatch rejected; cost-dependent admission rejected.')
