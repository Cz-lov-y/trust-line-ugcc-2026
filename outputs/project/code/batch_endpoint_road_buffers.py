"""GeoPandas road proxies from sourced EPSG:4326 endpoint pairs.

Fetches the official 2021 StatCan RNF when --acquire-roads is supplied. RNF is
cartographic: an undirected shortest path is an explicit geometry scenario,
not an approved rail alignment, legal driving route, or station walkshed.
"""
from pathlib import Path
import argparse,csv,json,zipfile,hashlib
import geopandas as gpd
import networkx as nx
import shapely
from shapely.geometry import Point,LineString,shape
from shapely.ops import substring,unary_union,linemerge
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/corridor_batch_v0.5'
O=ROOT/'outputs/corridor_batch_v0.5'
def load_roads(paths=None):
 paths=paths or [E/'official_roads.geojson',E/'official_roads_east.geojson']
 if all(p.exists() for p in paths):
  parts=[gpd.read_file(p) for p in paths]
 else:
  archive=E/'official_RNF_source_pages.zip'
  manifest=json.loads((E/'packed_road_acquisition_manifest.json').read_text())
  if hashlib.sha256(archive.read_bytes()).hexdigest()!=manifest['archive_sha256']:raise ValueError('Official RNF archive checksum mismatch')
  with zipfile.ZipFile(archive) as z:
   for record in manifest['resources']:
    if hashlib.sha256(z.read(record['archive_member'])).hexdigest()!=record['sha256']:raise ValueError('Official RNF source member checksum mismatch')
   features=[]
   for n in z.namelist():
    if n.endswith('.geojson'):features.extend(json.loads(z.read(n))['features'])
  parts=[gpd.GeoDataFrame.from_features(features,crs=4326)]
 import pandas as pd
 roads=gpd.GeoDataFrame(pd.concat(parts,ignore_index=True),crs=4326).drop_duplicates('NGD_UID').to_crs(2952).explode(index_parts=False).reset_index(drop=True)
 if roads.geometry.is_empty.any() or not roads.geometry.is_valid.all():raise ValueError('Invalid source roads')
 return roads

def graph_from_roads(roads):
 graph=nx.Graph()
 def node(c):return tuple(round(float(v),2) for v in c[:2])
 for row in roads.itertuples():
  g=row.geometry
  if g.geom_type!='LineString':raise ValueError('Unexpected RNF geometry')
  a,b=node(g.coords[0]),node(g.coords[-1])
  if a==b or g.length<=0:continue
  attrs=dict(weight=g.length,geometry=g,source_id=str(row.NGD_UID))
  if not graph.has_edge(a,b) or graph[a][b]['weight']>g.length:graph.add_edge(a,b,**attrs)
 return graph,node

def snap_endpoint(graph,node,point,roads,tree,maximum):
 index=int(tree.nearest(point));g=roads.geometry.iloc[index]
 distance=g.distance(point)
 if distance>maximum:raise ValueError(f'Endpoint {distance:.1f} m from nearest official road; exceeds snap limit')
 offset=g.project(point);anchor=g.interpolate(offset);n=node(anchor.coords[0])
 a,b=node(g.coords[0]),node(g.coords[-1])
 for terminal,start,end in [(a,0,offset),(b,offset,g.length)]:
  part=substring(g,start,end)
  if part.geom_type=='LineString' and part.length>0.005 and n!=terminal:
   graph.add_edge(n,terminal,weight=part.length,geometry=part,source_id=str(roads.iloc[index]['NGD_UID']))
 if n not in graph:raise ValueError('Snapped road node not connected')
 return n,dict(source_road_id=str(roads.iloc[index]['NGD_UID']),snap_distance_m=distance,snapped_x=n[0],snapped_y=n[1])

def build(config_path=None,acquire=False):
 config=json.loads(Path(config_path or ROOT/'data/corridor_endpoint_coordinates_v0.5.json').read_text())
 override=None
 if acquire:
  from acquire_v0_5_support import roads,MANIFEST
  endpoints=[spec[k] for spec in config['specifications'] for k in ['endpoint_a','endpoint_b']]
  # Query a geographic envelope enclosing input points plus roughly 4 km of routing margin.
  bounds=dict(xmin=min(p['longitude'] for p in endpoints)-0.05,
              xmax=max(p['longitude'] for p in endpoints)+0.05,
              ymin=min(p['latitude'] for p in endpoints)-0.04,
              ymax=max(p['latitude'] for p in endpoints)+0.04)
  import hashlib
  prefix='rnf_'+hashlib.sha256(json.dumps(bounds,sort_keys=True).encode()).hexdigest()[:10]
  roads(prefix=prefix,**bounds)
  (E/'endpoint_driven_road_acquisition_manifest.json').write_text(json.dumps(dict(bounds=bounds,resources=MANIFEST),indent=2)+'\n')
  override=[E/'official_roads_east.geojson']
 if config['crs']!='EPSG:4326' or config['metric_crs']!='EPSG:2952' or config['buffer_m']!=500:raise ValueError('Unexpected CRS/buffer contract')
 roads=load_roads(override);tree=shapely.STRtree(roads.geometry.to_numpy());base,node=graph_from_roads(roads)
 old=ROOT/'outputs/corridor_batch_v0.4'
 lines=gpd.read_file(old/'corridor_road_proxies.geojson').to_crs(2952)
 buffers=gpd.read_file(old/'corridor_buffers_500m.geojson').to_crs(2952)
 new_lines=[];new_buffers=[];audit=[]
 for spec in config['specifications']:
  cid=spec['corridor_id'];graph=base.copy()
  points=gpd.GeoSeries([Point(spec[k]['longitude'],spec[k]['latitude']) for k in ['endpoint_a','endpoint_b']],crs=4326).to_crs(2952)
  a,sa=snap_endpoint(graph,node,points.iloc[0],roads,tree,config['maximum_node_snap_m'])
  b,sb=snap_endpoint(graph,node,points.iloc[1],roads,tree,config['maximum_node_snap_m'])
  path=nx.shortest_path(graph,a,b,weight='weight') # Disconnected graph raises; no invented link.
  edges=[graph[u][v] for u,v in zip(path,path[1:])]
  parts=[e['geometry'] for e in edges]
  route=unary_union(parts);buf=route.buffer(500)
  if buf.is_empty or not buf.is_valid:raise ValueError('Invalid catchment')
  props=dict(corridor_id=cid,geometry_status='shortest_road_proxy_pending_review',geographic_review='pending',measured_route_length_km=sum(e['weight'] for e in edges)/1000,endpoint_method='sourced_provisional_coordinates_snap_to_official_RNF',route_method=config['route_method'],buffer_area_km2=buf.area/1e6)
  new_lines.append(dict(**props,geometry=route));new_buffers.append(dict(**props,geometry=buf))
  audit.append(dict(**props,endpoint_a=sa,endpoint_b=sb,source_road_ids=[e['source_id'] for e in edges],source_edge_count=len(edges),node_rounding_m=0.01,source_network_vintage=2021,limitations='Undirected cartographic shortest road proxy; no transit alignment, travel restriction, or grade-separation review; existing 17 proxies use named-road paths'))
  print(cid,round(props['measured_route_length_km'],3),'km',round(sa['snap_distance_m'],1),round(sb['snap_distance_m'],1),'m snaps',flush=True)
 import pandas as pd
 for name,oldframe,new in [('corridor_road_proxies.geojson',lines,new_lines),('corridor_buffers_500m.geojson',buffers,new_buffers)]:
  frame=gpd.GeoDataFrame(pd.concat([oldframe,gpd.GeoDataFrame(new,crs=2952)],ignore_index=True),crs=2952)
  if len(frame)!=24 or set(frame.corridor_id.astype(int))!=set(range(1,25)):raise ValueError('24 unique geometries required')
  O.mkdir(parents=True,exist_ok=True);frame.to_crs(4326).to_file(O/name,driver='GeoJSON')
 (O/'endpoint_route_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 return audit
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--endpoints',type=Path);parser.add_argument('--acquire-roads',action='store_true');a=parser.parse_args();build(a.endpoints,a.acquire_roads)
