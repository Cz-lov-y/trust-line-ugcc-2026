"""User-authorized provisional shortlist, preserving the v0.1 evidence gate.

A conservative policy exclusion is different from demonstrated physical
infeasibility. Conditional admission enables scenarios without changing source facts.
"""
from pathlib import Path
import csv
import hashlib
import json

from screen_tech_feasibility_v0_1 import screen

ROOT = Path(__file__).resolve().parents[1]


def classify(alternative, policy, declaration):
    strict = screen(alternative, policy)
    requested = declaration['requested_decision']
    if declaration['technology_id'] != strict['technology_id']:
        raise ValueError('Technology declaration mismatch')
    if requested not in ('conditional_pass', 'exclude_by_conservative_policy'):
        raise ValueError('Unknown policy decision')
    if set(declaration['required_condition_ids']) != {'COST','OPENING','ROW','DEPOT'}:
        raise ValueError('All four conditions must remain')
    if strict['screening_status'] == 'excluded':
        decision, basis = 'verified_fail', 'evidence_based_hard_failure'
    elif strict['screening_status'] == 'eligible_for_mcda':
        decision, basis = 'verified_pass', 'all_original_hard_gates_pass'
    elif requested == 'conditional_pass':
        decision, basis = 'conditional_pass', 'user_authorized_assumption_based_admission'
    else:
        decision, basis = 'policy_fail', 'user_authorized_conservative_exclusion'
    return dict(technology_id=strict['technology_id'], policy_decision=decision,
        decision_basis=basis, provisional_shortlisted=decision in ('conditional_pass','verified_pass'),
        strict_budget=strict['budget'], strict_schedule=strict['schedule'],
        strict_route_engineering=strict['route_engineering'], strict_depot=strict['depot'],
        verified_feasible=decision=='verified_pass',
        demonstrated_hard_failure=decision=='verified_fail',
        implementation_feasibility_certified=decision=='verified_pass',
        rationale=declaration['rationale'])


def read_csv(path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def run(root=ROOT):
    config_path=root/'data/task2_screening_policy_v0.2.json'
    config=json.loads(config_path.read_text())
    policy=json.loads((root/config['strict_policy_file']).read_text())
    alternatives=json.loads((root/config['strict_input_file']).read_text())
    if len(alternatives)!=3 or {a['technology_id'] for a in alternatives}!={'BRT','LRT','SUBWAY'}:
        raise ValueError('Three distinct technology dossiers required')
    for key in ('corridor_id','length_km','capital_ceiling_cad','planning_window_years','operational_deadline'):
        if config[key] != policy[key]:
            raise ValueError(f'Original hard constraint changed: {key}')
    declarations={a['technology_id']:a for a in config['alternatives']}
    if set(declarations)!={'BRT','LRT','SUBWAY'} or len(config['alternatives'])!=3:
        raise ValueError('Three distinct technology declarations required')
    evidence={r['evidence_id']:r for r in read_csv(root/'evidence/tech_evidence_v0.1.csv')}
    conditions={c['id']:c for c in config['conditions']}
    if set(conditions)!={'COST','OPENING','ROW','DEPOT'}:
        raise ValueError('Hard conditions cannot be dropped')
    rows=[];costs=[];register=[]
    for alt in alternatives:
        declaration=declarations[alt['technology_id']]
        if not set(declaration['reference_evidence_ids']) <= evidence.keys():
            raise ValueError('Unknown evidence citation')
        rows.append(classify(alt,policy,declaration))
        partial=declaration['partial_cost_scenario']
        if partial['full_capital_estimate'] is not False or partial['use_as_mcda_cost'] is not False:
            raise ValueError('Historical partial envelopes cannot become complete capital estimates')
        lo,hi=partial['lower_cad'],partial['upper_cad']
        if not 0<lo<=hi:
            raise ValueError('Invalid cost assumption range')
        product=(partial['reference_total_cad']/partial['reference_length_km']*config['length_km']
                 if 'reference_total_cad' in partial else None)
        costs.append(dict(technology_id=alt['technology_id'],lower_cad=lo,upper_cad=hi,
            exact_unadjusted_reference_transfer_cad='' if product is None else product,
            price_and_scope_basis=partial['reference_price_basis'],bound_provenance=partial['bound_provenance'],
            full_capital_estimate=False,budget_verified=False,use_as_mcda_cost=False))
        for cid in declaration['required_condition_ids']:
            field={'COST':'strict_budget','OPENING':'strict_schedule','ROW':'strict_route_engineering','DEPOT':'strict_depot'}[cid]
            strict_status=rows[-1][field]
            register.append(dict(technology_id=alt['technology_id'],condition_id=cid,
                condition_status={'pass':'met','fail':'failed'}.get(strict_status,'open'),acceptance_criterion=conditions[cid]['acceptance'],
                reopen_or_release_action='Resolve for verified admission' if alt['technology_id']!='SUBWAY' else 'Resolve for reconsideration of policy exclusion'))
    out=root/'outputs/task2_v0.2';out.mkdir(parents=True,exist_ok=True)
    for name,data in [('technology_policy_screen.csv',rows),('partial_cost_assumptions.csv',costs),('conditions_register.csv',register)]:
        with (out/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    summary=dict(corridor_id=23,length_km=7.101,
        conditional_shortlist=[r['technology_id'] for r in rows if r['policy_decision']=='conditional_pass'],
        policy_excluded=[r['technology_id'] for r in rows if r['policy_decision']=='policy_fail'],
        verified_feasible=[r['technology_id'] for r in rows if r['verified_feasible']],
        verified_failures=[r['technology_id'] for r in rows if r['demonstrated_hard_failure']],
        scenario_development_ready=any(r['provisional_shortlisted'] for r in rows),
        comparable_numeric_mcda_inputs_ready=False,technology_ranking_performed=False,
        selected_technology=None,task2_complete=False,
        reason='User-authorized conditional shortlist is executable. Target full-cost, matched demand/time and implementation evidence remain to be developed; no physical-infeasibility claim for Subway.')
    (out/'policy_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    bound=[config_path,root/config['strict_policy_file'],root/config['strict_input_file'],
           root/'evidence/tech_evidence_v0.1.csv',Path(__file__)]
    bound+=sorted(out.glob('*.csv'))+[out/'policy_summary.json']
    manifest={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in bound}
    (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return summary


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
