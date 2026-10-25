# 原版普通／旧式民族精神来源独立覆盖审计（0.1.8）

审计日期：2026-10-25。只读审计；未改动生产模组或原版。结论范围为本机原版 1.19.3 文件与当前 519 个页面词条，不包括第三方重写的同名精神。

**结论：文件扫描完整，但不能确认民族精神的悬停来源已经全部覆盖。** 页面合计读取 `ROOT.modifier@key`，不依赖下面的来源映射；“没有来源”不能等同于“合计漏加”。

本报告使用独立 lexer/tree scanner 重新读原版，未调用生产生成器的 parser 或接受其“已覆盖”计数。JSON 保留全部定义、行号、直接值、traits 引用及遗漏清单。DLC 路径完整性由主审计单独核验。

## 范围与计数

| 项目 | 结果 |
|---|---:|
| ideas 文件 / 定义 | 213 / 6508 |
| 独立解析失败 | 0 |
| EOF 不闭合但可读取的外层 ideas | SOV、persia、switzerland 共 3 文件 |
| 当前页面词条 / 基础注册词条 | 519 / 559 |
| 普通／隐藏精神、法案、军种精神：非零直接修正，落在当前页面键 | 10302 |
| 上述已有来源绑定 | 9979 |
| 有中文名、do_effect 未适配 | 246 条 / 36 个精神 |
| traits 承载的国家精神未适配 | 7 条 / 4 个精神 |
| 无中文来源名，被当前显示策略排除 | 77 条 / 31 个精神 |
| 当前页面键中的非字面量直接 modifier 值 | 0 |

已对全部 9 张现行来源表交叉核验：下文 36 个 do_effect 精神的 246 条贡献及 4 个 traits 精神的 7 条贡献，在对应修正键的 activation_script 中均无该精神 ID 的持有适配。合计 **40 个具名国家精神、253 条当前页面来源贡献明确未适配**；并非被另一来源表补齐。

“条”指一个来源组件对一个当前页面修正键的贡献，不是缺失的页面词条数量。不能用 6508 减去已绑定精神数作为遗漏数量，因为其中包含法案、顾问、设计商、无所选修正及用户不展示项目。

## 明确仍未适配的普通民族精神

### 条件生效 do_effect

当前代码整项排除带 `do_effect` 的精神。要补齐应在 `has_idea` 之外原样核验其生效条件，不能仅以持有精神推断有贡献。斯柯达的条件是仍控制至少一个核心州；意大利科研合作有阵营条件。CZE 外包武器生产虽然也带 do_effect，但在当前范围只有 targeted_modifier，不计入本节246条。

| 精神 ID | 名称 | 当前页面贡献数 | 原版位置 |
|---|---|---:|---|
| `CZE_skoda_no_focus_optimization_1_idea` | 斯柯达优先事项：重工业重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:6` |
| `CZE_skoda_no_focus_optimization_2_idea` | 斯柯达优先事项：重工业重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:52` |
| `CZE_skoda_no_focus_optimization_3_idea` | 斯柯达优先事项：重工业重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:99` |
| `CZE_skoda_no_focus_optimization_4_idea` | 斯柯达优先事项：重工业重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:146` |
| `CZE_skoda_no_focus_optimization_5_idea` | 斯柯达优先事项：重工业重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:192` |
| `CZE_skoda_no_focus_optimization_6_idea` | 斯柯达优先事项：重工业重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:238` |
| `CZE_skoda_no_focus_optimization_7_idea` | 斯柯达优先事项：重工业重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:284` |
| `CZE_skoda_infantry_focus_optimization_1_idea` | 斯柯达优先事项：步兵重心 | 6 | `common/ideas/czechoslovakia_skoda.txt:336` |
| `CZE_skoda_infantry_focus_optimization_2_idea` | 斯柯达优先事项：步兵重心 | 6 | `common/ideas/czechoslovakia_skoda.txt:381` |
| `CZE_skoda_infantry_focus_optimization_3_idea` | 斯柯达优先事项：步兵重心 | 6 | `common/ideas/czechoslovakia_skoda.txt:426` |
| `CZE_skoda_infantry_focus_optimization_4_idea` | 斯柯达优先事项：步兵重心 | 6 | `common/ideas/czechoslovakia_skoda.txt:471` |
| `CZE_skoda_infantry_focus_optimization_5_idea` | 斯柯达优先事项：步兵重心 | 6 | `common/ideas/czechoslovakia_skoda.txt:516` |
| `CZE_skoda_infantry_focus_optimization_6_idea` | 斯柯达优先事项：步兵重心 | 6 | `common/ideas/czechoslovakia_skoda.txt:561` |
| `CZE_skoda_infantry_focus_optimization_7_idea` | 斯柯达优先事项：步兵重心 | 6 | `common/ideas/czechoslovakia_skoda.txt:606` |
| `CZE_skoda_tanks_focus_optimization_1_idea` | 斯柯达优先事项：坦克重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:655` |
| `CZE_skoda_tanks_focus_optimization_2_idea` | 斯柯达优先事项：坦克重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:707` |
| `CZE_skoda_tanks_focus_optimization_3_idea` | 斯柯达优先事项：坦克重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:759` |
| `CZE_skoda_tanks_focus_optimization_4_idea` | 斯柯达优先事项：坦克重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:811` |
| `CZE_skoda_tanks_focus_optimization_5_idea` | 斯柯达优先事项：坦克重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:863` |
| `CZE_skoda_tanks_focus_optimization_6_idea` | 斯柯达优先事项：坦克重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:915` |
| `CZE_skoda_tanks_focus_optimization_7_idea` | 斯柯达优先事项：坦克重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:967` |
| `CZE_skoda_planes_focus_optimization_1_idea` | 斯柯达优先事项：飞机重心 | 8 | `common/ideas/czechoslovakia_skoda.txt:1025` |
| `CZE_skoda_planes_focus_optimization_2_idea` | 斯柯达优先事项：飞机重心 | 8 | `common/ideas/czechoslovakia_skoda.txt:1076` |
| `CZE_skoda_planes_focus_optimization_3_idea` | 斯柯达优先事项：飞机重心 | 8 | `common/ideas/czechoslovakia_skoda.txt:1127` |
| `CZE_skoda_planes_focus_optimization_4_idea` | 斯柯达优先事项：飞机重心 | 8 | `common/ideas/czechoslovakia_skoda.txt:1178` |
| `CZE_skoda_planes_focus_optimization_5_idea` | 斯柯达优先事项：飞机重心 | 8 | `common/ideas/czechoslovakia_skoda.txt:1229` |
| `CZE_skoda_planes_focus_optimization_6_idea` | 斯柯达优先事项：飞机重心 | 8 | `common/ideas/czechoslovakia_skoda.txt:1280` |
| `CZE_skoda_planes_focus_optimization_7_idea` | 斯柯达优先事项：飞机重心 | 8 | `common/ideas/czechoslovakia_skoda.txt:1331` |
| `CZE_skoda_naval_focus_optimization_1_idea` | 斯柯达优先事项：海军重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:1387` |
| `CZE_skoda_naval_focus_optimization_2_idea` | 斯柯达优先事项：海军重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:1430` |
| `CZE_skoda_naval_focus_optimization_3_idea` | 斯柯达优先事项：海军重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:1473` |
| `CZE_skoda_naval_focus_optimization_4_idea` | 斯柯达优先事项：海军重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:1516` |
| `CZE_skoda_naval_focus_optimization_5_idea` | 斯柯达优先事项：海军重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:1559` |
| `CZE_skoda_naval_focus_optimization_6_idea` | 斯柯达优先事项：海军重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:1602` |
| `CZE_skoda_naval_focus_optimization_7_idea` | 斯柯达优先事项：海军重心 | 7 | `common/ideas/czechoslovakia_skoda.txt:1645` |
| `ITA_scientific_cooperation_ns` | 科研合作 | 1 | `common/ideas/italy.txt:2924` |

### traits 承载的精神

下列精神本身未绑定；领袖表或其他国家顾问表出现同名 trait，并不能覆盖这些精神，因为各自的持有触发器不同。

| 精神 | trait | 词条 | 值 | 原版位置 |
|---|---|---|---:|---|
| 乔治五世国王 (`george_v`) | `popular_figurehead` | 稳定度 | 0.15 | `common/ideas/britain.txt:4` |
| 乔治六世 (`ENG_george_vi`) | `popular_figurehead` | 稳定度 | 0.15 | `common/ideas/britain.txt:85` |
| 威廉明娜 (`HOL_wilhelmina`) | `popular_figurehead` | 稳定度 | 0.15 | `common/ideas/netherlands.txt:96` |
| 古斯塔夫五世国王 (`SWE_gustaf_v_idea`) | `SWE_former_autocrat` | 政治点数 | -0.1 | `common/ideas/sweden.txt:4` |
| 古斯塔夫五世国王 (`SWE_gustaf_v_idea`) | `SWE_former_autocrat` | 法西斯主义外交接纳度 | 20 | `common/ideas/sweden.txt:4` |
| 古斯塔夫五世国王 (`SWE_gustaf_v_idea`) | `SWE_former_autocrat` | 中立主义外交接纳度 | 20 | `common/ideas/sweden.txt:4` |
| 古斯塔夫五世国王 (`SWE_gustaf_v_idea`) | `SWE_former_autocrat` | 每日指挥点数增长乘数 | 0.15 | `common/ideas/sweden.txt:4` |

## 旧式顾问与设计商

这些数据确实存在于 `common/ideas`，没有被现代 character/advisor 适配表自动覆盖。以下是定义层面的候选，不是“所有这些旧式人物在当前局一定能聘用”的运行时结论；仍需核验 DLC、allowed/available/do_effect 与实际聘用接口。

- 旧式顾问的 traits：{len(adv)} 条当前页面键贡献候选；其中有明确中文名的 {sum(bool(r['names_zh']) for r in adv)} 条，涉及 {len(set(r['idea'] for r in adv if r['names_zh']))} 个顾问，集中在白俄罗斯、克罗地亚、维希法国。没有任何同 idea_token 的现行顾问来源绑定。
- 其余 1259 条来自无静态中文名／通用旧式人物；不能直接输出原始 ID，需先解决原版运行时人物名称。
- 旧式设计商有 452 条直接 modifier 和 376 条 traits 候选落在页面键；均没有旧式设计商持有适配。这里不包括 equipment_bonus／research_bonus 嵌套对象。用户允许设计商提供的国家修正，故它们应单列待适配。

### 有中文名的旧式顾问清单

| 顾问 ID | 名称 | 贡献数 | 原版位置 |
|---|---|---:|---|
| `BLR_boris_berman` | 鲍里斯·贝尔曼 | 2 | `common/ideas/belarus.txt:68` |
| `BLR_jozeph_ryzhykov` | 约瑟夫·莱兹可夫 | 4 | `common/ideas/belarus.txt:79` |
| `BLR_vasily_sokolovsky` | 瓦西里·索科洛夫斯基 | 1 | `common/ideas/belarus.txt:93` |
| `BLR_ivan_yakubovsky` | 伊万·雅库鲍夫斯基 | 1 | `common/ideas/belarus.txt:108` |
| `BLR_ivan_pstygo` | 伊万·普斯特戈 | 1 | `common/ideas/belarus.txt:126` |
| `BLR_fedor_dobysh` | 费奥多尔·多贝什 | 1 | `common/ideas/belarus.txt:141` |
| `BLR_valentin_drozd` | 瓦连金·德罗兹德 | 1 | `common/ideas/belarus.txt:160` |
| `BLR_georgy_holostyakov` | 格奥尔吉·霍洛斯贾科夫 | 1 | `common/ideas/belarus.txt:175` |
| `BLR_piotr_kozlov` | 彼得·科兹洛夫 | 1 | `common/ideas/belarus.txt:193` |
| `BLR_alexander_akulich` | 亚历山大·阿库里奇 | 2 | `common/ideas/belarus.txt:209` |
| `BLR_maksim_antonyuk` | 马克西姆·安东纽克 | 2 | `common/ideas/belarus.txt:225` |
| `BLR_aleksei_antonov` | 阿列克谢·安东诺夫 | 1 | `common/ideas/belarus.txt:243` |
| `BLR_stepan_krasovsky` | 斯捷潘·克拉索夫斯基 | 1 | `common/ideas/belarus.txt:255` |
| `CRO_ivan_subasic` | 伊凡·萨巴斯奇 | 3 | `common/ideas/croatia.txt:69` |
| `CRO_alojzije_stepinac` | 阿洛茨杰·斯蒂芬纳克 | 1 | `common/ideas/croatia.txt:84` |
| `CRO_gaspar_njegovan` | 加斯帕尔·涅戈万 | 4 | `common/ideas/croatia.txt:95` |
| `CRO_vladimir_laxa` | 弗拉迪米尔·拉克萨 | 1 | `common/ideas/croatia.txt:111` |
| `CRO_fedor_dragojlov` | 罗伊·达拉根诺维奇 | 1 | `common/ideas/croatia.txt:126` |
| `CRO_friedrich_navratil` | 弗雷德利希·纳瓦拉提尔 | 1 | `common/ideas/croatia.txt:147` |
| `CRO_adalbert_rogulja` | 阿达尔贝特·罗古加 | 1 | `common/ideas/croatia.txt:162` |
| `CRO_edgar_angeli` | 埃德加·安盖利 | 1 | `common/ideas/croatia.txt:180` |
| `CRO_nikola_steinfl` | 尼古拉·斯坦福 | 4 | `common/ideas/croatia.txt:195` |
| `CRO_slavko_stancer` | 斯拉夫克·斯坦瑟 | 2 | `common/ideas/croatia.txt:214` |
| `CRO_vilko_begic` | 维勒库·贝基奇 | 2 | `common/ideas/croatia.txt:230` |
| `CRO_vladimir_kren` | 弗拉迪米尔·克伦 | 1 | `common/ideas/croatia.txt:262` |
| `CRO_djuro_jakcin` | 杜约洛·贾克希 | 2 | `common/ideas/croatia.txt:278` |
| `CRO_sismundo_pejacevic` | 西斯蒙多·佩雅切维奇 | 1 | `common/ideas/croatia.txt:297` |
| `CRO_ivan_crnkovic` | 伊万·克恩科维奇 | 1 | `common/ideas/croatia.txt:309` |
| `CRO_mihajlo_tomasic` | 米哈伊洛·托马西奇 | 1 | `common/ideas/croatia.txt:321` |
| `VIC_marius_viple` | 马里于斯·维普勒 | 1 | `common/ideas/vichy_france.txt:19` |
| `VIC_rene_bousquet` | 勒内·布斯凯 | 3 | `common/ideas/vichy_france.txt:31` |
| `VIC_charles_huntziger` | 夏尔·安齐热 | 1 | `common/ideas/vichy_france.txt:46` |
| `VIC_lucien_lacaze` | 罗伯特哈斯 | 1 | `common/ideas/vichy_france.txt:60` |
| `VIC_maxime_weygand` | 马克西姆·魏刚 | 1 | `common/ideas/vichy_france.txt:93` |
| `VIC_jean_marie_bergeret` | 让-玛丽·贝热雷 | 1 | `common/ideas/vichy_france.txt:114` |
| `VIC_jean_romatet` | 让·罗马泰 | 1 | `common/ideas/vichy_france.txt:132` |
| `VIC_jean_francois_darlan` | 让·弗朗索瓦·达尔朗 | 1 | `common/ideas/vichy_france.txt:154` |
| `VIC_jean_marie_abrial` | 让-玛丽·阿布里亚尔 | 1 | `common/ideas/vichy_france.txt:172` |
| `VIC_jean_francois_jannekeyn` | 让-弗朗索瓦·珍妮肯 | 3 | `common/ideas/vichy_france.txt:194` |
| `VIC_jean_de_laborde` | 让·德·拉博德 | 2 | `common/ideas/vichy_france.txt:213` |
| `VIC_marcel_bruno_gensoul` | 马塞尔·布鲁诺·让苏尔 | 2 | `common/ideas/vichy_france.txt:232` |
| `VIC_pierre_le_gloan` | 皮耶尔·勒·格洛昂 | 1 | `common/ideas/vichy_france.txt:251` |

## 与遗漏区分的项目

- 当前 40 个主动移出页面的 registry 键不在审计缺口分母内。
- 零值不显示。
- 77 条无中文来源名的条目单列，不以英文 ID 冒充名称，也不直接归为已经确认应展示的来源。
- targeted_modifier 中有 40 个当前页面键的出现，但它们带特定对象上下文，不能并入无目标的国家全局值。
- equipment_bonus／research_bonus、on_add／on_remove 不是持有时可直接相加的国家 modifier；前者是对象/科技效果，后者可能产生其他精神或动态修正，应沿实际来源体系跟踪，不能重复计入。
- 本报告只核查 ideas；dynamic_modifiers 的完整性与运行时数值表达式由独立动态审计处理。

## 复核文件

- `audit_static_ideas_v018.py`：独立读取脚本。
- `static-idea-coverage-audit-v018.json`：完整机器可读清单，含每项源码位置。
- `summarize_static_ideas_v018.py`：本报告生成器。

建议依次补齐：36 个 do_effect 精神 → 4 个 traits 精神 → 可用的旧式顾问/国家设计商来源。每类验证添加、移除、条件失效和切换国家后的来源，保持合计直接读取引擎、不制造差额。
