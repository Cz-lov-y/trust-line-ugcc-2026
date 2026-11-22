"""Plot and present the provisional assumptions, scores and method sensitivity."""
from pathlib import Path
import csv
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches,Pt

ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/task2_v0.3'


def read(name):
    with (O/name).open(newline='') as f:return list(csv.DictReader(f))


def plot():
    summary=json.loads((O/'model_summary.json').read_text())
    curve=read('weight_switch_curve.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(12.5,4.9))
    x=[float(r['efficiency_weight']) for r in curve]
    for mode,color in [('BRT','#146c78'),('LRT','#b45c37')]:
        axes[0].plot(x,[float(r[mode.lower()+'_score']) for r in curve],label=mode,color=color,lw=2.6)
    switch=summary['efficiency_weight_switch'];axes[0].axvline(switch,ls='--',color='#5c6770')
    axes[0].text(switch+.02,.68,f'Tie at {switch:.2%}',fontsize=10)
    axes[0].set(xlabel='Capital-efficiency weight',ylabel='Provisional utility score',
                title='The weight choice changes the winner',xlim=(0,1),ylim=(.35,1.03))
    axes[0].legend();axes[0].grid(alpha=.2)
    scores=read('scenario_scores.csv');cases=[]
    for method in ('ratio_to_best','minmax'):
        rows={r['technology_id']:float(r['score']) for r in scores if r['scenario_id']=='user_baseline' and r['efficiency_definition']=='ridership_index_per_cost_billion' and r['normalization']==method and r['weight_profile']=='equal'}
        cases.append(rows)
    for i,(mode,color) in enumerate([('BRT','#146c78'),('LRT','#b45c37')]):
        positions=[j+(i-.5)*.3 for j in range(2)];vals=[c[mode] for c in cases]
        axes[1].bar(positions,vals,width=.28,color=color,label=mode)
        for pos,value in zip(positions,vals):axes[1].text(pos,value+.025,f'{value:.3f}',ha='center',fontsize=11)
    axes[1].set(xticks=[0,1],xticklabels=['Ratio to best','Min–max'],ylim=(0,1.03),ylabel='Equal-weight score',title='Normalization also changes the winner')
    axes[1].legend(loc='upper right');axes[1].grid(axis='y',alpha=.2)
    fig.suptitle('Fixed user assumptions: hypothetical costs; R index 1 vs 1.2; time savings 2.5 vs 3.5 min',fontsize=11,y=.98)
    fig.text(.5,.015,'Two-technology assumption model. No complete capital estimate or implementation feasibility certified.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.045,1,.95))
    for extension in ('png','pdf','svg'):
        path=O/('baseline_decision_sensitivity.'+extension);fig.savefig(path,dpi=200)
        if extension=='svg':path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    plt.close(fig)


def build():
    plot();summary=json.loads((O/'model_summary.json').read_text())
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    ink=RGBColor.from_string('203D55');teal=RGBColor.from_string('146C78')
    def text(s,x,y,w,h,value,size=20,bold=False):
        frame=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame;frame.word_wrap=True
        for i,line in enumerate(value.split('\n')):
            p=frame.paragraphs[0] if i==0 else frame.add_paragraph();p.text=line
            p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=ink;p.space_after=Pt(9)
    def slide(title):
        s=prs.slides.add_slide(prs.slide_layouts[6]);text(s,.5,.25,12.3,.8,title,27,True)
        text(s,.5,7.05,12.3,.3,'TRUST-Line Task 2 v0.3 | AI-assisted analytical review draft | Assumptions, not observed forecasts or submission clearance',9)
        return s
    def table(s,rows,y,h,widths):
        t=s.shapes.add_table(len(rows),len(rows[0]),Inches(.6),Inches(y),Inches(12.1),Inches(h)).table
        for col,width in zip(t.columns,widths):col.width=Inches(width)
        for i,row in enumerate(rows):
            for j,value in enumerate(row):
                c=t.cell(i,j);c.text=str(value)
                if i==0:c.fill.solid();c.fill.fore_color.rgb=teal
                for p in c.text_frame.paragraphs:p.font.name='Arial';p.font.size=Pt(17);p.font.bold=i==0;p.font.color.rgb=RGBColor(255,255,255) if i==0 else ink
    s=slide('A declared baseline makes the conditional model executable')
    table(s,[['User assumption / diagnostic','BRT','LRT'],['Cost point (hypothetical CAD)','0.35B','0.95B'],
             ['Cost per km (diagnostic only)','49.29M','133.78M'],['Relative ridership index','1.0','1.2'],
             ['One-way end-to-end saving','2.5 min','3.5 min']],1.4,2.9,[6.4,2.85,2.85])
    text(s,.7,4.65,11.9,1.55,'These are explicitly chosen scenario inputs. No daily passenger total is invented. The cost points are rounded choices, not exact interval midpoints or full capital estimates.\nSurface LRT is not automatically grade-separated; greater capacity does not prove a 20% demand premium.',20)
    text(s,.7,6.4,11.9,.35,'Reference context: Viva / Finch West cost scope and TTC TSP (T2_REF_001, 008, 017–019). Numeric premiums are user assumptions.',11)
    s=slide('Score three criteria; report cost per km without scoring it twice')
    table(s,[['Criterion','Definition','BRT utility','LRT utility'],
             ['Capital effectiveness','Ridership index / CAD billion','1.000','0.442'],
             ['Relative demand','Index, not absolute forecast','0.833','1.000'],
             ['Time savings','Assumed min per one-way trip','0.714','1.000']],1.4,2.65,[2.5,4.4,2.6,2.6])
    text(s,.7,4.2,11.9,1.45,f'Primary normalization: divide each benefit by its best value. Equal weights give BRT {summary["baseline_equal_weight_scores"]["BRT"]:.3f}, LRT {summary["baseline_equal_weight_scores"]["LRT"]:.3f}. BRT wins this baseline.\nEfficiency already includes ridership. We test an inverse-cost definition to expose overlap; no stakeholder weights are claimed.',20)
    text(s,.7,6.25,11.9,.5,'Capital-efficiency priority selects BRT; service-benefit priority selects LRT. Both remain conditional, with final feasibility unverified.',15,True)
    s=slide('The baseline winner is sensitive to values and method')
    s.shapes.add_picture(str(O/'baseline_decision_sensitivity.png'),Inches(.45),Inches(1.3),width=Inches(12.4),height=Inches(4.86))
    support={r['normalization']:r for r in read('weight_support.csv') if r['efficiency_definition']=='ridership_index_per_cost_billion'}
    text(s,.7,6.32,11.9,.55,f'10,000 uniform-simplex weight draws: BRT wins {float(support["ratio_to_best"]["brt_weight_share"]):.2%} with ratio normalization, {float(support["minmax"]["brt_weight_share"]):.2%} with min–max. Fixed inputs; preference shares, not statistical confidence.',13)
    s=slide('State the assumptions, preserve the release conditions')
    text(s,.7,1.35,11.9,4.8,'15 eligible signals are assumed, not surveyed. Equal contribution means 10 sec/signal for BRT or 14 for LRT. TTC pilot maxima do not validate these averages.\nDo not add savings to speeds already incorporating TSP. The matched before-trip baseline and passenger trip lengths remain unmeasured.\nPoint costs are below CAD16.657B. Complete capital, nine-year delivery, opening by 2035-12-31, route fit and allocated depot/access remain conditions.\nBRT wins the equal-weight ratio baseline. LRT wins other declared weights or normalization. No robust final technology choice is established.',21)
    path=ROOT/'slides/task2_baseline_v0.3_review_draft.pptx';prs.save(path)
    print(f'Saved {len(prs.slides)} baseline review slides: {path}')


if __name__=='__main__':build()
