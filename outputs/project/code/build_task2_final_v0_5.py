"""Create BRT recommendation drafts, honest disclosure, abstracts and rehearsal.

This locks the user's recommendation without changing earlier model evidence.
Guideline compliance and live rehearsal are not inferred from generated files.
"""
from pathlib import Path
from datetime import date
import csv
import hashlib
import html
import json
import re
import zipfile

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches,Pt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer

ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/task2_v0.5'

ABSTRACT=(
    'TRUST-Line recommends bus rapid transit (BRT) for the 7.101 km Finch East corridor from Yonge Street to Victoria Park Avenue, selected using a cost-independent, tiered first-stage model. '
    'Subway is excluded from the conservative base case because a credible nine-year delivery and depot strategy has not been demonstrated. '
    'We computationally compare BRT and light rail transit using capital effectiveness, relative ridership and travel-time savings. '
    'Explicit scenario inputs are CAD350 million versus CAD950 million, ridership indices of 1.0 versus 1.2, and one-way savings of 2.5 versus 3.5 minutes. '
    'BRT leads under equal and capital-efficiency priorities; service-benefit priorities favour LRT. '
    'Reference-project cost proportions and four milestones make assumptions transparent (Metrolinx, 2020; Toronto Transit Commission, 2026). '
    'We recommend assessing feasible corridor and utility reservations for possible future LRT conversion, which would require separate engineering, funding and approval. '
    'Key limitations are transferred costs, assumed demand and time savings, policy-dependent results, and delivery risks. '
    'The analysis does not establish verified total costs, guaranteed 2035 opening or seamless conversion.'
)
ABSTRACT_ZH='我们推荐在Finch East的Yonge—Victoria Park段建设BRT。地铁因工期与车辆段方案未获证实，被保守筛除；BRT与LRT按成本效益、客流及时间节省比较，BRT在等权和资本效率优先下胜出，服务优先则转向LRT。建议研究路权与管线预留，保留未来LRT转换可能；升级须另行设计、审批和融资。成本、客流与工期仍为声明假设。'

REFERENCES=[
    ('Aecon. (2018, May 7). Aecon consortium reaches financial close on Finch West Light Rail Transit project.', 'https://www.aecon.com/press-room/news/2018/05/07/1428-Aecon-consortium-reaches-financial-close-on-Finch-West-Light-Rail-Transit-project'),
    ('City of Toronto. (2026). Congestion management plan 2026–2028: Attachments [Attachment 6, enhanced transit signal priority].', 'https://www.toronto.ca/legdocs/mmis/2026/ie/bgrd/backgroundfile-285484.pdf'),
    ('Metrolinx. (2020a, February). Eglinton Crosstown West Extension initial business case.', 'https://assets.metrolinx.com/image/upload/v1668540646/Images/Metrolinx/2020-02-28_ECWE_IBC.pdf'),
    ('Metrolinx. (2020b, June). Finch West Light Rail Transit project: Frequently asked questions.', 'https://assets.metrolinx.com/image/upload/v1663240053/Documents/Metrolinx/Finch-West-LRT-FAQs-Revised-June9.pdf'),
    ('Metrolinx. (2025). Finch West LRT is now open.', 'https://www.metrolinx.com/en/news/finch-west-lrt-is-now-open'),
    ('OpenAI. (n.d.). ChatGPT [Large language model; ChatGPT/Codex assistance in this project].', 'https://chatgpt.com/'),
    ('Toronto Transit Commission. (2026, April 16). Improving LRT and streetcar speed and reliability.', 'https://www.toronto.ca/legdocs/mmis/2026/ttc/bgrd/backgroundfile-285894.pdf'),
    ('UTSRI. (2026). UGCC 2026 guideline package. [Supplied competition document; pp.11–13, 19–22].', ''),
    ('UTSRI & NRCI. (2026). Drawing Toronto’s line of best fit [Statistical Sciences case brief; pp.6, 9–11].', ''),
    ('York Region Rapid Transit Corporation. (2020, January 3). Viva bus rapid transit segments opening in Vaughan and Newmarket.', 'https://www.yrrtc.ca/news_releases/2020-01-03_Viva-Bus-Rapid-Transit-Segments-Opening-in-Vaughan-and-Newmarket')
]

SPEECH={
'title':'''We recommend BRT for the fixed Finch East corridor, with practical safeguards for a possible future rail conversion. Our decision connects the choice we can defend today with the options we should preserve for tomorrow. These slides present our Task Two analysis.''',
'core_1':'''The corridor is fixed: Finch East, from Yonge Street to Victoria Park Avenue, using the City's assumed construction length of 7.101 kilometres. Our first decision is which technologies to carry into the base-case comparison.

We exclude Subway under a conservative delivery and depot policy. We have not demonstrated a complete nine-year underground programme or an allocated, compatible depot and access solution. That is a reason for our screening decision. It is not proof that subway construction is physically impossible, and it is not a claim that Wilson has zero spare capacity.

We retain BRT and LRT as conditional alternatives. Our chosen scenario costs are 350 million and 950 million Canadian dollars. To check their composition, we use the mostly surface-running option in the Eglinton West business case. After a disclosed professional-services exclusion proxy, we allocate the remaining proportions inside those totals.

That distinction matters. We do not add vehicles, land or contingency again on top of the totals. We also do not claim that a balanced allocation independently validates a complete capital estimate. The low source land share reflects its airport acquisition assumptions, and the same LRT composition is only an approximation for BRT.

Our first result is a transparent comparison: a fixed corridor, a declared shortlist, and costs whose assumptions remain visible.''',
'core_2':'''A deadline becomes meaningful when we state what has to happen before opening. We use four milestones: planning and approvals; property and utility enabling works; core construction and systems; and testing and commissioning.

The assumed durations are one to two years, one to two years, three to four years, and one year. Sequentially, that is six to nine years. In the illustrative upper case, a January 2027 programme start leads to approvals by the end of 2028, enabling works by 2030, construction and systems by 2034, and operational readiness by the end of 2035.

The nine-year case has no extra delay buffer. We therefore cannot promise that BRT automatically guarantees the deadline, or say that its construction is proven to take four to six years. Fleet procurement, depot access and systems must fit within the milestones we show. They cannot appear as additional phases after the deadline.

Local experience is a reality check. The Newmarket BRT segment took roughly four years from construction to opening. Finch West took roughly nine years from early gas relocation to opening, before counting earlier planning. Those histories inform judgement without becoming a precise forecast for this corridor.

Our recommendation therefore includes a delivery discipline: agree the operator and depot strategy early, identify land and utility risks, and preserve the testing year. This is the credible milestone argument requested by the case, with its uncertainty stated openly.''',
'core_3':'''The benefit comparison also separates evidence from assumptions. TTC reports improvements of up to thirty seconds at selected intersections; the City reports up to twenty-five seconds in its corresponding pilot discussion. Finch West's roughly twenty-minute round-trip improvement since opening includes several operational changes alongside signal priority.

Those figures are not whole-corridor forecasts for Finch East. Our target assumptions remain fifteen signals, two and a half minutes saved for BRT, and three and a half for LRT on a one-way end-to-end trip. If the signals contributed equally, these would imply ten and fourteen seconds per signal. Being below a pilot maximum does not establish a target average.

We also assume relative ridership of one for BRT and one point two for LRT. We do not invent a daily passenger total or infer demand directly from vehicle capacity.

The existing model combines capital effectiveness, relative demand and time savings, with ratio-to-best normalization. Under equal weights, BRT scores zero point eight four nine and LRT zero point eight one four. Capital-efficiency priority also selects BRT. Service-benefit priority selects LRT.

That is the useful policy result: the recommendation has a visible boundary. With demand and time weights equal, the efficiency-weight tie is about twenty-eight point eight five percent. We disclose that effectiveness already contains demand; weight switching exposes priorities rather than mathematically removing the overlap. Our earlier normalization sensitivity is retained in the supporting analysis.''',
'ai':'''Our work used OpenAI ChatGPT and Codex assistance for source review, code, data processing, modelling, analysis, figures and substantive writing, including these drafts. The supplied guideline restricts substantive AI use. Disclosure does not resolve that issue, and we have not verified an applicable exception. This material remains a review draft without submission clearance.''',
'references':'''These are the official project and operating sources behind our assumptions and checks. The supporting files preserve locators, calculations and limitations.''',
'core_4':'''Our final recommendation to LARPERS is BRT for the entire Finch East corridor, with future LRT options considered in design.

We choose the technology that wins our declared equal-weight baseline and capital-efficiency priority. Its assumed 350-million-dollar point cost is approximately two point one percent of the 16.657-billion-dollar ceiling. That is scenario arithmetic, not a verified funding surplus. Our reason for choosing BRT is the combination of that capital advantage and its performance under the priorities we have stated, while acknowledging that a service-priority policy would favour LRT.

LRT-readiness means protecting useful options where feasible. Before irreversible decisions, assess corridor and structure clearances, coordinate utility siting, and preserve reliable as-built information. Monitor demand and operating performance before considering conversion.

It does not mean installing two technologies now, promising free reservations, or assuming seamless conversion. A future LRT decision would need its own engineering, land and access, approvals, rail vehicles, systems, maintenance strategy and funding. We have not costed that future project or certified conversion feasibility.

The commitment we ask for today is clear: BRT as the recommended current technology, a transparent delivery and cost basis, and disciplined protection of future choices. Put a defensible service decision in front of today's riders. Keep tomorrow's rail option open only where the evidence and design support it.'''
}

PLAN_10=[('title',0,20),('core_1',20,140),('core_2',140,260),('core_3',260,400),('ai',400,430),('references',430,450),('core_4',450,570),('buffer',570,600)]
PLAN_15=[('title',0,30),('core_1',30,210),('core_2',210,390),('core_3',390,600),('ai',600,645),('references',645,675),('core_4',675,855),('buffer',855,900)]
LABELS={'title':'Title / opening','core_1':'Core 1: screen Subway and compare costs','core_2':'Core 2: four milestones','core_3':'Core 3: evidence, assumptions and policy scores','ai':'AI Use Disclosure — present aloud','references':'References — identify sources','core_4':'Core 4: Final Recommendation: BRT','buffer':'Buffer — stop, do not add a new claim'}


def words(text):return len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b",text))


def read_csv(path):
    with path.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))


def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def build_abstract(metadata):
    name_line=', '.join(metadata['member_full_names']) or '[ADD ALL TEAM MEMBERS’ FULL NAMES]'
    title=metadata['presentation_title'];status='AI-assisted review draft — not cleared for submission.'
    count=words(ABSTRACT);conservative=len(re.findall(r'\b\w+\b',ABSTRACT+' '+status))
    if max(count,conservative)>=200 or len(ABSTRACT_ZH)>200:raise ValueError('Abstract length exceeds requested limit')
    (O/'abstract_en.txt').write_text(ABSTRACT+'\n')
    (O/'abstract_zh_under200.txt').write_text(ABSTRACT_ZH+'\n')
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='AbstractBody',fontName='Helvetica',fontSize=11,leading=15,spaceAfter=12))
    styles.add(ParagraphStyle(name='Review',fontName='Helvetica-Bold',fontSize=9,leading=12,textColor=colors.darkred,spaceAfter=12))
    story=[Paragraph(html.escape(title),styles['Title']),Paragraph(html.escape(name_line),styles['Normal']),Spacer(1,12),
        Paragraph(status,styles['Review']),Paragraph(html.escape(ABSTRACT),styles['AbstractBody'])]
    # Abstract has two APA references only; presentation uses suffixes where two Metrolinx 2020 items coexist.
    refs=[REFERENCES[2][0].replace('(2020a, February)','(2020, February)')+' '+REFERENCES[2][1],REFERENCES[6][0]+' '+REFERENCES[6][1]]
    for ref in refs:story.append(Paragraph(html.escape(ref),styles['Normal']));story.append(Spacer(1,7))
    path=O/'abstract_review_draft.pdf';SimpleDocTemplate(str(path),pagesize=letter,leftMargin=50,rightMargin=50,topMargin=45,bottomMargin=45).build(story)
    (O/'ABSTRACT_REVIEW.md').write_text('# Abstract review draft\n\n'+title+'\n\n'+name_line+'\n\n'+status+'\n\n'+ABSTRACT+'\n\n## References\n\n'+'\n\n'.join(refs)+'\n')
    return dict(english_body_words=count,english_conservative_count_including_review_label=conservative,
                chinese_characters=len(ABSTRACT_ZH),reference_count=2,team_names_complete=bool(metadata['member_full_names']),submission_ready=False)


def build_deck(metadata,decision,core_only=False):
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    ink=RGBColor.from_string('203D55');teal=RGBColor.from_string('146C78');red=RGBColor.from_string('A23D32')
    def text(s,x,y,w,h,value,size=19,bold=False,color=ink):
        frame=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame;frame.word_wrap=True
        for i,line in enumerate(value.split('\n')):
            p=frame.paragraphs[0] if i==0 else frame.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color;p.space_after=Pt(8)
    def slide(title,key=None):
        s=prs.slides.add_slide(prs.slide_layouts[6]);text(s,.5,.25,12.3,.8,title,27,True)
        text(s,.5,7.06,12.3,.25,f'TRUST-Line v0.5 | AI-assisted review draft; no compliance clearance | {len(prs.slides)}',9)
        if key:s.notes_slide.notes_text_frame.text=SPEECH[key]
        return s
    def table(s,rows,y,h,widths,size=16):
        t=s.shapes.add_table(len(rows),len(rows[0]),Inches(.6),Inches(y),Inches(12.1),Inches(h)).table
        for col,w in zip(t.columns,widths):col.width=Inches(w)
        for i,row in enumerate(rows):
            for j,v in enumerate(row):
                c=t.cell(i,j);c.text=str(v)
                if i==0:c.fill.solid();c.fill.fore_color.rgb=teal
                for p in c.text_frame.paragraphs:p.font.name='Arial';p.font.size=Pt(size);p.font.bold=i==0;p.font.color.rgb=RGBColor(255,255,255) if i==0 else ink
    if not core_only:
        s=slide('TRUST-Line: BRT for Finch East','title')
        text(s,.7,1.5,11.9,1.0,'A current BRT recommendation. Feasible future rail options.',30,True,color=teal)
        text(s,.7,2.85,11.9,1.0,'Corridor 23 | Yonge–Victoria Park | 7.101 km\nTask 2 recommendation package for LARPERS',22)
        team=metadata['team_name'] or '[ADD TEAM NAME]';names='; '.join(metadata['member_full_names']) or '[ADD ALL TEAM MEMBERS’ FULL NAMES]'
        text(s,.7,4.2,11.9,.9,team+'\n'+names,20,True,color=red if not metadata['member_full_names'] else ink)
        text(s,.7,5.65,11.9,.85,'Review draft: substantive AI assistance is disclosed. Guideline eligibility remains unresolved; disclosure alone is not clearance.',18,True,color=red)
    s=slide('Screen first. Keep the cost assumptions visible.','core_1')
    text(s,.7,1.1,11.9,.65,'Subway: excluded by conservative delivery/depot policy — physical impossibility is not proven.',17,True)
    rows=[['Allocation inside assumed total','Share','BRT CAD M','LRT CAD M']]
    allocation=read_csv(ROOT/'outputs/task2_v0.4/cost_ratio_allocation.csv');lookup={(r['technology_id'],r['category']):r for r in allocation}
    for key,label in [('property','Property'),('vehicles','Vehicles'),('systems','Systems'),('contingency','Contingency'),('other_capital_and_reconciliation','Other / indirect / tax')]:
        b,l=lookup['BRT',key],lookup['LRT',key];rows.append([label,f'{float(b["template_share"]):.2%}',f'{float(b["allocated_cad"])/1e6:.2f}',f'{float(l["allocated_cad"])/1e6:.2f}'])
    rows.append(['TOTAL — unchanged','100%','350.00','950.00']);table(s,rows,1.95,3.1,[5.1,1.6,2.7,2.7],16)
    text(s,.7,5.35,11.9,.95,'ECWE surface-option proportions, with a disclosed professional-services exclusion proxy. Allocation balances the chosen totals; it does not validate complete capital or Finch East land needs.',18)
    text(s,.7,6.5,11.9,.3,'(Metrolinx, 2020a, Table 19, pp.70–71; UTSRI & NRCI, 2026, pp.6, 10–11). User-selected totals; source/table reconciliation retained.',11)
    s=slide('Four milestones to a conditional 2035 opening','core_2')
    rows=[['Milestone','Assumed duration','Upper-case completion']]
    for r in read_csv(ROOT/'outputs/task2_v0.4/delivery_milestones.csv'):
        lo,hi=float(r['lower_years']),float(r['upper_years']);rows.append([r['stage'],f'{lo:g}–{hi:g} years' if lo!=hi else f'{hi:g} year',r['illustrative_upper_case_completion']])
    table(s,rows,1.4,2.9,[6.0,2.2,3.9],16)
    text(s,.7,4.65,11.9,1.25,'Illustrative start January 2027. Sequential range 6–9 years; the upper case opens by December 2035 with zero extra delay buffer. Fleet, depot/access and systems must fit inside these phases.',20)
    text(s,.7,6.05,11.9,.55,'A milestone assumption, not a guaranteed 4–6 year BRT programme or proof that LRT must take longer.',16,True)
    text(s,.7,6.65,11.9,.25,'(Metrolinx, 2020b, p.1; Metrolinx, 2025; York Region Rapid Transit Corporation, 2020; UTSRI & NRCI, 2026, p.10).',11)
    s=slide('Compare benefits. Show where policy changes the answer.','core_3')
    table(s,[['Assumed target input / primary score','BRT','LRT'],['Cost point, hypothetical CAD','350M','950M'],['Relative ridership index','1.0','1.2'],['One-way end-to-end saving','2.5 min','3.5 min'],['Equal-weight ratio score','0.849','0.814']],1.35,2.7,[6.5,2.8,2.8],17)
    text(s,.7,4.35,11.9,1.5,'TTC/City report selected-intersection maxima of 30/25 sec. At 15 assumed signals, the target savings imply 10/14 sec each; maxima do not validate those averages.\nEqual and capital-efficiency priorities favour BRT; service-benefit priority favours LRT. E=R/C overlaps with R; that limitation stays visible.',19)
    text(s,.7,6.3,11.9,.45,'(Toronto Transit Commission, 2026, pp.1, 6, 9; City of Toronto, 2026, Attachment 6, p.20). Target demand/time are user assumptions.',11)
    if not core_only:
        s=slide('AI Use Disclosure','ai')
        text(s,.7,1.35,11.9,.65,'Tool: OpenAI ChatGPT/Codex assistant',23,True)
        text(s,.7,2.05,11.9,2.2,'Used for source discovery/review, data processing, code, model/scenario development, computation, figures, and substantive slides, documents, abstract and rehearsal text.\nThese outputs are not represented as unaided student work. Exact individual contributions require team verification.',21)
        text(s,.7,4.65,11.9,1.35,'Guideline p.22 restricts substantive AI use. No applicable designated-case exception is verified. Adding this slide does not itself establish compliance; the material remains an uncleared review draft.',21,True,color=red)
        text(s,.7,6.3,11.9,.4,'(OpenAI, n.d.; UTSRI, 2026, pp.11, 19, 22). Do not relabel these uses as spelling/grammar only.',12)
        for number,chunk in enumerate([REFERENCES[:5],REFERENCES[5:]],1):
            s=slide(f'References ({number}/2)','references' if number==1 else None)
            value='\n\n'.join(ref+'\n'+url if url else ref for ref,url in chunk)
            text(s,.65,1.25,12.0,5.55,value,13)
    s=slide(metadata['slide_last_title'],'core_4')
    text(s,.7,1.3,11.9,.75,'BRT now. Preserve feasible future LRT options.',29,True,color=teal)
    share=decision['scenario_cost_cad']/decision['capital_ceiling_cad']
    text(s,.7,2.25,11.9,1.35,f'Choose BRT for the full Finch East corridor under the declared baseline.\nCAD350M scenario cost = {share:.2%} of the capital ceiling; equal and capital-efficiency profiles support BRT. The cost point and delivery remain assumptions.',21)
    text(s,.7,3.9,11.9,1.75,'LRT-readiness: assess feasible corridor/structure clearances, coordinate utilities and retain useful as-built information. Reconsider rail when observed demand and operating constraints justify it.\nFuture conversion needs separate design, approvals, fleet/MSF, funding and works. Readiness and conversion costs are unestimated; no seamless-upgrade promise.',20)
    text(s,.7,6.15,11.9,.65,'One technology for the current project. Service-priority weights can favour LRT; final engineering and AI compliance are not certified.',15,True)
    text(s,.7,6.83,11.9,.2,'Source: preserved v0.3 model / v0.4 milestones; future-option measures are team proposals. (UTSRI & NRCI, 2026, pp.10–11).',10)
    path=ROOT/'slides'/('task2_brt_core_v0.5_rehearsal_only.pptx' if core_only else 'task2_brt_recommendation_v0.5_review_draft.pptx');prs.save(path)
    return path


def build_rehearsal():
    transcript=['# BRT rehearsal: review draft','',
        'This is a timed practice plan and script, not a completed live rehearsal. No speech recognition, generated voice or recorded presentation is used. Guideline AI restrictions still apply to substantive script generation.',
        '', 'Ten-minute standalone Task 2 practice target; actual full-case timing must also include Task 1. The fifteen-minute option is an expanded practice aid pending clarification of the guideline timing conflict.','']
    audit=[]
    for key,start,end in PLAN_10:
        script=SPEECH.get(key,'');n=words(script);duration=end-start
        audit.append(dict(segment=key,label=LABELS[key],planned_start_seconds=start,planned_end_seconds=end,
            word_count=n,estimated_speech_seconds_at_130_wpm=n/130*60,
            remaining_slot_seconds=duration-n/130*60,actual_elapsed_seconds='',actual_rehearsal_completed=False))
        transcript += [f'## {start//60}:{start%60:02d}–{end//60}:{end%60:02d} | {LABELS[key]}','',script or 'Keep as time reserve; close before the limit.','']
    transcript += ['## Fifteen-minute extension prompts','',
        'Use only after resolving the 10/15-minute conflict and budgeting Task 1. Expand the source cost denominator, explain one sensitivity example, and discuss a concrete future-conversion condition. Do not add invented performance numbers to fill time.','',
        '## Integrated full-case practice','',
        'Suggested conservative ten-minute whole-case allocation: 0:00–0:20 title; 0:20–4:20 Task 1 model/EDA/selection; 4:20–8:50 the four Task 2 core slides; 8:50–9:20 AI disclosure; 9:20–9:40 references; 9:40–10:00 reserve. This package alone does not supply the Task 1 presentation.','',
        '## Private Chinese closing cue','',
        '今天推荐的是整条走廊采用BRT。我们选择一个在既定价值权重下有依据的方案，同时谨慎保护未来转换的可能。预留需要设计和成本，升级也需要新的审批与投资；不把“可研究的选择权”说成“无缝升级的保证”。','',
        '## Live practice checklist','',
        'Open the timer privately. Deliver the four core sections aloud; present the disclosure as well. Record actual splits in the CSV. Repeat with all speakers and slide transitions. If late, cut optional explanation rather than accelerating the final recommendation. Do not show or distribute speaking notes or handouts to judges.','']
    (O/'REHEARSAL_SCRIPT.md').write_text('\n'.join(transcript))
    write_csv(O/'rehearsal_timing_plan.csv',audit)
    plan15=[dict(segment=key,label=LABELS[key],start_seconds=start,end_seconds=end) for key,start,end in PLAN_15]
    (O/'rehearsal_15min_plan.json').write_text(json.dumps(plan15,indent=2)+'\n')
    total=sum(r['word_count'] for r in audit)
    timing=dict(script_words=total,estimated_speech_seconds_at_130_wpm=total/130*60,
        target_seconds=600,reserve_seconds=30,segment_slots_overrun_at_130_wpm=[r['segment'] for r in audit if r['remaining_slot_seconds']<0],
        actual_timed_rehearsal_completed=False,estimated_timing_is_not_observed=True,full_case_includes_task1=False)
    (O/'rehearsal_estimate.json').write_text(json.dumps(timing,indent=2)+'\n')
    plans={'10':[(k,s,e) for k,s,e in PLAN_10],'15':[(k,s,e) for k,s,e in PLAN_15]}
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Private BRT rehearsal timer</title>
<style>body{font:20px system-ui;background:#142d40;color:#fff;max-width:900px;margin:50px auto;padding:20px}h1{font-size:28px}#clock{font-size:90px;font-variant-numeric:tabular-nums}button,select{font:inherit;padding:10px;margin:8px}#stage{font-size:26px;color:#8ed5d8}.warn{color:#ffd080}small{display:block;margin-top:30px;line-height:1.5}</style>
<h1>Private rehearsal — BRT recommendation</h1><p>Practice aid only; do not present or distribute to judges.</p>
<select id="mode"><option value="10">10-minute standalone Task 2 practice</option><option value="15">15-minute expanded practice — rule clarification pending</option></select>
<div id="clock">10:00</div><div id="stage">Ready</div><p id="next"></p><button id="start">Start / Pause</button><button id="reset">Reset</button>
<small>Guideline timing conflict: Statistical Science p.12 says 15 minutes; pp.10/19 say 10. This is not a complete full-case timing plan; allocate Task 1 separately. No audio, external assets or telemetry.</small>
<script>const plans=PLANS, labels=LABELS;let running=false, elapsed=0,last=0;const q=id=>document.getElementById(id);function fmt(s){s=Math.max(0,Math.ceil(s));return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}function draw(){const p=plans[q('mode').value],limit=p.at(-1)[2],s=p.find(x=>elapsed>=x[1]&&elapsed<x[2]);q('clock').textContent=fmt(limit-elapsed);q('stage').textContent=s?labels[s[0]]:(elapsed>=limit?'STOP — limit reached':'Ready');q('next').textContent=s?'Current slot ends at '+fmt(s[2])+' elapsed. '+fmt(s[2]-elapsed)+' left in slot.':'';q('clock').className=limit-elapsed<30?'warn':'';if(elapsed>=limit)running=false}q('start').onclick=()=>{running=!running;last=performance.now()};q('reset').onclick=()=>{running=false;elapsed=0;draw()};q('mode').onchange=()=>q('reset').click();setInterval(()=>{let now=performance.now();if(running)elapsed+=(now-last)/1000;last=now;draw()},100);draw();</script></html>'''
    page=page.replace('PLANS',json.dumps(plans)).replace('LABELS',json.dumps(LABELS))
    (O/'private_rehearsal_timer.html').write_text(page)
    return timing


def audit_deck(path):
    prs=Presentation(path);texts=[]
    for slide in prs.slides:
        texts.append('\n'.join(shape.text for shape in slide.shapes if shape.has_text_frame))
    with zipfile.ZipFile(path) as z:
        names=z.namelist();objects=[n for n in names if n.startswith('ppt/embeddings/') or n.startswith('ppt/media/')]
        external_media=[]
        for name in names:
            if name.endswith('.rels'):
                data=z.read(name).decode('utf-8')
                if 'TargetMode="External"' in data and any(k in data for k in ['/video','/audio','/oleObject']):external_media.append(name)
    return dict(slide_count=len(prs.slides),has_title='TRUST-Line' in texts[0],
        has_AI_disclosure=any(t.startswith('AI Use Disclosure') for t in texts),
        has_references=any(t.startswith('References') for t in texts),
        last_slide_title=texts[-1].split('\n')[0],embedded_media_or_OLE_files=objects,external_media_relationships=external_media,
        outside_slide_prop_plan='None; only slides and verbal delivery. Private cues not shown/distributed.',
        actual_room_and_physical_props_verified=False)


def run():
    O.mkdir(parents=True,exist_ok=True)
    metadata=json.loads((ROOT/'data/presentation_metadata_v0.5.json').read_text());decision=json.loads((ROOT/'data/task2_final_decision_v0.5.json').read_text())
    if decision['recommended_technology']!='BRT' or decision['future_LRT_option']['mixed_mode_current_project']:
        raise ValueError('User locked one current BRT technology')
    abstract=build_abstract(metadata);deck=build_deck(metadata,decision);core=build_deck(metadata,decision,True)
    timing=build_rehearsal();audit=audit_deck(deck)
    results=dict(recommendation_locked=True,recommended_technology='BRT',final_slide_title=audit['last_slide_title'],
        assumed_cost_ceiling_share=decision['scenario_cost_cad']/decision['capital_ceiling_cad'],abstract=abstract,deck=audit,
        rehearsal=timing,AI_compliance_clearance=False,identity_complete=bool(metadata['member_full_names']),
        external_physical_props_not_planned=True,actual_live_setup_verified=False,submission_ready=False,
        material_issues=['Substantive AI use exceeds the verified guideline permission; exception not established','Team names pending' if not metadata['member_full_names'] else 'Team identity supplied; team verification needed','Timing rules conflict','Task 2 deck requires Task 1 integration for a full-case presentation'])
    (O/'review_audit.json').write_text(json.dumps(results,indent=2)+'\n')
    return results


if __name__=='__main__':print(json.dumps(run(),indent=2))
