"""Assemble S06's integrated final files and a compact offline model archive."""
from pathlib import Path
import csv
import hashlib
import html
import json
import re
import shutil
import zipfile
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches,Pt
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer

from build_task2_final_v0_5 import ABSTRACT,ABSTRACT_ZH,REFERENCES,words
from replay_final_models_v1_0 import replay

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent.parent
DEST=REPO/'deliverables/S06_FINAL'

NOTES=[
'''We are S06. TRUST-Line makes two linked decisions: select the corridor independently of cost, then choose its technology. We recommend Finch East BRT, preserving feasible future rail options.''',
'''Part One starts with all twenty-four City corridors. We retain five cost-independent need indicators: current speed, forecast load, current maximum load, competitiveness and a Census-based low-income concentration proxy. The City scores stay unchanged. Equity uses uniform within-tract allocation to a five-hundred-metre road-proxy catchment and is standardized against the sixteen common-baseline corridors.

The source-only correlation plot shows the relationships we actually examined. No pair reaches our exploratory absolute-correlation threshold of point seven, but that does not prove independence. Concept budgets and deletion tests address repeated weighting separately. Missing City cells use declared minimum and mean scenarios; suppressed Census contributions remain flagged. This is a transparent need-priority model with partial place and prosperity coverage, not a claim to measure every policy outcome.''',
'''One source ambiguity changed our recommendation. Jane's reported subsection lengths appear inconsistent with road-proxy lengths, but we found no official correction. We did not swap lengths or alter standardized scores. Instead, we removed the disputed length-scaled current-ridership indicator and repeated the paired analysis.

Jane twelve's top-five support fell to about sixty-six point six percent. Finch East remained first or second in the six specified method and weight cases. Those cases were resampled ten thousand times with fixed selectors; they are six scenarios, not ten thousand independent data sets. This is why the source-quality check matters: the corridor choice responds to a disputed input rather than hiding its influence.''',
'''We therefore select corridor twenty-three under our declared service and equity agenda. All twenty-four receive contextual evaluation, while the eight conditional extensions retain prerequisite and bundle assessments. Their scores assume different networks, so we do not invent a pooled common-baseline rank.

The word robust needs a boundary. Finch East is top-five in one hundred percent of the original paired support, but only eighty-one point eight two percent under our broader illustrative block-weight prior. These are assumption-dependent preference frequencies, not statistical confidence. Stronger place-growth and employment evidence could change the decision. We accept and disclose that scope as we carry one fixed corridor into Part Two.''',
'''Now we compare technologies on the fixed seven point one zero one kilometre corridor. Subway is excluded from our conservative base-case shortlist because a complete nine-year delivery programme and allocated depot/access strategy have not been demonstrated. This is a screening policy, not proof of physical impossibility.

We retain BRT and LRT with explicit cost points of three hundred and fifty million and nine hundred and fifty million dollars. The Eglinton West surface-option proportions allocate land, vehicles, systems and contingency within those totals. We remove the separately reported professional-services allowance as a disclosed proxy; it is not an audited consultant-only reconciliation. Nor does the allocation validate a complete project budget. Its low land share reflects airport acquisition assumptions. The purpose is to expose cost composition without adding the same components twice.''',
'''Delivery uses four milestones, not a detailed construction schedule. Our assumed phases are one to two years for planning, one to two for property and utilities, three to four for core construction and one for testing. That is six to nine years.

The upper calendar starts in January twenty-twenty-seven and reaches operational readiness in December twenty-thirty-five. It has no extra delay buffer. Fleet, systems and depot access must fit inside these milestones. We do not claim a guaranteed opening or a proven four-to-six-year BRT programme. The recommendation carries explicit delivery conditions instead of treating the deadline as a slogan.''',
'''Benefits are also declared assumptions. We use ridership indices of one and one point two, with one-way end-to-end savings of two and a half and three and a half minutes. TTC and City signal-priority pilots provide context; their selected-intersection maxima do not validate Finch East averages.

The existing model combines capital effectiveness, relative demand and time savings with ratio-to-best normalization. Equal weights give BRT point eight four nine and LRT point eight one four. Capital-efficiency priority also selects BRT; service-benefit priority selects LRT. Effectiveness contains demand, so we disclose the overlap and retain earlier definition and normalization sensitivities. Choosing BRT is a stated policy judgement, not a claim that every possible weighting selects it.''',
'''OpenAI ChatGPT and Codex assistance supported source review, data processing, code, models, computation, figures and substantive writing, including these slides, the abstract and rehearsal material. We disclose these actual uses under the applicable AI permissions confirmed by our team. Accuracy, interpretation and the final recommendation remain our responsibility.''',
'''Official reports, data sources and numerical outputs are identified here and in the supporting archive.''',
'''The reference list continues.''',
'''Our final recommendation to LARPERS is BRT for the entire Finch East corridor. Under the assumed three-hundred-and-fifty-million-dollar cost point, it uses about two point one percent of the budget ceiling; that arithmetic is not a verified fiscal surplus. It wins our unchanged equal baseline and capital-efficiency priority, while LRT remains the service-priority alternative.

We propose protecting feasible future rail options through corridor and structure checks, coordinated utility siting and useful as-built records. Future conversion would need separate engineering, approvals, rail vehicles, maintenance arrangements, works and funding. It is not a seamless or free upgrade, and we have not costed it.

Choose BRT now under the priorities we have stated. Make its delivery assumptions accountable, and preserve tomorrow's options where evidence and design support them.'''
]
ENDS=[20,100,170,230,320,380,445,475,483,490,570]
TITLES=['Title','Part 1: indicators and EDA','Part 1: Jane-to-Finch stress','Part 1: selected corridor and limits','Part 2: screening and costs','Part 2: milestones','Part 2: benefits and policy','AI Use Disclosure','References 1','References 2','Final Recommendation: BRT']


def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def build_presentation(meta):
    prs=Presentation(ROOT/'slides/task2_brt_recommendation_v0.5_review_draft.pptx')
    prs.core_properties.title=meta['presentation_title']
    prs.core_properties.author='Team '+meta['team_number']+': '+'; '.join(meta['member_full_names'])
    prs.core_properties.subject='UGCC 2026 Statistical Sciences: corridor and technology recommendation'
    prs.core_properties.keywords='S06, TRUST-Line, Finch East, BRT, AI assistance disclosed'
    ink=RGBColor.from_string('203D55');teal=RGBColor.from_string('146C78')
    def text(slide,x,y,w,h,value,size=19,bold=False):
        tf=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame;tf.word_wrap=True
        for i,line in enumerate(value.split('\n')):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=ink;p.space_after=Pt(8)
    def add(title,position):
        s=prs.slides.add_slide(prs.slide_layouts[6]);text(s,.5,.25,12.3,.8,title,27,True)
        sid=prs.slides._sldIdLst[-1];prs.slides._sldIdLst.remove(sid);prs.slides._sldIdLst.insert(position,sid)
        return s
    s=add('Part 1: five cost-independent indicators, all 24 assessed',1)
    text(s,.65,1.35,6.75,4.85,'Main rank: 16 common-baseline corridors\nReserves: 8 conditional extensions, with prerequisites\n\nSpeed need • forecast load • current max load\nCompetitiveness • low-income concentration\n\nS = weighted sum of five standardized inputs\nEquity reference: mean 13.72%, SD 2.47 percentage points\n\nSource-only relationships: no |r|≥0.7 screen flag. This does not prove independence.',18)
    s.shapes.add_picture(str(ROOT/'outputs/model_argument_v0.8/correlation_source_compact.png'),Inches(7.65),Inches(1.35),width=Inches(5.1),height=Inches(4.22))
    text(s,.65,6.35,12.05,.45,'City values unchanged; minimum/mean missing-data scenarios. Uniform CT/500m proxy, not official LIM prevalence. (City of Toronto, 2024; Statistics Canada, 2022).',11)
    s=add('A disputed input changed Jane 12 → Finch East 23',2)
    s.shapes.add_picture(str(ROOT/'outputs/jane_stress_v0.7/jane_finch_rank_stress.png'),Inches(.45),Inches(1.15),width=Inches(12.4),height=Inches(5.68))
    text(s,.6,6.85,12.1,.18,'Reported Jane lengths remain unresolved. Scores were not edited. (City of Toronto, 2024, Table 2; paired source-preserving stress model).',10)
    s=add('Select Finch East under the declared service/equity agenda',3)
    text(s,.7,1.35,11.9,.65,'23: Finch Ave E | Yonge–Victoria Park | 7.101 km',29,True)
    text(s,.7,2.35,11.9,3.65,'After disputed-ridership exclusion: rank 1–2 in all six exact main-tier cases.\nAll 24 evaluated contextually; eight conditional corridors retain bundle/prerequisite review.\n\n100% top-five applies to the original paired scenario support.\nBroader block-weight prior: 81.82% top-five — no absolute-immunity claim.\n\nThree-principle coverage remains partial: service/equity need is scored; housing, growth and jobs are not fully measured.',22)
    text(s,.7,6.45,11.9,.35,'(City of Toronto, 2024; Statistics Canada, 2022). Source, substitution and broader-weight analyses are supplied in the archive.',11)
    # Replace title metadata and obsolete draft-policy notices in the current copy only.
    for shape in prs.slides[0].shapes:
        if not shape.has_text_frame:continue
        value=shape.text
        if value.startswith('TRUST-Line:'):shape.text=meta['presentation_title']
        elif '[ADD TEAM NAME]' in value:
            shape.text='Team '+meta['team_number']+' | '+meta['team_name']+'\n'+'; '.join(meta['member_full_names'])
        elif 'Task 2 recommendation package' in value:shape.text=value.replace('Task 2 recommendation package','Two-stage corridor and technology recommendation')
        elif value.startswith('Review draft:'):shape.text='Final recommendation and disclosed assumptions | AI Use Disclosure included'
        for p in shape.text_frame.paragraphs:p.font.name='Arial';p.font.color.rgb=ink;p.font.size=Pt(20 if not value.startswith('TRUST-Line:') else 27)
    ai=next(sl for sl in prs.slides if sl.shapes[0].text=='AI Use Disclosure')
    for shape in list(ai.shapes)[1:]:shape._element.getparent().remove(shape._element)
    text(ai,.7,1.4,11.9,.6,'Tool: OpenAI ChatGPT / Codex assistant',24,True)
    text(ai,.7,2.2,11.9,2.45,'Used for source discovery/review, data processing, code, model/scenario development, computational analysis, figures, and substantive slide, abstract, documentation and rehearsal writing.\nThe team reviewed the evidence, adopted the decision priorities and selected the final recommendation.',22)
    text(ai,.7,5.1,11.9,1.0,'AI use is disclosed under the applicable permissions confirmed by the team. Accuracy, interpretation and final decisions remain the team’s responsibility.',21,True)
    text(ai,.7,6.4,11.9,.3,'(OpenAI, n.d.). Actual assistance is not represented as grammar-only or unaided student work.',12)
    refs=list(REFERENCES)+[
        ('City of Toronto. (2024, February 12). Prioritization of higher-order transit: Corridor evaluation procedure.', 'https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243172.pdf'),
        ('Statistics Canada. (2022). Census Profile, 2021 Census of Population [Data set; 2020 income and 2021 population/geography].','https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/')]
    refs.sort(key=lambda x:x[0])
    reference_slides=[sl for sl in prs.slides if sl.shapes[0].text.startswith('References')]
    for j,slide in enumerate(reference_slides):
        for shape in list(slide.shapes)[1:]:shape._element.getparent().remove(shape._element)
        text(slide,.65,1.25,12.0,5.55,'\n'.join(ref+' '+url if url else ref for ref,url in refs[j*6:(j+1)*6]),12)
    if len(prs.slides)!=11:raise ValueError('Expected whole-case eleven-slide deck')
    for i,slide in enumerate(prs.slides):
        for shape in list(slide.shapes):
            if shape.has_text_frame and shape.text.startswith('TRUST-Line v0.5 |'):
                shape._element.getparent().remove(shape._element)
        text(slide,.5,7.13,12.3,.22,f'S06 | TRUST-Line | AI assistance disclosed; scenario estimates and limits stated | {i+1}',9)
        slide.notes_slide.notes_text_frame.text=NOTES[i]
    path=DEST/'S06_TRUST_LINE_FINAL.pptx';prs.save(path)
    (DEST/'REFERENCES.md').write_text('# References\n\n'+'\n\n'.join((ref+' '+url).rstrip() for ref,url in refs)+'\n')
    return path


def build_abstract(meta):
    if words(ABSTRACT)>=200:raise ValueError('Abstract must be fewer than 200 words')
    style=getSampleStyleSheet();style.add(ParagraphStyle(name='BodyFinal',fontName='Helvetica',fontSize=11,leading=15,spaceAfter=12))
    members='; '.join(meta['member_full_names'])
    story=[Paragraph(html.escape(meta['presentation_title']),style['Title']),Paragraph('Team '+meta['team_number']+' | '+html.escape(members),style['Normal']),Spacer(1,15),Paragraph(html.escape(ABSTRACT),style['BodyFinal'])]
    for ref,url in [REFERENCES[2],REFERENCES[6]]:
        ref=ref.replace('(2020a, February)','(2020, February)')
        story.extend([Paragraph(html.escape(ref+' '+url),style['Normal']),Spacer(1,8)])
    SimpleDocTemplate(str(DEST/'S06_ABSTRACT.pdf'),pagesize=letter,title=meta['presentation_title'],author='Team '+meta['team_number']+': '+members,leftMargin=50,rightMargin=50,topMargin=45,bottomMargin=45).build(story)
    (DEST/'ABSTRACT_EN.txt').write_text(ABSTRACT+'\n');(DEST/'ABSTRACT_ZH.txt').write_text(ABSTRACT_ZH+'\n')


def build_rehearsal():
    rows=[];start=0;text=['# S06 whole-case ten-minute rehearsal','',
        'Integrated Task 1 + Task 2. Word-rate pacing is an estimate, not a completed live rehearsal. Read every speaker transition aloud; record actual splits. The 10-minute target avoids reliance on conflicting 15-minute wording.','']
    for i,(note,end,title) in enumerate(zip(NOTES,ENDS,TITLES),1):
        count=words(note);duration=end-start
        speaker='Zhuo Chen' if i<=3 else 'Yue Tang' if i<=5 else 'Yuen Song (Rain)' if i<=7 else 'Zihan Cao (Dalton)'
        row=dict(slide=i,title=title,proposed_speaker=speaker,start_seconds=start,end_seconds=end,words=count,estimated_seconds_at_130_wpm=count/130*60,slot_margin_seconds=duration-count/130*60,actual_elapsed_seconds='')
        rows.append(row)
        text += [f'## Slide {i}: {start//60}:{start%60:02d}–{end//60}:{end%60:02d} | {title}',f'Proposed speaker: {speaker} (team may reassign).','',note,''];start=end
    text += ['## 9:30–10:00 reserve','', 'Stop on the recommendation. Do not use reserve to add new claims.','',
        '## Private practice checklist','', 'Use the offline timer. Practice with every named speaker, include the disclosure, and log actual splits. Do not distribute private notes or use external models/posters/handouts with judges. The shorter prior Q&A file remains supporting practice material.','']
    (DEST/'REHEARSAL_10MIN.md').write_text('\n'.join(text))
    with (DEST/'REHEARSAL_SPLITS.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    segments=[{'start':r['start_seconds'],'end':r['end_seconds'],'title':f"Slide {r['slide']}: {r['title']}"} for r in rows]+[{'start':570,'end':600,'title':'Reserve — stop by 10:00'}]
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>S06 whole-case rehearsal timer</title><style>body{background:#173547;color:white;font:20px system-ui;max-width:900px;margin:50px auto;padding:20px}#clock{font-size:90px;font-variant-numeric:tabular-nums}button{font:inherit;padding:12px;margin:8px}#stage{color:#91d5d8;font-size:26px}</style><h1>S06 — integrated ten-minute rehearsal</h1><p>Private practice only. Includes both models, AI disclosure and references.</p><div id="clock">10:00</div><div id="stage">Ready</div><p id="slot"></p><button id="go">Start / pause</button><button id="reset">Reset</button><p>No voice, external assets or telemetry. Actual spoken timing must be measured by the team.</p><script>const stages=STAGES;let elapsed=0,running=false,last=0;const q=id=>document.getElementById(id);const fmt=s=>{s=Math.max(0,Math.ceil(s));return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')};function draw(){let s=stages.find(x=>elapsed>=x.start&&elapsed<x.end);q('clock').textContent=fmt(600-elapsed);q('stage').textContent=s?s.title:'STOP — time limit';q('slot').textContent=s?'Slot remaining: '+fmt(s.end-elapsed):'';if(elapsed>=600)running=false}q('go').onclick=()=>{running=!running;last=performance.now()};q('reset').onclick=()=>{elapsed=0;running=false;draw()};setInterval(()=>{let now=performance.now();if(running)elapsed+=(now-last)/1000;last=now;draw()},100);draw();</script></html>'''
    (DEST/'REHEARSAL_TIMER.html').write_text(page.replace('STAGES',json.dumps(segments)))
    return rows


def run():
    DEST.mkdir(parents=True,exist_ok=True)
    meta=json.loads((ROOT/'data/final_metadata_v1.0.json').read_text())
    if len(meta['member_full_names'])!=4 or meta['team_number']!='S06':raise ValueError('Team metadata incomplete')
    replay_result=replay(ROOT,ROOT/'outputs/final_replay_v1.0')
    path=build_presentation(meta);build_abstract(meta);timing=build_rehearsal()
    status=dict(team_number=meta['team_number'],members=meta['member_full_names'],corridor_id=23,technology='BRT',
        final_artifacts_assembled=True,whole_case_model_coverage=True,slide_count=11,core_task2_slides=4,
        abstract_body_words=words(ABSTRACT),chinese_short_abstract_characters=len(ABSTRACT_ZH),
        last_slide_title=Presentation(path).slides[-1].shapes[0].text,
        team_confirmed_AI_permission=True,organizer_AI_permission_independently_verified=False,AI_disclosure_included=True,
        live_rehearsal_completed=False,script_words=sum(r['words'] for r in timing),
        speech_estimate_seconds_at_130_wpm=sum(r['estimated_seconds_at_130_wpm'] for r in timing),
        slot_overruns_at_130_wpm=[r['slide'] for r in timing if r['slot_margin_seconds']<0],
        numerical_replay_passed=replay_result['model_replay_passed'],external_submission_performed=False,
        full_capital_or_delivery_or_conversion_certified=False)
    (DEST/'STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
    (DEST/'README.md').write_text('''# S06 TRUST-Line — final assembled version

Recommendation: **corridor 23, Finch East (Yonge–Victoria Park), BRT**, with feasible future LRT options studied rather than promised. Team: Zhuo Chen; Yue Tang; Yuen Song (Rain); Zihan Cao (Dalton).

## Use these files

- `S06_TRUST_LINE_FINAL.pptx`: integrated eleven-slide whole-case presentation. Both models, EDA, sensitivity, single-technology recommendation, AI disclosure and references are present. Last slide: **Final Recommendation: BRT**.
- `S06_ABSTRACT.pdf`: 167-word English body, two references, full team identification; no figures/tables/equations. Plain English and Chinese short versions are provided.
- `REHEARSAL_10MIN.md`, `REHEARSAL_SPLITS.csv`, `REHEARSAL_TIMER.html`: one whole-case pacing plan, including Task 1, disclosure and references. Actual speaking/transition times are not invented; practice aloud and record them. Notes and timer are private, not judge-facing props.
- `REFERENCES.md`, `STATUS.json`, `MANIFEST.json`: citations, factual readiness/limitations and file checksums.

## Decisions and limits

The primary formula and equal weights are unchanged. BRT wins the equal/capital-efficiency cases; LRT wins the declared service-benefit case. No universal-robustness claim is made. Eight conditional corridors retain prerequisite/bundle assessment instead of fabricated common-base ranks. Census allocation, City missing-value scenarios, partial principle coverage, cost price/scope and assumed demand/time are disclosed.

The cost point is hypothetical, the milestone programme is assumed 6–9 years with zero extra buffer in its upper case, and future LRT conversion has not been costed or certified. There is no guaranteed opening, verified fiscal surplus or seamless-conversion claim.

AI policy basis: the team/user explicitly confirmed on 2026-11-22 that AI is unrestricted under the applicable rules and instructed final assembly. Actual AI assistance remains fully disclosed. This confirmation is not represented as an independently obtained organizer letter. Earlier v0.5 cautionary files are historical snapshots, superseded on that policy premise and on team identity. No outside message or competition submission has been sent.

The ten-minute whole-case version is intentionally conservative because the supplied guideline contains both general ten-minute wording and Statistical Science fifteen-minute wording. No fifteen-minute permission is assumed.

## Supporting archive: numerical replay

The sibling `S06_TRUST_LINE_FINAL.zip` contains these deliverables plus structured data, computational source, delivered outputs and provenance/documentation. After extraction from the archive's root:

```sh
python -m pip install numpy
python outputs/project/code/replay_final_models_v1_0.py
```

The offline entry point recomputes all 144 contextual Part 1 scores, main-tier rank support and Part 2 scores/weight support, comparing with the delivered results. It uses delivered Census overlay estimates; it does not rebuild GIS overlays. Large geographic archives and public source PDFs are referenced through their original URLs/checksums rather than duplicated in this compact model package. The complete repository preserves raw acquisitions and historical validators: https://github.com/Cz-lov-y/trust-line-ugcc-2026

Full historical tests and source-byte audits should be run from the complete repository with its GIS and presentation requirements, rather than the compact archive. Do not confuse numerical replay with engineering certification or completed human rehearsal.
''')
    return status


def package():
    """Build compact source/data/output ZIP without recursive delivery archives."""
    if not (DEST/'STATUS.json').exists():raise ValueError('Build deliverables first')
    files={p.relative_to(DEST).as_posix():p for p in DEST.iterdir() if p.is_file() and p.name!='MANIFEST.json'}
    (DEST/'MANIFEST.json').write_text(json.dumps({k:sha(p) for k,p in files.items()},indent=2)+'\n')
    files['MANIFEST.json']=DEST/'MANIFEST.json'
    for folder in ['data','code','outputs']:
        for p in (ROOT/folder).rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
            if folder=='code' and p.name.startswith('test_'):continue
            if folder=='outputs' and p.relative_to(ROOT/'outputs').parts[0] not in ['tiered_v0.6','jane_stress_v0.7','model_argument_v0.8','task2_v0.1','task2_v0.2','task2_v0.3','task2_v0.4','final_replay_v1.0']:continue
            files[p.relative_to(REPO).as_posix()]=p
    for p in (ROOT/'evidence').rglob('*'):
        if p.is_file() and p.suffix in ['.csv','.json','.md'] and p.stat().st_size<2_000_000:
            files[p.relative_to(REPO).as_posix()]=p
    files['outputs/project/README.md']=ROOT/'README.md'
    index={k:sha(p) for k,p in files.items()}
    archive=DEST.parent/'S06_TRUST_LINE_FINAL.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,p in sorted(files.items()):z.write(p,'S06_TRUST_LINE_FINAL/'+name)
        z.writestr('S06_TRUST_LINE_FINAL/ARCHIVE_CONTENTS_SHA256.json',json.dumps(index,indent=2)+'\n')
    return archive


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--package',action='store_true');a=p.parse_args()
    if a.package:print(package())
    else:print(json.dumps(run(),indent=2))
