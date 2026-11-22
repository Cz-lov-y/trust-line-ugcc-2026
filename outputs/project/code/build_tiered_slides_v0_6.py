"""Generate a traceable analytical-review deck, with explicit AI-use disclosure."""
from pathlib import Path
import csv,json
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/tiered_v0.6';S=ROOT/'slides'
def read(p):
 with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def build():
 prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
 blue=RGBColor.from_string('203D55');teal=RGBColor.from_string('146C78')
 def box(slide,x,y,w,h,text,size=18,color=blue,bold=False):
  shape=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=shape.text_frame;tf.word_wrap=True
  for i,line in enumerate(text.split('\n')):
   p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.color.rgb=color;p.font.bold=bold;p.space_after=Pt(8)
  return shape
 def slide(title):
  s=prs.slides.add_slide(prs.slide_layouts[6]);box(s,.5,.25,12.3,.7,title,27,bold=True);box(s,.5,7.12,12.1,.25,'TRUST-Line v0.6 | Analytical review draft | Declared proxy scenarios; not a cleared competition submission',10);return s
 def table(s,rows,x,y,width,height,widths=None):
  t=s.shapes.add_table(len(rows),len(rows[0]),Inches(x),Inches(y),Inches(width),Inches(height)).table
  if widths:
   for col,w in zip(t.columns,widths):col.width=Inches(w)
  for i,row in enumerate(rows):
   for j,value in enumerate(row):
    cell=t.cell(i,j);cell.text=str(value)
    if i==0:cell.fill.solid();cell.fill.fore_color.rgb=blue
    for p in cell.text_frame.paragraphs:
     p.font.name='Arial';p.font.size=Pt(16 if len(rows)<7 else 13);p.font.bold=i==0;p.font.color.rgb=RGBColor(255,255,255) if i==0 else blue
  return t
 summary=json.loads((O/'tiered_model_summary.json').read_text());accept={int(r['corridor_id']):r for r in read(O/'rank_acceptability.csv')}
 s=slide('Compare common baselines; keep extensions conditional')
 box(s,.65,1.15,5.8,1.65,'Main comparison: 16 CITY_BASE_0 corridors\nConditional reserve: 8 dependency bundles\nAll 24 alternatives remain assessed.',22,bold=True)
 rows=[['Main shortlist','Top-five frequency','Interpretation']]
 for cid in summary['main_shortlist']:
  r=accept[cid];rows.append([f'{cid}: {r["corridor_name"]}',f'{100*float(r["top5_frequency"]):.2f}%','Stable in all 6 cases' if r['high_confidence_candidate']=='True' else 'Weight-sensitive third candidate'])
 table(s,rows,.65,3,12,2.2,[5,2.2,4.8]);box(s,.7,5.5,11.8,1.25,'Only corridors 12 and 23 exceed 90% top-five inclusion. This is scenario stability, not statistical confidence. Jane construction-length/source-score interpretation remains a material review issue.',18)
 s=slide('A reproducible uncertainty design')
 box(s,.65,1.15,12,1.45,'Seed 20261121 · 10,000 independent scenario draws\nTwo City missing-data methods × three declared weight profiles = six distinct cases. Exact enumeration checks all six.',21)
 table(s,[['Profile','Speed','Forecast load','Max load','Ridership','Choice','Equity'],['Equal','1/6','1/6','1/6','1/6','1/6','1/6'],['Ridership priority','.10','.20','.25','.25','.10','.10'],['Equity priority','.10','.10','.10','.10','.10','.50']],.65,2.8,12,1.9,[2.1,1.45,1.7,1.7,1.7,1.65,1.7])
 box(s,.7,5,11.7,1.7,'Published City z scores are retained. Equity is converted to a population-SD z score fitted on the 16 main-tier corridors, then frozen across stress comparisons.\nWeights are declared stress assumptions, not stakeholder estimates. Correlated demand criteria may double count demand.',17)
 for name in ['bump_top5','top5_acceptability']:
  s=prs.slides.add_slide(prs.slide_layouts[6]);s.shapes.add_picture(str(O/(name+'.png')),Inches(.15),Inches(.1),width=Inches(13.0),height=Inches(7.2))
 s=slide('Conditional corridors are future network-expansion reserves')
 box(s,.65,1.05,12,.8,'Conditional-baseline corridors do not enter an unanchored absolute ranking. Each is assessed with its full prerequisite closure.',18,bold=True)
 pairs=read(O/'conditional_pair_analysis.csv');rows=[['Extension','Required sequence','Additional residents*','Additional low-income*']]
 for r in pairs:rows.append([r['corridor_id'],r['dependency_sequence'],f'{float(r["incremental_population_estimate"]):,.0f}',f'{float(r["incremental_low_income_estimate"]):,.0f}'])
 table(s,rows,.65,1.95,12,3.9,[1.3,4.2,3.3,3.2]);box(s,.65,6,12,.9,'*Uniform-CT estimates in the additional union catchment; overlap counted once. These are geographic coverage estimates, not causal ridership or transport-benefit forecasts. City z scores are not added across projects.',14)
 s=slide('Ready to execute within a declared scope')
 box(s,.65,1.1,5.6,1.8,'core_ready = true\nlimitations_ready = true\nmodel_ready = true\nlimitations_flagged = true',24,teal,True)
 box(s,6.6,1.1,6,2,'unrestricted_model_ready = false\nNo surveyed-station, independent forecast, construction-feasibility or final-submission claim.',21)
 wood=json.loads((O/'woodbine_sensitivity_summary.json').read_text())
 box(s,.7,3.35,11.9,2.8,'Woodbine: shared anchor tested at nominal + eight 250 m bearings; both routes, buffers and Census shares rebuilt.\n5: equity 9.215%–9.324%, route 2.612–4.520 km. 6: equity 10.449%–10.572%, route 3.725–4.696 km. A completed stress test does not verify the official station site.\nThe shortlist set is unchanged in these local tests. Wider alignment uncertainty, historical vintages, uniform CT density and Jane length anomalies remain.',18)
 s=slide('AI Use Disclosure — review before any competition submission')
 box(s,.7,1.2,11.8,4.8,'AI assistance has been used for coding, data-processing workflows, scenario-model development, analysis, generated charts, documentation and this draft deck.\nThese outputs are not represented as unaided student work. The team must verify all source evidence and calculations.\nThe supplied full guideline, physical page 22, restricts AI use and requires disclosure; page 19 mentions limited designated-case exceptions. Applicability of any exception to this work has not been established.\nThis analytical review draft is not confirmation of competition compliance or permission to submit AI-generated substantive work.',20)
 box(s,.7,6.2,11.8,.6,'Evidence: reference/competition/UGCC 2026 Guideline Package.pdf. Team must disclose actual tools and uses accurately.',14)
 S.mkdir(exist_ok=True);prs.save(S/'tiered_robustness_v0.6_review_draft.pptx');print('Review deck slides:',len(prs.slides))
if __name__=='__main__':build()
