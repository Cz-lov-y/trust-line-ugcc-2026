"""Build a review deck with the 12-to-23 pivot and explicit evidence boundaries."""
from pathlib import Path
import json,csv
import numpy as np
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/model_argument_v0.8'
def read(p):
 with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def compact_heatmap():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fields=json.loads((ROOT/'data/jane_stress_policy_v0.7.json').read_text())['fields'];matrix=np.eye(5);ns=np.zeros((5,5),int)
 for r in read(O/'indicator_correlations.csv'):
  if r['population']=='pairwise_source_available_main_tier' and r['method']=='Pearson':
   i,j=fields.index(r['field_x']),fields.index(r['field_y']);matrix[i,j]=matrix[j,i]=float(r['corr']);ns[i,j]=ns[j,i]=int(r['n'])
 plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'});fig,ax=plt.subplots(figsize=(6.4,5.3));im=ax.imshow(matrix,vmin=-1,vmax=1,cmap='RdBu_r')
 labels=['Speed','Forecast\nload','Current\nload','Choice','Equity'];ax.set_xticks(range(5),labels);ax.set_yticks(range(5),labels)
 for i in range(5):
  for j in range(5):ax.text(j,i,'1.00' if i==j else f'{matrix[i,j]:.2f}\nn={ns[i,j]}',ha='center',va='center',fontsize=11,color='white' if abs(matrix[i,j])>.65 else '#203d55')
 ax.set_title('Source-available Pearson relationships',fontweight='bold');fig.colorbar(im,ax=ax,fraction=.05);fig.tight_layout()
 for ext in ['png','svg','pdf']:
  p=O/('correlation_source_compact.'+ext);fig.savefig(p,dpi=210)
  if ext=='svg':p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
 plt.close(fig)
def build():
 compact_heatmap();prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5);ink=RGBColor.from_string('203D55');teal=RGBColor.from_string('146C78')
 def text(s,x,y,w,h,value,size=19,bold=False,color=ink):
  tf=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame;tf.word_wrap=True
  for i,line in enumerate(value.split('\n')):
   p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color;p.space_after=Pt(9)
 def slide(title):
  s=prs.slides.add_slide(prs.slide_layouts[6]);text(s,.45,.25,12.4,.9,title,27,True);text(s,.45,7.13,12.3,.25,'TRUST-Line v0.8 | Analytical review draft | Declared assumptions, original sources preserved | Not submission clearance',9);return s
 def table(s,rows,y,h,widths=None):
  t=s.shapes.add_table(len(rows),len(rows[0]),Inches(.6),Inches(y),Inches(12.1),Inches(h)).table
  if widths:
   for c,w in zip(t.columns,widths):c.width=Inches(w)
  for i,row in enumerate(rows):
   for j,value in enumerate(row):
    cell=t.cell(i,j);cell.text=str(value)
    if i==0:cell.fill.solid();cell.fill.fore_color.rgb=ink
    for p in cell.text_frame.paragraphs:p.font.name='Arial';p.font.size=Pt(15 if len(rows)<7 else 12);p.font.bold=i==0;p.font.color.rgb=RGBColor(255,255,255) if i==0 else ink
 s=slide('A disputed indicator changed our recommendation')
 text(s,.7,1.2,11.8,.9,'12: Jane  →  23: Finch East',34,True,teal)
 table(s,[['Corridor','Original top-five','After ridership exclusion','New rank range'],['12: Jane St','100%','66.59%','2–9'],['23: Finch Ave E','100%','100%','1–2']],2.35,1.55,[3.1,2.6,3.7,2.7])
 text(s,.7,4.3,11.8,1.4,'We kept the published standard scores and changed the model, rather than inventing a corrected score. Corridor 23 alone passes the specified stability screen in both models.',23,True)
 text(s,.7,5.95,11.8,.85,'100% applies to the original six paired cases, resampled 10,000 times. It is not immunity to every weight or indicator change. Jane remains assessed; it is no longer the primary recommendation.',16)
 s=slide('The change is visible, not hidden')
 s.shapes.add_picture(str(ROOT/'outputs/jane_stress_v0.7/jane_finch_rank_stress.png'),Inches(.3),Inches(1.15),width=Inches(12.7),height=Inches(5.82))
 s=slide('Source audit: a suspected inconsistency, not a made-up correction')
 table(s,[['Jane row','Defined section','Reported assumed length','Road-proxy length'],['11','Bloor–Eglinton','11.269 km','4.075 km'],['12','Eglinton–Pioneer Village','4.076 km','11.181 km']],1.45,1.7,[1.4,4.4,3.15,3.15])
 text(s,.7,3.6,11.8,2.8,'The source labels these as assumed construction lengths. No one-side or Jane extension-length note explains 4.076 km. A transposition is suspected; no official erratum or internal score denominator is established.\nWe isolate dependence on the length-scaled current-ridership input by excluding it. We do not swap source lengths, rescale z scores or claim the source issue has disappeared.',20)
 text(s,.7,6.5,11.8,.35,'Evidence: City evaluation attachment pp.1,6,7; main report p.25. Fresh official PDF hashes match the archives.',12)
 s=slide('Correlation informs the model; it does not dictate values')
 s.shapes.add_picture(str(O/'correlation_source_compact.png'),Inches(.45),Inches(1.35),width=Inches(7.0),height=Inches(5.8))
 text(s,7.65,1.55,5.1,4.9,'No pair reaches |r|≥0.7 in any reported Pearson/Spearman view.\nForecast/current-load Pearson r=0.151 (n=13).\nSource pairs use n=11–14; joint source-complete n=11.\nMinimum and mean substitutions change associations. Low linear correlation does not prove independence or eliminate conceptual over-weighting.',19)
 s=slide('Control concept budgets, not just the number of columns')
 table(s,[['Nominal profile','Service / choice','Load pressure','Equity'],['Equal columns','40.00%','40.00%','20.00%'],['Demand priority','26.67%','60.00%','13.33%'],['Equity priority','22.22%','22.22%','55.56%']],1.4,1.85,[3.5,2.9,2.9,2.8])
 text(s,.7,3.7,11.8,2.6,'Three conceptual blocks are not the three RTEF principles. Fix a block budget, then split it among its members.\nCorridor 23 stays top-three in all eight block-profile cases. But deleting competitiveness within a fixed service-block budget puts it sixth in both City methods. This is a real boundary on the recommendation.',21)
 s=slide('Weights are declared choices, not invented stakeholder evidence')
 text(s,.7,1.35,11.8,4.9,'The City initially weights RTEF criteria equally; that is not an endorsement of equal weight for our selected five columns.\nEqual, demand-priority and equity-priority profiles are auditable analytical preferences. Five-variable weights were proportionally inherited after the disputed indicator was removed.\nNo survey, expert AHP exercise or agency preference elicitation took place. Correlation and data variance cannot determine the social value of equity.\nBroader preference tests assess how the recommendation changes when those values change.',22)
 s=slide('Wider tests bound the “100%” claim')
 s.shapes.add_picture(str(O/'preference_prior_sensitivity.png'),Inches(.95),Inches(1.15),width=Inches(11.4),height=Inches(5.7))
 s=slide('Three principles: separate evidence from coverage gaps')
 table(s,[['Principle','What is actually scored','What remains unmeasured'],['Serve People','Service / choice pressure and equity need','Realized benefits, transfers, station accessibility'],['Strengthen Places','No direct scored development outcome','Housing / development / environmental outcomes'],['Support Prosperity','City current-load Affordability proxy','Jobs, productivity, economic growth, actual financial efficiency']],1.35,3.1,[2.7,4.8,4.6])
 text(s,.7,4.85,11.8,1.6,'All 24 have unscored 2021 residential-intensity context. It is not future housing growth and does not enter the main score. Cost-scaled City growth scores are not used to fill the gap.\nThis is a transparent need-priority subset, not complete empirical coverage of the full RTEF.',19)
 s=slide('All 24 are evaluated; eight do not receive fabricated Base-0 ranks')
 text(s,.7,1.35,11.8,4.9,'24 corridors × 5 selected variables × 6 method/profile cases are assessed in their source baseline contexts. The coverage table has 144 contextual score rows.\n16 CITY_BASE_0 corridors enter the one-step main comparison. Eight source results assume other evaluated predecessors; their missing Base-0 counterfactual cannot be invented.\nEach reserve has all five contextual measures, source/substitution flags, full dependency closure and additional union-catchment population estimates. No City z scores are summed across projects.\nThis policy does not prove the eight are inferior or physically infeasible, nor identify an unconditional optimum across 24 independent projects.',21)
 s=slide('The reserves have quantitative, traceable assessments')
 pairs=read(O/'conditional_assessment_detail.csv');rows=[['Extension','Required sequence','Additional residents*','Additional low-income*']]
 for p in pairs:rows.append([p['corridor_id'],p['required_sequence'],f'{float(p["incremental_population_estimate"]):,.0f}',f'{float(p["incremental_low_income_estimate"]):,.0f}'])
 table(s,rows,1.3,4.2,[1.4,4.1,3.3,3.3]);text(s,.7,5.85,11.8,1,'*Uniform CT estimates of extra geometric coverage, not additional ridership or causal benefit. Reassess against a common counterfactual once prerequisites are in the baseline, or under an authorized bundle study. Corridor 24 remains a 23→24 future option, not part of the selected corridor.',16)
 s=slide('Recommendation and honest limits')
 table(s,[['Evidence set','Corridor 23 top-five inclusion'],['Original paired six-case supports','100%'],['Fixed-budget member deletion catalogue','75%'],['Broad continuous block-weight prior','81.82%'],['Illustrative 10%–60% budget subset','97.63%']],1.35,2.7,[7.4,4.7])
 text(s,.7,4.5,11.8,2,'Our current first choice remains Finch East under the declared service/equity agenda. We changed the choice when the disputed indicator changed the evidence.\nWe do not claim absolute robustness, 100% immunity, fully measured three-principle coverage or an unconditional all-24 optimum.',21,True)
 s=slide('AI-use disclosure and draft status')
 text(s,.7,1.4,11.8,4.9,'AI assistance has supported source review, code, data processing, scenario/model development, analysis, generated figures, documentation and this draft deck. These outputs are not represented as unaided student work.\nThe supplied full guideline p.22 restricts substantive AI use and requires disclosure; any designated-case exception for this work has not been established. This is an analytical review draft, not submission clearance.\nThe team remains responsible for evidence verification, value choices, scope acceptance and final submission requirements.',22)
 out=ROOT/'slides/model_argument_v0.8_review_draft.pptx';prs.save(out);print('Model-argument review slides:',len(prs.slides))
if __name__=='__main__':build()
