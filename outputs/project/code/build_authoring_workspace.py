"""Provide source-linked worksheets for independent understanding and writing.

No submission artifact is edited and no claim of unaided authorship is generated.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import zipfile

import fitz
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches as DocInches,Pt as DocPt
from openpyxl import Workbook
from openpyxl.styles import Alignment,Font,PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches,Pt

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent.parent
DEST=REPO/'deliverables/S06_AUTHOR_WORKSPACE'
NAMES=['Zhuo Chen','Yue Tang','Yuen Song (Rain)','Zihan Cao (Dalton)']

ITEMS=[
('A01','摘要 Abstract','四人共同','先独立写清：问题、方法、结果、预期效果、限制；再写少于200词的英文摘要。','S06_FINAL/ABSTRACT_EN.txt；原题p.13','保持24→23→BRT逻辑；成本/需求/节省标明假设；最多2条参考文献。'),
('A02','11页PPT的标题与正文','四人共同','每页先用自己的话说出一个主张，再写两三条证据/理由；口述后由同伴记录。','EXISTING_SLIDE_TEXT_AND_NOTES.md','姓名、数据、公式及来源事实按证据保留；不能通过改数配合新措辞。'),
('A03','Task 1指标选择与权重理由',NAMES[0],'自行解释为什么选这些指标、为何排除争议客流、为什么采用这些权重；可以提出不同选择并在副本中重新检验。','data_reference/jane_stress_policy_v0.7.json；source_reading/City_Corridor_Evaluation.pdf','现有主模型4个City分数＋公平性；数据不证明唯一正确权重。'),
('A04','基线、缺失与公平性方法',NAMES[1],'自行画24→16＋8流程，解释最小值/均值替代、CT面积分配、受抑制计数和公平性z分数。','data_reference/；模型说明链接','均匀密度是假设；z分数不创造正态分布；8条仍被评估。'),
('A05','Task 1压力测试与选择23',NAMES[0],'解释从12转23的证据；明确六个情景、配对抽样、并列排名及更广权重范围的局限。','data_reference/paired_scenario_comparison.csv','未确认Jane官方勘误；100%只在指定支持集内，不是人口置信度。'),
('A06','Task 2成本、工期和效益假设',NAMES[2],'自行评估是否接受350M/950M、1/1.2、2.5/3.5分钟及里程碑；用来源说明能支持什么、不能支持什么。','source_reading/；data_reference/task2_baseline_assumptions_v0.3.json','比例分配不验证总成本；6–9年上限无额外缓冲；TSP最大值不是目标平均值。'),
('A07','最终BRT取舍及未来LRT选项',NAMES[3],'说明为什么你们接受BRT；承认什么政策偏好会改选LRT；分别列出现阶段与未来转换需做的事。','data_reference/baseline_scores.csv','单一BRT技术；无缝升级、免费预留及确定工期均未被证实。'),
('A08','2张图的设计、标题与解读','四人共同','查看图的原始CSV，独立决定展示何种关系，自己生成或重画并解释；如复用原AI辅助代码/图应照实记录。','reference_figures/；data_reference/indicator_correlations.csv','图值不能凭审美修改；重新运行旧脚本不等于独立编写该脚本。'),
('A09','代码、计算与方法说明',NAMES[3],'逐项把输入、变换、目标函数和输出连起来；手算关键结果，再运行副本核对；记录哪些实现由谁独立完成。','code_reference/replay_final_models_v1_0.py','理解、运行、复核、改写、独立实现是不同贡献；不要混称。'),
('A10','讲稿、过渡语和问答','四人共同','根据自己理解重新口述，保留个人自然用语；记录真实四人排练时间和修改。','现有逐页notes；AUTHOR_WORKBOOK.docx','计划/语速估计不是已经发生的真人排练；真实经历不能编造。'),
('A11','参考文献、数据与来源核对','四人共同','逐条打开原文，核对作者、日期、页码、单位和适用范围，标记你们实际阅读的位置。','source_reading/；REFERENCES.md','书目事实和官方数值需要准确引用，不作同义改写以改变含义。'),
('A12','AI使用与个人贡献记录','四人共同','分别写清过去的AI协助、本轮由谁亲自完成什么、哪些决定由团队独立作出；据实更新披露。','CONTRIBUTION_LOG.csv','重写不能把过去的AI使用变成未发生；不生成“未用AI”证明。')
]

SLIDE_PROMPTS={
1:('研究问题与团队身份','你们要解决哪两个决定？为什么先选走廊、再选技术？用你们自己的句子介绍。','S06及四人注册姓名保留准确。'),
2:('指标、EDA与尺度','为什么选这五个指标？有哪些重复信息？图中的n和相关系数说明什么？公平性为什么做z分数？','City标准分保留；16条公平性参考不等于City原参考；正态性不是前提。'),
3:('Jane→Finch的真实取舍','源长度问题是什么？为什么删指标而没有改官方数值？如果没有这次检验，你们会怎样选择？','原始数值和未获勘误状态保留；不能说已证明11/12官方对调。'),
4:('23号结论的范围','为什么16/8分层？另外8条怎样评估？你们愿意接受哪些政策权重和未测量原则的局限？','100%配对支持与81.82%广权重支持范围不同。'),
5:('Subway筛选与成本','你们为何接受保守筛选？350M/950M的来源与假设是什么？为什么按比例分配不等于证明总造价？','专业服务剔除是代理；征地比例可能不转移到Finch East。'),
6:('四阶段交付叙事','逐阶段解释谁在做什么，车辆与车辆段放在哪一段；哪里可能延迟？你们怎样表达2035目标而不作保证？','2027启动为示意；6–9年；上限情景无额外缓冲。'),
7:('效益、公式和政策选择','亲手算E、归一化和总分。为什么LRT在另一组权重下胜出？R同时出现在E和R里有什么影响？','1/1.2和2.5/3.5是声明假设；TSP试点上限不验证目标平均。'),
8:('真实AI使用披露','按实际情况列工具、任务、产生的内容与你们的新贡献。由全队核对，不能写成从未使用AI。','原有源审阅、代码、模型、图、文案等协助记录保持真实。'),
9:('文献核对一','打开每份报告，核对被引用的实际段落与页码；标记你们读到的证据边界。','书目信息与URL可保留，不能用新措辞伪造来源结论。'),
10:('文献核对二','核对剩余数据与文献，包括Census分母/年份和TSP单位；记录阅读人。','引用格式可以规范，来源事实不可为了风格改动。'),
11:('最终推荐与承诺边界','每个人独立写一段自己的BRT推荐理由，再讨论合并。你们在哪些条件下会改变决定？未来LRT到底预留什么？','当前仅BRT；成本未认证；无免费/无缝转换保证。')
}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_slides(prs):
    result=[]
    for number,slide in enumerate(prs.slides,1):
        blocks=[];images=[]
        for shape in slide.shapes:
            if shape.has_text_frame:blocks.append(shape.text)
            if shape.has_table:
                blocks.append('\n'.join(' | '.join(c.text for c in row.cells) for row in shape.table.rows))
            if shape.shape_type==13:
                image=shape.image;name=f'slide_{number:02d}_reference.{image.ext}'
                (DEST/'reference_figures'/name).write_bytes(image.blob);images.append('reference_figures/'+name)
        result.append(dict(slide=number,title=slide.shapes[0].text,existing_slide_text='\n\n'.join(blocks),
            existing_speaker_notes=slide.notes_slide.notes_text_frame.text,reference_images=images))
    return result


def make_docx(slides):
    d=Document();sec=d.sections[0];sec.top_margin=DocInches(.7);sec.bottom_margin=DocInches(.7)
    normal=d.styles['Normal'];normal.font.name='Arial';normal.font.size=DocPt(11)
    normal._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
    d.core_properties.title='S06 自主复核与写作工作簿';d.core_properties.author='S06 worksheet prepared with AI assistance'
    d.add_heading('S06 自主复核与写作工作簿',0)
    d.add_paragraph('用途：帮助团队独立理解、作出判断、验证并用自己的语言写作。已有AI协助的事实与披露应保留；本工作簿不是未使用AI或原创性认证。')
    d.add_paragraph('成员：'+'；'.join(NAMES))
    d.add_heading('使用顺序',1)
    for s in ['先关闭原稿，用自己的话回答问题；同伴追问并记录。','打开原始来源/数据核对，区分来源事实、派生计算、分析假设、政策选择。','在空白区写你们的解释和取舍；不同意见可以保留，模型实验放副本并记录。','写完自己的版本后，再打开现有稿检查遗漏和数值一致性。','交叉复核并记录真实贡献，最后更新英文摘要、幻灯片与口头讲稿。']:
        d.add_paragraph(s,style='List Number')
    d.add_heading('一、英文摘要：先写自己的提纲',1)
    d.add_paragraph('正式正文须少于200词；标题、注册姓名和参考文献不计入正文。最多2条参考文献，不含图表/公式。此处不提供一篇新的代写答案。')
    for prompt in ['问题与拟解决的决定','方法与关键理由','你们接受的结果及其范围','假设与限制','你们自己写的英文正文（写完后计词）']:
        d.add_heading(prompt,2);d.add_paragraph('\n________________________________________\n________________________________________\n')
    d.add_page_break();d.add_heading('二、逐页自己写',1)
    for r in slides:
        n=r['slide'];topic,prompt,guard=SLIDE_PROMPTS[n]
        d.add_heading(f'第{n}页：{topic}',2)
        d.add_paragraph('现有页标题：'+r['title']);d.add_paragraph('独立思考：'+prompt)
        d.add_paragraph('核对边界：'+guard)
        for label in ['我自己的主张：','来源/数据/计算依据：','我为什么接受这个选择、还有什么不确定：','我自己的英文标题与要点：','我能自然讲出的过渡语：']:
            d.add_paragraph(label+'\n________________________________________\n________________________________________')
        d.add_paragraph('本人：________  交叉复核人：________  实际完成日期：________')
        if n not in [11]:d.add_page_break()
    d.add_page_break();d.add_heading('三、必须亲自解释的决定',1)
    for item in ITEMS:
        d.add_heading(item[0]+' '+item[1],2);d.add_paragraph(item[3]);d.add_paragraph('证据入口：'+item[4])
        d.add_paragraph('我的解释、是否同意现有取舍、理由：\n________________________________________\n________________________________________')
    d.add_heading('四、自己重算，记录过程',1)
    tasks=[
        '把比例0.16用参考均值0.13716878222779566、SD 0.02473132688714528换成z分数；解释为什么不需要正态分布。',
        '从data_reference/five_indicator_inputs.csv取走廊1的一行，用五个0.2权重算总分；再核对既有输出。',
        '用C=(0.35,0.95)十亿、R=(1,1.2)、T=(2.5,3.5)算E=R/C，再按列除以最大值，手算等权和服务优先总分。',
        '画出并列占第4–6位的情形，说明为什么不能从严保证前五。',
        '算31/2935与31/(2935−422)，解释两种征地占比的分母为何不同；在350M总额内分配，不能再追加在350M之外。',
        '解释2种缺失处理×3种权重只有6种不同情景；抽样10,000次与10,000份独立数据有什么不同。'
    ]
    for task in tasks:d.add_paragraph(task,style='List Number');d.add_paragraph('过程与解释：\n________________________________________\n________________________________________')
    d.add_heading('五、实际贡献与复核记录',1)
    d.add_paragraph('请区分：阅读/理解、运行现有代码、独立复核、修改现有实现、独立实现、独立写作。运行或改写已有AI辅助工作，不自动改变其历史来源。')
    t=d.add_table(rows=1,cols=4);t.style='Table Grid'
    for c,v in zip(t.rows[0].cells,['姓名','亲自完成的工作及文件','此前/本轮实际AI协助','同伴复核']):c.text=v
    for name in NAMES:
        row=t.add_row().cells;row[0].text=name
        for c in row[1:]:c.text='待本人填写'
    d.add_paragraph('最后确认：数据与来源未被无理由改动；假设标签保留；实际协助如实披露；任何新模型结果经过重算；没有编造专家咨询、实地调查或真人排练。')
    path=DEST/'S06_自主复核与写作工作簿.docx';d.save(path);return path


def make_tracker(slides):
    wb=Workbook();ws=wb.active;ws.title='全部人工工作清单'
    ws.append(['编号','内容','建议带读/负责','你们亲自完成什么','来源入口','事实/假设边界','实际执笔人','复核人','状态','新稿文件','贡献备注'])
    for row in ITEMS:ws.append([*row,'','','未开始','',''])
    s=wb.create_sheet('逐页核对');s.append(['页码','现有标题','独立思考题','必须保留的边界','自己的标题','自己的要点','来源已打开','已脱稿解释','状态'])
    for r in slides:
        _,prompt,guard=SLIDE_PROMPTS[r['slide']];s.append([r['slide'],r['title'],prompt,guard,'','','','','未开始'])
    log=wb.create_sheet('真实贡献记录');log.append(['姓名','实际任务','阅读/复核/实现/写作','产出文件','AI实际用途','证据/复核','日期'])
    for name in NAMES:log.append([name,'','','','','',''])
    for sheet in wb:
        sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
        for c in sheet[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='203D55')
        for row in sheet.iter_rows():
            for c in row:c.alignment=Alignment(vertical='top',wrap_text=True)
        for col in sheet.columns:sheet.column_dimensions[col[0].column_letter].width=28
        for row in range(2,sheet.max_row+1):sheet.row_dimensions[row].height=95
    ws.column_dimensions['D'].width=70;ws.column_dimensions['F'].width=55
    s.column_dimensions['C'].width=75;s.column_dimensions['D'].width=65;s.column_dimensions['B'].width=55
    for sheet,col in [(ws,'I'),(s,'I')]:
        dv=DataValidation(type='list',formula1='"未开始,独立解释完成,来源核对完成,本人新稿完成,交叉复核完成"');sheet.add_data_validation(dv);dv.add(f'{col}2:{col}{sheet.max_row}')
    path=DEST/'S06_人工工作与贡献跟踪表.xlsx';wb.save(path);return path


def make_template(slides):
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    for r in slides:
        n=r['slide'];topic,prompt,guard=SLIDE_PROMPTS[n];s=prs.slides.add_slide(prs.slide_layouts[6])
        def text(x,y,w,h,value,size):
            box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame;tf.word_wrap=True;tf.text=value
            for p in tf.paragraphs:p.font.name='Arial';p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string('203D55')
        text(.6,.3,12.1,.7,f'{n}. {topic} — YOUR OWN DRAFT',25)
        text(.7,1.35,11.9,4.6,'[Your claim / 自己写的主张]\n\n[Evidence and citation / 证据与引用]\n\n[Assumptions or limits / 假设与局限]\n\n[Your explanation / 自己能讲出的解释]',21)
        text(.7,6.3,11.9,.7,'Private authoring worksheet — incomplete, not a submission deck. Preserve truthful attribution of prior assistance.',12)
        s.notes_slide.notes_text_frame.text='独立思考：'+prompt+'\n核对：'+guard
    prs.save(DEST/'S06_空白自主写作模板.pptx')


def run():
    DEST.mkdir(parents=True,exist_ok=True)
    for folder in ['data_reference','reference_figures','source_reading','code_reference','method_reference']:(DEST/folder).mkdir(exist_ok=True)
    original=REPO/'deliverables/S06_FINAL/S06_TRUST_LINE_FINAL.pptx'
    prs=Presentation(original);slides=extract_slides(prs)
    (DEST/'SLIDE_INVENTORY.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2)+'\n')
    text=['# 现有AI辅助稿：逐页文字、表格与讲稿','',
        '这是现有版本的完整摘录，明确保留其AI辅助来源。建议先独立回答工作簿问题，再用此文件核对事实；此文件不是重新代写的“人工版”。','']
    for r in slides:
        text += [f"## 第{r['slide']}页：{r['title']}",'','### 现有页内文字及表格','',r['existing_slide_text'],'','### 现有讲稿','',r['existing_speaker_notes'],'','### 图表入口','',', '.join(r['reference_images']) or '无','']
    (DEST/'EXISTING_SLIDE_TEXT_AND_NOTES.md').write_text('\n'.join(text))
    for src in ['ABSTRACT_EN.txt','ABSTRACT_ZH.txt','REFERENCES.md']:
        shutil.copyfile(REPO/'deliverables/S06_FINAL'/src,DEST/('EXISTING_'+src))
    references=[
        'data/city_standardized_scores_v0.1.csv','data/supplemental_model_inputs_v0.5.csv','data/jane_stress_policy_v0.7.json',
        'data/task2_baseline_assumptions_v0.3.json','outputs/jane_stress_v0.7/five_indicator_inputs.csv',
        'outputs/jane_stress_v0.7/paired_scenario_comparison.csv','outputs/jane_stress_v0.7/rank_acceptability_comparison.csv',
        'outputs/model_argument_v0.8/indicator_correlations.csv','outputs/model_argument_v0.8/descriptive_statistics.csv',
        'outputs/model_argument_v0.8/all24_contextual_scores.csv','outputs/model_argument_v0.8/conditional_assessment_detail.csv',
        'outputs/task2_v0.3/baseline_inputs.csv','outputs/task2_v0.3/baseline_scores.csv','outputs/task2_v0.3/weight_support.csv',
        'outputs/task2_v0.4/cost_ratio_allocation.csv','outputs/task2_v0.4/delivery_milestones.csv','outputs/task2_v0.4/TSP_citation_table.csv'
    ]
    for rel in references:shutil.copyfile(ROOT/rel,DEST/'data_reference'/Path(rel).name)
    for name in ['replay_final_models_v1_0.py','calculate_equity_v0_5.py','run_jane_stress_v0_7.py','run_task2_baseline_v0_3.py']:
        shutil.copyfile(ROOT/'code'/name,DEST/'code_reference'/name)
    for rel in ['outputs/model_argument_v0.8/MODEL_JUSTIFICATION.md','outputs/task2_v0.3/BASELINE_MODEL.md','outputs/task2_v0.4/COMPETITION_PACKAGE.md','data/equity_proxy_method_v0.5.json']:
        shutil.copyfile(ROOT/rel,DEST/'method_reference'/Path(rel).name)
    (DEST/'method_reference/READ_FIRST.md').write_text('# 现有方法说明：参考来源\n\n这些是此前AI辅助整理的模型与方法说明，供核对定义、算法和假设；它们不是你们本轮独立写作的产出。请先尝试独立解释，再与这些文件、实际数据和原报告对照。各版本的决定状态属于当时快照，当前选择与最新提交文件为准。\n')
    (DEST/'code_reference/READ_CODE.md').write_text('# 代码阅读入口\n\n此处为现有数值复算源码参考副本，带有此前AI辅助来源。实际运行请在完整仓库或支持ZIP的原目录结构中执行，不要直接在此缩减的数据目录运行。逐行对应输入、变换、评分、比较输出；若自行实现请另建副本并记录贡献。\n')
    excerpts=[
        (REPO/'reference/competition/STAT Case UGCC 2026.pdf',[6,8,9,10,11,13],'STAT_CASE_key_pages.pdf'),
        (ROOT/'evidence/tech_support_v0.4/ecwe_ibc_2020.pdf',[78,79],'ECWE_cost_scope_and_Table19.pdf'),
        (ROOT/'evidence/tech_support_v0.1/city_tsp_attachments_2026.pdf',[19,20],'City_TSP_key_pages.pdf')
    ];index=[]
    for source,pages,name in excerpts:
        d=fitz.open(source);out=fitz.open()
        for p in pages:out.insert_pdf(d,from_page=p-1,to_page=p-1)
        path=DEST/'source_reading'/name;out.save(path,garbage=4,deflate=True)
        index.append(dict(excerpt=name,original_file=str(source.relative_to(REPO)),original_physical_pages=pages,original_sha256=digest(source),excerpt_sha256=digest(path)))
    for source,name in [
        (ROOT/'evidence/source_documents/city_2024_corridor_evaluation.pdf','City_Corridor_Evaluation.pdf'),
        (ROOT/'evidence/tech_support_v0.1/ttc_tsp_report_2026.pdf','TTC_TSP_Report_2026.pdf')
    ]:
        path=DEST/'source_reading'/name;shutil.copyfile(source,path)
        index.append(dict(excerpt=name,original_file=str(source.relative_to(REPO)),original_physical_pages='full document',original_sha256=digest(source),excerpt_sha256=digest(path)))
    (DEST/'source_reading/SOURCE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    make_docx(slides);make_tracker(slides);make_template(slides)
    with (DEST/'CONTRIBUTION_LOG.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['姓名','真实完成的任务','具体文件','阅读/复核/改写/独立实现','实际AI协助','复核人','完成日期'])
        for name in NAMES:w.writerow([name,'','','','','',''])
    (DEST/'START_HERE_CN.md').write_text('''# S06 自主复核与写作包

目标：让你们亲自理解、独立判断、复核计算，并用自己的语言表达。已有AI协助不能通过改写变成未曾发生；此包不提供检测规避或“未用AI”的认证。实际贡献和工具使用应如实记录。

## 先打开这三个文件

1. `S06_自主复核与写作工作簿.docx`：摘要、11页逐页写作问题、方法取舍、手算任务及空白草稿区。
2. `S06_人工工作与贡献跟踪表.xlsx`：12类任务、11页核对及四人贡献记录；所有状态从“未开始”起，不伪造完成记录。
3. `S06_空白自主写作模板.pptx`：供你们亲自写入标题、主张、证据与局限；它是不完整的私人工作模板，不能直接提交。

## 内容范围

需要亲自重新决定或表达：摘要；PPT标题/正文/解读；指标与权重理由；基线与缺失处理解释；压力测试与选择理由；成本/效益/工期假设；最终推荐和未来转换边界；自己的讲稿、过渡与答辩。

需要亲自复核但不必凭空改写：官方数据、数学公式、出处、书目信息、固定事实、代码与图的准确性。若独立重做图或实现代码，应记录实际完成的工作；运行现有AI辅助代码不等于独立编写。若有充分理由改变模型，请在副本建立新版本并重新生成所有结果，不随意改数来贴合预定结论。

需要据实更新而不能抹去：AI使用披露与个人贡献说明。此前的AI辅助稿可作为有来源的参考，不能声称改写后整个项目从未使用AI。

## 建议顺序

- 四人先关闭现有稿，各自解释一页；同伴追问和记录。
- 对照`source_reading/`摘页与原文核对，再填写工作簿。
- 在`data_reference/`数据上手算关键结果；必要时到完整仓库运行复算入口。
- 自己完成新稿后，打开`EXISTING_SLIDE_TEXT_AND_NOTES.md`核对事实。它包含旧稿的全部11页文字、3个表格、讲稿及图表入口，保留AI辅助来源。
- 用跟踪表交叉复核，再用自己真正会说的句子排练，记录真实时间。

## 来源与原文件

`source_reading/`含原题、ECWE表19和City TSP的明确摘页，以及City走廊评估和TTC报告全文。摘页编号对应原PDF物理页码，完整文件路径和SHA-256在`SOURCE_INDEX.json`中，引用仍应指向原报告。

`reference_figures/`是现有图的参考副本，不能因放入新PPT就改称纯人工创作。底层数据已另附。

`method_reference/`保留现有Task 1、Task 2和CT公平性方法说明；`code_reference/`附公平性计算、Jane压力测试、技术比较和总复算源码供阅读，仍保留其此前AI辅助来源。运行时请使用完整项目副本的目录和依赖。

正式提交的三份文件仍在`../S06_SUBMISSION/`，本包不会改动它们。当前包是内部学习/自主写作材料，不是第四份提交文件或给评委的实体手册。
''')
    manifest={p.relative_to(DEST).as_posix():digest(p) for p in DEST.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
    (DEST/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    archive=DEST.parent/'S06_AUTHOR_WORKSPACE.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file():z.write(p,'S06_AUTHOR_WORKSPACE/'+p.relative_to(DEST).as_posix())
    return dict(slides=11,table_count=sum(sh.has_table for s in prs.slides for sh in s.shapes),reference_figures=2,work_categories=len(ITEMS),independent_team_drafts_filled=False,unaided_authorship_claim=False,submission_files_modified=False,archive=str(archive),bytes=archive.stat().st_size)


if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
