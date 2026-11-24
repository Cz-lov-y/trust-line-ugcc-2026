"""Export the actual current draft into editable prose, not another worksheet."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches,Pt,RGBColor
from pptx import Presentation

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent.parent
SOURCE=REPO/'deliverables/S06_FINAL';DEST=REPO/'deliverables/S06_EDITABLE_ORIGINAL'

FACTS=[
('队伍','S06：Zhuo Chen；Yue Tang；Yuen Song (Rain)；Zihan Cao (Dalton)','注册信息'),
('最终选择','23号Finch East；Yonge–Victoria Park；7.101 km；当前技术BRT','走廊/技术选择与City假设施工长度'),
('Task 1比较范围','16条共同基线主排名＋8条条件走廊情景/前置项目评估','不把24条都伪装成相同基线'),
('当前指标','current_speed、unimproved_load、current_max_load、competitiveness、low_income_population_share_500m','4个City分数＋公平性；排除current_ridership'),
('公平性标准化','z=(fraction−0.13716878222779566)/0.02473132688714528','16条参考固定；不要求或产生正态分布'),
('Task 1公式','S_i = Σ_j w_j z_ij；权重非负且和为1','City公开分数保留；公平性转z分'),
('排名与情景','并列按最差名次判断Top-k；2种缺失处理×3种权重=6种不同情景','10,000次重抽样不是10,000份独立数据或统计置信度'),
('争议指标剔除结果','Jane 12前五支持66.59%、排名2–9；Finch East 23前五100%、排名1–2','仅原先配对支持集；更广权重下23前五81.82%'),
('成本点','BRT CAD350M；LRT CAD950M','声明情景值；并非已验证完整资本成本'),
('需求与时间','R指数1/1.2；单程端到端节省2.5/3.5分钟；15个信号灯','用户假设；不是实际日客流或测得平均效益'),
('Task 2公式','E=R/C（C以十亿加元计）；u_tj=x_tj/max_t(x_tj)；U_t=Σ_j w_j u_tj','E与R共享信息；不声称权重切换消除了重叠'),
('等权结果','BRT 0.8492063492；LRT 0.8140350877','当前比例标准化基准'),
('政策结果','成本效益优先BRT；服务效益优先LRT；其余两权重均分时效率权重切换点28.8477%','分析偏好，不是官方调查得到的权重'),
('工期','四阶段合计6–9年；示意2027启动、2035年底上限投运','上限情景没有额外延期缓冲；不是4–6年保证'),
('未来LRT','只提出可行的选择权预留；转换另需工程、审批、车辆/系统/MSF、资金和施工','未估算预留/转换成本，不作无缝免费升级承诺'),
('来源和披露','核对原报告及页码；按实际保留工具使用与个人贡献','重写表达不能改变来源事实或过去发生的协助')
]


def run():
    DEST.mkdir(parents=True,exist_ok=True)
    prs=Presentation(SOURCE/'S06_TRUST_LINE_FINAL.pptx');d=Document()
    normal=d.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(11)
    normal._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Microsoft YaHei')
    d.core_properties.title='S06 现有原文：可直接改写';d.core_properties.author='S06 original draft export; prior AI assistance retained'
    d.add_heading('S06 现有原文：可直接改写',0)
    intro='这份文件直接收录现有稿，供你们逐段删改、调整顺序并写成自己的表达，不是需要填写的问卷。来源为此前AI辅助版本；改写时核对事实，并如实记录新的个人贡献。原提交文件未被覆盖。'
    d.add_paragraph(intro)
    d.add_paragraph('可在Word打开“修订”，直接改下面的原文。表格数值、公式、书目信息和假设标签另见文末核对区。')
    md=['# S06 现有原文：可直接改写','',intro,'']
    en=(SOURCE/'ABSTRACT_EN.txt').read_text().strip();zh=(SOURCE/'ABSTRACT_ZH.txt').read_text().strip()
    d.add_heading('一、摘要原文',1);d.add_heading('英文原文',2);d.add_paragraph(en)
    d.add_heading('中文参考原文',2);d.add_paragraph(zh)
    d.add_paragraph('正文少于200词；标题/署名/参考文献与正文分开核对。')
    md+=['## 一、摘要原文','',en,'','### 中文参考','',zh,'']
    d.add_page_break();d.add_heading('二、PPT每页现有文字',1)
    md+=['## 二、PPT每页现有文字','']
    inventory=[];figures=0;tables=0
    for i,slide in enumerate(prs.slides,1):
        title=slide.shapes[0].text;d.add_heading(f'第{i}页：{title}',2);md += [f'### 第{i}页：{title}','']
        block_count=0
        for j,shape in enumerate(slide.shapes):
            if shape.has_text_frame:
                value=shape.text
                if j==0 or value.startswith('S06 | TRUST-Line |'):continue
                d.add_paragraph(value);md.extend([value,'']);block_count+=1
            if shape.has_table:
                t=shape.table;out=d.add_table(rows=len(t.rows),cols=len(t.columns));out.style='Table Grid'
                for ri,row in enumerate(t.rows):
                    vals=[c.text for c in row.cells]
                    for cell,value in zip(out.rows[ri].cells,vals):cell.text=value
                    md.append(' | '.join(vals))
                md.append('');tables+=1
            if shape.shape_type==13:
                import io
                d.add_picture(io.BytesIO(shape.image.blob),width=Inches(6.0));figures+=1
                d.add_paragraph('现有图表参考；数据与原始图表来源不因文字改写而改变。')
                md.extend(['[本页图表见Word或此前作者工作包；请结合底层CSV核对。]',''])
        inventory.append(dict(slide=i,title=title,editable_text_blocks=block_count,speaker_notes=slide.notes_slide.notes_text_frame.text))
        if i!=len(prs.slides):d.add_page_break()
    d.add_page_break();d.add_heading('三、逐页讲稿原文',1);md+=['## 三、逐页讲稿原文','']
    for row in inventory:
        heading=f"第{row['slide']}页：{row['title']}";d.add_heading(heading,2);md += ['### '+heading,'']
        for paragraph in row['speaker_notes'].split('\n\n'):
            if paragraph.strip():d.add_paragraph(paragraph.strip());md += [paragraph.strip(),'']
    d.add_page_break();d.add_heading('四、答辩问答原文',1);md+=['## 四、答辩问答原文','']
    qa=(SOURCE/'REHEARSAL_QA.md').read_text()
    for line in qa.splitlines():
        if not line.strip() or line.startswith('#') or line.startswith('Private speaking aid'):continue
        d.add_paragraph(line.replace('**',''));md += [line,'']
    d.add_page_break();d.add_heading('五、改表达时核对的事实与假设',1)
    t=d.add_table(rows=1,cols=3);t.style='Table Grid'
    for cell,value in zip(t.rows[0].cells,['项目','现有值/定义','解释与边界']):cell.text=value
    md+=['## 五、事实与假设核对','']
    for name,value,boundary in FACTS:
        for cell,text in zip(t.add_row().cells,[name,value,boundary]):cell.text=text
        md += [f'- **{name}**：{value}。{boundary}。']
    d.add_heading('六、参考文献原文',1);md+=['','## 六、参考文献原文','']
    refs=(SOURCE/'REFERENCES.md').read_text()
    for line in refs.splitlines():
        if line and not line.startswith('#'):d.add_paragraph(line)
    md.append(refs)
    docx=DEST/'S06_现有原文_可直接改写.docx';d.save(docx)
    (DEST/'S06_现有原文_纯文字.md').write_text('\n'.join(md).rstrip()+'\n')
    with (DEST/'逐页定位.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['slide','title','editable_text_blocks']);w.writeheader();w.writerows({k:v for k,v in r.items() if k!='speaker_notes'} for r in inventory)
    (DEST/'README_CN.md').write_text('''# 直接改原文

打开`S06_现有原文_可直接改写.docx`即可在原句上删改，不必填写空白练习册。内容按摘要、PPT11页正文、逐页讲稿、答辩问答、事实/公式核对、参考文献排列。图表与三个表格也已保留。

你们可以换成自己自然会说的词、压缩句子、调整论证次序、加入自己确实作过的判断。需要保留证据边界：事实、数据、公式、引用与假设标签要核对；若有新的模型选择，需另建版本重新计算。原稿此前的AI辅助来源不会因改写而消失，贡献记录按实际填写。

现有正式提交三件套没有改动。改好后请重新检查摘要词数、所有数值与出处以及整场口述时间。
''')
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DEST.iterdir() if p.is_file() and p.name!='MANIFEST.json'}
    (DEST/'MANIFEST.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n')
    archive=DEST.parent/'S06_EDITABLE_ORIGINAL.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in DEST.iterdir():
            if p.is_file():z.write(p,'S06_EDITABLE_ORIGINAL/'+p.name)
    return dict(slides=len(inventory),tables=tables,figures=figures,word_document=str(docx),zip=str(archive),original_submission_files_modified=False)


if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
