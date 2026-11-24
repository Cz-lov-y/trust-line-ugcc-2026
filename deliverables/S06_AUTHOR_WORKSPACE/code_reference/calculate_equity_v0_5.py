"""CT area allocation with auditable DA reconstruction / peer-rate scenarios."""
from pathlib import Path
import csv,json,statistics,math,hashlib
import geopandas as gpd
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/corridor_batch_v0.5';O=ROOT/'outputs/corridor_batch_v0.5'
KEY='low_income_population_share_500m'
def read(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def source_index(paths):
 index={}
 for path in paths:
  for r in read(path):
   if r['GENDER']!='1' or r['STATISTIC']!='1' or r['TIME_PERIOD']!='2021':raise ValueError('Unexpected profile dimensions')
   k=(r['ALT_GEO_CODE'],r['CHARACTERISTIC'])
   if k in index:raise ValueError('Duplicate profile count')
   index[k]=r
 return index
def observed(index,geo,char):
 r=index.get((geo,char))
 if not r or r['FLAG'] or r['OBS_VALUE']=='':return None
 n=float(r['OBS_VALUE'])
 if not math.isfinite(n) or n<0:raise ValueError('Invalid source count')
 return n
def replacements():
 peers=source_index(sorted(E.glob('peer_CT_profile_*.csv')))
 ids=json.loads((E/'toronto_peer_CT_ids.json').read_text())
 if {g for g,c in peers}!=set(ids):raise ValueError('Peer pool source coverage incomplete')
 rates=[];peer_rows=[]
 for ct in ids:
  pop=observed(peers,ct,'1');low=observed(peers,ct,'326')
  if pop is not None and pop>0 and low is not None:
   if low>pop:raise ValueError('Income count exceeds all-pop denominator')
   rates.append(low/pop);peer_rows.append(dict(CTUID=ct,population_2021=pop,low_income_population=low,custom_low_income_share=low/pop,CSDUID='3520005'))
 if not rates:raise ValueError('No eligible municipal peers')
 med=statistics.median(rates);mean=statistics.fmean(rates)
 das=source_index([E/'affected_DA_profiles.csv']);membership=json.loads((E/'suppressed_CT_DA_membership.json').read_text())
 output={};trace=[]
 for ct,da_ids in membership.items():
  pop=observed(peers,ct,'1')
  da_pop=[observed(das,da,'1') for da in da_ids];da_low=[observed(das,da,'326') for da in da_ids]
  if not da_ids or pop is None or any(v is None for v in da_pop) or sum(da_pop)!=pop:raise ValueError('DA membership/population does not reconcile with CT')
  complete=all(v is not None for v in da_low)
  method='reconstructed_from_complete_DA_sum' if complete else 'suppressed_CT_imputed'
  primary=sum(da_low) if complete else med*pop
  alternative=primary if complete else mean*pop
  output[ct]=dict(primary=primary,mean=alternative,status=method)
  trace.append(dict(CTUID=ct,CSDUID='3520005',source_CT_low_income_flag=peers[(ct,'326')]['FLAG'],population_2021=pop,all_DA_ids=';'.join(da_ids),DA_count=len(da_ids),DA_available_LIM_count=sum(v is not None for v in da_low),DA_population_sum=sum(da_pop),DA_aggregation_complete=complete,method=method,peer_count=len(rates),peer_rate_median=med,peer_rate_mean=mean,analysis_low_income_count=primary,mean_sensitivity_low_income_count=alternative,formula='sum(all DA LIM counts)' if complete else 'median(complete same-CSD CT LIM / CT total population) * suppressed CT total population',notes='User-authorized scenario estimate. Original suppressed count remains blank. Unweighted CT-rate median/mean; not population-weighted municipal prevalence; no DA partial sum is treated as complete.'))
 write(O/'municipal_CT_peer_rates.csv',peer_rows);write(O/'suppression_imputation_trace.csv',trace)
 return output,trace

def calculate(output=O,model_path=None):
 output=Path(output);output.mkdir(parents=True,exist_ok=True)
 manifest=json.loads((E/'census_acquisition_manifest.json').read_text())
 for entry in manifest['resources']:
  if entry['status']!='acquired':raise ValueError('Incomplete source acquisition')
  if digest(ROOT/entry['file'])!=entry['sha256']:raise ValueError('Source checksum mismatch')
 buffer_path=ROOT/'outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson'
 if digest(buffer_path)!=manifest['buffer_sha256']:raise ValueError('Changed catchment')
 for filekey,hashkey in [('processed_file','processed_sha256'),('geometry_file','geometry_sha256')]:
  if digest(ROOT/manifest[filekey])!=manifest[hashkey]:raise ValueError('Changed Census input')
 counts={r['CTUID']:r for r in read(ROOT/manifest['processed_file'])}
 replacements_by_id,trace=replacements()
 tracts=gpd.read_file(ROOT/manifest['geometry_file']).to_crs(2952)
 if not tracts.is_valid.all():tracts.geometry=tracts.geometry.make_valid()
 buffers=gpd.read_file(buffer_path).to_crs(2952)
 allocations=[];rows=[];analysis_counts=[]
 for ct,s in counts.items():
  replacement=replacements_by_id.get(ct)
  analysis_counts.append(dict(**s,analysis_low_income_population=replacement['primary'] if replacement else s['low_income_population'],analysis_value_status=replacement['status'] if replacement else 'source_observed_or_missing'))
 for row in buffers.sort_values('corridor_id').itertuples():
  cid=int(row.corridor_id);catchment=row.geometry;pop=income=mean_income=0.;pieces=[];affected=[];missing=[];zeros=[]
  for idx in tracts.sindex.query(catchment,predicate='intersects'):
   source=tracts.iloc[idx];ct=str(source['CTUID']);geometry=source.geometry
   intersection=catchment.intersection(geometry)
   if intersection.area<=1e-6:continue
   fraction=intersection.area/geometry.area;s=counts[ct]
   p=float(s['population_2021']) if s['population_2021']!='' else None
   low=float(s['low_income_population']) if s['low_income_population']!='' else None
   alt=low;status='source_observed';rep=replacements_by_id.get(ct)
   if low is None and p==0:low=alt=0.;status='zero_contribution_from_observed_zero_total_population';zeros.append(ct)
   elif low is None and rep:
    low=rep['primary'];alt=rep['mean'];status=rep['status'];affected.append(ct)
   if p is None or low is None:missing.append(ct)
   if p is not None:pop+=fraction*p
   if low is not None:income+=fraction*low;mean_income+=fraction*alt
   pieces.append(intersection)
   allocations.append(dict(corridor_id=cid,CTUID=ct,area_fraction=fraction,source_population_2021=s['population_2021'],source_low_income_population=s['low_income_population'],source_low_income_flag=s['low_income_population_source_flag'],analysis_low_income_count=low if low is not None else '',mean_sensitivity_low_income_count=alt if alt is not None else '',allocated_population=fraction*p if p is not None else '',allocated_low_income=fraction*low if low is not None else '',allocated_low_income_mean=fraction*alt if alt is not None else '',value_status=status))
  coverage=unary_union(pieces)
  if sum(g.area for g in pieces)-coverage.area>1:raise ValueError('Overlapping CT land support')
  available=not missing and pop>0;share=income/pop if available else ''
  if available and not 0<=share<=1:raise ValueError('Invalid share')
  rows.append(dict(corridor_id=cid,**{KEY:share},low_income_population_estimate=income if available else '',total_population_estimate=pop if available else '',mean_sensitivity_share=mean_income/pop if available else '',allocation_method='ct_area_fraction_uniform_density',estimation_status='pilot_estimate' if available else 'pending_source_counts',value_status='suppressed_CT_imputed' if affected else 'area_weighted_observed_counts',imputed_CTUIDs=';'.join(sorted(affected)),missing_CTUIDs=';'.join(sorted(missing)),structural_zero_CTUIDs=';'.join(sorted(zeros)),geographic_review_status='pending',intersecting_CT_count=len(pieces),area_outside_CT_cartographic_frame_m2=catchment.difference(coverage).area,source_id='STATCAN2021_LIM_PROFILE;STATCAN2021_CT_BOUNDARIES;RNF2021_ENDPOINT_PROXY',notes='Uniform within-CT density; LIM count / all-resident population (custom proxy, not official LIM prevalence). Income reference 2020. Provisional road geometry; 7 general shortest-road proxies versus 17 named-road proxies; cartographic coastline and endpoint reviews pending.'+(' User-authorized suppressed_CT_imputed; municipal peer-rate median primary, mean sensitivity; source blanks preserved.' if affected else '')))
 write(output/'corridor_CT_allocations.csv',allocations);write(ROOT/'data/census_ct_analysis_v0.5.csv',analysis_counts)
 path=Path(model_path or ROOT/'data/supplemental_model_inputs_v0.5.csv');write(path,rows)
 summary=dict(coverage_count=sum(r[KEY]!='' for r in rows),corridor_count=24,missing_corridor_ids=[r['corridor_id'] for r in rows if r[KEY]==''],suppression_affected_corridors=[r['corridor_id'] for r in rows if r['imputed_CTUIDs']],suppressed_CT_replacements=trace,max_mean_vs_median_share_change=max(abs(r[KEY]-r['mean_sensitivity_share']) for r in rows if r[KEY]!=''),all_geographic_reviews_pending=True,source_counts_preserved=True,model_ready=False,allocation_method='ct_area_fraction_uniform_density')
 (output/'equity_batch_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));return rows
if __name__=='__main__':calculate()
