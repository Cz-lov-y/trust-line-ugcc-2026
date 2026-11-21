from pathlib import Path
import re, json, csv, html, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs'
URL='https://www.toronto.ca/legdocs/mmis/2024/ex/bgrd/backgroundfile-243172.pdf'
ns={'h':'http://www.w3.org/1999/xhtml'}
pages=ET.parse(ROOT/'work/city_bbox.html').getroot().findall('.//h:page',ns)
textpages=(ROOT/'work/city_2024_layout.txt').read_text(encoding='utf-8').split('\f')

# Metadata transcribed from Table 2. Values are preserved; suspected source issues are flagged.
raw_corridors=[
('Sheppard Ave West','Sheppard W Stn.','Sheppard Stn.','Subway',4.404,88,0),
('Sheppard Ave East','Don Mills Stn.','McCowan Rd','Subway',7.387,148,0),
('Waterfront West LRT #1','Long Branch','Park Lawn','Streetcar/LRT',3,12,4),
('Waterfront West LRT #2','Park Lawn','Union Station','Streetcar/LRT',9.3,37,0),
('Finch West LRT Extension #1','Humber College','Woodbine GO','LRT',3.3,13,0),
('Finch West LRT Extension #2','Woodbine GO','Pearson Airport','LRT',2.8,11,5),
('Finch Ave West','Finch West Stn.','Finch Station','LRT',6.344,25,0),
('Ontario Line West extension','Ontario Place','Dundas West Stn.','Subway',4,80,0),
('Ontario Line North extension','Eglinton Ave E','Steeles Ave','Subway',10.57,211,0),
('Line 2 west extension','Kipling Station','Sherway Gardens','Subway',4.3,86,0),
('Jane St','Bloor St','Eglinton Ave','LRT',11.269,46,12),
('Jane St','Eglinton Ave','Pioneer Village Stn.','LRT',4.076,16,0),
('St Clair Ave W','Weston Rd','Jane St','Streetcar/LRT',2.04,8,11),
('Steeles','Pioneer Village Stn.','Bathurst St','BRT',5.34,5,15),
('Steeles','Bathurst St','Bayview Ave','BRT',4.316,4,0),
('Steeles','Bayview Ave','Milliken Go Stn.','BRT',8.367,87,15),
('Steeles','Milliken Go Stn.','Morningside Ave','BRT',4.123,4,16),
('Kingston Rd E','Victoria Park Stn.','Eglinton','BRT',8.851,9,0),
('McCowan','Sheppard Ave E','Markham Centre','Subway',4.85,97,0),
('Wilson Ave W','Weston Rd','Wilson Stn.','BRT',7.398,7,0),
('Dufferin St','Dufferin Gate Loop','Eglinton Ave W','BRT',7.04,7,0),
('Lawrence Ave W','Weston Rd','Lawrence Ave W Stn.','BRT',6.055,6,0),
('Finch Ave E','Yonge St','Victoria Park Ave','BRT',7.101,7,0),
('Finch Ave E','Victoria Park Ave','Morningside Ave.','BRT',9.514,10,23)]
corridors=[]
for i,r in enumerate(raw_corridors,1):
    note=''
    if i==3: note='原文为3加上标脚注6，不是36；脚注称已有立体分隔轨道，因此是缩减后的建设长度，不宜当作完整线路长度。'
    if i in (11,12): note='按原文保留；两段长度与端点对应关系建议另行地图/工程资料核验，不擅自交换。'
    if i==16: note='Relative Cost原文确为87；与同表BRT长度及相对成本口径不一致，疑似源表问题，未改成8。'
    corridors.append([i,*r,'原报告给定的属性/假设；Relative Cost为派生值', '排除Relative Cost；技术与Base作元数据，长度另核用途',7,URL+'#page=7',note])

# id, category, name, exact description (Table 1), Chinese definition, type, source, scaling, physical unit/limitation, direction caveat, overlap
spec=[
('current_speed','Experience','Current speed','Fall 2022-observed speed corresponding to 95th-percentile travel time','2022年秋观测的第95百分位行程时间所对应的速度。','观测摘要统计','TTC','---','速度；本附件未注明km/h等原始单位','改善需求导向可考虑越慢需求越高；不能把现状越快直接等同项目越优','竞争力、时间节省'),
('travel_time_savings','Experience','Travel time savings (TTS)','Projected travel time savings using transit demand from base 2051 forecast network','使用2051基准预测网络的公交需求估算行程时间节省。','预测/情景收益派生值','GTAModel v4','Cost','时间收益；未交代分钟/人时、统计期及聚合口径','收益通常越大越好；需原始量及口径','就业可达性、客流、公平性时间收益'),
('unimproved_load','Experience','Unimproved load','Projected load (maximum number of on-board riders) on unimproved corridor.','未改善走廊上的预测最大车上乘客数。','基准预测值','GTAModel v4','---','人；未注明峰小时/方向等统计口径','需求/拥挤压力指标，不是改善后运能','现状最大载客量、现状客流、新增客流'),
('population','Shaping the City','Population','Projected 2051 population within 500 m buffer around transit stations','站点500米缓冲区人口；采用2021值+0.8×2021至2051预测增长。','人口预测与空间汇总派生值','Census; LNA','Cost','人；原始人数未列出','覆盖效益通常越大越好','人口可达性、住宅潜力、客流、公平性覆盖'),
('access_employment','Shaping the City','Access employment','Projected change in weighted transit access to employment (see Section 2.3)','改善项目相对基准情景带来的加权公交就业可达性变化。','网络情景差值/派生值','GTAModel v4','Cost','加权可达性；未给权重函数、阈值和物理单位','改善越大通常越好','时间节省、就业覆盖、公平性就业可达性'),
('residential_potential','Shaping the City','Residential potential','Residential development potential within 500 m radius around transit stations.','站点500米范围内住宅开发潜力。','空间规划派生指标','Official Plan Map 2','Cost','未注明面积、住房数或潜力指数口径','通常越大越好，须补充定义','人口覆盖、就业开发潜力'),
('auto_vkt','Environment & public health','Auto VKT','Projected auto vehicle kilometres travelled savings','预测小汽车车辆行驶公里数节省。','预测/情景收益派生值','GTAModel v4','Cost','车辆公里；未给统计期/网络范围细节','节省越大通常越好','汽车方式占比下降、新增公交客流、时间节省'),
('auto_mode_share','Environment & public health','Auto mode share','Projected decrease in auto drive mode share of within-Toronto trips','预测多伦多市内出行中小汽车驾驶方式占比下降。','预测比例差值','GTAModel v4','Cost','占比变化；未明确百分比或百分点表示','下降量越大通常越好','VKT节省、新增公交客流'),
('employment','Supports Growth','Employment','Projected 2051 employment within 500 m buffer around transit stations','站点500米缓冲区就业岗位；采用2021值+0.8×2021至2051预测增长。','就业预测与空间汇总派生值','TES; LNA','Cost','就业岗位数；原始数未列出','覆盖效益通常越大越好','就业可达性、就业潜力、客流'),
('access_population','Supports Growth','Access population','Projected change in weighted transit access to population (see Section 2.3)','改善项目相对基准情景带来的加权公交人口可达性变化。','网络情景差值/派生值','GTAModel v4','Cost','加权可达性；权重函数/阈值未给','改善越大通常越好','站点人口覆盖、就业可达性、时间节省'),
('employment_potential','Supports Growth','Employment potential','Employment development potential within 500 m radius around transit stations.','站点500米范围内就业开发潜力。','空间规划派生指标','Official Plan Map 2','Cost','未注明面积、岗位数或潜力指数口径','通常越大越好，须补充定义','就业覆盖、住宅潜力'),
('current_max_load','Affordability','Current max Load','Current maximum number of on-board riders in the corridor.','走廊现状最大车上乘客数。','观测摘要统计','TTC','---','人；未注明峰小时/方向','需求/拥挤压力；不是总客流','未改善预测最大载客量、现状客流'),
('current_ridership','Affordability','Current ridership','Fall 2022-observed number of riders in the corridor','2022年秋观测走廊客流；公布分数先按建设长度缩放。','观测客流；公布前另作长度派生','TTC','Length','原始为乘客数；缩放后为每建设公里乘客数，统计期未给','需求导向通常越大越好','现状最大载客量、人口就业覆盖、新增客流'),
('new_riders','Affordability','New riders','Projected increase of transit riders','相对相关基准情景预测新增公交乘客量。','预测情景差值','GTAModel v4','Cost','新增乘客数；未给统计期','通常越大越好；不是未来总客流','现状客流、VKT、方式占比、可达性'),
('competitiveness','Choice','Competitiveness','Fall 2022: ratio of transit and auto travel times to traverse corridor.','2022年秋沿走廊乘公交与驾车行程时间之比。','观测时间比值/派生指标','TTC; HERE','---','无量纲比值；分子分母/评分反向公式未完整列出','服务竞争力与改善需求两种目标方向不同，不能重复反向处理公布分数','现状速度、时间节省')]

metrics=[]
for key,cat,name,eng,zh,typ,src,scale,unit,direction,overlap in spec:
    loc=11 if cat in ['Experience','Shaping the City','Environment & public health'] else 12
    flag='排除现有Cost缩放分数；可另取无成本原始指标' if scale=='Cost' else '无显式成本缩放，可作为候选；仍须核验方向/缺失/口径'
    metrics.append([key,cat,name,eng,zh,typ,src,scale,'标准化分数，无量纲，通常两位小数；不是原始单位','未提供24走廊原始量',unit,flag,direction,overlap,'Table 1 p.6；'+('Table 6 p.11' if loc==11 else 'Table 7 p.12'),URL+f'#page={loc}'])
groups=[('low_income','Low Income','低收入群体'),('racialized','Racialized People','种族化群体'),('single_parent','Single Parent Family','单亲家庭'),('long_commute','Long Commute','长通勤群体'),('recent_immigrants','Recent Immigrants','近期移民')]
eqtypes=[('tts','Travel Time Savings','平均行程时间节省的群体相对受益','时间节省、同一群体就业可达性'),('access_employment','Access Employment','公交就业可达性变化的群体相对受益','总体就业可达性、时间节省'),('census_distribution','2021 Census Distribution','拟建站点500米服务人口的群体相对受益；表头使用2021 Census','总体人口覆盖、其他群体人口分布')]
for g,ge,gz in groups:
    for t,te,tz,over in eqtypes:
        metrics.append([f'equity_{g}_{t}','Equity',f'{ge} / {te}','Section 2.4; Table 8 (group × benefit dimension)',gz+'：'+tz+'。','群体收益Palma比率，再标准化','§2.4；Table 8（Census/网络分析，未逐列完整列来源）','未注明；Table 1仅转引§2.4','标准化分数，无量纲；不是原始Palma比率','原始比率、群体人数及群体收益未列出','原始Palma无量纲；原文未提供完整分子分母公式','未发现显式成本缩放；条件候选，核验转换方向/群体定义','原始比率<1偏向公平群体；标准化分数不可按1作阈值，反向方式未明',over+'；五群体可能重叠','§2.4 p.3；Table 8 p.13',URL+'#page=13'])

index=[
['Figure 1',2,'RTEF三原则及八项准则','框架图；Healthy Neighbourhoods未纳入本次分析','非指标数据矩阵',URL+'#page=2'],
['§2.2', '1–2','长度/成本缩放及标准化','BRT/LRT/Subway相对成本1/4/20；分数均值0、标准差1','Cost同时除以建设长度与相对技术成本',URL+'#page=1'],
['§2.3–2.5','2–4','可达性、公平性、基准与汇总','群体、预测基准、依赖Base、缺失单元说明','§2.4在p.3；不完整原始公式需核验',URL+'#page=3'],
['Table 1',6,'指标定义、数据来源、Scaling','15个一般指标；Equity转引§2.4','不是24走廊原始值表；Cost10项、Length1项、---4项',URL+'#page=6'],
['Table 2',7,'24条走廊、端点、技术、建设长度、相对成本、Base','原报告元数据与假设；Relative Cost为派生值','Relative Cost排除；完整线路长度不等于建设长度',URL+'#page=7'],
['Table 3',8,'按五分位分组的最终评分','24条走廊，已混合成本指标','原最终分数与排名不可用于Part 1选择',URL+'#page=8'],
['Table 4',9,'三种相对成本设定的最终分数与五分位','1:4:20 / 1:3:15 / 1:1:1','前两组含相对成本；第三组仍是原技术假设与长度口径下的聚合结果',URL+'#page=9'],
['Table 5',10,'七类别分数及Final Score','类别分数在汇总前再次标准化（脚注7）','含Cost指标的类别及总分排除；Choice无显式成本；Equity另核',URL+'#page=10'],
['Table 6',11,'Experience / Shaping the City / Environment & Public Health明细','8个一般指标分数＋3个Combined','其中6个Cost；Current speed、Unimproved load无显式成本',URL+'#page=11'],
['Table 7',12,'Supports Growth / Affordability / Choice明细','7个一般指标分数＋2个Combined','其中4个Cost；Current max Load、Current ridership、Competitiveness另核',URL+'#page=12'],
['Table 8',13,'五公平群体×三收益维度及Final Equity','15个标准化公平子指标＋1个汇总','非群体人数/比例原始表；Final Equity与Table 5 Equity尺度不同',URL+'#page=13']]

overlaps=[
['需求与承载','Current ridership; Current max Load; Unimproved load; New riders','总客流、单断面最大载客量、基准预测压力、新增客流不是同一量，但共同反映需求','区分现状/预测、总量/增量、总客流/断面量；不可重复命名为ridership'],
['人口与开发','Population; Residential potential; Access population','近站人口、潜在住宅增长、通过网络能接触到的人口有联系但不同','地理覆盖与网络可达性分开，核查增长人口是否已包含开发潜力'],
['就业与经济','Employment; Employment potential; Access employment','近站岗位、开发潜力和网络就业可达性不是同一量','保留定义差异，避免将多个相关指标全部高权重计分'],
['时间与可达性','Travel time savings; Access employment; Access population; Competitiveness; Current speed','网络时间改变可能共同驱动可达性与竞争力','先查收益聚合口径，区分现状问题与改善收益'],
['汽车转移','Auto VKT; Auto mode share; New riders','共同涉及方式转移，但距离、份额和乘客数量不同','不可当作三个独立环境效益重复累加；负标准分不等于负效益'],
['总体与公平','总体TTS/就业可达性/Population 与各公平群体相应列','效率总量与群体分配共享收益基础','明确公平是收益分布维度，不再次把群体分数当收益总量'],
['公平群体交叉','五组Equity列','低收入、种族化、单亲、长通勤、移民群体可交叉','群体人数不可简单相加；组权重不能解释为互斥人口份额'],
['明细与汇总','Table 6/7 Combined; Table 8 Final Equity; Table 5类别/Final Score','上下层派生量共享同一批底层指标','同一模型避免同时计入明细与其Combined/类别/总分']]

issues=[
['原始量缺失','Tables 6–8 pp.11–13','已公布的是标准化分数；未给完整人口数、客流量、时间收益原始矩阵','不能标成原始数据；本文件标为report score'],
['不可直接去成本','§2.2 pp.1–2；Table 1 p.6','Cost缩放后才标准化；原尺度的均值/标准差未公布','不能用z分数×相对成本（或×长度）冒充去成本原始量；需原始数据/有依据重建'],
['建设长度脚注','Table 2 p.7，ID3','3加脚注6；已有立体分隔轨道使建设长度缩减','记录3 km；不记36，不当完整走廊长度'],
['源表相对成本异常','Table 2 p.7，ID16','原文87，不是提取时把8和脚注7合并','按原文保存并标待核；Part 1不使用该字段'],
['长度与端点核验','Table 2 p.7，ID11/12','原文Bloor–Eglinton=11.269，Eglinton–Pioneer Village=4.076','保留原文；地图/工程资料核验前不交换'],
['Base依赖','§2.5 pp.3–4；Table 2 p.7','3→4；6→5；11→12；13→11；14→15；16→15；17→16；24→23','Base非0为延伸的边际效益；须与单条项目口径区分，间接依赖也保留'],
['2051预测对2035任务','Table 1 p.6','多项依据2051网络/人口就业；题目要求2035运营','不得把2051原预测直接标成2035预测；这里只定位不换算'],
['人口就业增长折扣','Table 1脚注3 p.6','2021值+0.8×2021至2051预测增长','这是报告既有派生假设，不是团队新测量'],
['缺失值','§2.5 p.4；Tables 5–7','灰底/N/A表示该项未能计算；不能自动当0','单独保留缺失状态，不插补、不建模'],
['公平分数方向','§2.4 p.3；Table 8 p.13','原始Palma<1偏向公平群体；Table8是标准化分数，含负数','原文未给完整比率及反向转换公式；不可用1阈值或再次机械取负'],
['公平群体定义','§2.4 p.3','附件列出五群体，具体收入门槛、近期移民年限、长通勤阈值等未给','原文指向主报告；此附件内不能补成自定义阈值'],
['可达性口径','§2.3 pp.2–3；Table1 p.6','加权公交可达性变化；未给完整衰减函数/阈值/权重','不等于站点500米就业/人口覆盖'],
['速度和竞争力方向','Table1 p.6；Tables6–7','现状服务质量与优先改善需求可能方向相反；分数方向变换未详列','先明确评价目标，再核对原分数转换'],
['Affordability名称','Table1 p.6；Table7 p.12','类别内Current max Load无成本；Current ridership仅按长度；New riders按Cost','按字段排除，不能只按类别名称一刀切'],
['重复标准化','Table5脚注7 p.10','类别分数从后续明细的Combined再次标准化后汇总','不能把Table5类别直接当Table6/7 Combined，也不能混用尺度'],
['等相对成本情景','Table4 p.9','1:1:1情景取消技术成本差异，但保留既有技术服务与建设长度假设','作为定位信息保存，未将其直接当作团队无成本评价结果'],
['未单列的建议指标','Figure1 p.2；Table1 p.6','Healthy Neighbourhoods明确省略；无车家庭、残障、专门安全量、设施可达性、换乘连通性未单列','不得宣称报告已有这些可直接提取的指标'],
['工期/实际资本成本','Tables1–2','无每技术的实际金额资本估算、工程时间线、成本概率分布','相对成本不是加元预算；本报告不够直接建立Part2技术估算']]

def words(k):
    return [dict(t=x.text or '',x=float(x.attrib['xMin']),y=float(x.attrib['yMin']),xc=(float(x.attrib['xMin'])+float(x.attrib['xMax']))/2) for x in pages[k-1].findall('.//h:word',ns)]

def numeric_rows(k,anchor_col_x,tolerance=9):
    ww=words(k)
    numeric=[w for w in ww if re.fullmatch(r'-?\d+\.\d{2}|N/A',w['t'])]
    anchors=sorted([w for w in numeric if abs(w['x']-anchor_col_x)<4],key=lambda w:w['y'])
    assert len(anchors)==24,(k,len(anchors))
    # Column centers are taken from the first complete row, avoiding wrapped text order.
    first=sorted([w for w in numeric if abs(w['y']-anchors[0]['y'])<1],key=lambda w:w['x'])
    centers=[w['xc'] for w in first]
    rows=[['']*len(centers) for _ in anchors]
    for w in numeric:
        ri=min(range(24),key=lambda i:abs(anchors[i]['y']-w['y']))
        if abs(anchors[ri]['y']-w['y'])>tolerance: continue
        ci=min(range(len(centers)),key=lambda i:abs(centers[i]-w['xc']))
        assert rows[ri][ci]=='',(k,ri,ci,w)
        rows[ri][ci]=w['t']
    return rows

t5=numeric_rows(10,696.6)
t6=numeric_rows(11,394.56)
t7=numeric_rows(12,603.61)
t8=numeric_rows(13,733.82)
# Table 7 has grey N/A cells spanning BOTH current-load and current-ridership columns.
for i in [4,6,8,10]:
    assert t7[i-1][4]=='' and t7[i-1][5]=='N/A',(i,t7[i-1])
    t7[i-1][4]='N/A'
assert all(all(v!='' for v in row) for tab in (t5,t6,t7,t8) for row in tab)

fields5=['category_experience','category_shaping','category_environment','category_growth','category_affordability','category_choice','category_equity','city_final_score']
fields6=['current_speed','travel_time_savings','unimproved_load','combined_experience','population','access_employment','residential_potential','combined_shaping','auto_vkt','auto_mode_share','combined_environment']
fields7=['employment','access_population','employment_potential','combined_growth','current_max_load','current_ridership','new_riders','combined_affordability','competitiveness']
fields8=[r[0] for r in metrics[15:]]+['combined_equity']
metad={r[0]:r for r in metrics}
records=[]
def add(k,p,i,f,t,extra=''):
    if f in metad: flag=metad[f][11]
    elif f in ['category_choice','category_equity','combined_equity']: flag='派生汇总；Choice无显式成本，Equity另核转换'
    else: flag='源报告派生汇总/情景结果；不作Part1原始输入'
    records.append([k,p,i,f,None if t=='N/A' else float(t),t,'未能计算' if t=='N/A' else '报告公布分数/五分位',flag,URL+f'#page={p}',extra])
for k,p,tab,fields in [(5,10,t5,fields5),(6,11,t6,fields6),(7,12,t7,fields7),(8,13,t8,fields8)]:
    for i,row in enumerate(tab,1):
        for f,v in zip(fields,row):
            note=''
            if k==7 and i in [4,6,8,10] and f in ['current_max_load','current_ridership']: note='源表两个现状列灰底合并标N/A；两列均记录缺失'
            add(k,p,i,f,v,note)

# Table 3 is a source presentation order, not a recomputed ranking.
order3=[20,14,21,22,18,23,15,5,12,9,6,7,24,16,17,3,2,1,10,19,13,4,8,11]
for pos,i in enumerate(order3):
    q=5 if pos<5 else 4 if pos<10 else 3 if pos<14 else 2 if pos<19 else 1
    add(3,8,i,'city_final_score',t5[i-1][-1],'按Table3公布分组及顺序记录')
    add(3,8,i,'city_quintile',str(q),'源表五分位')

# Table 4: six numeric columns; group on y using the rightmost quintile as anchor.
w4=words(9)
last=[w for w in w4 if w['t'] in list('12345') and w['x']>535 and w['y']>150]
last=sorted(last,key=lambda w:w['y'])
assert len(last)==24,len(last)
for i,a in enumerate(last,1):
    wr=sorted([w for w in w4 if w['x']>370 and abs(w['y']-a['y'])<2 and re.fullmatch(r'-?\d+\.\d{2}|[1-5]',w['t'])],key=lambda w:w['x'])
    assert len(wr)==6,(i,wr)
    for f,w in zip(['cost_1_4_20_score','cost_1_4_20_quintile','cost_1_3_15_score','cost_1_3_15_quintile','cost_1_1_1_score','cost_1_1_1_quintile'],wr): add(4,9,i,f,w['t'])

missing=[]
for p,tab,fields in [(11,t6,fields6),(12,t7,fields7),(13,t8,fields8)]:
    for j,f in enumerate(fields):
        ids=[i for i,r in enumerate(tab,1) if r[j]=='N/A']
        if ids: missing.append([f,p,len(ids),', '.join(map(str,ids)),'灰底/N/A，未插补；不是0'])

sheets=[
{'name':'阅读说明','headers':['项目','说明'],'rows':[
['范围','仅做City 2024报告定位、元数据转录、原报告分数提取与审阅标记；未跑模型、未排名、未插补。'],
['来源','City of Toronto, Prioritization of Higher-Order Transit: Corridor Evaluation Procedure, 2024'],
['报告链接',URL],['页码规则','采用独立PDF从1开始的页序，共13页，不是委员会总文件页码。'],
['原始值与原文值','从报告直接抄下的数值叫原文值；不等于未加工原始观测。指标字典另列基础量性质和公布形式。'],
['数量','24走廊；15一般指标（10 Cost、1 Length、4未缩放）＋15公平子指标；Combined/类别/总分另为派生汇总。'],
['成本排除','Cost缩放分数及混入它们的汇总不可直接进入Part1；无成本版本的底层效益概念不因名称而被永久排除。'],
['未做的事','没有逆标准化、去成本、方向转换、相关分析、标准化、加权、概率模拟或方案推荐。'],
['定义','指标字典保留英文名称、Table1原定义、中文释义、源表Scaling和单位缺口。公平子指标按§2.4及Table8定位。'],
['源表分数','报告分数长表复制Tables3–8的结果，按Table2 ID对齐；均为原报告结果，非团队模型结果。'],
['合并缺失','Table7的ID4/6/8/10两个现状列合并灰底标N/A；提取为两列均缺失。'],
['下一步资料缺口','需无成本底层量、可达性/时间收益口径、公平比率和方向转换、Base可比性及长度核验；本次未补数据。']]},
{'name':'指标字典','headers':['指标ID','RTEF类别','英文原名','报告原定义或定位','中文释义','基础量性质','原报告数据来源','原文Scaling','公布值形式','24条原始值可得性','原始单位及缺口','Part1成本标记','方向/解释注意','潜在概念重复','定义与数值页码','源链接'],'rows':metrics},
{'name':'24条走廊','headers':['ID','走廊原名','From','To','原假定技术','原假定建设长度km','原Relative Cost_排除','Base','数值性质','Part1使用边界','页码','源链接','核验备注'],'rows':corridors},
{'name':'表格页码','headers':['表或节','PDF页','内容','值类型/范围','使用注意','源链接'],'rows':index},
{'name':'概念重复','headers':['概念组','涉及指标','可能重复之处','后续检查'],'rows':overlaps},
{'name':'待核验问题','headers':['问题','位置','已确认事实/限制','处理边界'],'rows':issues},
{'name':'原表缺失','headers':['指标ID','页码','缺失走廊数','走廊ID','状态'],'rows':missing},
{'name':'报告分数_非原始量','headers':['原Table','PDF页','走廊ID','字段ID','报告数值','原文标记','值状态','Part1使用边界','源链接','提取备注'],'rows':records}]

OUT.mkdir(exist_ok=True)
(ROOT/'work/inventory_data.json').write_text(json.dumps(sheets,ensure_ascii=False,indent=2),encoding='utf-8')
for name,rows in [('city_2024_corridors',corridors),('city_2024_metrics',metrics),('city_2024_report_scores_NOT_RAW',records)]:
    sheet=next(s for s in sheets if s['rows'] is rows)
    with (OUT/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(sheet['headers']);w.writerows(rows)

# Compact browser-readable inventory. Exact English definitions and all scores remain in Excel/CSV.
esc=lambda x:html.escape(str(x))
def table(headers,rows):return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc('' if x is None else x)+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>City 2024 指标定位与数据审阅</title><style>body{font:16px/1.65 "Microsoft YaHei",Arial,sans-serif;color:#183247;max-width:1400px;margin:40px auto;padding:0 25px}h1{font-size:28px}h2{font-size:21px;margin-top:35px}.note{background:#fff3d7;padding:18px;border-left:4px solid #c28524}table{border-collapse:collapse;width:100%;font-size:14px}th{background:#223e55;color:white;text-align:left}td,th{padding:10px;border-bottom:1px solid #dce4ea;vertical-align:top}tr:nth-child(even){background:#f2f6f9}.scroll{overflow:auto}a{color:#1a60a6}</style><h1>City 2024 报告：指标定位与数据审阅</h1><p>页码均指独立PDF页序1–13。未运行任何评价或优化模型。</p><p>来源：<a href="'+URL+'">City of Toronto 原报告</a></p><div class="note">核心发现：详细指标表给的是标准化分数，不是24条走廊的原始物理量。15个一般指标中10个明确按Cost缩放。无成本的基础效益概念可保留，但现有成本缩放分数不能直接进入Part 1，也不能仅乘回成本恢复原量。</div>']
for title,h,r in [('表格与页码',sheets[3]['headers'],index),('一般指标：定义、成本标记和重叠',['英文原名','中文定义','基础量性质','Scaling','Part1标记','数值页码','可能重复'],[[m[2],m[4],m[5],m[7],m[11],m[14],m[13]] for m in metrics[:15]]),('公平性15子指标',['群体/子指标','定义','使用注意'],[[m[2],m[4],m[12]] for m in metrics[15:]]),('24条走廊（均见Table2 p.7）',['ID','走廊','From','To','原假定技术','建设长度km','Base','核验备注'],[[r[0],r[1],r[2],r[3],r[4],r[5],r[7],r[-1]] for r in corridors]),('潜在概念重复',sheets[4]['headers'],overlaps),('待核验及数据缺口',sheets[5]['headers'],issues),('原表缺失',sheets[6]['headers'],missing)]:
    parts+=['<h2>'+title+'</h2>',table(h,r)]
parts+=['<p>Excel与CSV中的原报告分数仅作来源审计。未将其视为无成本输入或团队推荐结果。</p></html>']
(OUT/'City_2024_指标定位与审阅.html').write_text('\n'.join(parts),encoding='utf-8')
print(json.dumps({'metrics':len(metrics),'corridors':len(corridors),'source_score_cells':len(records),'missing':missing},ensure_ascii=False))
