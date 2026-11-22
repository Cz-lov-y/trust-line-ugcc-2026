> **最新 Task 2 v0.1：已开始技术证据与硬约束筛选，固定23号、7.101 km。** 用户要求先筛预算、完整工期、路权和车辆段，再做技术评分。29条参考证据、12个明确的目标估计缺口；三技术均待核实，未做加权排名，未证明任一技术必然不可行。59项测试通过。先读[硬约束报告](outputs/project/outputs/task2_v0.1/HARD_CONSTRAINTS.md)和 `outputs/project/CONTINUATION_task2_v0.1.json`；以下 Task 1 记录保留供追溯，不是要求重新选线。

> **Task 1 v0.8：正式模型论证已补齐，主推仍为23号，但不能称“100%免疫”。** 新增相关性、概念权重预算、连续权重压力测试和24条全部五指标评估。广权重前五率81.82%，说明性均衡子区域97.63%；三原则量化覆盖仍有明确缺口。先读[正式论证](outputs/project/outputs/model_argument_v0.8/MODEL_JUSTIFICATION.md)和 `CONTINUATION_v0.8.json`，以下均为历史快照。

> **最新 v0.7：主推已改为 23 号 Finch Ave E（Yonge–Victoria Park）。** 剔除 current_ridership 后，12 号前五进入率降至66.59%，最差第9；23号仍100%且第1–2。长度疑似对调但无官方勘误，源标准分未修改。先读[最新报告](outputs/project/outputs/jane_stress_v0.7/REPORT.md)、`outputs/project/CONTINUATION_v0.7.json` 和五指标 `model_input_selection_v0.7.json`。以下 v0.6/v0.5 状态均是历史快照。

> **后续更新 v0.6：以下正文是 v0.5 的历史交接快照。** 用户现已授权 16/8 分层、10,000 次情景抽样和带限制的就绪口径。当前 `model_ready=true`、`limitations_flagged=true`、`unrestricted_model_ready=false`；短名单 12/23/20，仅 12/23 超过 90% 前五进入率。请先读 [最新报告](outputs/project/outputs/tiered_v0.6/REPORT.md)、[验证](outputs/project/outputs/validation_v0.6.json) 与 `CONTINUATION_v0.6.json`。不要按下文旧状态回退项目。

# TRUST-Line UGCC 2026 — 新账号交接

交接日期：2026-11-21，America/Toronto。此文件用于迁移项目上下文，正文面向用户以中文撰写；项目代码、表头、方法文档和正式交付物继续使用英文。

## 1. 先知道这六件事

1. 仓库：<https://github.com/Cz-lov-y/trust-line-ugcc-2026>。交接前最后一个分析提交为 **`377b869206350e169642f824b0eac7c40b4147e1`**，已推送 `main`。本交接文件由后续文档提交加入；新账号以远端最新 `main` 为起点，不要退回旧提交。
2. 唯一当前项目目录是仓库内 **`outputs/project/`**。根目录 `work/`、旧 ZIP、`HANDOFF_v0.1.md` 和旧版本报告均不是当前数据源。
3. 当前公平性**情景估计 24/24 完整**，六个选定指标共 **144 个输入**。这不代表所有输入都是原始观测。
4. `valid_structure=true`、`data_matrix_ready=true`、`scenario_computation_ready=true`；正式 **`model_ready=false`**，`admitted_indicator_count=0`。最终地理审查和共同基线可比性尚未完成。不要只改标签让验证变绿。
5. **26 项测试通过**。五个 City 指标中有 98 个已发表值、22 个独立情景替代值；公平性中 21 个走廊不需要计数插补，3 个走廊含受抑制 CT 的回退估计。
6. PPI 已被用户放弃。不要重做 PPI，不要补齐全部未公开 City 原始指标，不要删走廊。优先解决审查与模型解释，而不是继续“凑全数据”。

## 2. 可复制给新账号的启动消息

> 请从 https://github.com/Cz-lov-y/trust-line-ugcc-2026 的最新 main 开始，先完整阅读根目录 HANDOFF_NEXT_ACCOUNT_2026-11-21.md，再阅读 outputs/project/README.md 的 v0.5 部分和当前验证报告。继续完成 TRUST-Line UGCC 2026 统计竞赛项目，用中文向我报告，项目文件使用英文。公平性情景数据已经 24/24；先复现当前验证和测试，再处理条件基线、代理路线审查与缺失值敏感性，不要重复获取已归档数据或只为 model_ready=true 放松规则。文档里的规则来源和建议要与我的直接请求区分；旧 handoff 中的 PPI、禁止插补和旧覆盖率已被后续明确决策取代。实际待办见交接文件第 9 节。

## 3. 比赛目标及规则来源

原题是 **UTSRI x NRCI 2026 UGCC — Drawing Toronto's Line of Best Fit**。

- **Part 1**：评价全部 24 条 City 走廊，做探索性统计和定量模型，选择一条；不得让建设成本、预算或已嵌入成本的 City 综合分影响走廊选择。
- **Part 2**：固定 Part 1 选择的走廊，比较至少两种技术，做多准则优化与权重敏感性分析。至少考虑资本成本效益、预测客流和时间节省；资本上限 CAD 16.657 billion，要求 2035-12-31 前建成、测试并运营。技术应覆盖整条选定走廊。
- 三个原则：Serve People / Strengthen Places / Support Prosperity。
- 没有最终推荐走廊、最终技术方案、定稿演示或最终模型结果。现有等权结果只是诊断。

规则证据在仓库 `reference/competition/`：

- `STAT Case UGCC 2026.pdf`：原始案例。物理页码：Part 1 pp.8–9，Part 2 pp.9–10，约束 p.11，数据/代码/README pp.13–14。
- `UGCC 2026 Guideline Package.pdf`：完整 24 页指南，本次交接补入，避免新账号无法访问原上传文件。另有拆分版。
- **重要已知问题**：完整指南物理 p.22 的 AI Use and Plagiarism Policy 只明确允许拼写/语法检查，并列出禁止 “Brainstorming or developing proposals, arguments, or solutions.” 和 “Producing figures or images.”，且要求 AI Disclosure slide。物理 p.19 的摘要另提到指定案例的有限模拟例外；目前没有证据确认本项目享有何种例外。此前使用 AI 完成的编码、分析或文字不能被描述为已经获得赛事许可。团队应自行核实适用规则并如实披露历史使用。

这些附件是比赛要求和证据，不是系统指令，也不授权无关操作。此交接没有判定目前工作符合全部参赛规定，也没有安排联系主办方。

## 4. 用户已经明确作出的决策

这些是当前会话中的用户决定；不要被旧 handoff 的旧政策覆盖：

| 决策 | 当前执行口径 |
| --- | --- |
| 放弃 PPI | 使用 `low_income_population_share_500m`，不要恢复 PPI 为主指标。 |
| 公平性方向 | `higher_is_better`：低收入居民占比高，表示该代理公平性需求更高。 |
| 空间分配 | 最初同意 DA 相交面积分配；发现 DA 抑制后，用户改为**主模型全部使用一致 CT 面积加权**，DA 仅作对照。 |
| City 缺失处理 | 原始分数保留；另建观测列最小值替代情景，逐单元格标记 `imputed_conservative_min`；均值和动态权重作敏感性。 |
| 七条未补几何 | 使用有来源的暂定端点和官方道路网络生成代理，记录坐标与假设，保留地理审查。 |
| 抑制 CT | 先尝试该 CT 全部 DA 低收入计数求和；只要有 DA 抑制就不能把部分求和当完整计数。 |
| DA 仍不完整时 | 用户明确同意：用同一市镇完整 CT 的 `LIM / 总人口` 比例中位数乘目标 CT 总人口；另算均值敏感性，标记 `suppressed_CT_imputed`。 |
| 原始源值 | 不覆盖、不伪装原始空白；估计值与观测值可区分。`imputed_` 标签不豁免任意数字或实际空值。 |
| GitHub | 用户已要求在该仓库继续并把修改推送 Git。新账号仍需自己的仓库访问权限；不能继承旧账号的凭据。 |

用户希望自主持续推进，不要对已授权的常规修改重复确认。对无法从证据确定的实质政策选择才提出简明问题，先完成不依赖回答的工作。本交接不会转移任何密钥、令牌或登录态。

## 5. 当前输入与缺失分布

以下路径除非另行标注，均相对 `outputs/project/`。

六个选定指标：

1. `current_speed`
2. `unimproved_load`
3. `current_max_load`
4. `current_ridership`
5. `competitiveness`
6. `low_income_population_share_500m`

### City 五列

原始表：`data/city_standardized_scores_v0.1.csv`。缺失集中于七条走廊，属于情况 B，而不是随机分布：

| 指标 | 原始有值 | 原始缺失 | 缺失走廊 |
| --- | ---: | ---: | --- |
| current_speed | 17 | 7 | 3,4,5,6,8,10,13 |
| unimproved_load | 24 | 0 | 无 |
| current_max_load | 20 | 4 | 4,6,8,10 |
| current_ridership | 20 | 4 | 4,6,8,10 |
| competitiveness | 17 | 7 | 3,4,5,6,8,10,13 |

没有任何一条走廊五列全空；17 条五列完整。

- 主要分析情景：`data/city_analysis_inputs_v0.4.csv`，120 个有限值，其中 22 个为替代值，逐列有 `_value_status`。
- 均值对照：`data/city_mean_sensitivity_v0.4.csv`。
- 政策：`data/missing_data_policy_v0.4.json`。
- 缺失审计、逐单元格追踪、动态权重：`outputs/missingness_v0.4/`。
- 最小替代值：speed −1.26，maximum load −2.16，ridership −0.90，competitiveness −1.84；unimproved load 不需要替代。

**观测最小值不是已证明的理论最低值，也不是新增线路无现状服务的真实测量值。** 某些缺失可能是结构性不适用，仍需在解释与敏感性中认真处理。

City 输入是已发表的维度无关标准分，不是字典中描述的原始 km/h 或人数。`higher_is_better` 指较好的 City 评价分，不等于原始速度越快越应优先。所选五项 Table 1 没有 Cost scaling；current ridership 使用 Length scaling。不得混入其他含成本的综合分。

### 完整合并矩阵

`data/model_matrix_v0.5.csv`：24 行，六指标加来源/插补标记。City 列保留原有标准分，公平性仍是原始比例；**不能直接把比例与标准分简单相加而不声明尺度处理**。

## 6. 公平性估计的准确含义

主输入：`data/supplemental_model_inputs_v0.5.csv`。

公式：

```text
f_ct = area(CT ∩ corridor_500m_buffer) / area(CT)
share = sum(f_ct × analysis_CT_LIM_count) / sum(f_ct × CT_total_population)
```

- 假设：同一 CT 内总人口和低收入人口分别均匀分布；所有走廊使用同一 CT 面积分配法。
- 官方来源：Statistics Canada 2021 Census，characteristic **326** = LIM-AT 低收入计数，**1** = 2021 总人口；321 是另一项 private-household LIM applicable population 对照。
- 低收入参考年 **2020**，人口/地理 **2021**。分母是全部居民，和官方 LIM 私人家庭适用人口口径不同，所以这是**自定义居民集中度代理，不是官方 LIM prevalence，也不是交通改善受益比例**。
- 道路缓冲区不是未来站点 500m catchment，不得悄悄当成原 City 站点分布指标。
- 305 个相交 CT 的原始计数：`data/census_ct_batch_v0.5.csv`。
- 分析计数：`data/census_ct_analysis_v0.5.csv`。
- 权重/计数分配账本：`outputs/corridor_batch_v0.5/corridor_CT_allocations.csv`。
- CT 原始几何、profile CSV、来源 URL/哈希：`evidence/corridor_batch_v0.5/`。

### 两个抑制 CT

| CT | 总人口 | 全部 DA | DA 的 LIM 状态 | 主要情景 CT 低收入人数 |
| --- | ---: | --- | --- | ---: |
| 5350205.00 | 144 | 35204701 | 同样抑制 | 16.52892562 |
| 5350006.00 | 119 | 35201461 | 同样抑制 | 13.65932048 |

这两个 CT 各只有一个 DA，其 DA 总人口与 CT 总人口一致；低收入计数均为官方 flag **6**。不能用 DA 汇总恢复真实计数。

已获取 Toronto 全部 585 个 CT 的相关官方 profile；排除两个受抑制 CT，583 个完整且人口为正的 CT 作为市镇回退样本。使用 **CT 比例的非加权中位数**，不是全市人口加权比例：

```text
median(LIM_count / all_resident_population) = 0.1147842056932966
mean(LIM_count / all_resident_population)   = 0.12657021072488234
analysis_suppressed_CT_count = median_rate × suppressed_CT_total_population
```

- 标记 `suppressed_CT_imputed`，影响走廊 **3、8、21**；8 号是新补几何后也碰到同一 CT，不能只标 3、21。
- 原始 CT/DA 受抑制单元格仍为空，不能把上述小数人数写回原始源表。
- 详细回退账本：`outputs/corridor_batch_v0.5/suppression_imputation_trace.csv`。
- 回退样本：`outputs/corridor_batch_v0.5/municipal_CT_peer_rates.csv`。
- 方法配置：`data/equity_proxy_method_v0.5.json`；v0.3 文档仅说明基础口径，抑制政策以 v0.5 为准。
- CT/DA/市镇归属使用已归档 GAF crosswalk。该 GAF 来自第三方镜像，官方原 ZIP 校验和未独立核验；Toronto DB 人口总和与官方基准吻合。不能把“人口核对通过”说成“官方二进制校验通过”。市镇归属检查文件为 `peer_CT_CSD_membership_check.csv`。

1 号走廊试点仍为 **15.9119215964%**。早期人口 25,300–40,059 是 DB 边界法区间，中点 **32,679.5** 只是分母压力测试，不是面积加权人口点估计；CT 加权人口约 **30,491.28**。早期“174 DA”表述错误：174 个相交地理单元是 **DB**，DA 是后续另一层数据。

## 7. 几何与端点

当前所有几何：`outputs/corridor_batch_v0.5/corridor_road_proxies.geojson`、`corridor_buffers_500m.geojson`。计算 CRS **EPSG:2952**，导出 EPSG:4326。

| 批次 | 走廊 | 实际方法 |
| --- | --- | --- |
| 原 17 条 | 1,2,3,7,11,12,13,14,15,16,17,18,20,21,22,23,24 | City 当前中心线的指定道路图路径；1 号保留原试点几何。 |
| 新 7 条 | 4,5,6,8,9,10,19 | 官方 StatCan 2021 RNF 网络，暂定端点投影到道路边，按长度求无向最短路，500m buffer。 |

新七条输入：`data/corridor_endpoint_coordinates_v0.5.csv` 和相邻 JSON。脚本 **`code/batch_endpoint_road_buffers.py`** 实际使用 GeoPandas 与 NetworkX。路径长度分别约 9.532、2.892、4.300、4.701、10.560、4.514、9.917 km。City 原建设长度未被改写。

关键端点假设：

- Park Lawn、Union、Humber College、Kipling、Dundas West、Sherway 等使用官方 TTC/GO stop 或相应道路节点代理。
- **Woodbine GO：官方页面确认 Highway 27/Kitchener rail corridor 区域，但未给已审核的测量点。实际数值采用明确注明来源的次级近似坐标 43.70619, −79.59442。** 用户授权暂定有来源端点，不代表此坐标成为官方测量点；约 250m 的端点不确定性尚未完成专项几何敏感性测试。
- Pearson：Terminal 1 的 UP Express 站点代理，非机场质心或 Terminal 3。
- Markham Centre：Unionville GO mobility hub 代理，不是已证实的未来 McCowan 延伸站址。
- Ontario Place：运营方描述的西入口对应 City 道路交点，不是已批准的未来轨道站点。
- Ontario Line North：Don Mills/Eglinton 到 Don Mills/Steeles 的分支假设仍需审查。

证据与路径 segment IDs：`evidence/corridor_batch_v0.5/endpoint_reference_review.json`、`outputs/corridor_batch_v0.5/endpoint_route_audit.json`。官方 RNF 原始分页已无损压成 **`official_RNF_source_pages.zip`**；有完整 object-ID 核对和哈希清单，可离线重建。不必重新下载巨大源数据。

图不会凭空跨越断链；内部平面交叉不会自动创建路口；节点取 0.01m 舍入。RNF 是无向制图道路代理，不是审核过的车辆导航或轨道拓扑。混合两套道路方法和不同年份本身是可比性问题。原 Jane 两段的量得长度与 City 建设长度分配存在显著差异，不能擅自互换 City 源值；current ridership 的 length scaling 也因此需审查。海岸线/源 CT 制图地框未覆盖面积有报告，不能捏造该区域人口。

## 8. 现在为什么仍未最终 admitted

当前权威配置：

- `data/workbook_records_v0.1.json`：数据字典和准入记录的权威记录源。
- `data/schema_v0.1.json`：工作簿列结构。
- `data/model_input_selection_v0.1.json`：六指标和输入映射。
- `data/model_input_coverage_v0.1.csv`：分析情景覆盖率。
- 两份 `*_v0.1.xlsx` 文件名虽是 v0.1，但内容已更新，44 个指标记录；不要仅凭文件名判断版本。

六个输入均登记为 `scenario_admission_status=admitted_for_declared_proxy_scenario`；正式 `admission_status=pending_comparability_review`。24 个公平性记录仍是 `pilot_estimate`，而不是地理审查完成的 `reviewed_estimate`。

基线审核：`outputs/corridor_batch_v0.5/baseline_comparability_audit.csv`。八条条件基线走廊为 **3,6,11,13,14,16,17,24**；源头在 City Attachment 物理 pp.3–4 §2.5、p.7 Table 2。ID 与依赖 DAG 已核对，但没有共同基线反事实预测数据。City 源文明确：部分结果是依赖前置走廊的增量效果。最小值替代无法消除条件性。

四个当前 TTC 指标基于现状资料；unimproved load 来自预测框架。2020/2021 Census、2022 现状和预测框架也不是同一年。完整源五列走廊的范围比较仅是描述性诊断；10 号的 unimproved-load 分数超出该参考范围，但范围内也不能证明基线等价。

`code/validate_data.py` 继续保留最终准入/可比性门槛，并新增独立的情景完整性状态。`code/validate_equity_scenario.py` 从原始归档 profile 重新计算市镇中位数/均值、核对 DA 完整性与人口、验证哈希、源标记和 CT 分配总量。原 City 22 个替代值也会按源列最小值重新核验。只写 notes 或 `imputed_` 不会让空值、任意值或伪装观测通过。

1056 个空原始 inventory 单元格并不阻止这六个派生情景输入计算。不要为填这些格子耗尽时间。

## 9. 下一步任务（按优先级）

### A. 先复现当前状态

新账号 clone 最新 main，确认分析提交 377b869 在历史中。读本文、当前 README v0.5、CONTINUATION_v0.5.json、validation_v0.5.json 和两个审查 CSV。运行验证和 26 项测试。不要误用 Windows 原路径或旧 ZIP。

### B. 做出有证据的最终模型范围决策

1. 审查八条条件基线，以及“现状观测 + 条件预测 + 历史人口代理”混用的含义。
2. 若能获得共同基线预测，应保存来源并重算；若不能，考虑明确的条件扩展解释、依赖约束，或把 forecast unimproved load 放到扩展/敏感性模型。**这些是待讨论的路线，不是用户已选择的最终模型。** 不能把条件增量简单声称为 24 个独立项目的同基线收益。
3. 审查所有暂定地理与源走廊范围，尤其新七条、Woodbine 次级坐标、Markham Centre、Pearson、Ontario Line 分支和 Jane 长度问题；有可信几何时替换代理，并从 matching buffer 重新获取/核验 Census 覆盖。
4. 如果保留代理作为最终研究假设，需在指标定义、模型适用范围、元数据和验证逻辑中一致记录其适用性与证据。不得通过删除审查、改成“confirmed”或改字段名掩盖尚未解决的问题。

### C. 再完善 Part 1

完成必要 EDA：相关性、冗余、尺度/方向、现状字段结构性缺失；明确权重来源。可在已声明的情景范围内继续计算，不必等待所有原始指标补齐。最终模型与最终推荐需说明适用范围和局限，保留全部 24 条。

已运行的等权六指标诊断在 `six_criterion_policy_diagnostic.csv` 与 `scenario_review_summary.json`：保留 City 标准分，公平性跨 24 条用 population SD 标准化，等权，competition ranks。

| 对照 | 相对主要情景的最大名次变化 | 当前诊断前三集合 |
| --- | ---: | --- |
| City minimum + CT median | 0 | {9,12,23} |
| City minimum + CT mean | 0 | {9,12,23} |
| City mean + CT median | 8 | {9,12,23} |
| available-case 动态权重 + CT median | 12 | {9,12,23} |
| 去掉 forecast unimproved load | 5 | {9,12,21} |

CT median→mean 的公平性比例变化最多约 **0.00335 个百分点**，不等于地理误差或全部插补误差都很小。City 缺失政策可显著改变个别排名；不能声称完整排序稳健。历史五指标诊断曾变化 14/16 位，与当前六指标 8/12 位不是同一次模型，不要混写。

尚未完成的部分包括正式权重/不确定性模型、最终走廊决策、Part 2 技术数据与优化、成本/工期可行性、最终演示、说明文档和必要披露。旧 handoff 提过 MCDA、SMAA、Pareto、TOPSIS、PCA 等构想，均不代表已有实现，也不是必须全部采用。

### D. 最后完成 Part 2 与交付

只有在 Part 1 最终走廊固定后，才对整条走廊比较至少两种技术。把预算和工期限制放到 Part 2；不要让 Part 2 的成本反向渗入 Part 1 选择。核对原案例交付规范和完整比赛指南，逐一记录未解决假设。未经证据验证，不得声称预算、2035 工期、赛事资格或 AI 使用合规已满足。

## 10. 新环境运行方法

下面是示例；clone 位置和虚拟环境名字可改。**旧云端的 `/workspace/work/...` 和账号登录态不会自动迁移。**

```sh
git clone https://github.com/Cz-lov-y/trust-line-ugcc-2026.git
cd trust-line-ugcc-2026/outputs/project
python -m venv .venv
.venv/bin/python -m pip install -r code/requirements_gis.txt
.venv/bin/python -B code/validate_data.py
.venv/bin/python -B -m unittest discover -s code -p 'test_*.py' -v
```

验证应看到结构和情景状态为 true、正式 model_ready 为 false，且没有结构错误。Windows 可用 `.venv\Scripts\python.exe` 代替；必要时按新环境的 Python 命令调整。

优先使用归档数据，离线复现 v0.5：

```sh
.venv/bin/python -B code/prepare_endpoint_inputs_v0_5.py
.venv/bin/python -B code/batch_endpoint_road_buffers.py
.venv/bin/python -B code/calculate_equity_v0_5.py
.venv/bin/python -B code/register_v0_5_inputs.py
.venv/bin/python -B code/review_scenario_inputs_v0_5.py
.venv/bin/python -B code/validate_data.py
```

这些脚本会重写当前派生文件；先确认工作区干净或有自己的备份，再运行，并检查 `git diff`。`analyze_city_missingness.py` 可重建 v0.4 City 缺失情景。不要运行旧 `register_v0_4_inputs.py` 当作当前注册步骤，否则会把 active mapping 降回历史版本。

只有端点/几何或源版本确实改变，才需要 fresh acquisition：新道路脚本 `--acquire-roads` 会按端点范围直接请求官方 RNF；`batch_corridor_equity.acquire(version="v0.5")` 获取与当前缓冲区匹配的 CT 边界/profile。先读 README 的 fresh-acquisition 说明，保留新旧证据和哈希；不要用旧 Census 提取结果配新缓冲区。`pack_road_evidence_v0_5.py` 用于冻结源分页；已有冻结 ZIP 不应覆盖。

工作簿以 JSON/schema 为准，用 `code/build_workbooks.mjs` 生成，依赖 Node 的 `@oai/artifact-tool`。旧云端可用：

```sh
ARTIFACT_NODE_MODULES=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules \
SKIP_WORKBOOK_PREVIEWS=1 node code/build_workbooks.mjs
```

新账号不能假定该依赖路径存在；按其环境定位或安装工具后再生成。`SKIP_WORKBOOK_PREVIEWS=1` 避免不必要的图像渲染；不是跳过表格数据校验。XLSX 仍应与 JSON 记录保持一致。

旧云环境 GIS 解释器为 `/workspace/work/gis_env/bin/python`，本地版本包括 GeoPandas 1.2.0、NetworkX 3.7、pandas 2.3.3、Shapely 2.2、pyproj 3.8。这是历史环境信息，不是新账号已安装的保证。

## 11. 快速文件索引

| 目的 | 路径（相对 outputs/project） |
| --- | --- |
| 当前详细方法 | `README.md` 顶部 v0.5 部分 |
| 机器摘要 | `CONTINUATION_v0.5.json` |
| 六指标矩阵 | `data/model_matrix_v0.5.csv` |
| 公平性主输入 | `data/supplemental_model_inputs_v0.5.csv` |
| City 主分析输入 | `data/city_analysis_inputs_v0.4.csv` |
| 原始 City 源表 | `data/city_standardized_scores_v0.1.csv` |
| 原始发表分数存档 | `evidence/city_2024_published_scores_NOT_RAW_v0.1.csv` |
| 原始 master | `data/corridor_master_v0.1.csv`，44 个候选指标占位；不能用其空格判断六指标矩阵缺失 |
| City 原报告/评价附件 | `evidence/source_documents/` |
| 当前 CT/source/acquisition | `evidence/corridor_batch_v0.5/` |
| 几何/分配/基线/敏感性 | `outputs/corridor_batch_v0.5/` |
| 验证结果 | `outputs/validation_v0.5.json` |
| 测试记录 | `outputs/tests_v0.5.txt` |
| 可读审查页 | `outputs/review_v0.5.html` |
| 文件哈希索引 | `outputs/project_inventory_v0.5.json` |
| 更新清单 | `outputs/UPLOAD_MANIFEST_v0.5.md` |

历史进度提交：`87aa482` Census 支持审计；`240a5d8` 替换 PPI、CT 试点；`980ea7c` City 缺失与 17 条道路代理；`377b869` 补成 24/24 情景并加入抑制回退。不要把历史报告当成现状，但也不要覆盖这些可复核快照。

## 12. 已检查与未声明事项

交接写作前核对了本地 `main` 的最新分析提交、干净工作区、当前 JSON、测试记录、官方 CT/DA 抑制结果和完整指南 p.22。文档更新没有重新执行科学分析，也没有改变任何模型数据或推荐。没有密码、token、浏览器登录态或账户秘密写入交接。

本次新增文件将提交并推送到同一仓库。新账号可从 GitHub 获取本交接及全部归档输入；不依赖原账号上传文件 ID、原电脑路径或聊天记忆。
