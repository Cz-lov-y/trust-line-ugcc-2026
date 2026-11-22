"""Freeze stress/audit artifacts without rewriting the six-criterion baseline."""
from tiered_common import ROOT,sha,dump
O=ROOT/'outputs/jane_stress_v0.7'
def run():
 sources=[ROOT/'data/jane_stress_policy_v0.7.json',ROOT/'data/model_input_selection_v0.7.json',ROOT/'data/task1_decision_v0.7.json',ROOT/'data/corridor_master_v0.1.csv',ROOT/'data/city_standardized_scores_v0.1.csv',ROOT/'data/city_analysis_inputs_v0.4.csv',ROOT/'data/city_mean_sensitivity_v0.4.csv',ROOT/'data/supplemental_model_inputs_v0.5.csv',ROOT/'data/tiered_model_policy_v0.6.json',ROOT/'outputs/tiered_v0.6/run_manifest.json',ROOT/'outputs/tiered_v0.6/six_scenario_scores.csv',ROOT/'outputs/tiered_v0.6/monte_carlo_draws.csv',ROOT/'evidence/source_documents/city_2024_corridor_evaluation.pdf',ROOT/'evidence/source_documents/city_2024_main_report.pdf',ROOT/'code/run_jane_stress_v0_7.py',ROOT/'code/audit_jane_lengths_v0_7.py',ROOT/'code/validate_jane_stress_v0_7.py']
 sources+=list((ROOT/'evidence/jane_audit_v0.7').iterdir())
 outputs=[p for p in O.iterdir() if p.is_file() and p.name!='run_manifest.json']
 dump(O/'run_manifest.json',dict(source_files={str(p.relative_to(ROOT)):sha(p) for p in sorted(sources)},output_files={str(p.relative_to(ROOT)):sha(p) for p in sorted(outputs)}))
 print('Jane stress manifest frozen')
if __name__=='__main__':run()
