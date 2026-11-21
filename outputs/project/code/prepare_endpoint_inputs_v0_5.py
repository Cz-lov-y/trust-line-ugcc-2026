"""Rebuild the seven explicitly provisional endpoint pairs from archived sources."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/corridor_batch_v0.5'
def stop(agency,i,note=''):
 rows={r['stop_id']:r for r in csv.DictReader((E/f'{agency}_official_stops.csv').open(encoding='utf-8-sig'))};r=rows[i]
 return dict(label=r['stop_name'],longitude=float(r['stop_lon']),latitude=float(r['stop_lat']),coordinate_source=f'evidence/corridor_batch_v0.5/{agency}_official_stops.csv',source_record_id=i,anchor_basis='Official operator GTFS stop coordinate; provisional corridor endpoint',limitations=note)
def main():
 # The archived named-road subset includes Lake Shore/Ontario Drive.
 src=ROOT/'evidence/corridor_batch_v0.5/ontario_place_road_nodes.geojson'
 features=json.loads(src.read_text())['features']
 def nodes(name):
  out={}
  for f in features:
   p=f['properties']
   if p['LINEAR_NAME_FULL']!=name:continue
   c=f['geometry']['coordinates'];c=c[0] if f['geometry']['type']=='MultiLineString' else c
   out[str(p['FROM_INTERSECTION_ID'])]=c[0];out[str(p['TO_INTERSECTION_ID'])]=c[-1]
  return out
 a,b=nodes('Lake Shore Blvd W'),nodes('Ontario Dr')
 common=sorted(set(a)&set(b))
 if not common:raise ValueError('Ontario Place entrance road node not archived')
 i=common[0];coord=a[i]
 ontario=dict(label='Ontario Place west entrance: Lake Shore Blvd W / Ontario Dr',longitude=coord[0],latitude=coord[1],coordinate_source=str(src.relative_to(ROOT)),source_record_id=i,anchor_basis='Official City centreline shared intersection node; entrance location supported by Ontario Place operator',supporting_url='https://ontarioplace.com/en/visit-us/site-access/',limitations='West public entrance proxy; distinct from future Ontario Line Exhibition station and full Ontario Place boundary')
 # Official planning source confirms Highway 27 rail-corridor location, but does not publish a surveyed point.
 # Secondary numeric anchor is deliberately identified, never described as an official station coordinate.
 woodbine=dict(label='Future Woodbine GO station provisional area anchor',longitude=-79.59442,latitude=43.70619,coordinate_source='https://en.wikipedia.org/wiki/Woodbine_GO_Station',source_record_id='43.70619,-79.59442',anchor_basis='Approximate secondary coordinate for official Highway 27 / Kitchener rail-corridor site',supporting_url='https://www.metrolinx.com/en/projects-and-programs/kitchener-line-go-expansion/what-were-building/woodbine-go-station',limitations='Not a published surveyed station point; approximate 250 m anchor sensitivity required; future entrance not established')
 pairs=[(4,stop('TTC','5195'),stop('GO','UN')),(5,stop('TTC','16289'),woodbine),(6,woodbine,stop('UP','PA','Pearson is represented by Terminal 1 UP Express, not the airport centroid or Terminal 3')),(8,ontario,stop('TTC','14662')),(9,stop('TTC','9126'),stop('TTC','1974','Don Mills Road at Steeles chosen as an explicit provisional branch/terminus assumption; not an approved extension alignment')),(10,stop('TTC','14717'),stop('TTC','3117','Mall bus stop chosen; future Sherway station site is unknown')),(19,stop('TTC','1318'),stop('GO','UI','Markham Centre represented by Unionville GO mobility hub; this is a terminus-area assumption, not a continuation of McCowan Road to an approved station'))]
 config=dict(crs='EPSG:4326',metric_crs='EPSG:2952',buffer_m=500,maximum_node_snap_m=500,route_method='undirected_shortest_cartographic_road_path',geographic_review='pending',authorization='User accepted sourced provisional endpoints and road proxies; 2026-11-21',specifications=[dict(corridor_id=i,endpoint_a=a,endpoint_b=b) for i,a,b in pairs])
 (ROOT/'data/corridor_endpoint_coordinates_v0.5.json').write_text(json.dumps(config,indent=2)+'\n')
 rows=[dict(corridor_id=i,endpoint_a_longitude=a['longitude'],endpoint_a_latitude=a['latitude'],endpoint_b_longitude=b['longitude'],endpoint_b_latitude=b['latitude'],endpoint_a_source=a['coordinate_source'],endpoint_b_source=b['coordinate_source']) for i,a,b in pairs]
 with (ROOT/'data/corridor_endpoint_coordinates_v0.5.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
