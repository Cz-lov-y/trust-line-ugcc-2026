"""Replay limited-scope readiness; labels alone cannot admit a tiered model."""
import csv,json,math,statistics
from pathlib import Path
from tiered_common import read,sha,tiers,rank_intervals

def validate_tiered_contract(root,core_ready):
 root=Path(root);issues=[];config={};summary={}
 try:
  config=json.loads((root/'data/tiered_model_policy_v0.6.json').read_text())
  master,main,conditional,closure=tiers(read(root/'data/corridor_master_v0.1.csv'),config)
  if config['fields']!=['current_speed','unimproved_load','current_max_load','current_ridership','competitiveness','low_income_population_share_500m']:raise ValueError('Tiered model fields must exclude cost-bearing measures')
  selection=json.loads((root/'data/model_input_selection_v0.1.json').read_text())
  if selection.get('selected_indicator_ids')!=config['fields']:raise ValueError('Exactly six declared core fields required')
  admissions=json.loads((root/'data/workbook_records_v0.1.json').read_text())['indicator_admission']
  chosen=[r for r in admissions if r['indicator_id'] in config['fields']]
  if len(chosen)!=6 or {r['indicator_id'] for r in chosen}!=set(config['fields']):raise ValueError('Tiered admissions incomplete')
  if any(r.get('admission_status')!='admitted_with_limitations' or r.get('model_admission_scope')!='tiered_proxy_scenario_with_declared_limitations' or r.get('cost_dependence') not in {'no','none'} for r in chosen):raise ValueError('Tiered admission scope/cost contract inconsistent')
  if config['draws']!=10000 or not isinstance(config['seed'],int):raise ValueError('Expected 10000 fixed-seed draws')
  if config['city_methods']!=['imputed_conservative_min','imputed_observed_mean'] or set(config['weight_profiles'])!={'equal','ridership_priority','equity_priority'}:raise ValueError('Unexpected scenario support')
  for w in config['weight_profiles'].values():
   if len(w)!=6 or any(not math.isfinite(v) or v<0 for v in w) or not math.isclose(sum(w),1,abs_tol=1e-12):raise ValueError('Invalid weight profile')
  if not config.get('geometry_policy') or len(config.get('limitations',[]))<5:raise ValueError('Proxy assumptions/limitations undeclared')
  manifest=json.loads((root/'outputs/tiered_v0.6/run_manifest.json').read_text())
  for section in ['source_files','output_files']:
   if not manifest.get(section):raise ValueError('No auditable run manifest')
   for rel,digest in manifest[section].items():
    path=(root/rel).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file() or sha(path)!=digest:raise ValueError('Missing or changed tiered evidence: '+rel)
  # Recompute normalized inputs and all six score/rank vectors, independent of stored ranks.
  source={int(r['corridor_id']):r for r in read(root/'data/city_standardized_scores_v0.1.csv')}
  citytables=[{int(r['corridor_id']):r for r in read(root/path)} for path in ['data/city_analysis_inputs_v0.4.csv','data/city_mean_sensitivity_v0.4.csv']]
  eq={int(r['corridor_id']):float(r['low_income_population_share_500m']) for r in read(root/'data/supplemental_model_inputs_v0.5.csv')}
  mu=statistics.fmean(eq[cid] for cid in main);sd=statistics.pstdev(eq[cid] for cid in main)
  if sd<=0 or set(eq)!=set(range(1,25)):raise ValueError('Invalid equity calibration')
  cases=[]
  for method,table in zip(config['city_methods'],citytables):
   if set(table)!=set(range(1,25)):raise ValueError('City scenario coverage incomplete')
   for f in config['fields'][:5]:
    values=[float(r[f]) for r in source.values() if r[f]!=''];replacement=min(values) if method=='imputed_conservative_min' else statistics.fmean(values)
    for cid,r in table.items():
     expected=float(source[cid][f]) if source[cid][f]!='' else replacement
     flag='source_observed' if source[cid][f]!='' else method
     if not math.isclose(float(r[f]),expected,abs_tol=1e-12) or r[f+'_value_status']!=flag:raise ValueError('City method provenance mismatch')
   matrix=[[*[float(table[cid][f]) for f in config['fields'][:5]],(eq[cid]-mu)/sd] for cid in main]
   for profile,weights in config['weight_profiles'].items():
    scores=[sum(v*w for v,w in zip(row,weights)) for row in matrix];lo,hi=rank_intervals(scores)
    cases.append(dict(method=method,profile=profile,scores=scores,lo=lo,hi=hi))
  stored=read(root/'outputs/tiered_v0.6/six_scenario_scores.csv')
  if len(stored)!=96 or len({(r['case_id'],r['corridor_id']) for r in stored})!=96:raise ValueError('Six-scenario score grid incomplete')
  for r in stored:
   case=cases[int(r['case_id'])];j=main.index(int(r['corridor_id']))
   if not math.isclose(float(r['score']),case['scores'][j],abs_tol=1e-10) or int(r['rank_best'])!=case['lo'][j] or int(r['rank_worst'])!=case['hi'][j]:raise ValueError('Score/rank replay mismatch')
  draws=read(root/'outputs/tiered_v0.6/monte_carlo_draws.csv')
  if len(draws)!=10000 or [int(r['draw_id']) for r in draws]!=list(range(1,10001)):raise ValueError('Monte Carlo draw IDs incomplete')
  freq=[0]*6
  for r in draws:
   k=int(r['case_id']);case=cases[k];freq[k]+=1
   if r['city_method']!=case['method'] or r['weight_profile']!=case['profile']:raise ValueError('Draw selector/provenance mismatch')
   if any(int(r[f'corridor_{cid}_rank_worst'])!=case['hi'][j] for j,cid in enumerate(main)):raise ValueError('Draw ranks conflict with source scenarios')
  if min(freq)<=0:raise ValueError('Monte Carlo failed to sample every scenario')
  accept=read(root/'outputs/tiered_v0.6/rank_acceptability.csv')
  if len(accept)!=16 or {int(r['corridor_id']) for r in accept}!=set(main):raise ValueError('Rank acceptability includes wrong tier')
  for r in accept:
   j=main.index(int(r['corridor_id']));exact=sum(c['hi'][j]<=5 for c in cases)/6;observed=sum(freq[k] for k,c in enumerate(cases) if c['hi'][j]<=5)/10000
   if not math.isclose(float(r['top5_frequency']),observed,abs_tol=1e-12) or not math.isclose(float(r['exact_top5_frequency']),exact,abs_tol=1e-12):raise ValueError('Top-five acceptability not reproduced')
   expected=observed>.9 and exact>.9
   if (r['high_confidence_candidate']=='True')!=expected:raise ValueError('Unsupported high-confidence claim')
  summary=json.loads((root/'outputs/tiered_v0.6/tiered_model_summary.json').read_text())
  if summary['main_tier_corridor_ids']!=main or summary['conditional_tier_corridor_ids']!=conditional or summary['seed']!=config['seed'] or summary['draws']!=10000:raise ValueError('Tiered result policy mismatch')
  expected_candidates={int(r['corridor_id']) for r in accept if r['high_confidence_candidate']=='True'}
  if set(summary['high_confidence_top5_candidates'])!=expected_candidates:raise ValueError('High-confidence summary mismatch')
  expected_shortlist=sorted(accept,key=lambda r:(-float(r['exact_top5_frequency']),-float(r['exact_top3_frequency']),float(r['exact_mean_midpoint_rank']),int(r['worst_rank']),int(r['corridor_id'])))[:3]
  if summary['main_shortlist']!=[int(r['corridor_id']) for r in expected_shortlist]:raise ValueError('Shortlist does not follow declared exact-scenario rule')
  tierrows=read(root/'data/corridor_tiers_v0.6.csv')
  if len(tierrows)!=24 or {int(r['corridor_id']) for r in tierrows}!=set(range(1,25)):raise ValueError('All 24 corridor tier records required')
  for r in tierrows:
   cid=int(r['corridor_id'])
   if r['main_rank_eligible']!=str(cid in main) or r['prerequisite_closure']!=';'.join(map(str,closure[cid])):raise ValueError('Tier eligibility/dependency declaration conflicts with source')
  pairs=read(root/'outputs/tiered_v0.6/conditional_pair_analysis.csv')
  if len(pairs)!=8 or {int(r['corridor_id']) for r in pairs}!=set(conditional):raise ValueError('Conditional pair review incomplete')
  for r in pairs:
   if r['required_predecessors']!=';'.join(map(str,closure[int(r['corridor_id'])])) or r['main_absolute_rank']!='not_applicable' or r['City_score_bundle_total']!='not_additive_not_computed':raise ValueError('Conditional corridor was pooled or missing dependencies')
  declarations=read(root/'data/geometry_declarations_v0.6.csv')
  if len(declarations)!=24 or {int(r['corridor_id']) for r in declarations}!=set(range(1,25)):raise ValueError('Proxy geometry declarations incomplete')
  if any(r['proxy_declared']!='True' or not r['limitations'] or r['official_alignment_verified']!='False' for r in declarations):raise ValueError('Proxy geometry provenance undeclared')
  sensitivity=json.loads((root/'outputs/tiered_v0.6/woodbine_sensitivity_summary.json').read_text())
  if sensitivity.get('status')!='proxy_with_sensitivity_check' or sensitivity.get('completed') is not True or sensitivity.get('route_recalculations')!=18 or sensitivity.get('shared_anchor_cases')!=9:raise ValueError('Woodbine sensitivity not actually completed')
  tests=read(root/'outputs/tiered_v0.6/woodbine_anchor_sensitivity.csv')
  if len(tests)!=18 or len({(r['corridor_id'],r['anchor_case']) for r in tests})!=18:raise ValueError('Woodbine case coverage incomplete')
  for cid in [5,6]:
   subset=[r for r in tests if int(r['corridor_id'])==cid]
   if len(subset)!=9 or any(not 0<=float(r['low_income_population_share_500m'])<=1 for r in subset):raise ValueError('Woodbine sensitivity invalid')
   nominal=next(r for r in subset if r['anchor_case']=='nominal')
   if not math.isclose(float(nominal['low_income_population_share_500m']),eq[cid],abs_tol=1e-10):raise ValueError('Nominal Woodbine sensitivity failed reproduction')
  if not core_ready:issues.append('Core source/provenance validation is incomplete')
 except (OSError,ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as error:issues.append('Tiered contract: '+str(error))
 return dict(core_ready=bool(core_ready),limitations_ready=not issues,model_ready=bool(core_ready) and not issues,model_scope=config.get('readiness_scope','unverified'),limitations_flagged=True,limitations=config.get('limitations',[]),readiness_issues=issues,main_shortlist=summary.get('main_shortlist',[]),high_confidence_top5_candidates=summary.get('high_confidence_top5_candidates',[]),unrestricted_model_ready=False)
