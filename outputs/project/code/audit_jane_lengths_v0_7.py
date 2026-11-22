"""Audit published length labels and two Jane rows without correcting source values."""
from pathlib import Path
import json,csv,hashlib
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/jane_audit_v0.7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 E.mkdir(parents=True,exist_ok=True)
 attachment=ROOT/'evidence/source_documents/city_2024_corridor_evaluation.pdf';main=ROOT/'evidence/source_documents/city_2024_main_report.pdf'
 a=PdfReader(attachment);m=PdfReader(main)
 for name,text in [('attachment_length_definition_physical_p1.txt',a.pages[0].extract_text()),('attachment_measure_scaling_physical_p6.txt',a.pages[5].extract_text()),('attachment_table2_physical_p7.txt',a.pages[6].extract_text()),('main_table1_physical_p25.txt',m.pages[24].extract_text())]:(E/name).write_text('\n'.join(line.rstrip() for line in text.splitlines()).strip()+'\n')
 required=['Assumed','Length (km)','11.269','4.076','Eglinton Ave','Pioneer']
 if any(v not in a.pages[6].extract_text() for v in required):raise ValueError('Source table text no longer matches audited evidence')
 with (ROOT/'data/corridor_master_v0.1.csv').open(encoding='utf-8-sig') as f:master={int(r['corridor_id']):r for r in csv.DictReader(f)}
 features=json.loads((ROOT/'outputs/corridor_batch_v0.4/corridor_road_proxies.geojson').read_text())['features'];proxies={int(f['properties']['corridor_id']):f['properties'] for f in features}
 rows=[]
 for cid in [11,12]:
  r=master[cid];proxy=float(proxies[cid]['measured_route_length_km']);length=float(r['length_km'])
  rows.append(dict(corridor_id=cid,corridor_name=r['corridor_name'],endpoint_a=r['endpoint_a'],endpoint_b=r['endpoint_b'],reported_assumed_construction_length_km=length,reported_baseline=r['baseline_scenario_id'],measured_named_road_proxy_length_km=proxy,reported_minus_proxy_km=length-proxy,proxy_is_not_approved_transit_alignment=True,reported_length_preserved=True))
 with (E/'jane_length_comparison.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 result=dict(attachment_url='https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243172.pdf',attachment_sha256=sha(attachment),main_report_url='https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243162.pdf',main_report_sha256=sha(main),table='Evaluation attachment Table 2, physical p.7; matching main-report Table 1, physical p.25',header='Assumed Length (km)',scaling_definition='Attachment physical p.1 Section 2.2: benefit divided by length of construction',measure_rule='Attachment physical p.6 Table 1: Current ridership scaling = Length; Current max load and Unimproved load show no length scaling in this table',corridor_12_interpretation='Published assumed construction length assigned to the Eglinton Ave–Pioneer Village row. No single-side, one-direction, partial-extension or Jane-specific reduced-length annotation is supplied.',corridor_12_base='CITY_BASE_0',corridor_11_base='CITY_BASE_AFTER_12',footnote_review='The reduced-length footnote 6 is attached to corridor 3 Waterfront West LRT #1, not to Jane corridor 12.',rows=rows,main_report_repeats_same_assignments=True,possible_transposition='The two published lengths resemble the opposite named-road subsection proxy lengths. This is a plausible source-table transposition hypothesis, not a verified official correction.',official_erratum_located=False,physical_full_length_4_076_confirmed=False,internal_score_denominator_confirmed=False,why_score_denominator_unknown='No unscaled ridership inputs or calculation workbook identifies the actual denominator behind the published standardized score. A table inconsistency alone does not prove the score used that length.',action='Do not swap lengths or reconstruct z scores. Exclude current_ridership from a paired five-criterion stress model and preserve the six-criterion baseline.')
 (E/'jane_length_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
