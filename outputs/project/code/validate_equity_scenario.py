"""Standard-library replay of actual Census substitutions and allocation totals."""
from pathlib import Path
import csv,json,math,statistics,hashlib

def read(p):
 with Path(p).open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def close(a,b):return math.isfinite(float(a)) and math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-8)
def validate_equity_scenario(root,column,dataset):
 errors=[];root=Path(root);e=root/'evidence/corridor_batch_v0.5';o=root/'outputs/corridor_batch_v0.5'
 try:
  if column!='low_income_population_share_500m':raise ValueError('Wrong equity column')
  for name in ['profiles_acquisition_manifest.json','census_acquisition_manifest.json']:
   manifest=json.loads((e/name).read_text());resources=manifest if isinstance(manifest,list) else manifest['resources']
   for record in resources:
    if record.get('status','acquired')!='acquired':raise ValueError('Source acquisition incomplete')
    if hashlib.sha256((root/record['file']).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Official source archive checksum mismatch')
  manifest=json.loads((e/'census_acquisition_manifest.json').read_text())
  for filekey,hashkey in [('geometry_file','geometry_sha256'),('processed_file','processed_sha256')]:
   if hashlib.sha256((root/manifest[filekey]).read_bytes()).hexdigest()!=manifest[hashkey]:raise ValueError('Census processed/boundary checksum mismatch')
  if hashlib.sha256((o/'corridor_buffers_500m.geojson').read_bytes()).hexdigest()!=manifest['buffer_sha256']:raise ValueError('Census buffer checksum mismatch')
  def index(paths):
   result={}
   for p in paths:
    for r in read(p):
     if (r['GENDER'],r['STATISTIC'],r['TIME_PERIOD'])!=('1','1','2021'):raise ValueError('Unexpected Census dimensions')
     key=r['ALT_GEO_CODE'],r['CHARACTERISTIC']
     if key in result:raise ValueError('Duplicate Census profile cell')
     result[key]=r
   return result
  def value(source,geo,char):
   r=source.get((geo,char),{})
   if not r or r.get('FLAG') or r.get('OBS_VALUE','')=='':return None
   n=float(r['OBS_VALUE'])
   if not math.isfinite(n) or n<0:raise ValueError('Invalid count')
   return n
  peers=index(sorted(e.glob('peer_CT_profile_*.csv')));das=index([e/'affected_DA_profiles.csv'])
  ids=set(json.loads((e/'toronto_peer_CT_ids.json').read_text()))
  if {g for g,c in peers}!=ids:raise ValueError('Incomplete municipal peer source pool')
  geography={r['CTUID']:r for r in read(e/'peer_CT_CSD_membership_check.csv')}
  if set(geography)!=ids or any(r['CSDUIDs']!='3520005' or r['entire_CT_in_Toronto']!='True' for r in geography.values()):raise ValueError('Peer municipal membership inconsistent')
  rates=[value(peers,ct,'326')/value(peers,ct,'1') for ct in ids if value(peers,ct,'1') not in (None,0) and value(peers,ct,'326') is not None]
  median,mean=statistics.median(rates),statistics.fmean(rates)
  membership=json.loads((e/'suppressed_CT_DA_membership.json').read_text());replacement={}
  traces={r['CTUID']:r for r in read(o/'suppression_imputation_trace.csv')}
  if set(traces)!=set(membership):raise ValueError('Suppression trace membership mismatch')
  for ct,daids in membership.items():
   pop=value(peers,ct,'1');totals=[value(das,d,'1') for d in daids];lows=[value(das,d,'326') for d in daids]
   if pop is None or None in totals or sum(totals)!=pop:raise ValueError('DA universe/population incomplete')
   complete=None not in lows
   primary=sum(lows) if complete else median*pop;alt=primary if complete else mean*pop
   status='reconstructed_from_complete_DA_sum' if complete else 'suppressed_CT_imputed'
   t=traces[ct]
   if t['method']!=status or t['all_DA_ids']!=';'.join(daids) or int(t['peer_count'])!=len(rates) or int(t['DA_available_LIM_count'])!=sum(v is not None for v in lows):raise ValueError('False reconstruction/imputation provenance')
   if not all(close(t[k],v) for k,v in [('analysis_low_income_count',primary),('mean_sensitivity_low_income_count',alt),('peer_rate_median',median),('peer_rate_mean',mean)]):raise ValueError('Census imputation statistic mismatch')
   replacement[ct]=(primary,alt,status)
  counts={r['CTUID']:r for r in read(root/'data/census_ct_batch_v0.5.csv')};sums={};seen=set();affected={}
  for a in read(o/'corridor_CT_allocations.csv'):
   cid,ct=a['corridor_id'],a['CTUID'];key=(cid,ct)
   if key in seen:raise ValueError('Duplicate CT/corridor allocation')
   seen.add(key);s=counts[ct];fraction=float(a['area_fraction'])
   if not math.isfinite(fraction) or not 0<fraction<=1+1e-9:raise ValueError('Invalid CT allocation fraction')
   if a['source_low_income_population']!=s['low_income_population'] or a['source_low_income_flag']!=s['low_income_population_source_flag']:raise ValueError('Source suppression overwritten')
   pop=float(s['population_2021']);low=float(s['low_income_population']) if s['low_income_population']!='' else None;alt=low;status='source_observed'
   if low is None and pop==0:low=alt=0.;status='zero_contribution_from_observed_zero_total_population'
   elif low is None and ct in replacement:low,alt,status=replacement[ct];affected.setdefault(cid,set()).add(ct)
   if low is None:raise ValueError('Blank Census contribution cannot be waived by an imputed label')
   if a['value_status']!=status:raise ValueError('Wrong allocation provenance')
   for k,v in [('analysis_low_income_count',low),('mean_sensitivity_low_income_count',alt),('allocated_population',fraction*pop),('allocated_low_income',fraction*low),('allocated_low_income_mean',fraction*alt)]:
    if not close(a[k],v):raise ValueError('CT allocation does not match source/statistic')
   total=sums.setdefault(cid,[0.,0.,0.]);total[0]+=fraction*pop;total[1]+=fraction*low;total[2]+=fraction*alt
  if set(sums)!={str(i) for i in range(1,25)}:raise ValueError('Equity allocation coverage is not 24/24')
  for cid,(pop,low,alt) in sums.items():
   row=dataset.get(cid,{})
   if pop<=0:raise ValueError('Nonpositive catchment denominator')
   for k,v in [(column,low/pop),('low_income_population_estimate',low),('total_population_estimate',pop),('mean_sensitivity_share',alt/pop)]:
    if not close(row.get(k,''),v):raise ValueError('Equity model input does not reproduce CT allocations at corridor '+cid)
   if row.get('imputed_CTUIDs','')!=';'.join(sorted(affected.get(cid,set()))):raise ValueError('Imputed CT list mismatch')
   expected='suppressed_CT_imputed' if affected.get(cid) else 'area_weighted_observed_counts'
   if row.get('value_status')!=expected:raise ValueError('Equity provenance status mismatch')
 except (ValueError,KeyError,TypeError,OSError,ZeroDivisionError) as error:errors.append('Census scenario verification: '+str(error))
 return errors
