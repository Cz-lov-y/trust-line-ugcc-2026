from pathlib import Path
import sys,json,heapq,time,requests
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'gis_pydeps'))
from shapely.geometry import shape,LineString,Point,mapping
from shapely.ops import transform
from pyproj import Transformer
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=W.parent/'outputs/project/outputs/sheppard_west_pilot';OUT.mkdir(parents=True,exist_ok=True)
tf=Transformer.from_crs(4326,2952,always_xy=True);back=Transformer.from_crs(2952,4326,always_xy=True)
d=json.loads((W/'sheppard_roads.geojson').read_text());edges=[f for f in d['features'] if f['properties']['LINEAR_NAME_FULL']=='Sheppard Ave W']
graph={};coords={}
for f in edges:
 p=f['properties'];a=p['FROM_INTERSECTION_ID'];b=p['TO_INTERSECTION_ID'];line=shape(f['geometry']);length=transform(tf.transform,line).length
 graph.setdefault(a,[]).append((b,length,f));graph.setdefault(b,[]).append((a,length,f));coords[a]=list(line.coords)[0];coords[b]=list(line.coords)[-1]
start,end=13450458,13448689 # Official road-network nodes at Allen/Sheppard and Yonge/Sheppard.
queue=[(0,start)];best={start:0};prev={}
while queue:
 dist,a=heapq.heappop(queue)
 if dist!=best[a]:continue
 if a==end:break
 for b,c,f in graph[a]:
  nd=dist+c
  if nd<best.get(b,float('inf')):best[b]=nd;prev[b]=(a,f);heapq.heappush(queue,(nd,b))
assert end in best
path=[];cur=end
while cur!=start:a,f=prev[cur];path.append((a,cur,f));cur=a
path.reverse();points=[]
for a,b,f in path:
 cc=list(shape(f['geometry']).coords)
 if Point(cc[-1]).distance(Point(coords[a])) < Point(cc[0]).distance(Point(coords[a])):cc.reverse()
 if points:
  gap=transform(tf.transform,LineString([points[-1],cc[0]])).length
  assert gap<1,(a,b,gap)
 points+=cc if not points else cc[1:]
line=LineString(points);metres=transform(tf.transform,line);area=metres.buffer(500,quad_segs=48);boundary=transform(back.transform,area)
assert area.is_valid and line.is_simple and abs(metres.length-best[end])<0.1
def collection(features):return {'type':'FeatureCollection','features':features}
def feat(geom,p):return {'type':'Feature','geometry':mapping(geom),'properties':p}
properties={'corridor_id':1,'corridor_name':'Sheppard Ave West','status':'analytical road-centreline proxy; not approved transit alignment','source':'City of Toronto Centreline FeatureServer/2','retrieved':'2026-11-21','measured_length_km':round(metres.length/1000,6),'report_assumed_length_km':4.404}
(OUT/'corridor_01_centerline.geojson').write_text(json.dumps(collection([feat(line,properties)]),indent=2),encoding='utf-8')
(OUT/'corridor_01_buffer_500m.geojson').write_text(json.dumps(collection([feat(boundary,dict(corridor_id=1,buffer_m=500,area_km2=round(area.area/1e6,6),method='EPSG:2952 planar buffer; round caps; no municipal/land clipping',interpretation='corridor proximity area, not station walkshed'))]),indent=2),encoding='utf-8')
eps=[feat(Point(coords[start]),{'endpoint':'A','label':'Sheppard West area / Allen Rd intersection','node_id':start}),feat(Point(coords[end]),{'endpoint':'B','label':'Sheppard-Yonge area / Yonge St intersection','node_id':end})]
(OUT/'corridor_01_endpoints.geojson').write_text(json.dumps(collection(eps),indent=2),encoding='utf-8')
(OUT/'source_centerline_segments.geojson').write_text(json.dumps(collection([f for a,b,f in path]),indent=2),encoding='utf-8')
summary=dict(corridor_id=1,segment_count=len(path),segment_ids=[f['properties']['CENTRELINE_ID'] for a,b,f in path],measured_length_km=metres.length/1000,city_assumed_length_km=4.404,length_difference_m=metres.length-4404,buffer_m=500,buffer_area_km2=area.area/1e6,projected_crs='EPSG:2952',geojson_crs='EPSG:4326',endpoint_method='Road junction proxies near named stations; not station centroids or approved future tunnel terminals',ready_for_final_population_estimation=False,limitations=['Current road data are not the 2024 proposed subway alignment.','500 m Euclidean road corridor buffer differs from 500 m station buffers and walking-network access.','Road intersections approximate station-area endpoints; exact station/platform endpoint must be approved before final calculations.','No tract intersection, PPI aggregation or population calculation performed.'])
(OUT/'pilot_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
# Download a bounded set of official background centreline features for an offline map.
background=W/'sheppard_background.geojson'
if not background.exists():
 bounds=boundary.bounds;env=','.join(map(str,bounds));params={'f':'geojson','where':'1=1','geometry':env,'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','outSR':4326,'outFields':'LINEAR_NAME_FULL,FEATURE_CODE','returnGeometry':'true','resultRecordCount':2000}
 r=requests.get('https://gis.toronto.ca/arcgis/rest/services/cot_geospatial/FeatureServer/2/query',params=params,timeout=90);r.raise_for_status();background.write_text(r.text)
bg=json.loads(background.read_text())
fig,ax=plt.subplots(figsize=(13,5.3));fig.patch.set_facecolor('#f7f8fa');ax.set_facecolor('#f7f8fa')
for f in bg.get('features',[]):
 g=shape(f['geometry']);gs=list(g.geoms) if hasattr(g,'geoms') else [g]
 for l in gs:
  ll=transform(tf.transform,l);ax.plot(*ll.xy,color='#c6ccd3',lw=.65,zorder=1)
ax.fill(*area.exterior.xy,color='#70c3c4',alpha=.28,zorder=2);ax.plot(*area.exterior.xy,color='#087f8c',lw=1.5,zorder=3,label='500 m corridor buffer')
ax.plot(*metres.xy,color='#e35a3e',lw=3,zorder=4,label='Official road centreline proxy')
for node,label,off in [(start,'A  Sheppard West area\nAllen Rd / Sheppard Ave W',(5,-32)),(end,'B  Sheppard-Yonge area\nYonge St / Sheppard Ave W',(-180,25))]:
 x,y=tf.transform(*coords[node]);ax.scatter(x,y,s=65,c='#203c51',zorder=5);ax.annotate(label,(x,y),xytext=off,textcoords='offset points',fontsize=10,color='#203c51',bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=4))
x0,y0,x1,y1=area.bounds;ax.set_xlim(x0-200,x1+200);ax.set_ylim(y0-300,y1+300);ax.set_aspect('equal');ax.axis('off')
sx,sy=x0+150,y0-70;ax.plot([sx,sx+1000],[sy,sy],color='#203c51',lw=3);ax.text(sx+500,sy-85,'1 km',ha='center',fontsize=9)
ax.annotate('N',xy=(x1-100,y1-50),xytext=(x1-100,y1-400),ha='center',arrowprops=dict(arrowstyle='-|>',color='#203c51'),fontsize=12)
ax.legend(loc='lower right',fontsize=9,frameon=True)
fig.suptitle('Corridor 01 | Sheppard Avenue West boundary pilot',fontsize=18,fontweight='bold',x=.07,ha='left',color='#203c51')
fig.text(.07,.87,f'Road proxy: {metres.length/1000:.3f} km   |   Buffer: 500 m each side   |   Area: {area.area/1e6:.3f} km²',fontsize=11,color='#203c51')
fig.text(.07,.035,'Source: City of Toronto Centreline, retrieved 21 Nov 2026. EPSG:2952. Analytical buffer; not a proposed transit footprint or station walkshed.',fontsize=8,color='#526475')
fig.subplots_adjust(left=.04,right=.98,bottom=.10,top=.83)
fig.savefig(OUT/'corridor_01_boundary_pilot.png',dpi=180);fig.savefig(OUT/'corridor_01_boundary_pilot.svg');plt.close(fig)
import folium
m=folium.Map(location=[line.centroid.y,line.centroid.x],tiles='OpenStreetMap')
folium.GeoJson(collection([feat(boundary,{'name':'500 m corridor buffer'})]),name='500 m corridor buffer',style_function=lambda f:{'color':'#087f8c','weight':2,'fillOpacity':.2}).add_to(m)
folium.GeoJson(collection([feat(line,properties)]),name='Road centreline proxy',style_function=lambda f:{'color':'#e35a3e','weight':5}).add_to(m)
for f in eps:folium.Marker([f['geometry']['coordinates'][1],f['geometry']['coordinates'][0]],tooltip=f['properties']['label']).add_to(m)
m.fit_bounds([[boundary.bounds[1],boundary.bounds[0]],[boundary.bounds[3],boundary.bounds[2]]]);folium.LayerControl().add_to(m);m.save(str(OUT/'corridor_01_interactive_map.html'))
print(json.dumps(summary,indent=2),flush=True)
