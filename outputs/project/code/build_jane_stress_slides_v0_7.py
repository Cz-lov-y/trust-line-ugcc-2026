"""Build the current source-audit and exclusion-test review deck."""
from pathlib import Path
import json,csv
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'outputs/jane_stress_v0.7'
def build():
 prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5);ink=RGBColor.from_string('203D55')
 def text(s,x,y,w,h,value,size=19,bold=False):
  tf=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame;tf.word_wrap=True
  for i,line in enumerate(value.split('\n')):
   p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Arial';p.font.size=Pt(size);p.font.color.rgb=ink;p.font.bold=bold;p.space_after=Pt(9)
 def slide(title):
  s=prs.slides.add_slide(prs.slide_layouts[6]);text(s,.5,.3,12.3,.8,title,27,True);text(s,.5,7.1,12.2,.3,'TRUST-Line v0.7 | Analytical review draft | Original City scores preserved | Not a cleared competition submission',10);return s
 def table(s,rows,x,y,w,h):
  t=s.shapes.add_table(len(rows),len(rows[0]),Inches(x),Inches(y),Inches(w),Inches(h)).table
  for i,row in enumerate(rows):
   for j,value in enumerate(row):
    cell=t.cell(i,j);cell.text=str(value)
    if i==0:cell.fill.solid();cell.fill.fore_color.rgb=ink
    for p in cell.text_frame.paragraphs:p.font.name='Arial';p.font.size=Pt(16);p.font.bold=i==0;p.font.color.rgb=RGBColor(255,255,255) if i==0 else ink
 s=slide('Primary recommendation switches to corridor 23')
 text(s,.65,1.3,12,1,'Finch Ave E: Yonge St → Victoria Park Ave\nProvisional Task 1 primary after the indicator-exclusion stress test.',23,True)
 table(s,[['Corridor','Six-criterion top-five','Five-criterion top-five','Five-criterion rank range'],['12: Jane St','100%','66.59%','2–9'],['23: Finch Ave E','100%','100%','1–2']],.65,2.8,12,1.6)
 text(s,.7,4.9,11.8,1.8,'We stress-tested indicator definitions by removing length-scaled current ridership. Corridor 12 loses its stable top-five status; corridor 23 survives in both models.\nThese are frequencies under six declared scenarios, not statistical confidence. The length discrepancy remains unresolved.',20)
 s=slide('What the official length table actually establishes')
 table(s,[['Corridor','Endpoints','Reported assumed length','Named-road proxy'],['11: Jane St','Bloor → Eglinton','11.269 km','4.075 km'],['12: Jane St','Eglinton → Pioneer Village','4.076 km','11.181 km']],.65,1.4,12,1.8)
 text(s,.7,3.5,11.8,2.7,'Table 2 labels these values “Assumed Length (km)”; Section 2.2 defines length scaling by construction length. No Jane-specific note identifies 4.076 km as one side, one direction or a reduced extension segment.\nThe source assignments suggest a possible transposition, but no official erratum or calculation workbook was located. We do not swap lengths, infer a corrected z score, or claim the published score used the suspect denominator.',19)
 text(s,.7,6.35,11.8,.55,'Sources: City evaluation attachment physical pp.1,6,7; main report physical p.25. Fresh official PDFs match archived source hashes.',13)
 s=slide('Paired rank stress: the disputed criterion matters')
 s.shapes.add_picture(str(O/'jane_finch_rank_stress.png'),Inches(.25),Inches(1.05),width=Inches(12.8),height=Inches(5.87))
 s=slide('Change the indicator set, preserve the source data')
 table(s,[['Profile','Speed','Forecast load','Current max load','Competitiveness','Equity'],['Equal','.2000','.2000','.2000','.2000','.2000'],['Demand priority','.1333','.2667','.3333','.1333','.1333'],['Equity priority','.1111','.1111','.1111','.1111','.5556']],.65,1.25,12,1.9)
 text(s,.7,3.55,11.8,2.8,'Remove current_ridership and proportionally renormalize surviving weights. Keep the same 16 common-baseline candidates, two imputation methods, seed 20261121, all 10,000 paired selectors and frozen equity z-score calibration.\nNo source score or reported length is edited. Eight dependent corridors stay in their separate prerequisite-bundle assessment. No transfer-connectivity criterion is included. Further EDA, weight rationale and final Task 1 deliverables remain.',19)
 s=slide('AI-use disclosure and limits of this draft')
 text(s,.7,1.3,11.8,5.1,'AI assistance has been used for source review, coding, data processing, scenario analysis, generated figures, documentation and this draft deck. These outputs are not represented as unaided student work.\nThe supplied full guideline physical p.22 restricts substantive AI uses and requires disclosure; applicability of any designated-case exception has not been established. This is not a cleared competition submission.\nIndependent source verification, Jane-length clarification, broader model rationale and final deliverable review remain the team’s responsibility. No claim is made that a successful stress test resolves all model uncertainty or competition requirements.',22)
 out=ROOT/'slides/jane_length_stress_v0.7_review_draft.pptx';prs.save(out);print('Five-slide stress review deck written')
if __name__=='__main__':build()
