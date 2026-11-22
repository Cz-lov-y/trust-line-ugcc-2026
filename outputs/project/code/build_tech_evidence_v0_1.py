"""Build the auditable reference inventory and illustrative, unadmitted checks.

All numeric reference values remain attached to their original projects. This
script does not manufacture Finch East forecasts by scaling reference ridership.
"""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'evidence/tech_support_v0.1'
O = ROOT / 'outputs/task2_v0.1'


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build():
    O.mkdir(parents=True, exist_ok=True)
    sources = {r['source_id']: r for r in json.loads((E / 'acquisition_manifest.json').read_text())}
    rows = []

    def add(tech, criterion, value, unit, source, locator, project, notes,
            *, year='', price='', lo='', hi='', status='reference_fact', length=''):
        src = sources[source]
        if src['status'] != 'acquired':
            raise ValueError(f'Unarchived source {source}')
        file = ROOT / src['file']
        if hashlib.sha256(file.read_bytes()).hexdigest() != src['sha256']:
            raise ValueError(f'Archive changed: {source}')
        rows.append(dict(evidence_id=f'T2_REF_{len(rows)+1:03}', corridor_id=23,
            technology_id=tech, technology_name={'BRT':'Bus Rapid Transit','LRT':'Light Rail Transit','SUBWAY':'Subway'}[tech],
            criterion_id=criterion, value=value, unit=unit, value_status=status,
            reference_year=year, price_year=price, currency='CAD' if 'CAD' in unit else '',
            scenario_id='reference_project_only', lower_bound=lo, upper_bound=hi,
            uncertainty_basis='See notes; bounds are not confidence intervals', source_id=source,
            source_locator=locator, notes=notes, evidence_role='reference_only',
            reference_project=project, reference_length_km=length,
            target_transfer_status='not_admitted_as_Finch_East_estimate', use_in_optimization=False,
            source_url=src['url'], source_file=src['file'], source_sha256=src['sha256']))

    add('BRT','capital_program_investment',1.4e9,'CAD_2009','VIVA_OPENING',
        '2020-01-03 release; investment and program paragraphs','York Viva rapidways phase 1',
        'Provincial program investment for 34 km and 38 stations; not a full capital cost breakdown. Consultant, fleet and owner-scope exclusions are unresolved.',year=2020,price=2009,length=34)
    add('BRT','initial_capital_reference',1.086e9,'CAD_2023','DSBRT_PDBC',
        'physical p.129, Table 54, Option 1','Durham–Scarborough BRT',
        'Excludes already funded ICIP work; 36 km is the full route, not the unfunded-cost denominator. Includes 227M combined professional/agency costs, 276M land and 39M vehicles. Do not scale this subtotal by 36 km or subtract all professional/agency costs as consultants.',year=2024,price=2023,length=36)
    add('BRT','daily_ridership_forecast',37400,'riders_per_day','DSBRT_PDBC',
        'physical p.18, Table ES1, Option 1','Durham–Scarborough BRT',
        '2041 full-route total daily riders, closed-door policy; not capacity, net-new riders or a Finch East demand forecast.',year=2041,length=36)
    add('BRT','daily_ridership_policy_sensitivity',45700,'riders_per_day','DSBRT_PDBC',
        'physical p.18, Table ES1, Open Door sensitivity','Durham–Scarborough BRT',
        'Different boarding policy from the 37,400 reference; not a statistical upper confidence bound.',year=2041,length=36)
    add('BRT','end_to_end_saving',19,'minutes_per_one_way_end_to_end_trip','DSBRT_PDBC',
        'physical p.18, Table ES1, Option 1','Durham–Scarborough BRT',
        'Forecast route end-to-end saving versus its own BAU; not TSP-only or average passenger saving. Do not length-scale to Finch East.',year=2041,length=36)
    add('BRT','construction_start','2015-fall','date_season','VIVA_NEW_MARKET',
        'project description, Newmarket rapidway construction','Yonge Newmarket rapidway',
        'Construction start for 2.4 km segment; earlier planning excluded.',year=2015,length=2.4)
    add('BRT','operational_opening','2020-01-05','date','VIVA_OPENING',
        'opening paragraphs for Newmarket and Vaughan segments','Yonge Newmarket rapidway',
        'Observed opening, roughly four years after fall 2015 construction start; not evidence of 2–3 years all-in.',year=2020,length=2.4)

    add('LRT','construction_contract_component',1.2e9,'CAD_nominal_award','FINCH_CONSTRUCTION_COST',
        '2018-05-07 release, opening paragraph','Finch West LRT',
        'Construction component of 2.5B DBFM contract. Not complete owner capital; do not use gross DBFM as construction cost. Constant-price basis not established.',year=2018,length=11)
    add('LRT','gross_dbfm_contract',2.5e9,'CAD_nominal_contract','FINCH_CONSTRUCTION_COST',
        '2018-05-07 release, opening paragraph','Finch West LRT',
        'DBFM financing and maintenance scope; deliberately not eligible capital under the case ceiling.',year=2018,length=11)
    add('LRT','initial_capital_reference',4.2e9,'CAD_2020','EELRT_IBC',
        'physical p.40, section 4.3.1; Table 12','Eglinton East LRT',
        '2020 Class 4 full-project range 4.0–4.4B; midpoint 4.2B; report restates midpoint as 4.4B in 2022 prices. Includes fleet/property/contingency; consultant component unresolved. Different scope from 2023 construction estimate.',year=2022,price=2020,lo=4e9,hi=4.4e9)
    add('LRT','construction_reference',4.65e9,'CAD_escalated_construction_midpoint','EELRT_COST',
        'physical p.21, Table 1 and explanatory paragraph','Eglinton East LRT',
        'Construction-only estimate at 10% design, escalated to midpoint of potential 2027–2034 construction. Range -20%/+30%; includes MSF but excludes property, procurement, vehicles and lifecycle/O&M. Not a 2023 constant-dollar full capital estimate.',year=2023,lo=3.72e9,hi=6.045e9,length=18.6)
    add('LRT','daily_ridership_forecast',46000,'riders_per_weekday','FINCH_FAQ_2020',
        'physical p.1, Quick Facts','Finch West LRT',
        'Historical forecast, not observed riders. Weekday forecast horizon not separately specified; nearby annual forecast is 12M by 2031. Do not silently assign its year to this weekday figure.',year=2020,length=11)
    add('LRT','end_to_end_journey_time',38,'minutes_per_one_way_end_to_end_trip','FINCH_FAQ_2020',
        'physical p.1, Quick Facts','Finch West LRT',
        'Historical planned journey time, not saving; no matched before-trip time. Not a Finch East prediction.',year=2020,length=11)
    add('LRT','early_utility_start','2016-12','date_month','FINCH_FAQ_2020',
        'physical p.1, Quick Facts','Finch West LRT',
        'Gas relocation started Dec 2016, completed Apr 2019. Delivery timeline must include utilities, not only main civil works.',year=2016,length=11)
    add('LRT','major_construction_start',2019,'calendar_year','FINCH_FAQ_2020',
        'physical p.1; physical p.2 question 3','Finch West LRT',
        'Observed start at MSF/Highway 400; older planned completion in 2023 was not actual opening.',year=2019,length=11)
    add('LRT','operational_opening','2025-12-07','date','FINCH_OPENING',
        'page meta description: New Line 6 begins service Dec. 7, 2025','Finch West LRT',
        'Actual opening; early utilities to opening spans approximately nine years, before counting earlier planning. Historical description length retained, not mixed with current 10.3 km track measurement.',year=2025,length=11)
    add('LRT','intersection_tsp_saving_upper',30,'seconds_per_intersection','TTC_TSP_2026',
        'physical p.6, Spadina at Dundas/College','Spadina enhanced TSP pilot',
        'TTC reports up to 30 seconds, time-of-day dependent, at selected intersections. Not a lower bound, corridor-wide percentage or guaranteed Finch East result.',year=2026)
    add('LRT','intersection_tsp_saving_upper_city',25,'seconds_per_direction_per_intersection','CITY_TSP_2026',
        'physical p.20, Attachment 6 pilot discussion','Spadina enhanced TSP pilot',
        'City reports up to 25 seconds at Dundas/College; TTC reports up to 30. Preserve source difference; do not average or silently reconcile.',year=2026)
    add('LRT','round_trip_operational_improvement',20,'minutes_per_round_trip','TTC_TSP_2026',
        'physical pp.1,9, LRT Operations','Line 6 Finch West',
        'Approximate afternoon-peak improvement versus initial opening, after TSP and multiple operational changes; not causal TSP-only, bus-versus-LRT saving or 10 min guaranteed each direction.',year=2026)

    add('SUBWAY','capital_scope_reference',5.2e9,'CAD_published_capex_basis_unresolved','YNSE_SUPPLEMENT',
        'physical p.11, Capital Cost','Yonge North Subway Extension refined Option 3',
        '2021 published scope capex estimate, not 2020 present-value capital table. Price/cash-flow basis and consultant exclusion require reconciliation; not transferable as Finch East total.',year=2021)
    add('SUBWAY','daily_ridership_forecast',94100,'riders_per_day','YNSE_SUPPLEMENT',
        'physical p.7, Table 1','Yonge North Subway Extension refined Option 3',
        'Forecast assumed same as Option 3, subject to refinement; connected Line 1 extension, not a new standalone Finch East line. Table does not independently state forecast horizon.',year=2021)
    add('SUBWAY','specific_od_saving',22,'minutes_per_one_way_specific_OD_trip','YNSE_SUPPLEMENT',
        'physical p.7, Table 1, travel-time savings','Yonge North Subway Extension',
        'Langstaff/Ruggles to Yonge/Queen journey saving, not mean passenger or Finch East corridor saving.',year=2021)
    add('SUBWAY','new_line1_tmsf_requirement_year',2035,'calendar_year','TTC_EXPANSION_2026',
        'physical p.14, 25 growth trains risks','TTC Line 1 capacity enhancement',
        'New TMSF required for 25 growth trains and target headways. Does not quantify free Wilson slots or prove a Finch East connection is possible.',year=2026)
    add('SUBWAY','new_line1_tmsf_storage_scope',34,'train_sets','TTC_EXPANSION_2026',
        'physical p.22, Facilities and Yards','TTC Line 1 capacity enhancement',
        'Proposed new TMSF storage scope, not available surplus at Wilson. Storage, heavy maintenance, physical connection and fleet compatibility all need separate confirmation.',year=2026)

    for tech in ('BRT','LRT'):
        add(tech,'planned_right_of_way_width',36,'metres','FINCH_ROW_2026',
            'physical pp.5,13, Official Plan / Road Widening','179–181 Finch Avenue East frontage',
            'Within target corridor; planned ROW, not measured available paved width or verified full-corridor minimum. Do not infer 36 minus 4.90 as current full width.',year=2026)
        add(tech,'frontage_widening_dedication_required',4.90,'metres','FINCH_ROW_2026',
            'physical p.13, Road Widening','179–181 Finch Avenue East frontage',
            'Local frontage dedication needed to achieve planned 36m ROW; does not establish a route-wide deficit or engineering impossibility.',year=2026)

    add('LRT','reference_msf_location','York Gate Boulevard near Norfinch/Oakdale','place','FINCH_FAQ_2020',
        'physical p.1, Quick Facts','Finch West LRT',
        'Reference facility only; no verified connecting track or allocated capacity for Finch East.',year=2020,length=11)

    template = rows[0]
    for tech in ('BRT','LRT','SUBWAY'):
        for criterion, unit in [('capital_cost_total','CAD'), ('full_delivery_duration','years'),
                                ('projected_ridership','riders_per_day'),
                                ('travel_time_saving','minutes_per_one_way_matched_trip')]:
            pending = {key:'' for key in template}
            pending.update(evidence_id=f'T2_TARGET_{tech}_{criterion}', corridor_id=23,
                technology_id=tech, technology_name={'BRT':'Bus Rapid Transit','LRT':'Light Rail Transit','SUBWAY':'Subway'}[tech],
                criterion_id=criterion, unit=unit, value_status='pending_evidence',
                scenario_id='Finch_East_target_not_yet_estimated', evidence_role='target_required',
                reference_project='Finch Ave E: Yonge–Victoria Park',reference_length_km=7.101,
                target_transfer_status='missing_corridor_specific_basis', use_in_optimization=False,
                notes='Reference project facts are not substituted. Complete a consistent corridor-specific estimate/assumption with source and scope before admission.')
            rows.append(pending)

    write_csv(ROOT / 'evidence/tech_evidence_v0.1.csv', rows)
    # These checks deliberately remain outside the admission gate.
    cost = [dict(technology_id='SUBWAY', evidence_role='user_assumption_only',
        length_km=7.101, lower_unit_cost_cad_per_km=500e6, upper_unit_cost_cad_per_km=1e9,
        lower_product_cad=7.101*500e6, upper_product_cad=7.101*1e9,
        ceiling_cad=16.657e9, scope_and_price_basis_verified=False,
        budget_admitted=False, notes='Arithmetic screening envelope only; no proof of complete project capital, consultant exclusion, price year or depot/station scope.')]
    write_csv(O / 'subway_unit_cost_assumption_check.csv', cost)
    schedules=[]
    for tech, lo, hi in [('BRT',2,3),('LRT',4,6),('SUBWAY',8,10)]:
        schedules.append(dict(technology_id=tech, evidence_role='illustrative_assumption_only',
            approvals_design_procurement_lower_years=1, approvals_design_procurement_upper_years=2,
            construction_lower_years=lo, construction_upper_years=hi,
            separate_testing_lower_years=.5, separate_testing_upper_years=1,
            elapsed_lower_years=1+lo+.5, elapsed_upper_years=2+hi+1,
            planning_window_years=9, assumed_sequential=True,
            result_in_this_assumption_only='fails' if 1+lo+.5>9 else 'within_window',
            use_in_hard_gate=False,
            notes='Construction ranges and prework are user examples, not verified target estimates. Testing 0.5–1 yr is an analyst stress assumption. No overlap; if construction already includes tests do not add tests again. Yard/utilities and procurement may change critical path.'))
    write_csv(O / 'illustrative_schedule_envelope.csv', schedules)
    sensitivities=[]
    for n in (10,15,20):
        for enabled_fraction in (0,.5,1):
            sensitivities.append(dict(assumed_eligible_intersections=n,
                assumed_fraction_effective=enabled_fraction,
                lower_saving_minutes=0,
                city_report_based_ceiling_minutes=n*enabled_fraction*25/60,
                ttc_report_based_ceiling_minutes=n*enabled_fraction*30/60,
                evidence_role='transfer_sensitivity_only',
                use_in_optimization=False,
                notes='Counts are illustrative, not surveyed. Upper envelopes only, not expected savings. Cap by baseline signal-delay budget when measured; no addition to a mode speed already including TSP.'))
    write_csv(O / 'tsp_transfer_sensitivity.csv', sensitivities)
    audit = dict(reference_records=sum(r['evidence_role']=='reference_only' for r in rows),
                 target_estimates_pending=sum(r['evidence_role']=='target_required' for r in rows),
                 admitted_target_estimates=sum(r['use_in_optimization'] is True for r in rows),
                 source_archive_hashes_verified=True,
                 sources_acquired=sum(r['status']=='acquired' for r in sources.values()),
                 source_requests_failed=[sid for sid, r in sources.items() if r['status']!='acquired'],
                 note='Archive acquisition does not establish substantive content or transferability. No weighted technology ranking performed.')
    (O / 'evidence_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    return len(rows)


if __name__ == '__main__':
    print(f'Wrote {build()} reference/pending records; no target forecasts admitted.')
