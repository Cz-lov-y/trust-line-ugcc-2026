"""Shared source-preserving tier/dependency contracts for v0.6."""
from pathlib import Path
import csv,json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/'outputs/tiered_v0.6'
POLICY=ROOT/'data/tiered_model_policy_v0.6.json'
def read(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,rows):
 Path(path).parent.mkdir(parents=True,exist_ok=True)
 with Path(path).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def dump(path,obj):Path(path).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def policy(root=ROOT):return json.loads((Path(root)/'data/tiered_model_policy_v0.6.json').read_text())
def tiers(master,config):
 byid={int(r['corridor_id']):r for r in master}
 if len(master)!=24 or set(byid)!=set(range(1,25)):raise ValueError('Exactly 24 unique source corridors required')
 main=sorted(i for i,r in byid.items() if r['baseline_scenario_id']=='CITY_BASE_0')
 conditional=sorted(set(byid)-set(main))
 if main!=config['main_tier_ids'] or conditional!=config['conditional_tier_ids']:raise ValueError('Policy tier IDs conflict with source baselines')
 direct={}
 for cid,r in byid.items():
  if cid in main:direct[cid]=[]
  else:
   prefix='CITY_BASE_AFTER_'
   if not r['baseline_scenario_id'].startswith(prefix):raise ValueError('Unknown baseline')
   direct[cid]=[int(r['baseline_scenario_id'][len(prefix):])]
 def closure(cid,stack=()):
  if cid in stack or cid not in direct:raise ValueError('Invalid/cyclic dependency')
  result=[]
  for p in direct[cid]:
   for parent in [*closure(p,(*stack,cid)),p]:
    if parent not in result:result.append(parent)
  return result
 result={}
 for cid,r in byid.items():
  parents=closure(cid)
  declared={int(v) for v in r['prerequisite_corridor_ids'].split(';') if v}
  if set(parents)!=declared:raise ValueError('Prerequisite closure does not match source metadata')
  result[cid]=parents
 return byid,main,conditional,result

def rank_intervals(scores,tolerance=1e-12):
 """Worst rank is conservative at a tied top-k boundary."""
 lows=[];highs=[]
 for s in scores:
  lows.append(1+sum(v>s+tolerance for v in scores));highs.append(sum(v>=s-tolerance for v in scores))
 return lows,highs
