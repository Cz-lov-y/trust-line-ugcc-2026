from pathlib import Path
import csv,json,sys,importlib.metadata as m
root=Path(__file__).resolve().parent.parent
p=root/'outputs/project'
print('PYTHON',sys.executable,sys.version)
for f in sorted(p.rglob('*.csv')):
    rows=list(csv.DictReader(f.open(encoding='utf-8-sig')))
    print('CSV',f.relative_to(p).as_posix(),len(rows))
rows=list(csv.DictReader((p/'data/corridor_master_v0.1.csv').open(encoding='utf-8-sig')))
print('CORRIDORS')
for r in rows:
    print(' | '.join(r[k] for k in ['corridor_id','corridor_name','endpoint_a','endpoint_b','length_km','prerequisite_corridor_ids']))
x=json.loads((p/'data/workbook_records_v0.1.json').read_text(encoding='utf-8'))
print('PPI',json.dumps([r for k,v in x.items() for r in v if r.get('indicator_id')=='priority_populations_index'],indent=2))
print('GIS_DEPENDENCIES',[(d.metadata['Name'],d.version) for d in m.distributions(path=[str(root/'work/gis_pydeps')])])
import subprocess
case=Path(r'C:\Users\pipis\OneDrive\桌面\ugcc\STAT Case UGCC 2026.pdf')
target=root/'work/stat_case_handoff_reference.txt'
subprocess.run(['pdftotext','-layout',str(case),str(target)],check=True)
print('CASE_PAGES',len([p for p in target.read_text(encoding='utf-8').split('\f') if p.strip()]))
