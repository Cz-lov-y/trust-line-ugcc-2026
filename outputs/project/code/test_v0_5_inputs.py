"""Checks for real 24/24 scenario inputs, suppression replay and proxy topology."""
from pathlib import Path
import csv,json,unittest,copy
import geopandas as gpd
import networkx as nx
import shapely
from shapely.geometry import LineString,Point
from batch_endpoint_road_buffers import graph_from_roads,snap_endpoint
from validate_equity_scenario import validate_equity_scenario
from validate_data import validate
ROOT=Path(__file__).resolve().parents[1]
KEY='low_income_population_share_500m'
def read(p):
 with Path(p).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
class VersionFiveTests(unittest.TestCase):
 def setUp(self):self.rows={r['corridor_id']:r for r in read(ROOT/'data/supplemental_model_inputs_v0.5.csv')}
 def test_complete_matrix_and_replay_without_claiming_final_readiness(self):
  self.assertEqual(set(self.rows),{str(i) for i in range(1,25)})
  self.assertEqual(validate_equity_scenario(ROOT,KEY,self.rows),[])
  report=validate(ROOT);self.assertTrue(report['valid_structure']);self.assertTrue(report['data_matrix_ready']);self.assertTrue(report['scenario_computation_ready']);self.assertFalse(report['model_ready'])
 def test_note_or_imputation_label_cannot_waive_blank_or_wrong_value(self):
  for bad in ['', '0.999']:
   rows=copy.deepcopy(self.rows);rows['3'][KEY]=bad;rows['3']['notes']='suppressed_CT_imputed'
   self.assertTrue(validate_equity_scenario(ROOT,KEY,rows))
 def test_imputed_census_estimate_cannot_be_disguised(self):
  rows=copy.deepcopy(self.rows);rows['3']['value_status']='area_weighted_observed_counts'
  self.assertTrue(validate_equity_scenario(ROOT,KEY,rows))
 def test_affected_corridors_and_source_suppression_preserved(self):
  self.assertEqual([cid for cid,r in self.rows.items() if r['imputed_CTUIDs']],['3','8','21'])
  counts={r['CTUID']:r for r in read(ROOT/'data/census_ct_batch_v0.5.csv')}
  for ct in ['5350006.00','5350205.00']:
   self.assertEqual(counts[ct]['low_income_population'],'');self.assertEqual(counts[ct]['low_income_population_source_flag'],'6')
  trace=read(ROOT/'outputs/corridor_batch_v0.5/suppression_imputation_trace.csv')
  self.assertTrue(all(r['DA_available_LIM_count']=='0' and r['peer_count']=='583' for r in trace))
 def test_geopandas_overlay_reproduces_new_seven_and_pilot(self):
  buffers=gpd.read_file(ROOT/'outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson').to_crs(2952)
  cts=gpd.read_file(ROOT/'evidence/corridor_batch_v0.5/batch_ct_boundaries.geojson').to_crs(2952)
  counts={r['CTUID']:r for r in read(ROOT/'data/census_ct_analysis_v0.5.csv')}
  for cid in [1,4,5,6,8,9,10,19]:
   catchment=buffers.loc[buffers.corridor_id==cid].geometry.iloc[0];pop=low=0
   for idx in cts.sindex.query(catchment,predicate='intersects'):
    ct=cts.iloc[idx];intersection=catchment.intersection(ct.geometry)
    if intersection.area<=1e-6:continue
    fraction=intersection.area/ct.geometry.area;s=counts[ct.CTUID];p=float(s['population_2021']);l=float(s['analysis_low_income_population']) if s['analysis_low_income_population'] else 0
    self.assertTrue(s['analysis_low_income_population']!='' or p==0)
    pop+=fraction*p;low+=fraction*l
   self.assertAlmostEqual(low/pop,float(self.rows[str(cid)][KEY]),places=10)
  self.assertAlmostEqual(float(self.rows['1'][KEY]),0.15911921596379328,places=10)
 def test_planar_crossing_does_not_create_an_unobserved_connection(self):
  roads=gpd.GeoDataFrame({'NGD_UID':['a','b']},geometry=[LineString([(0,0),(10,0)]),LineString([(5,-5),(5,5)])],crs=2952)
  graph,node=graph_from_roads(roads)
  self.assertFalse(nx.has_path(graph,node((0,0)),node((5,5))))
  with self.assertRaises(ValueError):snap_endpoint(graph,node,Point(1000,1000),roads,shapely.STRtree(roads.geometry.to_numpy()),500)
 def test_all_seven_endpoint_pairs_have_traceable_numeric_inputs(self):
  config=json.loads((ROOT/'data/corridor_endpoint_coordinates_v0.5.json').read_text());self.assertEqual({r['corridor_id'] for r in config['specifications']},{4,5,6,8,9,10,19})
  for r in config['specifications']:
   for k in ['endpoint_a','endpoint_b']:
    self.assertTrue(r[k]['coordinate_source']);self.assertTrue(-80<r[k]['longitude']<-79);self.assertTrue(43<r[k]['latitude']<45)
if __name__=='__main__':unittest.main()
