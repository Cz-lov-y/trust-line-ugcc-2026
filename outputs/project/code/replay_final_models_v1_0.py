"""Offline numerical replay of both delivered decision models.

Uses original City cells and delivered Census overlay estimates. It does not
rebuild GIS overlays; source acquisition/geometry pipelines remain in the repo.
Run from the ZIP or repository: python outputs/project/code/replay_final_models_v1_0.py
"""
from pathlib import Path
import argparse
import csv
import json
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def ranks(scores):
    return [sum(v>=s-1e-12 for v in scores) for s in scores]


def replay(root=ROOT,out=None):
    root=Path(root);out=Path(out) if out else root/'outputs/final_replay_v1.0';out.mkdir(parents=True,exist_ok=True)
    config=json.loads((root/'data/jane_stress_policy_v0.7.json').read_text())
    master=read(root/'data/corridor_master_v0.1.csv');ids={int(r['corridor_id']) for r in master}
    if ids!=set(range(1,25)) or len(master)!=24:raise ValueError('All 24 corridors must be preserved')
    main=config['main_tier_ids'];conditional=config['conditional_tier_ids'];fields=config['fields']
    if set(main)&set(conditional) or set(main)|set(conditional)!=ids:raise ValueError('Invalid 16/8 partition')
    if len(fields)!=5 or 'current_ridership' in fields:raise ValueError('Disputed indicator cannot re-enter the active model')
    source={int(r['corridor_id']):r for r in read(root/'data/city_standardized_scores_v0.1.csv')}
    equity={int(r['corridor_id']):float(r[fields[-1]]) for r in read(root/'data/supplemental_model_inputs_v0.5.csv')}
    mu=float(np.mean([equity[i] for i in main]));sd=float(np.std([equity[i] for i in main],ddof=0))
    contextual=[];main_ranks=[]
    expected={(r['city_method'],r['weight_profile'],int(r['corridor_id'])):float(r['contextual_priority_index']) for r in read(root/'outputs/model_argument_v0.8/all24_contextual_scores.csv')}
    for method in config['city_methods']:
        replacements={}
        for field in fields[:-1]:
            observed=[float(r[field]) for r in source.values() if r[field]!='']
            replacements[field]=min(observed) if method=='imputed_conservative_min' else float(np.mean(observed))
        matrix={i:[*[float(source[i][f]) if source[i][f]!='' else replacements[f] for f in fields[:-1]],(equity[i]-mu)/sd] for i in range(1,25)}
        for profile,weights in config['weight_profiles'].items():
            if not math.isclose(sum(weights),1,abs_tol=1e-12):raise ValueError('Invalid weights')
            scores={i:sum(w*v for w,v in zip(weights,matrix[i])) for i in ids}
            for i in range(1,25):
                if not math.isclose(scores[i],expected[method,profile,i],abs_tol=1e-11):raise ValueError('Part 1 score differs from delivered result')
                contextual.append(dict(corridor_id=i,city_method=method,weight_profile=profile,tier='main' if i in main else 'conditional',contextual_score=scores[i],unanchored_cross_baseline_rank='not_computed'))
            main_ranks.append(ranks([scores[i] for i in main]))
    rng=np.random.Generator(np.random.PCG64(config['seed']))
    selectors=rng.integers(0,2,config['draws'])*3+rng.integers(0,3,config['draws'])
    rank_matrix=np.array(main_ranks);acceptance=[]
    old={int(r['corridor_id']):r for r in read(root/'outputs/jane_stress_v0.7/rank_acceptability_comparison.csv')}
    for j,i in enumerate(main):
        support=float(np.mean(rank_matrix[selectors,j]<=5))
        if not math.isclose(support,float(old[i]['five_top5_frequency']),abs_tol=1e-12):raise ValueError('Part 1 paired-draw support differs')
        acceptance.append(dict(corridor_id=i,top5_support_in_six_case_draws=support,best_rank=int(rank_matrix[:,j].min()),worst_rank=int(rank_matrix[:,j].max())))
    write(out/'part1_all24_contextual_scores.csv',contextual);write(out/'part1_main_rank_support.csv',acceptance)
    cfg=json.loads((root/'data/task2_baseline_assumptions_v0.3.json').read_text());b=cfg['baseline']
    costs=np.array([b['brt_cost_cad'],b['lrt_cost_cad']])/1e9
    demand=np.array([1,b['lrt_to_brt_ridership_ratio']]);times=np.array([b['brt_time_saving_min'],b['lrt_time_saving_min']])
    raw=np.column_stack((demand/costs,demand,times));utility=raw/raw.max(axis=0)
    old2={(r['weight_profile'],r['technology_id']):float(r['score']) for r in read(root/'outputs/task2_v0.3/baseline_scores.csv')}
    technology=[]
    for profile,w in cfg['weight_profiles'].items():
        score=utility@np.asarray(w)
        for j,mode in enumerate(['BRT','LRT']):
            if not math.isclose(float(score[j]),old2[profile,mode],abs_tol=1e-12):raise ValueError('Part 2 score differs')
            technology.append(dict(technology_id=mode,weight_profile=profile,score=float(score[j]),cost_cad=float(costs[j]*1e9),relative_ridership=float(demand[j]),assumed_time_saving_min=float(times[j]),value_status='declared_scenario_not_observed_forecast'))
    write(out/'part2_technology_comparison.csv',technology)
    delta=utility[0]-utility[1];rest=(delta[1]+delta[2])/2;switch=float(-rest/(delta[0]-rest))
    weights=np.random.Generator(np.random.PCG64(cfg['weight_seed'])).dirichlet(np.ones(3),cfg['weight_draws'])
    support=float(np.mean(weights@delta>0))
    expected_support=next(r for r in read(root/'outputs/task2_v0.3/weight_support.csv') if r['efficiency_definition']=='ridership_index_per_cost_billion' and r['normalization']=='ratio_to_best')
    if not math.isclose(support,float(expected_support['brt_weight_share']),abs_tol=1e-12):raise ValueError('Part 2 preference support differs')
    result=dict(model_replay_passed=True,corridors_preserved=24,main_corridors=16,conditional_corridors=8,
        part1_context_rows=len(contextual),part1_costs_used=False,equity_calibration_mean=mu,equity_calibration_sd=sd,
        selected_corridor=23,selected_technology='BRT',part2_profile_rows=len(technology),
        equal_scores=dict(zip(['BRT','LRT'],map(float,utility@np.array([1/3]*3)))),
        efficiency_weight_switch=switch,fixed_input_BRT_preference_support=support,
        spatial_overlay_rebuilt=False,full_capital_or_engineering_certified=False)
    (out/'replay_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path)
    a=p.parse_args();print(json.dumps(replay(a.root,a.output),indent=2))
