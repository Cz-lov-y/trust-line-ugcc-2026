"""Evaluate eight dependency bundles without summing nonadditive City z scores."""
import geopandas as gpd
from shapely.ops import unary_union
from tiered_common import ROOT,O,read,write,dump,policy,tiers

def run():
 master,main,conditional,closure=tiers(read(ROOT/'data/corridor_master_v0.1.csv'),policy())
 buffers=gpd.read_file(ROOT/'outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson').to_crs(2952)
 shapes={int(r.corridor_id):r.geometry for r in buffers.itertuples()}
 cts=gpd.read_file(ROOT/'evidence/corridor_batch_v0.5/batch_ct_boundaries.geojson').to_crs(2952)
 counts={r['CTUID']:r for r in read(ROOT/'data/census_ct_analysis_v0.5.csv')}
 city={int(r['corridor_id']):r for r in read(ROOT/'data/city_standardized_scores_v0.1.csv')}
 def allocate(geometry):
  total=low=0.;pieces=[];imputed=[]
  for i in cts.sindex.query(geometry,predicate='intersects'):
   ct=cts.iloc[i];piece=geometry.intersection(ct.geometry)
   if piece.area<=1e-6:continue
   s=counts[str(ct.CTUID)];p=float(s['population_2021']);l=float(s['analysis_low_income_population']) if s['analysis_low_income_population'] else None
   if l is None and p==0:l=0.
   if l is None:raise ValueError('Incomplete pair source contribution')
   if s['analysis_value_status']=='suppressed_CT_imputed':imputed.append(str(ct.CTUID))
   f=piece.area/ct.geometry.area;total+=f*p;low+=f*l;pieces.append(piece)
  covered=unary_union(pieces)
  if sum(p.area for p in pieces)-covered.area>1:raise ValueError('Source CT area overlaps')
  return dict(population_estimate=total,low_income_estimate=low,custom_low_income_share=low/total if total else '',imputed_CTUIDs=';'.join(sorted(imputed)),source_land_gap_m2=geometry.difference(covered).area)
 rows=[];geometries=[]
 for cid in conditional:
  parents=closure[cid];base=unary_union([shapes[p] for p in parents]);combined=unary_union([base,shapes[cid]]);increment=combined.difference(base)
  b,c,a=allocate(base),allocate(combined),allocate(increment)
  if abs(c['population_estimate']-b['population_estimate']-a['population_estimate'])>1e-5:raise ValueError('Pair catchment allocation nonadditive')
  rows.append(dict(corridor_id=cid,corridor_name=master[cid]['corridor_name'],baseline_scenario_id=master[cid]['baseline_scenario_id'],required_predecessors=';'.join(map(str,parents)),dependency_sequence=' -> '.join(map(str,[*parents,cid])),main_tier_root_ids=';'.join(str(p) for p in parents if p in main),main_absolute_rank='not_applicable',reserve_status='conditional_network_expansion',base_union_area_km2=base.area/1e6,with_extension_union_area_km2=combined.area/1e6,incremental_area_km2=increment.area/1e6,base_population_estimate=b['population_estimate'],with_extension_population_estimate=c['population_estimate'],incremental_population_estimate=a['population_estimate'],base_low_income_estimate=b['low_income_estimate'],with_extension_low_income_estimate=c['low_income_estimate'],incremental_low_income_estimate=a['low_income_estimate'],base_custom_low_income_share=b['custom_low_income_share'],with_extension_custom_low_income_share=c['custom_low_income_share'],incremental_custom_low_income_share=a['custom_low_income_share'],imputed_CTUIDs=c['imputed_CTUIDs'],source_unimproved_load_score=city[cid]['unimproved_load'],City_score_bundle_total='not_additive_not_computed',interpretation='Geometric additional coverage under uniform CT density; not causal transport benefit, additional ridership, construction feasibility or common-baseline score comparison'))
  geometries.extend([dict(corridor_id=cid,catchment_case='prerequisites',geometry=base),dict(corridor_id=cid,catchment_case='with_extension',geometry=combined)])
 write(O/'conditional_pair_analysis.csv',rows)
 gpd.GeoDataFrame(geometries,crs=2952).to_crs(4326).to_file(O/'conditional_bundle_buffers.geojson',driver='GeoJSON')
 dump(O/'conditional_pair_summary.json',dict(conditional_corridor_count=8,no_cross_baseline_rank=True,City_z_scores_summed=False,pairs=rows))
 print('Eight conditional dependency bundles calculated; no pooled scores or absolute ranks.');return rows
if __name__=='__main__':run()
