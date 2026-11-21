"""Archive official RNF, full Toronto CT peer pool, and affected DA profiles."""
from pathlib import Path
import csv, io, json, urllib.request, urllib.parse, hashlib, zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/corridor_batch_v0.5'
RNF='https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Road_Network_File/MapServer'
MANIFEST=[]
def fetch(name,url):
 p=E/name
 if not p.exists():
  with urllib.request.urlopen(url,timeout=90) as f: data=f.read()
  if name.endswith(('json','geojson')) and json.loads(data).get('error'): raise ValueError(data[:300])
  p.write_bytes(data)
 MANIFEST.append(dict(file=str(p.relative_to(ROOT)),url=url,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),retrieved_utc=datetime.now(timezone.utc).isoformat()))
 return p
def query(layer,params):return RNF+'/'+str(layer)+'/query?'+urllib.parse.urlencode(params)
def roads(prefix="rnf", xmin=-79.67, xmax=-79.27, ymin=43.58, ymax=43.91):
 envelope=json.dumps(dict(xmin=xmin,ymin=ymin,xmax=xmax,ymax=ymax,spatialReference={'wkid':4326}))
 tasks=[]
 for layer in range(5):
  p=fetch(f'{prefix}_ids_{layer}.json',query(layer,dict(f='json',where='1=1',returnIdsOnly='true',geometry=envelope,geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects')))
  ids=sorted(json.loads(p.read_text()).get('objectIds') or [])
  print('Road rank',layer+1,len(ids),flush=True)
  for start in range(0,len(ids),300):
   name=f'{prefix}_{layer}_{start//300:03}.geojson'
   cached=E/name
   if cached.exists() and {f['properties']['OBJECTID'] for f in json.loads(cached.read_text())['features']} != set(ids[start:start+300]):cached.unlink()
   tasks.append((name,query(layer,dict(f='geojson',objectIds=','.join(map(str,ids[start:start+300])),outFields='*',outSR=4326,returnGeometry='true'))))
 with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(lambda t:fetch(*t),tasks))
 unique={}
 for name,_ in tasks:
  data=json.loads((E/name).read_text())
  if data.get('exceededTransferLimit'):raise ValueError('RNF page truncated')
  for f in data['features']:
   key=f['properties']['NGD_UID']
   if key in unique and unique[key]['geometry']!=f['geometry']:raise ValueError('Conflicting source road ID')
   unique[key]=f
 # Reconcile all source object IDs, separately by layer.
 for layer in range(5):
  expected=set(json.loads((E/f'{prefix}_ids_{layer}.json').read_text()).get('objectIds') or [])
  actual=[]
  for name,_ in tasks:
   if name.startswith(f'{prefix}_{layer}_'):actual += [f['properties']['OBJECTID'] for f in json.loads((E/name).read_text())['features']]
  if set(actual)!=expected or len(actual)!=len(expected):raise ValueError('RNF IDs incomplete')
 (E/('official_roads.geojson' if prefix=='rnf' else 'official_roads_east.geojson')).write_text(json.dumps(dict(type='FeatureCollection',features=list(unique.values()))))
 print('Unique roads',len(unique),flush=True)
def roads_east():
 roads(prefix="rnf_east",xmin=-79.27,xmax=-79.22)

def profiles():
 with zipfile.ZipFile(ROOT/'evidence/census_support_v0.2/2021_92-151_X.zip') as z:
  rows=csv.DictReader(io.TextIOWrapper(z.open('2021_92-151_X.csv'),encoding='latin1'))
  membership={}; da={}
  for r in rows:
   ct=r['CTUID_SRIDU']
   if ct:membership.setdefault(ct,set()).add(r['CSDUID_SDRIDU'])
   if ct in {'5350205.00','5350006.00'}:da.setdefault(ct,set()).add(r['DAUID_ADIDU'])
 peers=sorted(ct for ct,codes in membership.items() if codes=={'3520005'})
 with (E/'peer_CT_CSD_membership_check.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['CTUID','CSDUIDs','entire_CT_in_Toronto']);w.writerows((ct,'3520005',True) for ct in peers)
 (E/'toronto_peer_CT_ids.json').write_text(json.dumps(peers,indent=2)+'\n')
 (E/'suppressed_CT_DA_membership.json').write_text(json.dumps({k:sorted(v) for k,v in da.items()},indent=2)+'\n')
 tasks=[]
 for start in range(0,len(peers),40):
  keys='+'.join('2021S0507'+ct.replace('.','_') for ct in peers[start:start+40])
  tasks.append((f'peer_CT_profile_{start//40:03}.csv',f'https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_CT/A5.{keys}.1.1+321+326.1?format=csv'))
 keys='+'.join('2021S0512'+d for ds in da.values() for d in ds)
 tasks.append(('affected_DA_profiles.csv',f'https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_DA/A5.{keys}.1.1+321+326.1?format=csv'))
 with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda t:fetch(*t),tasks))
 print('Peer CTs',len(peers),'affected DAs',da,flush=True)
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('task',choices=['roads','roads_east','profiles']);args=a.parse_args()
 E.mkdir(parents=True,exist_ok=True)
 try:globals()[args.task]()
 finally:(E/(args.task+'_acquisition_manifest.json')).write_text(json.dumps(MANIFEST,indent=2)+'\n')
if __name__=='__main__':main()
