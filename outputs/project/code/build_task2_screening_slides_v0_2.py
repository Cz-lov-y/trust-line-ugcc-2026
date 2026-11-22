"""Build a concise review deck; policy exclusion is visibly distinct from proof."""
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT=Path(__file__).resolve().parents[1]


def build():
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    ink=RGBColor.from_string('203D55');teal=RGBColor.from_string('146C78')

    def text(slide,x,y,w,h,value,size=19,bold=False,color=ink):
        tf=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame
        tf.word_wrap=True
        for i,line in enumerate(value.split('\n')):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line
            p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color
            p.space_after=Pt(9)

    def slide(title):
        s=prs.slides.add_slide(prs.slide_layouts[6]);text(s,.5,.25,12.3,.75,title,28,True)
        text(s,.5,7.05,12.3,.3,'TRUST-Line Task 2 v0.2 | Analytical review draft | AI-assisted; existing disclosure/submission caveats apply',10)
        return s

    def table(s,rows,y,h,widths):
        t=s.shapes.add_table(len(rows),len(rows[0]),Inches(.6),Inches(y),Inches(12.1),Inches(h)).table
        for col,w in zip(t.columns,widths):col.width=Inches(w)
        for i,row in enumerate(rows):
            for j,value in enumerate(row):
                cell=t.cell(i,j);cell.text=value
                if i==0:cell.fill.solid();cell.fill.fore_color.rgb=ink
                for p in cell.text_frame.paragraphs:
                    p.font.name='Arial';p.font.size=Pt(17);p.font.bold=i==0
                    p.font.color.rgb=RGBColor(255,255,255) if i==0 else ink

    s=slide('Feasibility first: a conditional shortlist')
    text(s,.65,1.12,12,.75,'Corridor 23 | Finch East: Yonge–Victoria Park | 7.101 km',22,True,teal)
    table(s,[['Technology','Decision for this round','Interpretation'],
        ['BRT','CONDITIONAL PASS','Retain for surface-busway scenarios'],
        ['LRT','CONDITIONAL PASS','Retain with tight delivery / MSF conditions'],
        ['Subway','CONSERVATIVE SCREEN FAIL','Exclude from base-case shortlist by policy']],2.0,2.4,[1.7,4.0,6.4])
    text(s,.7,4.75,11.9,1.4,'Subway lacks a demonstrated complete nine-year programme and allocated depot/access solution. Our conservative policy excludes it while these remain unresolved. This is not proof of physical impossibility or zero spare Wilson capacity.',21,True)
    text(s,.7,6.25,11.9,.55,'Source basis: Finch West early works/opening (T2_REF_014–016); TTC Line 1 TMSF need (T2_REF_023–024). No numerical failure probability inferred.',12)

    s=slide('Keep historical arithmetic separate from full capital budgets')
    table(s,[['Reference','Unadjusted transfer to 7.101 km','User scenario envelope'],
        ['Viva BRT programme','CAD1.4B / 34 × 7.101 = 0.292B','CAD0.29–0.40B'],
        ['Finch West LRT construction','CAD1.2B / 11 × 7.101 = 0.775B','CAD0.77–1.20B']],1.45,2.1,[3.1,5.5,3.5])
    text(s,.7,3.95,11.9,2.1,'BRT uses 2009 programme dollars. LRT uses a 2018 published construction component. The envelopes are user assumptions, not official uncertainty ranges.\nNeither is a complete comparable capital budget. Reconcile price/cash-flow basis, property, fleet, systems, utilities, depot/access, contingency and consultant exclusions before cost scoring.',22)
    text(s,.7,6.3,11.9,.45,'Sources: YRRTC 2020 opening release; Aecon 2018 award. Archived references T2_REF_001 and T2_REF_008. Budget sufficiency is conditional.',12)

    s=slide('Conditions stay hard even when analysis proceeds')
    table(s,[['Condition','Required before verified feasibility'],
        ['COST','Full comparable initial capital ≤ CAD16.657B; consultants excluded'],
        ['OPENING','Full delivery ≤9 years AND operational by 2035-12-31'],
        ['ROUTE','Actual continuous fit, property / utilities / structures mitigation'],
        ['DEPOT','Allocated compatible storage AND maintenance, access and fleet']],1.35,3.1,[2.0,10.1])
    text(s,.7,4.85,11.9,1.2,'Proceed with BRT/LRT scenarios; any verified hard failure overrides Conditional Pass. Reconsider Subway if a fully evidenced scheme clears the same gates. No weighted technology ranking has been run.',21,True)
    text(s,.7,6.25,11.9,.55,'Planned 36m ROW is not measured available width. A station interchange is not a rail connection. Conditional shortlist does not certify implementation feasibility.',13)
    path=ROOT/'slides/task2_screening_v0.2_review_draft.pptx'
    path.parent.mkdir(parents=True,exist_ok=True);prs.save(path)
    print(f'Saved {len(prs.slides)} review slides: {path}')


if __name__=='__main__':
    build()
