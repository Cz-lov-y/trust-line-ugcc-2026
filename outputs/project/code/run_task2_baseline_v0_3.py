"""Executable assumption-only two-technology MCDA with visible switching limits.

No reference fact, complete-capital flag or strict feasibility result is rewritten.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import numpy as np

from screen_tech_policy_v0_2 import classify

ROOT=Path(__file__).resolve().parents[1]
CRITERIA=('cost_effectiveness','ridership','time_saving')
MODES=('BRT','LRT')


def finite_nonnegative(value,positive=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or (positive and value==0):
        raise ValueError('Expected finite nonnegative number, positive where required')
    return value


def validate_inputs(values,ceiling):
    for key in ('brt_cost_cad','lrt_cost_cad','lrt_to_brt_ridership_ratio'):
        finite_nonnegative(values[key],positive=True)
    for key in ('brt_time_saving_min','lrt_time_saving_min'):
        finite_nonnegative(values[key])
    finite_nonnegative(ceiling,positive=True)
    if max(values['brt_cost_cad'],values['lrt_cost_cad'])>ceiling:
        raise ValueError('Hypothetical point cost breaches the unchanged capital ceiling')


def raw_criteria(values,definition='ridership_index_per_cost_billion'):
    costs=np.array([values['brt_cost_cad'],values['lrt_cost_cad']],float)/1e9
    demand=np.array([1,values['lrt_to_brt_ridership_ratio']],float)
    times=np.array([values['brt_time_saving_min'],values['lrt_time_saving_min']],float)
    if definition=='ridership_index_per_cost_billion':efficiency=demand/costs
    elif definition=='inverse_cost_billion':efficiency=1/costs
    else:raise ValueError('Unknown efficiency definition')
    return np.column_stack((efficiency,demand,times))


def normalize(raw,method='ratio_to_best'):
    raw=np.asarray(raw,dtype=float)
    if raw.shape!=(2,3) or not np.isfinite(raw).all() or (raw<0).any():
        raise ValueError('Expected two alternatives and three finite nonnegative benefit criteria')
    hi=raw.max(axis=0);lo=raw.min(axis=0)
    if method=='ratio_to_best':
        return np.divide(raw,hi,out=np.zeros_like(raw),where=hi>0)
    if method=='minmax':
        span=hi-lo
        return np.divide(raw-lo,span,out=np.full_like(raw,.5),where=span>1e-12)
    raise ValueError('Unknown normalization')


def score(utilities,weights):
    weights=np.asarray(weights,dtype=float)
    if weights.shape!=(3,) or not np.isfinite(weights).all() or (weights<0).any() or not math.isclose(float(weights.sum()),1,abs_tol=1e-12):
        raise ValueError('Three nonnegative weights must sum to one')
    return np.asarray(utilities)@weights


def winner(scores):
    delta=float(scores[0]-scores[1])
    return 'tie' if abs(delta)<=1e-12 else ('BRT' if delta>0 else 'LRT')


def efficiency_weight_switch(utilities):
    delta=np.asarray(utilities)[0]-np.asarray(utilities)[1]
    # Split the remaining budget equally between ridership and time savings.
    rest=float((delta[1]+delta[2])/2)
    denominator=float(delta[0]-rest)
    if abs(denominator)<1e-12:return None
    root=-rest/denominator
    return root if 0<=root<=1 else None


def uniform_simplex_brt_share(utilities):
    delta=np.asarray(utilities)[0]-np.asarray(utilities)[1]
    if not (delta[0]>0 and delta[1]<0 and delta[2]<0):return None
    # Winning triangle adjacent to efficiency vertex / full weight triangle.
    return float(delta[0]/(delta[0]-delta[1])*delta[0]/(delta[0]-delta[2]))


def write_csv(path,rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def run(root=ROOT):
    config=json.loads((root/'data/task2_baseline_assumptions_v0.3.json').read_text())
    policy_config=json.loads((root/config['policy_file']).read_text())
    strict_policy=json.loads((root/policy_config['strict_policy_file']).read_text())
    alternatives=json.loads((root/policy_config['strict_input_file']).read_text())
    declarations={a['technology_id']:a for a in policy_config['alternatives']}
    admitted={a['technology_id'] for a in alternatives if classify(a,strict_policy,declarations[a['technology_id']])['provisional_shortlisted']}
    if admitted!=set(MODES):raise ValueError('The current provisional gate must admit exactly BRT and LRT')
    for key in ('corridor_id','length_km','capital_ceiling_cad'):
        if config[key]!=strict_policy[key]:raise ValueError(f'Fixed constraint changed: {key}')
    if config['complete_capital_estimates'] is not False or config['implementation_feasibility_certified'] is not False:
        raise ValueError('Hypothetical assumptions cannot certify complete capital or engineering feasibility')
    if config['absolute_daily_ridership'] is not None:raise ValueError('This version uses relative demand, not invented absolute forecasts')
    if tuple(config['criteria'])!=CRITERIA:raise ValueError('Criterion order must match the declared weights')
    finite_nonnegative(config['signal_count'],positive=True)
    if not isinstance(config['signal_count'],int) or isinstance(config['signal_count'],bool):raise ValueError('Signal count must be an integer')
    if not isinstance(config['weight_draws'],int) or isinstance(config['weight_draws'],bool) or config['weight_draws']<1:raise ValueError('Positive integer draw count required')
    out=root/'outputs/task2_v0.3';out.mkdir(parents=True,exist_ok=True)
    base=config['baseline'];validate_inputs(base,config['capital_ceiling_cad'])
    raw=raw_criteria(base)
    inputs=[]
    for i,mode in enumerate(MODES):
        cost=base['brt_cost_cad' if i==0 else 'lrt_cost_cad']
        inputs.append(dict(technology_id=mode,scenario_id=config['baseline_scenario'],cost_cad=cost,
            cost_cad_per_km=cost/config['length_km'],ridership_index=float(raw[i,1]),
            absolute_daily_ridership='',time_saving_min_one_way=float(raw[i,2]),
            efficiency_ridership_index_per_cad_billion=float(raw[i,0]),
            assumed_signals=config['signal_count'],implied_seconds_saved_per_signal=float(raw[i,2]*60/config['signal_count']),
            point_cost_within_cap=cost<=config['capital_ceiling_cad'],
            cost_is_complete_capital_estimate=False,implementation_feasibility_certified=False,
            value_status='user_assumption_only',value_source='data/task2_baseline_assumptions_v0.3.json'))
    write_csv(out/'baseline_inputs.csv',inputs)
    scenarios=[(config['baseline_scenario'],base)]
    scenarios.extend((s['scenario_id'],dict(base,**s['overrides'])) for s in config['stress_scenarios'])
    if len({sid for sid,_ in scenarios})!=len(scenarios):raise ValueError('Scenario IDs must be unique')
    results=[];methods=[]
    for efficiency in ('ridership_index_per_cost_billion','inverse_cost_billion'):
        for method in ('ratio_to_best','minmax'):
            methods.append((efficiency,method))
            for sid,values in scenarios:
                validate_inputs(values,config['capital_ceiling_cad'])
                utility=normalize(raw_criteria(values,efficiency),method)
                for profile,weights in config['weight_profiles'].items():
                    scores=score(utility,weights);chosen=winner(scores)
                    for i,mode in enumerate(MODES):
                        results.append(dict(scenario_id=sid,efficiency_definition=efficiency,normalization=method,
                            weight_profile=profile,technology_id=mode,score=float(scores[i]),
                            utility_efficiency=float(utility[i,0]),utility_ridership=float(utility[i,1]),utility_time=float(utility[i,2]),
                            efficiency_weight=weights[0],ridership_weight=weights[1],time_weight=weights[2],
                            scenario_winner=chosen,assumptions_only=True))
    write_csv(out/'scenario_scores.csv',results)
    baseline_rows=[r for r in results if r['scenario_id']==config['baseline_scenario'] and r['efficiency_definition']==config['primary_efficiency_definition'] and r['normalization']==config['primary_normalization']]
    write_csv(out/'baseline_scores.csv',baseline_rows)
    rng=np.random.Generator(np.random.PCG64(config['weight_seed']))
    weights=rng.dirichlet(np.ones(3),size=config['weight_draws'])
    draws=[dict(draw_id=i+1,efficiency_weight=float(w[0]),ridership_weight=float(w[1]),time_weight=float(w[2])) for i,w in enumerate(weights)]
    summaries=[];switches=[]
    for efficiency,method in methods:
        key=efficiency+'__'+method;utility=normalize(raw_criteria(base,efficiency),method)
        margins=weights@(utility[0]-utility[1])
        winners=np.where(abs(margins)<=1e-12,'tie',np.where(margins>0,'BRT','LRT'))
        for row,chosen in zip(draws,winners):row[key+'_winner']=str(chosen)
        summaries.append(dict(efficiency_definition=efficiency,normalization=method,
            fixed_input_scenario=config['baseline_scenario'],draws=config['weight_draws'],seed=config['weight_seed'],
            brt_weight_share=float(np.mean(winners=='BRT')),lrt_weight_share=float(np.mean(winners=='LRT')),
            tie_weight_share=float(np.mean(winners=='tie')),exact_uniform_brt_share=uniform_simplex_brt_share(utility),
            interpretation='Illustrative criterion-weight support with fixed assumed inputs; not probability of project success or statistical confidence'))
        switches.append(dict(efficiency_definition=efficiency,normalization=method,
            efficiency_weight_at_tie=efficiency_weight_switch(utility),
            other_weights='(1-efficiency_weight)/2 each; baseline cost/demand/time fixed'))
    write_csv(out/'weight_draws.csv',draws);write_csv(out/'weight_support.csv',summaries);write_csv(out/'weight_switches.csv',switches)
    primary=normalize(raw,config['primary_normalization']);equal=score(primary,config['weight_profiles']['equal'])
    curve=[]
    for efficiency_weight in np.linspace(0,1,101):
        w=[efficiency_weight,(1-efficiency_weight)/2,(1-efficiency_weight)/2];scores=score(primary,w)
        curve.append(dict(efficiency_weight=float(efficiency_weight),brt_score=float(scores[0]),lrt_score=float(scores[1])))
    write_csv(out/'weight_switch_curve.csv',curve)
    summary=dict(corridor_id=23,length_km=7.101,
        assumption_model_ready=True,complete_capital_estimates=False,
        implementation_feasibility_certified=False,absolute_daily_ridership_forecast_available=False,
        task2_complete=False,selected_technology=None,
        baseline_equal_weight_scenario_winner=winner(equal),
        baseline_equal_weight_scores=dict(zip(MODES,map(float,equal))),
        efficiency_weight_switch=efficiency_weight_switch(primary),
        alternative_minmax_equal_weight_winner=winner(score(normalize(raw,'minmax'),config['weight_profiles']['equal'])),
        robust_winner_across_declared_methods=len({r['scenario_winner'] for r in results if r['scenario_id']==config['baseline_scenario'] and r['weight_profile']=='equal'})==1,
        note='Provisional assumption-only scores. Ratio normalization preserves relative magnitudes; with two alternatives minmax collapses each varying criterion to 0/1. Do not call scenario winner a final feasible recommendation.')
    (out/'model_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    files=[root/'data/task2_baseline_assumptions_v0.3.json',root/config['policy_file'],root/policy_config['strict_policy_file'],
           root/policy_config['strict_input_file'],root/'evidence/tech_evidence_v0.1.csv',Path(__file__)]
    files+=sorted(out.glob('*.csv'))+[out/'model_summary.json']
    (out/'run_manifest.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
    return summary


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
