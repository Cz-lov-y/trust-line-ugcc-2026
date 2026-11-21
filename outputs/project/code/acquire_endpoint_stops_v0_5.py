"""Acquire official GTFS and archive extracted stop tables with download hashes."""
import urllib.request,zipfile,io,csv,json,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
E=Path(__file__).resolve().parents[1]/'evidence/corridor_batch_v0.5'
urls={'TTC':'https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/7795b45e-e65a-4465-81fc-c36b9dfff169/resource/cfb6b2b8-6191-41e3-bda1-b175c51148cb/download/opendata_ttc_schedules.zip','GO':'https://assets.metrolinx.com/raw/upload/Documents/Metrolinx/Open%20Data/GO-GTFS.zip','UP':'https://assets.metrolinx.com/raw/upload/Documents/Metrolinx/Open%20Data/UP-GTFS.zip'}
def fetch(item):
 agency,u=item
 b=urllib.request.urlopen(u,timeout=90).read()
 z=zipfile.ZipFile(io.BytesIO(b));name=next(n for n in z.namelist() if n.endswith('stops.txt'))
 d=z.read(name); (E/f'{agency}_official_stops.csv').write_bytes(d)
 print(agency,len(b),[r for r in csv.DictReader(io.StringIO(d.decode('utf-8-sig'))) if any(x in r['stop_name'].lower() for x in ['kipling station','dundas west station','union station','unionville','pearson','humber college station'])][:30],flush=True)
 return dict(agency=agency,url=u,download_size=len(b),download_sha256=hashlib.sha256(b).hexdigest(),extracted_stops_sha256=hashlib.sha256(d).hexdigest())
with ThreadPoolExecutor(max_workers=3) as p:results=list(p.map(fetch,urls.items()))
(E/'official_stop_sources.json').write_text(json.dumps(results,indent=2)+'\n')
