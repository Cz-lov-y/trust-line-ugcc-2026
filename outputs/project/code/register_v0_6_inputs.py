"""Register the user-authorized tiered proxy model without claiming verified geography."""
import json,csv
from tiered_common import ROOT,O,read,write,dump,sha,policy

def legacy(path,obj):path.write_bytes(json.dumps(obj,indent=2).replace('\n','\r\n').encode())
def register():
 d=ROOT/'data';config=policy();selected=set(config['fields'])
 sensitivity=json.loads((O/'woodbine_sensitivity_summary.json').read_text())
 if not sensitivity['completed']:raise ValueError('Run actual Woodbine sensitivity first')
 declarations=[]
 buffers=json.loads((ROOT/'outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson').read_text())
 for f in buffers['features']:
  cid=int(f['properties']['corridor_id'])
  declarations.append(dict(corridor_id=cid,proxy_declared=True,proxy_status='proxy_with_sensitivity_check' if cid in [5,6] else 'declared_proxy_with_limitations',official_alignment_verified=False,buffer_m=500,measurement_crs='EPSG:2952',buffer_file='outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson',buffer_sha256=sha(ROOT/'outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson'),sensitivity_evidence='outputs/tiered_v0.6/woodbine_sensitivity_summary.json' if cid in [5,6] else 'not_performed_for_this_endpoint',limitations='Current-road proxy, not approved future alignment or station catchment. Mixed road source vintages and methods; CT uniform density; future endpoint and Jane length review limitations retained.'))
 write(d/'geometry_declarations_v0.6.csv',sorted(declarations,key=lambda r:r['corridor_id']))
 rows=read(d/'corridor_geometry_review_v0.1.csv')
 for r in rows:
  cid=int(r['corridor_id']);r.update(proxy_declared=True,sensitivity_status='proxy_with_sensitivity_check' if cid in [5,6] else 'declared_proxy_only',sensitivity_evidence='outputs/tiered_v0.6/woodbine_sensitivity_summary.json' if cid in [5,6] else '',official_alignment_verified=False)
  if cid in [5,6]:
   r['alignment_geometry_status']='proxy_with_sensitivity_check';r['next_action']='Retain approximate source coordinate; review official station site and future alignment. Local endpoint stress completed, not proof of site accuracy.'
   r['notes']=r['notes'].split(' v0.6:')[0]+' v0.6: Shared Woodbine anchor tested nominal + eight 250m bearings; source road routes, buffers and CT allocations rebuilt. Geometry remains a proxy, not a surveyed station location.'
 write(d/'corridor_geometry_review_v0.1.csv',rows)
 records=json.loads((d/'workbook_records_v0.1.json').read_text())
 for section,rows in records.items():
  for r in rows:
   if r['indicator_id'] not in selected:continue
   r['model_admission_scope']='tiered_proxy_scenario_with_declared_limitations'
   r['notes']=r.get('notes','').split(' v0.6:')[0]+' v0.6: User-authorized tiering compares only 16 CITY_BASE_0 corridors in the main ranking; eight conditional extensions evaluated with prerequisite closures and union catchments. Model readiness means executable declared proxy scenarios, not unrestricted evidence or submission clearance.'
   if r['indicator_id']=='low_income_population_share_500m':
    r.update(proxy_status='proxy_with_sensitivity_check_for_Woodbine; declared_proxy_for_other_endpoints',sensitivity_evidence='outputs/tiered_v0.6/woodbine_sensitivity_summary.json',unit='fraction 0-1 before main-tier z-score; dimensionless after declared normalization')
   if section=='indicator_admission':
    r.update(admission_status='admitted_with_limitations',scenario_admission_status='admitted_for_tiered_proxy_model',baseline_comparability='tiered_common_base_only; dependent_pairs_separate',spatial_comparability='declared_road_proxies; Woodbine_local_sensitivity_completed',temporal_comparability='source_vintages_declared_with_limitations',decision_reason='Complete source-replayed scenario inputs; explicit 16/8 tier isolation, dependency pair review, geometry declarations and real endpoint stress. Limitations remain visible; no unrestricted comparability claim.')
 legacy(d/'workbook_records_v0.1.json',records)
 s=json.loads((d/'model_input_selection_v0.1.json').read_text());s.update(model_contract='tiered_proxy_scenario_v0.6',model_policy_file='data/tiered_model_policy_v0.6.json',strategy='Tiered 16-corridor common-base ranking and 8 conditional dependency bundles; limited-scope executable proxy model',normalization_file='outputs/tiered_v0.6/normalized_main_tier_inputs.csv',limitations_flagged=True);legacy(d/'model_input_selection_v0.1.json',s)
 rows=read(d/'model_input_coverage_v0.1.csv')
 for r in rows:
  if r['indicator_id'] in selected:r['admission_status']='admitted_with_limitations'
 write(d/'model_input_coverage_v0.1.csv',rows)
 schema=json.loads((d/'schema_v0.1.json').read_text())
 for section in ['data_dictionary','indicator_admission']:
  for field in ['model_admission_scope','proxy_status','sensitivity_evidence']:
   if field not in schema[section]:schema[section].append(field)
 schema['v0_6_tiered_model_contract']=dict(model_ready='Core inputs replayed AND tiered policy, dependency pairs, declared proxies and endpoint stress validated',unrestricted_model_ready=False,limitations_flagged=True,main_tier_count=16,conditional_tier_count=8);legacy(d/'schema_v0.1.json',schema)
 issues=read(d/'review_issues_v0.1.csv')
 for row in issues:
  if row['issue']=='Baseline dependency':row.update(finding='v0.6: 16 CITY_BASE_0 corridors form main comparison; 8 conditional corridors isolated with complete prerequisite closures and additional union catchments.',action='No cross-baseline absolute ranking or summed City z scores. Preserve conditional interpretation; tiering is not reconstructed independent benefit.')
  if row['issue']=='Scenario readiness v0.5':row.update(finding='v0.6: User-authorized model_ready contract is limited to executable tiered proxy scenarios. Unrestricted readiness stays separate.',action='Validate actual source values, six scenarios, 10000 draw ranks, dependency closures, declarations and Woodbine stress; limitations_flagged must remain true.')
 write(d/'review_issues_v0.1.csv',issues)
 print('Six inputs admitted with limitations; 16/8 comparison and explicit proxy declarations registered.')
if __name__=='__main__':register()
