"""Rebuild both Woodbine-linked road proxies at nine shared anchor positions."""
import json,math,csv,urllib.request,io
from pathlib import Path
import geopandas as gpd
import networkx as nx
import shapely
from shapely.geometry import Point
from shapely.ops import unary_union
from batch_endpoint_road_buffers import load_roads,graph_from_roads,snap_endpoint
from tiered_common import ROOT,O,read,write,dump,sha

def run():
 O.mkdir(parents=True,exist_ok=True);e=ROOT/'evidence/tiered_v0.6';e.mkdir(parents=True,exist_ok=True)
 roads=load_roads();tree=shapely.STRtree(roads.geometry.to_numpy());base,node=graph_from_roads(roads)
 config=json.loads((ROOT/'data/corridor_endpoint_coordinates_v0.5.json').read_text())
 specs={s['corridor_id']:s for s in config['specifications']}
 wood=specs[5]['endpoint_b'];anchor=gpd.GeoSeries([Point(wood['longitude'],wood['latitude'])],crs=4326).to_crs(2952).iloc[0]
 cts=gpd.read_file(ROOT/'evidence/corridor_batch_v0.5/batch_ct_boundaries.geojson').to_crs(2952)
 counts={r['CTUID']:(float(r['population_2021']),float(r['analysis_low_income_population']) if r['analysis_low_income_population'] else None) for r in read(ROOT/'data/census_ct_analysis_v0.5.csv')}
 # Existing official municipal source pages also cover CTs not used by the nominal buffers.
 peers={}
 for path in sorted((ROOT/'evidence/corridor_batch_v0.5').glob('peer_CT_profile_*.csv')):
  for r in read(path):peers.setdefault(r['ALT_GEO_CODE'],{})[r['CHARACTERISTIC']]=r
 for ct,values in peers.items():
  if ct not in counts:
   p,l=values['1'],values['326']
   if p['OBS_VALUE'] and not p['FLAG'] and l['OBS_VALUE'] and not l['FLAG']:counts[ct]=float(p['OBS_VALUE']),float(l['OBS_VALUE'])
 buffers=[];audits=[]
 cases=[('nominal',0.,0.)]+[(f'bearing_{angle:03}',250*math.cos(math.radians(angle)),250*math.sin(math.radians(angle))) for angle in range(0,360,45)]
 for label,dx,dy in cases:
  moved=Point(anchor.x+dx,anchor.y+dy)
  lonlat=gpd.GeoSeries([moved],crs=2952).to_crs(4326).iloc[0]
  for cid in [5,6]:
   spec=specs[cid];graph=base.copy();points=[]
   for key in ['endpoint_a','endpoint_b']:
    endpoint=spec[key]
    if (cid==5 and key=='endpoint_b') or (cid==6 and key=='endpoint_a'):points.append(moved)
    else:points.append(gpd.GeoSeries([Point(endpoint['longitude'],endpoint['latitude'])],crs=4326).to_crs(2952).iloc[0])
   a,sa=snap_endpoint(graph,node,points[0],roads,tree,500);b,sb=snap_endpoint(graph,node,points[1],roads,tree,500)
   path=nx.shortest_path(graph,a,b,weight='weight');edges=[graph[u][v] for u,v in zip(path,path[1:])]
   route=unary_union([edge['geometry'] for edge in edges]);buf=route.buffer(500)
   buffers.append(dict(corridor_id=cid,anchor_case=label,dx_m=dx,dy_m=dy,geometry=buf))
   audits.append(dict(corridor_id=cid,anchor_case=label,anchor_longitude=lonlat.x,anchor_latitude=lonlat.y,dx_m=dx,dy_m=dy,route_length_km=sum(edge['weight'] for edge in edges)/1000,endpoint_a_snap_m=sa['snap_distance_m'],endpoint_b_snap_m=sb['snap_distance_m'],source_road_ids=[edge['source_id'] for edge in edges]))
 required=set()
 for b in buffers:
  for index in cts.sindex.query(b['geometry'],predicate='intersects'):
   ct=cts.iloc[index]
   if b['geometry'].intersection(ct.geometry).area>1e-6:required.add(str(ct.CTUID))
 missing=sorted(required-set(counts))
 extra_records=[]
 if missing:
  for start in range(0,len(missing),40):
   batch=missing[start:start+40];keys='+'.join('2021S0507'+ct.replace('.','_') for ct in batch)
   url=f'https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_CT/A5.{keys}.1.1+326.1?format=csv'
   p=e/f'woodbine_extra_profiles_{start//40:03}.csv'
   if not p.exists():p.write_bytes(urllib.request.urlopen(url,timeout=45).read())
   extra_records.append(dict(file=str(p.relative_to(ROOT)),url=url,sha256=sha(p)))
   index={}
   for r in read(p):
    if (r['GENDER'],r['STATISTIC'],r['TIME_PERIOD'])!=('1','1','2021'):raise ValueError('Unexpected extra source dimensions')
    index.setdefault(r['ALT_GEO_CODE'],{})[r['CHARACTERISTIC']]=r
   for ct in batch:
    p,l=index[ct]['1'],index[ct]['326']
    if p['FLAG'] or not p['OBS_VALUE'] or l['FLAG'] or not l['OBS_VALUE']:raise ValueError('New sensitivity CT has unresolved source counts: '+ct)
    counts[ct]=float(p['OBS_VALUE']),float(l['OBS_VALUE'])
 rows=[];ledger=[]
 for buffer,audit in zip(buffers,audits):
  pop=low=0.;pieces=[]
  for index in cts.sindex.query(buffer['geometry'],predicate='intersects'):
   ct=cts.iloc[index];piece=buffer['geometry'].intersection(ct.geometry)
   if piece.area<=1e-6:continue
   ctuid=str(ct.CTUID);fraction=piece.area/ct.geometry.area;p,l=counts[ctuid]
   if l is None and p==0:l=0.
   if l is None:raise ValueError('Unresolved sensitivity contribution')
   pop+=fraction*p;low+=fraction*l;pieces.append(piece)
   ledger.append(dict(corridor_id=buffer['corridor_id'],anchor_case=buffer['anchor_case'],CTUID=ctuid,area_fraction=fraction,analysis_CT_population=p,analysis_CT_low_income=l,allocated_population=fraction*p,allocated_low_income=fraction*l))
  coverage=unary_union(pieces)
  if sum(p.area for p in pieces)-coverage.area>1:raise ValueError('Overlapping source CT areas')
  if pop<=0:raise ValueError('Nonpositive sensitivity population')
  rows.append({k:v for k,v in audit.items() if k!='source_road_ids'}|dict(total_population_estimate=pop,low_income_population_estimate=low,low_income_population_share_500m=low/pop,intersecting_CT_count=len(pieces),area_outside_CT_frame_m2=buffer['geometry'].difference(coverage).area))
 write(O/'woodbine_anchor_sensitivity.csv',rows);write(O/'woodbine_CT_allocations.csv',ledger)
 gpd.GeoDataFrame(buffers,crs=2952).to_crs(4326).to_file(O/'woodbine_buffers.geojson',driver='GeoJSON')
 dump(O/'woodbine_route_audit.json',audits)
 nominal={int(r['corridor_id']):r for r in read(ROOT/'data/supplemental_model_inputs_v0.5.csv')}
 summary={}
 for cid in [5,6]:
  subset=[r for r in rows if r['corridor_id']==cid];first=subset[0]
  if not math.isclose(first['low_income_population_share_500m'],float(nominal[cid]['low_income_population_share_500m']),abs_tol=1e-10):raise ValueError('Nominal sensitivity route does not reproduce existing share')
  values=[r['low_income_population_share_500m'] for r in subset]
  summary[cid]=dict(min_share=min(values),max_share=max(values),max_absolute_share_change_from_nominal=max(abs(v-values[0]) for v in values),min_route_length_km=min(r['route_length_km'] for r in subset),max_route_length_km=max(r['route_length_km'] for r in subset))
 result=dict(status='proxy_with_sensitivity_check',completed=True,shared_anchor_cases=9,route_recalculations=18,radius_m=250,metric_crs='EPSG:2952',per_corridor=summary,additional_source_profiles=extra_records,official_station_site_verified=False,limitations='Eight sampled bearings at 250m are a local stress test, not an exhaustive envelope or surveyed station confirmation; shared Woodbine anchor applied consistently to both corridors.')
 dump(O/'woodbine_sensitivity_summary.json',result)
 dump(e/'woodbine_source_manifest.json',dict(source_files={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'data/corridor_endpoint_coordinates_v0.5.json',ROOT/'data/census_ct_analysis_v0.5.csv',ROOT/'evidence/corridor_batch_v0.5/batch_ct_boundaries.geojson',ROOT/'evidence/corridor_batch_v0.5/official_RNF_source_pages.zip']},additional_profiles=extra_records))
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
