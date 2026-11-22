"""Four competition-scope slides; no new scoring formula or project schedule model."""
from pathlib import Path
import csv
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches,Pt

ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/task2_v0.4'


def read(name):
    with (O/name).open(newline='') as f:return list(csv.DictReader(f))


def build():
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    ink=RGBColor.from_string('203D55');teal=RGBColor.from_string('146C78')
    def text(s,x,y,w,h,value,size=20,bold=False):
        tf=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame;tf.word_wrap=True
        for i,line in enumerate(value.split('\n')):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial'
            p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=ink;p.space_after=Pt(9)
    def slide(title):
        s=prs.slides.add_slide(prs.slide_layouts[6]);text(s,.5,.25,12.3,.8,title,27,True)
        text(s,.5,7.05,12.3,.3,'TRUST-Line Task 2 v0.4 | AI-assisted analytical review draft | Declared assumptions; not submission or engineering clearance',9)
        return s
    def table(s,rows,y,h,widths,size=17):
        t=s.shapes.add_table(len(rows),len(rows[0]),Inches(.6),Inches(y),Inches(12.1),Inches(h)).table
        for c,w in zip(t.columns,widths):c.width=Inches(w)
        for i,row in enumerate(rows):
            for j,value in enumerate(row):
                cell=t.cell(i,j);cell.text=str(value)
                if i==0:cell.fill.solid();cell.fill.fore_color.rgb=teal
                for p in cell.text_frame.paragraphs:p.font.name='Arial';p.font.size=Pt(size);p.font.bold=i==0;p.font.color.rgb=RGBColor(255,255,255) if i==0 else ink
    allocations=read('cost_ratio_allocation.csv')
    categories=[('property','Property'),('vehicles','Vehicles'),('systems','Systems'),('contingency','Contingency'),('other_capital_and_reconciliation','Other / tax / reconciliation')]
    lookup={(r['technology_id'],r['category']):r for r in allocations}
    rows=[['Within fixed assumed total','Share*','BRT CAD M','LRT CAD M']]
    for key,label in categories:
        b=lookup['BRT',key];l=lookup['LRT',key]
        rows.append([label,f'{float(b["template_share"]):.2%}',f'{float(b["allocated_cad"])/1e6:.2f}',f'{float(l["allocated_cad"])/1e6:.2f}'])
    rows.append(['TOTAL — unchanged','100%','350.00','950.00'])
    s=slide('Cost composition check: allocate within the total')
    table(s,rows,1.35,3.35,[5.1,1.6,2.7,2.7],16)
    text(s,.7,5.0,11.9,1.1,'*ECWE 2020 IBC Option 1: remove the separately reported professional-services allowance and renormalize. This is a declared fee-exclusion proxy, not an audited consultant-only reconciliation or validation of the total cost.',18)
    text(s,.7,6.3,11.9,.45,'Source: Table 19, physical p.79 / printed p.71. Low source land share reflects airport-only private acquisition. LRT-to-BRT composition is an analogy.',12)
    s=slide('Four milestones: an explicit 6–9 year scenario')
    milestone_rows=[['Milestone','User duration','Upper-case completion']]
    for r in read('delivery_milestones.csv'):
        lo=float(r['lower_years']);hi=float(r['upper_years']);duration=f'{lo:g}–{hi:g} years' if lo!=hi else f'{hi:g} year'
        milestone_rows.append([r['stage'],duration,r['illustrative_upper_case_completion']])
    table(s,milestone_rows,1.4,2.9,[6.2,2.0,3.9],17)
    text(s,.7,4.65,11.9,1.6,'Illustrative start: January 1, 2027. Upper case: 2+2+4+1=9 years; opening by December 31, 2035 with no extra delay buffer.\nFleet, systems and depot/access must fit inside these phases. This is a milestone assumption, not a verified delivery forecast.',19)
    text(s,.7,6.35,11.9,.4,'Case p.10 requires a credible timeline, not quantitative construction scheduling. Local BRT/LRT delivery histories provide context, not target guarantees.',12)
    s=slide('TSP evidence: support transparent assumptions')
    table(s,[['Existing evidence','What it measures'],
        ['TTC: up to 30 sec; King up to 10 sec','Selected intersection/time-of-day results'],
        ['City: up to 25 sec at Dundas/College','Keep source difference; no whole-route percentage'],
        ['Finch West: about 20 min round trip','TSP plus operational changes since opening']],1.4,2.4,[6.1,6.0],17)
    text(s,.7,4.15,11.9,1.95,'User assumptions stay fixed: 15 signals; BRT 2.5 min and LRT 3.5 min one-way savings. Equal-contribution equivalents are 10 and 14 sec per signal.\nBeing below a pilot maximum does not establish a Finch East average. No new runtime survey is needed here; do not add savings to speeds already including TSP.',19)
    text(s,.7,6.35,11.9,.4,'Sources: TTC April 2026 report pp.1,6,9; City 2026 attachments p.20. References T2_REF_017–019; full URLs in the companion citation table.',12)
    s=slide('The policy priority determines the conditional preference')
    scores=read('fixed_policy_scores.csv');lookup={(r['weight_profile'],r['technology_id']):r for r in scores}
    rows=[['Declared priority','E / R / T weights','BRT','LRT','Preference']]
    for key,label in [('equal','Equal baseline'),('capital_efficiency_priority','Capital efficiency'),('service_benefit_priority','Service benefit')]:
        b=lookup[key,'BRT'];l=lookup[key,'LRT'];w=' / '.join(f'{float(b[c]):.2f}' for c in ['efficiency_weight','ridership_weight','time_weight'])
        rows.append([label,w,f'{float(b["score"]):.3f}',f'{float(l["score"]):.3f}',b['scenario_winner']])
    table(s,rows,1.4,2.4,[3.3,3.6,1.4,1.4,2.4],17)
    text(s,.7,4.15,11.9,1.95,'Keep E=R/C, ratio-to-best and all prior inputs. Equal/capital-efficiency priorities select BRT; service-benefit priority selects LRT. Tie at 28.85% efficiency weight when the others split equally.\nPolicy switching exposes values; it does not remove shared R. Profiles are analytical choices, not official policy or measured public preferences.',19)
    text(s,.7,6.3,11.9,.45,'Conditional recommendation only: cost/price scope, route/depot assumptions and opening remain limitations. Prior method sensitivity is retained, not erased.',12)
    path=ROOT/'slides/task2_competition_v0.4_review_draft.pptx';prs.save(path)
    print(f'Saved {len(prs.slides)} competition review slides: {path}')


if __name__=='__main__':build()
