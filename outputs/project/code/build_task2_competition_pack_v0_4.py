"""Proportion check and milestone-level competition package; preserve v0.3 math."""
from pathlib import Path
from datetime import date
import csv
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def ratio_template(config):
    values=config['reference_components_million'];total=config['reference_reported_total_million']
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in [total,*values.values()]):
        raise ValueError('Reference costs must be finite and nonnegative')
    excluded=config['excluded_template_category'];net=total-values[excluded]
    if net<=0:raise ValueError('Nonpositive template denominator')
    rounding=total-sum(values.values())
    if abs(rounding)>total*.01:raise ValueError('Source reconciliation exceeds 1%; investigate instead of hiding it')
    selected=config['allocation_buckets'];used=set(selected.values())
    if len(used)!=len(selected) or excluded in used:raise ValueError('Overlapping/excluded cost categories')
    grouped=[(name,values[source_name]) for name,source_name in selected.items()]
    grouped.append(('other_capital_and_reconciliation',net-sum(v for _,v in grouped)))
    return [dict(category=name,reference_amount_million=value,published_total_share=value/total,
                 professional_services_excluded_template_share=value/net) for name,value in grouped],rounding,net


def milestones(config,deadline,window):
    stages=config['milestones']
    if len(stages)!=4:raise ValueError('Exactly four requested milestones')
    rows=[];lower=upper=0;previous=date.fromisoformat(config['programme_start_assumption'])
    for i,s in enumerate(stages,1):
        lo,hi=s['duration_lower_years'],s['duration_upper_years']
        if not 0<lo<=hi:raise ValueError('Invalid milestone duration range')
        lower+=lo;upper+=hi;end=date.fromisoformat(s['illustrative_completion'])
        if not previous<end:raise ValueError('Milestones must progress in calendar order')
        rows.append(dict(milestone=i,stage=s['stage'],lower_years=lo,upper_years=hi,
            sequential_cumulative_lower_years=lower,sequential_cumulative_upper_years=upper,
            illustrative_upper_case_completion=s['illustrative_completion'],contained_scope=s['contained_scope'],
            status='user_assumption_not_quantitative_construction_schedule'))
        previous=end
    if upper>window or previous>date.fromisoformat(deadline):raise ValueError('Milestone scenario breaches original delivery limits')
    return rows,lower,upper


def run(root=ROOT):
    config=json.loads((root/'data/task2_competition_pack_v0.4.json').read_text())
    baseline=json.loads((root/config['baseline_file']).read_text())
    hard=json.loads((root/'data/task2_hard_constraints_v0.1.json').read_text())
    if config['fixed_efficiency_definition']!=baseline['primary_efficiency_definition'] or config['fixed_normalization']!=baseline['primary_normalization']:
        raise ValueError('User requested preservation of the scoring formula and primary normalization')
    archive=json.loads((root/'evidence/tech_support_v0.4/acquisition_manifest.json').read_text())[0]
    if hashlib.sha256((root/config['source_file']).read_bytes()).hexdigest()!=archive['sha256']:
        raise ValueError('Reference archive changed')
    template,rounding,net=ratio_template(config)
    out=root/'outputs/task2_v0.4';out.mkdir(parents=True,exist_ok=True)
    excluded=config['excluded_template_category']
    fee=dict(category='professional_services_excluded',reference_amount_million=config['reference_components_million'][excluded],
        published_total_share=config['reference_components_million'][excluded]/config['reference_reported_total_million'],
        professional_services_excluded_template_share=0)
    write_csv(out/'reference_cost_ratios.csv',template+[fee])
    allocations=[]
    for mode,key in [('BRT','brt_cost_cad'),('LRT','lrt_cost_cad')]:
        point=baseline['baseline'][key]
        for row in template:
            fraction=row['professional_services_excluded_template_share']
            allocations.append(dict(technology_id=mode,category=row['category'],template_share=fraction,
                allocated_cad=point*fraction,fixed_total_cad=point,allocation_inside_total=True,
                value_status='source_ratio_times_user_cost_assumption',full_capital_cost_verified=False,
                source_id=config['source_id'],source_locator=config['source_locator']))
    write_csv(out/'cost_ratio_allocation.csv',allocations)
    stages,lower,upper=milestones(config,hard['operational_deadline'],hard['planning_window_years'])
    write_csv(out/'delivery_milestones.csv',stages)
    evidence={r['evidence_id']:r for r in read_csv(root/'evidence/tech_evidence_v0.1.csv')}
    tsp=[]
    for eid in config['TSP_evidence_ids']:
        row=evidence[eid]
        tsp.append({k:row[k] for k in ('evidence_id','reference_project','criterion_id','value','unit','source_locator','source_url','notes')})
    write_csv(out/'TSP_citation_table.csv',tsp)
    scores=read_csv(root/'outputs/task2_v0.3/baseline_scores.csv')
    selected=[r for r in scores if r['weight_profile'] in config['policy_profiles'] and r['efficiency_definition']==config['fixed_efficiency_definition'] and r['normalization']==config['fixed_normalization']]
    if len(selected)!=6:raise ValueError('Expected the three preserved two-technology policy cases')
    write_csv(out/'fixed_policy_scores.csv',selected)
    old_summary=json.loads((root/'outputs/task2_v0.3/model_summary.json').read_text())
    summary=dict(corridor_id=23,length_km=7.101,requested_four_deliverables_complete=True,
        competition_scope_analysis_package_ready=True,reference_reported_total_million=config['reference_reported_total_million'],
        excluded_professional_services_million=config['reference_components_million'][config['excluded_template_category']],
        allocation_template_denominator_million=net,published_total_difference_million=rounding,
        allocation_is_total_cost_validation=False,exact_consultant_exclusion_verified=False,
        programme_start_assumption=config['programme_start_assumption'],sequential_milestone_years_lower=lower,
        sequential_milestone_years_upper=upper,upper_case_opening=stages[-1]['illustrative_upper_case_completion'],
        upper_case_delay_buffer_years=hard['planning_window_years']-upper,
        quantitative_construction_scheduling_performed=False,independent_ridership_forecasting_performed=False,
        new_runtime_data_collection_performed=False,scoring_formula_changed=False,overlap_eliminated=False,
        baseline_winner=old_summary['baseline_equal_weight_scenario_winner'],
        capital_efficiency_priority_winner=next(r['scenario_winner'] for r in selected if r['weight_profile']=='capital_efficiency_priority'),
        service_benefit_priority_winner=next(r['scenario_winner'] for r in selected if r['weight_profile']=='service_benefit_priority'),
        efficiency_weight_switch=old_summary['efficiency_weight_switch'],implementation_feasibility_certified=False,
        recommendation='BRT under equal or capital-efficiency priorities; LRT under the declared service-benefit priority, conditional on the common cost, opening, route and depot assumptions.')
    (out/'package_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    files=[root/'data/task2_competition_pack_v0.4.json',root/config['baseline_file'],root/config['source_file'],
        root/'evidence/tech_support_v0.4/acquisition_manifest.json',root/'evidence/tech_evidence_v0.1.csv',
        root/'outputs/task2_v0.3/baseline_scores.csv',root/'outputs/task2_v0.3/model_summary.json',Path(__file__)]
    files+=sorted(out.glob('*.csv'))+[out/'package_summary.json']
    (out/'run_manifest.json').write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
    return summary


if __name__=='__main__':print(json.dumps(run(),indent=2))
