"""Freeze source/output fingerprints before evaluating limited-scope readiness."""
from tiered_common import ROOT,O,read,write,dump,sha
import json

def run():
 paths={ROOT/p for p in json.loads((O/'model_input_manifest.json').read_text())}
 paths|={ROOT/p for p in json.loads((ROOT/'evidence/tiered_v0.6/woodbine_source_manifest.json').read_text())['source_files']}
 paths|={ROOT/'evidence/tiered_v0.6/woodbine_source_manifest.json'}
 paths|={ROOT/'data'/p for p in ['workbook_records_v0.1.json','schema_v0.1.json','model_input_selection_v0.1.json','geometry_declarations_v0.6.csv','corridor_geometry_review_v0.1.csv','corridor_tiers_v0.6.csv']}
 paths|={ROOT/'code'/p for p in ['tiered_common.py','run_tiered_model_v0_6.py','woodbine_sensitivity_v0_6.py','analyze_extension_pairs_v0_6.py','register_v0_6_inputs.py','validate_data.py','validate_tiered_contract.py','validate_equity_scenario.py','batch_endpoint_road_buffers.py']}
 source={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
 outputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='run_manifest.json'}
 dump(O/'run_manifest.json',dict(source_files=source,output_files=outputs,notes='Run fingerprints exclude their own manifest and later validation/test reports. Ready means declared tiered proxy scenarios, not unrestricted evidence or submission clearance.'))
 print('Frozen source files',len(source),'output files',len(outputs))
if __name__=='__main__':run()
