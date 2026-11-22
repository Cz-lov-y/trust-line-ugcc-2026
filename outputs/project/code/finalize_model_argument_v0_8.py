"""Fingerprint documented argument evidence without rewriting any historical model."""
from tiered_common import ROOT,sha,dump
O=ROOT/'outputs/model_argument_v0.8'
def run():
 sources=[ROOT/'data/model_argument_policy_v0.8.json',ROOT/'data/jane_stress_policy_v0.7.json',ROOT/'data/model_input_selection_v0.7.json',ROOT/'data/corridor_master_v0.1.csv',ROOT/'data/city_standardized_scores_v0.1.csv',ROOT/'data/city_analysis_inputs_v0.4.csv',ROOT/'data/city_mean_sensitivity_v0.4.csv',ROOT/'data/supplemental_model_inputs_v0.5.csv',ROOT/'outputs/jane_stress_v0.7/five_indicator_inputs.csv',ROOT/'outputs/jane_stress_v0.7/paired_scenario_comparison.csv',ROOT/'outputs/jane_stress_v0.7/run_manifest.json',ROOT/'outputs/tiered_v0.6/conditional_pair_analysis.csv',ROOT/'outputs/corridor_batch_v0.5/corridor_buffers_500m.geojson',ROOT/'evidence/source_documents/city_2024_corridor_evaluation.pdf',ROOT.parent.parent/'reference/competition/STAT Case UGCC 2026.pdf']
 sources += [ROOT/'data/task1_decision_v0.8.json',ROOT/'CONTINUATION_v0.8.json',ROOT/'code/build_model_argument_slides_v0_8.py',ROOT/'slides/model_argument_v0.8_review_draft.pptx']
 sources += list((ROOT/'evidence/model_argument_v0.8').glob('*'))
 sources += [ROOT/'code'/p for p in ['analyze_model_argument_v0_8.py','assess_all_corridors_v0_8.py','validate_model_argument_v0_8.py']]
 # Competition document is outside the project; record separately against its repository-relative path.
 external={str(p.relative_to(ROOT.parent.parent)):sha(p) for p in sources if not p.is_relative_to(ROOT)}
 internal={str(p.relative_to(ROOT)):sha(p) for p in sources if p.is_relative_to(ROOT)}
 output={str(p.relative_to(ROOT)):sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='run_manifest.json'}
 dump(O/'run_manifest.json',dict(source_files=internal,repository_source_files=external,output_files=output))
 print('Argument evidence manifest frozen')
if __name__=='__main__':run()
