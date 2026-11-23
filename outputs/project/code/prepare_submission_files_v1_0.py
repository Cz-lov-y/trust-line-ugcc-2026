"""Prepare exactly three upload files; keep rehearsal/old review files separate."""
from pathlib import Path
import csv
import hashlib
import io
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent.parent
FINAL=REPO/'deliverables/S06_FINAL';DEST=REPO/'deliverables/S06_SUBMISSION'


def sha(data):return hashlib.sha256(data).hexdigest()


def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def csv_bytes(rows):
    s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return s.getvalue().encode('utf-8')


def build():
    DEST.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(FINAL/'S06_TRUST_LINE_FINAL.pptx',DEST/'S06_Presentation.pptx')
    shutil.copyfile(FINAL/'S06_ABSTRACT.pdf',DEST/'S06_Abstract.pdf')
    contents={}
    def add(path):contents[path.relative_to(REPO).as_posix()]=path.read_bytes()
    dataset_files=[
        'corridor_master_v0.1.csv','city_standardized_scores_v0.1.csv','city_analysis_inputs_v0.4.csv','city_mean_sensitivity_v0.4.csv',
        'supplemental_model_inputs_v0.5.csv','model_matrix_v0.5.csv','tiered_model_policy_v0.6.json','jane_stress_policy_v0.7.json',
        'model_argument_policy_v0.8.json','model_input_selection_v0.1.json','model_input_selection_v0.7.json','missing_data_policy_v0.4.json',
        'equity_proxy_method_v0.3.json','equity_proxy_method_v0.5.json','census_ct_analysis_v0.5.csv','census_ct_batch_v0.4.csv','census_ct_batch_v0.5.csv',
        'corridor_endpoint_coordinates_v0.5.csv','corridor_endpoint_coordinates_v0.5.json','corridor_geometry_review_v0.1.csv',
        'geometry_declarations_v0.6.csv','corridor_tiers_v0.6.csv','source_log_v0.1.csv','candidate_indicator_longlist_v0.1.csv',
        'city_2024_indicator_index_v0.1.csv','indicator_observations_v0.1.csv','task2_baseline_assumptions_v0.3.json',
        'task2_hard_constraints_v0.1.json','task2_screening_policy_v0.2.json','technology_screen_inputs_v0.1.json','task2_competition_pack_v0.4.json'
    ]
    for name in dataset_files:add(ROOT/'data'/name)
    # Computational source and acquisition/GIS lineage; omit presentation-writing helpers and tests.
    for p in (ROOT/'code').iterdir():
        if not p.is_file() or p.suffix not in ('.py','.txt'):continue
        if p.name.startswith(('test_','build_task2_final','assemble_final','prepare_submission','build_task2_baseline_slides','build_task2_competition_slides','build_task2_screening_slides','build_model_argument_slides','build_jane_stress_slides','build_tiered_slides')):continue
        add(p)
    for folder in ['tiered_v0.6','jane_stress_v0.7','model_argument_v0.8','task2_v0.3','task2_v0.4','final_replay_v1.0']:
        for p in (ROOT/'outputs'/folder).rglob('*'):
            if p.is_file() and p.suffix in ['.csv','.json','.png','.pdf','.svg','.md']:add(p)
    for p in (ROOT/'evidence').rglob('*'):
        if p.is_file() and p.suffix in ['.csv','.json','.md'] and p.stat().st_size<2_000_000:add(p)
    for name in [
        'source_documents/city_2024_corridor_evaluation.pdf','tech_support_v0.4/ecwe_ibc_2020.pdf',
        'tech_support_v0.1/ttc_tsp_report_2026.pdf','tech_support_v0.1/city_tsp_attachments_2026.pdf',
        'tech_support_v0.1/finch_faq_2020.pdf','tech_support_v0.1/finch_aecon_award_2018.html','tech_support_v0.1/viva_opening_2020.html'
    ]:add(ROOT/'evidence'/name)
    # Front-door datasets use the active five-criterion model, not the archived six-column matrix.
    master=read(ROOT/'data/corridor_master_v0.1.csv')
    city={r['corridor_id']:r for r in read(ROOT/'data/city_standardized_scores_v0.1.csv')}
    low={r['corridor_id']:r for r in read(ROOT/'data/supplemental_model_inputs_v0.5.csv')}
    norm={(r['corridor_id'],r['city_method']):r for r in read(ROOT/'outputs/jane_stress_v0.7/five_indicator_inputs.csv')}
    context=read(ROOT/'outputs/model_argument_v0.8/all24_contextual_scores.csv')
    context_lookup={(r['corridor_id'],r['city_method']):r for r in context if r['weight_profile']=='equal'}
    fields=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text())['fields']
    rows=[]
    for r in master:
        cid=r['corridor_id'];eq=low[cid]
        row={k:r[k] for k in ['corridor_id','corridor_name','endpoint_a','endpoint_b','length_km','baseline_scenario_id','prerequisite_corridor_ids']}
        row['main_rank_eligible']=r['baseline_scenario_id']=='CITY_BASE_0'
        for f in fields[:-1]:row[f+'_published_score']=city[cid][f]
        for f in ['low_income_population_share_500m','low_income_population_estimate','total_population_estimate','value_status','imputed_CTUIDs']:
            row['equity_'+f if f not in ['low_income_population_share_500m'] else f]=eq[f]
        for method,label in [('imputed_conservative_min','minimum_scenario'),('imputed_observed_mean','mean_scenario')]:
            source=norm.get((cid,method),context_lookup[cid,method])
            for f in fields:row[label+'_'+f]=source[f]
        rows.append(row)
    if len(rows)!=24 or {int(r['corridor_id']) for r in rows}!=set(range(1,25)):raise ValueError('24-corridor dataset incomplete')
    contents['datasets/Part1_Corridors_24.csv']=csv_bytes(rows)
    contents['datasets/Part1_All24_Scenario_Scores.csv']=(ROOT/'outputs/model_argument_v0.8/all24_contextual_scores.csv').read_bytes()
    technology=read(ROOT/'outputs/task2_v0.3/baseline_inputs.csv')
    if {r['technology_id'] for r in technology}!={'BRT','LRT'} or len(technology)!=2:raise ValueError('Two-technology dataset incomplete')
    contents['datasets/Part2_Technology_Comparison.csv']=csv_bytes(technology)
    contents['datasets/Part2_Weight_Sensitivity.csv']=(ROOT/'outputs/task2_v0.3/scenario_scores.csv').read_bytes()
    contents['REFERENCES.md']=(FINAL/'REFERENCES.md').read_bytes()
    contents['VALIDATION.txt']=(FINAL/'VALIDATION.txt').read_bytes()
    contents['requirements_replay.txt']=b'numpy>=1.26\n'
    contents['README.md']='''# S06 — Statistical Sciences supplementary materials

Team S06: Zhuo Chen; Yue Tang; Yuen Song (Rain); Zihan Cao (Dalton).
Recommendation: Finch East, Yonge–Victoria Park, 7.101 km, BRT, with feasible future rail options considered.

This ZIP is the supplementary dataset/code/documentation upload required by the case brief p.13. The presentation and abstract PDF are uploaded separately. Rehearsal notes, timers, author-placeholder drafts and obsolete review correspondence are intentionally excluded.

## Required contents

1. **Part 1 dataset:** `datasets/Part1_Corridors_24.csv` has exactly one row per corridor and the active five indicators, original City scores, explicit min/mean scenarios, baseline/prerequisite metadata and equity estimate flags. `Part1_All24_Scenario_Scores.csv` has all 144 contextual scenario rows.
2. **Part 2 dataset:** `datasets/Part2_Technology_Comparison.csv` has BRT and LRT for the fixed corridor, with hypothetical cost, relative demand, assumed time saving, efficiency and status labels. `Part2_Weight_Sensitivity.csv` contains the declared input/method/profile cases.
3. **Executable source:** `outputs/project/code/replay_final_models_v1_0.py` is the compact offline entry point for both delivered models. Original numerical/scenario source is preserved alongside it.
4. **Outputs:** `outputs/project/outputs/` contains corridor selection, correlations, disputed-indicator stress, technology scores and sensitivity figures/tables.
5. **Documentation:** this README, `documentation/TRANSFORMATIONS.md`, `REFERENCES.md`, source registry, method JSON and original model reports document preparation, units, assumptions and limitations.

## Offline numerical reproduction

From the extracted ZIP's root:

```sh
python -m pip install -r requirements_replay.txt
python outputs/project/code/replay_final_models_v1_0.py
```

The entry point recomputes all 144 contextual corridor scores, common-baseline rank support and the technology scores/preference support and checks agreement with the supplied results. Its output is written to `outputs/project/outputs/final_replay_v1.0/`. It requires Python 3 and NumPy; validation used Python 3.12 / NumPy 2.5.5. Additional original scripts may need Matplotlib or GIS dependencies listed in `outputs/project/code/requirements_gis.txt`.

The replay reuses delivered CT-overlay estimates. It does not rebuild geometry. Large Census/RNF/GeoJSON acquisitions remain in the full repository, with source URLs/hashes and calculation lineage included here. The complete historical test suite and byte-level raw acquisition audits require that full repository, rather than this compact upload. Selected official City, Metrolinx and TTC PDFs are included to support source review.

## Sources and transformations

City 2024 evaluation tables supply corridor metadata and published standardized scores. Statistics Canada 2021 population/geography and 2020 LIM-AT counts support the custom area-weighted equity proxy. Metrolinx/YRRTC project evidence and TTC/City TSP reports contextualize the declared technology assumptions. Public URLs and source locators are in `outputs/project/data/source_log_v0.1.csv`, `REFERENCES.md` and evidence manifests.

Original source values are retained. Missing City values use separate observed-column-minimum and observed-column-mean scenarios. Equity is a custom CT uniform-density estimate, not official LIM prevalence; suppressed-count substitutions remain flagged. Its frozen 16-corridor z calibration is not a normality assumption. The 16/8 baseline split, disputed-ridership exclusion, policy weights and fixed seeds are explicit in the method files. `documentation/TRANSFORMATIONS.md` identifies active versus historical matrices.

## Interpretation

Task 1 excludes construction costs. Conditional corridors are assessed in their own baseline contexts rather than assigned invented Base-0 ranks. Task 2 uses declared hypothetical costs, relative demand and time savings; they are not verified total capital, absolute daily forecasts or guaranteed delivery. The 6–9-year milestone assumption has zero extra buffer in its upper case. BRT wins equal/capital-efficiency profiles; service-benefit priority can select LRT. Shared R in E=R/C and R, source transfer, principle-coverage gaps and normalization sensitivity are disclosed.

Actual AI assistance is disclosed in the presentation under the applicable permissions confirmed by the team. No physical prop, judge handout or recorded voice is part of the presentation plan. No competition upload is performed by this archive or its code.

Full source repository: https://github.com/Cz-lov-y/trust-line-ugcc-2026
'''.encode('utf-8')
    contents['documentation/TRANSFORMATIONS.md']='''# Data preparation and active model map

## Part 1

- `corridor_master_v0.1.csv`: 24 original corridor definitions; City assumed construction lengths and network baseline metadata are retained.
- `city_standardized_scores_v0.1.csv`: original five City columns, with 98 published values and 22 blanks. These are standardized source scores, not physical km/h or passenger counts.
- The active five indicators are four City scores (`current_speed`, `unimproved_load`, `current_max_load`, `competitiveness`) plus `low_income_population_share_500m`. The disputed length-scaled `current_ridership` is excluded from the active five-criterion model; source values are not corrected or overwritten.
- Separate minimum/mean City input tables record the substitution assumptions. Missingness is not asserted to be random; substitutions are not observations.
- `supplemental_model_inputs_v0.5.csv`: all 24 equity estimates and numerator/denominator totals, with geometry/count-imputation flags. Population/LIM counts are allocated by intersected CT area fractions under uniform density. The numerator is divided by covered all-resident population, a custom proxy rather than official private-household LIM prevalence. Income reference is 2020; population/geography 2021. Complete same-CT DA sums are preferred for suppressed CTs; otherwise the authorized municipal CT-rate median is used with a mean sensitivity.
- Equity z=(fraction−0.13716878222779566)/0.02473132688714528, frozen on the 16 main corridors across stress comparisons. Z-scaling does not require or create a normal distribution. Published City normalization is retained.
- Common-baseline main IDs and eight conditional IDs are declared in `jane_stress_policy_v0.7.json`; conditional prerequisites/bundle results remain supplied. No unanchored common-base rank is invented for the eight.
- Scores are weighted sums; conservative tied ranks use tolerance 1e-12 and worst tied position for top-k. Two City methods × three profiles give six cases. PCG64 seed 20261121 selects identical cases across the paired models. Frequencies are scenario support, not population confidence. Broader block-weight sensitivity and correlation views are supplied separately.
- `datasets/Part1_Corridors_24.csv` is the active front-door table. `model_matrix_v0.5.csv` is the historical six-column scenario matrix, retained only for the paired baseline; do not use it to reintroduce `current_ridership` into the final five-criterion model.

## Part 2

- Fixed corridor 23, 7.101 km; BRT and LRT conditionally admitted, Subway excluded by the declared conservative delivery/depot policy, not demonstrated physical impossibility.
- User-selected scenario cost points CAD350M/CAD950M, relative ridership 1/1.2, one-way end-to-end savings 2.5/3.5 minutes and assumed 15 signals. No absolute passenger count, target before-trip observation or guaranteed priority benefit is fabricated.
- E=relative demand / cost in CAD billions; utilities use ratio to best and the stated weights. Cost per km is diagnostic only. Shared demand between E and R is disclosed. Alternative definitions/normalization, explicit profiles and stress cases remain sensitivity evidence.
- Fixed-input preference draws use PCG64 seed 20261122, Dirichlet(1,1,1), 10,000 draws. They describe an illustrative weight prior, not forecast accuracy or project-success probability.
- ECWE Table 19 Option 1 proportions allocate inside the unchanged cost points. A separately reported professional-services allowance is removed as a declared consultant-exclusion proxy; exact classification and source-to-target price/scope are not certified. This allocation is not independent validation of complete target capital.
- Four milestone durations 1–2, 1–2, 3–4 and 1 year sum to a 6–9-year scenario. The upper case starts January 2027 and reaches operational readiness December 2035 without extra delay buffer. No quantitative construction schedule is asserted.

For full reasoning, read `outputs/project/outputs/model_argument_v0.8/MODEL_JUSTIFICATION.md`, `outputs/project/outputs/jane_stress_v0.7/REPORT.md`, `outputs/project/outputs/task2_v0.3/BASELINE_MODEL.md` and `outputs/project/outputs/task2_v0.4/COMPETITION_PACKAGE.md`.
'''.encode('utf-8')
    index={name:sha(data) for name,data in contents.items()}
    support=DEST/'S06_Supporting_Materials.zip'
    with zipfile.ZipFile(support,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in sorted(contents.items()):z.writestr('S06_SUPPORTING_MATERIALS/'+name,data)
        z.writestr('S06_SUPPORTING_MATERIALS/CONTENTS_SHA256.json',json.dumps(index,indent=2)+'\n')
    required=['S06_Presentation.pptx','S06_Abstract.pdf','S06_Supporting_Materials.zip']
    if sorted(p.name for p in DEST.iterdir() if p.is_file())!=sorted(required):raise ValueError('Submission directory should contain exactly three files')
    bundle=DEST.parent/'S06_ALL_UPLOAD_FILES.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name in required:z.write(DEST/name,name)
    checklist=DEST.parent/'S06_SUBMISSION_CHECKLIST.md'
    checklist.write_text('''# S06 正式提交文件清单

按所提供总指南第13/19页和统计赛题第13页，准备以下三份文件：

| 文件 | 用途 | 内容 |
|---|---|---|
| `S06_SUBMISSION/S06_Presentation.pptx` | 演示文稿 | 11页；完整S06四人署名；Task 1/Task 2、AI披露、参考文献；末页Final Recommendation: BRT |
| `S06_SUBMISSION/S06_Abstract.pdf` | 摘要 | 英文正文167词，少于200；标题和四人署名；2条参考文献；无图表公式 |
| `S06_SUBMISSION/S06_Supporting_Materials.zip` | 统计赛题补充材料 | 24条走廊数据、BRT/LRT比较数据、代码、输出、来源与变换说明、README及离线复算入口 |

## 下载与上传

`S06_ALL_UPLOAD_FILES.zip`仅是方便一次下载的外层打包。**先解压，按提交页面要求上传上述三份文件；不要用外层总包替代统计赛题的Supporting_Materials.zip。**

正式提交目录只放这三份文件。排练稿、计时器、中文辅助摘要、旧版PPT、历史审阅稿均不需要另外上传；排练资料仍在`S06_FINAL/`中。

队号：S06。成员：Zhuo Chen；Yue Tang；Yuen Song (Rain)；Zihan Cao (Dalton)。

按所提供指南，截止时间为 **2026年11月23日23:59，多伦多时间（Eastern Time）**。提交入口：https://forms.gle/CYa5iEPHJUWGxBGT8 。指南要求只提交一次；本次整理未代替团队执行上传。

请最后用本机PowerPoint打开PPT确认显示，并由四人实际计时合练。文件结构检查与数值复算不等于真人排练或对工程/成本假设的实证认证。
''')
    report=dict(required_upload_count=3,submission_files={name:dict(bytes=(DEST/name).stat().st_size,sha256=sha((DEST/name).read_bytes())) for name in required},
        all_files_download_bundle=str(bundle.relative_to(REPO)),part1_dataset_rows=24,part1_scenario_rows=144,part2_technologies=['BRT','LRT'],
        rehearsal_and_old_review_files_excluded=True,actual_submission_performed=False)
    (DEST.parent/'S06_SUBMISSION_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':print(json.dumps(build(),indent=2))
