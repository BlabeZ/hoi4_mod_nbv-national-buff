# 重要修正词条与选择依据

本表是第一轮完整注册目录与候选；国家全局 BUFF UI 的展示选项请优先使用[二次筛选白名单](global-buff-review/README.md)。

推荐优先级与源码证据评分分别列出。P0/P1 是统计页面候选，不代表已经逐项确认 ROOT.modifier@ 的读值、单位或实时性。

证据分 = 40 × log(1+定义次数)/log(1+最大定义次数) + 25 × log(1+文件数)/log(1+最大文件数) + 15 × min(内容类型数,5)/5 + 20 × 模组采纳数/2。对数压缩抑制重复脚本的影响；该分数仅用于同优先级内排序。采纳数按规范键归并，大小写差异单独记录。

人工核心候选共 **45 项**。AI倾向、目标限定与对象局部数值不会仅因高频自动变成通用国家总量。

## 政治

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P0 | [political_power_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4413>)<br>政治点数 | 1087／99 | 决议、UI | 政治点数获取系数，不能与每日固定增量混为一项。 |
| P0 | [political_power_gain](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4418>)<br>每日政治点数获取 | 419／59 | 决议、UI | 每日政治点数固定增量，影响顾问、法律与决议节奏；须与增益系数分列。 |
| P0 | [stability_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4825>)<br>稳定度 | 1349／94 | 未选 | 稳定度修正关联政治和工业表现；该修正值不等于国家当前最终稳定度。 |
| P0 | [war_support_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5115>)<br>战争支持度 | 931／83 | 未选 | 战争支持度修正关系战争动员和政策条件；该修正值不等于最终战争支持度。 |
| P0 | [conscription_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2277>)<br>可征募人口 | 565／79 | 未选 | 可征募人口系数，不能与conscription直接相加。 |
| P0 | [conscription](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2272>)<br>可征募人口 | 297／61 | 未选 | 国家可征募人口修正，应与可征募人口系数分开。 |

## 工业

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P0 | [production_speed_buildings_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4492>)<br>建设速度 | 433／76 | 决议、UI | 全局建筑速度，须与民工军工等专项建筑速度分列。 |
| P0 | [production_speed_industrial_complex_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>民用工厂建设速度 | 378／68 | 决议、UI | 民用工厂建设速度，直接影响早期工业扩张。 |
| P0 | [production_speed_arms_factory_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>军用工厂建设速度 | 369／62 | 决议、UI | 军用工厂建设速度，直接影响军工扩张。 |
| P0 | [local_resources_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3230>)<br>战略资源获取效率 | 143／39 | 决议、UI | 资源获取修正连接资源供给与缺料生产惩罚；国家和州同名项须区分。 |
| P0 | [consumer_goods_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2287>)<br>生活消费品工厂系数 | 1032／108 | 未选 | 消费品工厂系数影响可用民工；不是直接减少同数值百分点的总需求。 |
| P0 | [industrial_capacity_factory](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2917>)<br>工厂产出 | 563／93 | 未选 | 军工产出，区别于军用工厂建设速度；两个BUFF模组均遗漏。 |
| P0 | [research_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4600>)<br>科研速度 | 431／67 | 未选 | 全局科研速度，影响工业与各军种升级；两个BUFF模组均遗漏。 |
| P0 | [fuel_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2827>)<br>从石油获得的燃油 | 44／14 | 决议、UI | 燃油供给关联陆海空作战持续能力，放工业并关联军种燃油消耗。 |
| P0 | [industrial_capacity_dockyard](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2907>)<br>海军船坞产出 | 336／68 | 未选 | 船坞产出，属于工业并交叉关联海军；区别于船坞建设速度。 |
| P0 | [production_factory_max_efficiency_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4464>)<br>生产效率上限 | 206／48 | 未选 | 生产效率上限决定成熟生产线效率空间；两个BUFF模组均遗漏。 |
| P0 | [production_factory_efficiency_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4459>)<br>生产效率增长 | 166／51 | 未选 | 生产效率增长决定生产线爬升速度；与上限和起始效率分列。 |

## 陆军

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P0 | [army_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1797>)<br>陆军师攻击 | 266／54 | 决议、UI | 陆军师通用攻击修正；读数不是特定师在战斗中的最终攻击。 |
| P0 | [army_org_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1952>)<br>陆军师组织度 | 266／51 | 决议、UI | 陆军组织度系数，影响持续作战；区别于恢复速率。 |
| P0 | [army_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1852>)<br>陆军师防御 | 189／46 | 决议、UI | 陆军师通用防御修正；与装备和具体战斗条件分别解释。 |
| P0 | [army_morale_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1932>)<br>陆军师组织度恢复速率 | 187／46 | 决议、UI | 陆军师组织度恢复速率，和组织度上限及其他恢复项分列。 |
| P0 | [army_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1967>)<br>陆军师速度 | 90／34 | 决议、UI | 陆军移动速度修正，最终速度仍受编制装备地形等约束。 |
| P0 | [supply_consumption_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4966>)<br>补给消耗 | 179／48 | 未选 | 补给消耗关系后勤压力；两个BUFF模组均遗漏。 |
| P0 | [land_reinforce_rate](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3027>)<br>增援率 | 48／24 | 未选 | 战斗增援率影响预备队进入战斗，不是装备补充速度。 |

## 海军

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P0 | [repair_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4575>)<br>船只修理速度 | 120／28 | 决议、UI | 船只修理速度，影响舰队周转；两个BUFF模组误标为工厂修理，须纠正。 |
| P0 | [positioning](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4428>)<br>阵位 | 37／11 | 决议、UI | 海军阵位修正，关系舰队战斗效率；避免按泛称误归陆军。 |
| P0 | [sortie_efficiency](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4755>)<br>舰载机出击效率 | 25／15 | 决议、UI | 舰载机出击效率，航母舰队重点，交叉关联空军。 |
| P0 | [naval_hit_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3833>)<br>海军命中率 | 32／6 | 决议、UI | 通用海军命中，与轻炮重炮鱼雷专项命中分列。 |
| P0 | [naval_defense_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3783>)<br>海军防御 | 42／9 | 未选 | 海军防御修正影响受到的伤害，不是舰船装甲最终值。 |
| P0 | [naval_damage_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3778>)<br>海军伤害 | 40／7 | 未选 | 通用海军伤害，概括海战输出并与炮种命中分列。 |

## 空军

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P0 | [air_range_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1652>)<br>空军航程 | 45／18 | 决议、UI | 航程影响区域覆盖和部署自由度。 |
| P0 | [air_mission_efficiency](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1627>)<br>空军任务效率 | 64／18 | 决议、UI | 任务效率修正，不等同区域面板最终任务效率。 |
| P0 | [air_cas_efficiency](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1537>)<br>密接支援任务效率 | 36／17 | 决议、UI | 近距支援任务效率，不等于对陆军全部伤害总乘数。 |
| P0 | [air_agility_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1517>)<br>机动 | 57／13 | 决议、UI | 空军机动修正，与空攻空防速度分列。 |
| P0 | [air_superiority_efficiency](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1682>)<br>夺取制空权任务效率 | 45／16 | 决议、UI | 制空任务专项效率，与全局任务效率分列。 |
| P0 | [air_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1522>)<br>对空攻击 | 24／7 | 决议、UI | 空中攻击修正，国家读数不是机型最终空攻。 |
| P0 | [air_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1552>)<br>空中防御 | 14／5 | 决议、UI | 空中防御修正，关系飞机生存。 |

## 情报

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P0 | [operative_slot](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4263>)<br>特工位 | 110／33 | 决议、UI | 特工位数量修正，决定可并行任务数量。 |
| P0 | [navy_intel_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4078>)<br>海军情报 | 21／11 | 决议、UI | 海军情报归情报主类，并关联海军。 |
| P0 | [agency_upgrade_time](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1412>)<br>情报机构升级时间 | 37／10 | 决议、UI | 机构升级时间关系解锁节奏，显示着色须遵守原版正负收益。 |
| P0 | [army_intel_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1887>)<br>陆军情报 | 25／12 | 决议、UI | 陆军情报归情报主类，并关联陆军。 |
| P0 | [airforce_intel_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1717>)<br>空军情报 | 15／9 | 决议、UI | 空军情报归情报主类，并关联空军。 |
| P0 | [civilian_intel_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2212>)<br>民政情报 | 20／9 | 决议、UI | 民事情报修正，不是针对某一敌国的最终情报百分比。 |
| P0 | [intelligence_agency_defense](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2972>)<br>反间谍 | 51／21 | 未选 | 反间谍能力，国家情报安全核心概览。 |
| P0 | [decryption_power_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2373>)<br>破译能力修正 | 2／2 | 决议、UI | 破译能力系数，与固定破译能力分列。 |

## 两个 BUFF 模组遗漏的核心候选

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P0 | [stability_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4825>)<br>稳定度 | 1349／94 | 未选 | 稳定度修正关联政治和工业表现；该修正值不等于国家当前最终稳定度。 |
| P0 | [consumer_goods_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2287>)<br>生活消费品工厂系数 | 1032／108 | 未选 | 消费品工厂系数影响可用民工；不是直接减少同数值百分点的总需求。 |
| P0 | [war_support_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5115>)<br>战争支持度 | 931／83 | 未选 | 战争支持度修正关系战争动员和政策条件；该修正值不等于最终战争支持度。 |
| P0 | [conscription_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2277>)<br>可征募人口 | 565／79 | 未选 | 可征募人口系数，不能与conscription直接相加。 |
| P0 | [industrial_capacity_factory](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2917>)<br>工厂产出 | 563／93 | 未选 | 军工产出，区别于军用工厂建设速度；两个BUFF模组均遗漏。 |
| P0 | [research_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4600>)<br>科研速度 | 431／67 | 未选 | 全局科研速度，影响工业与各军种升级；两个BUFF模组均遗漏。 |
| P0 | [industrial_capacity_dockyard](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2907>)<br>海军船坞产出 | 336／68 | 未选 | 船坞产出，属于工业并交叉关联海军；区别于船坞建设速度。 |
| P0 | [conscription](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2272>)<br>可征募人口 | 297／61 | 未选 | 国家可征募人口修正，应与可征募人口系数分开。 |
| P0 | [production_factory_max_efficiency_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4464>)<br>生产效率上限 | 206／48 | 未选 | 生产效率上限决定成熟生产线效率空间；两个BUFF模组均遗漏。 |
| P0 | [supply_consumption_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4966>)<br>补给消耗 | 179／48 | 未选 | 补给消耗关系后勤压力；两个BUFF模组均遗漏。 |
| P0 | [production_factory_efficiency_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4459>)<br>生产效率增长 | 166／51 | 未选 | 生产效率增长决定生产线爬升速度；与上限和起始效率分列。 |
| P0 | [intelligence_agency_defense](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2972>)<br>反间谍 | 51／21 | 未选 | 反间谍能力，国家情报安全核心概览。 |
| P0 | [land_reinforce_rate](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3027>)<br>增援率 | 48／24 | 未选 | 战斗增援率影响预备队进入战斗，不是装备补充速度。 |
| P0 | [naval_defense_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3783>)<br>海军防御 | 42／9 | 未选 | 海军防御修正影响受到的伤害，不是舰船装甲最终值。 |
| P0 | [naval_damage_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3778>)<br>海军伤害 | 40／7 | 未选 | 通用海军伤害，概括海战输出并与炮种命中分列。 |

## P1 分类页重点候选

这些项目适合分类页或专项详情。部分来自频次门槛筛选，仍需人工确认具体统计对象；完整数据逐项保留 priority_basis。

### 政治

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P1 | [justify_war_goal_time](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2997>)<br>正当化战争目标所需时间 | 231／45 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [communism_drift](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1312>)<br>每日共产主义支持率 | 436／71 | 未选 | 共产主义支持度变化；高频但路线相关，放政治分类页而非通用首页。 |
| P1 | [fascism_drift](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1312>)<br>每日法西斯主义支持率 | 432／65 | 未选 | 法西斯主义支持度变化；高频但路线相关，放政治分类页。 |
| P1 | [democratic_drift](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1312>)<br>每日民主主义支持率 | 345／64 | 未选 | 民主主义支持度变化；高频但路线相关，放政治分类页。 |
| P1 | [neutrality_drift](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1312>)<br>每日中立主义支持率 | 312／61 | 未选 | 中立主义支持度变化；高频但路线相关，放政治分类页。 |
| P1 | [drift_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2438>)<br>意识形态变化抵制力度 | 325／47 | 未选 | 意识形态变化抵御相关修正，与各意识形态增长分列。 |
| P1 | [mobilization_speed](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3440>)<br>动员速度 | 141／43 | 未选 | 动员速度影响人力进入可用池的速度；人口修正高不意味着立即得到人力。 |
| P1 | [resistance_target](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4645>)<br>抵抗目标 | 162／37 | 未选 | 占领治理的抵抗目标修正，不等于当前抵抗度。 |
| P1 | [send_volunteers_tension](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4725>)<br>派遣志愿军的紧张度限制 | 112／54 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [stability_weekly](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4830>)<br>每周稳定度 | 174／53 | 未选 | 稳定度每周变化，频次高；与稳定度总修正及当前最终值分列。 |
| P1 | [mobilization_laws_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>征兵法案花费 | 146／33 | 未选 | 征兵法案费用修正，关联人力动员决策。 |
| P1 | [political_advisor_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>政治顾问花费 | 174／40 | 未选 | 政治顾问费用修正，原版频次高且直接关联政治点数支出。 |
| P1 | [autonomy_gain](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2017>)<br>每日自治度进程增长 | 118／32 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [non_core_manpower](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4213>)<br>非核心人力 | 111／34 | 未选 | 非核心人力修正，必须说明适用领土条件。 |
| P1 | [weekly_manpower](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5150>)<br>每周人力 | 128／52 | 未选 | 每周人力增量，不能与人口比例类修正直接相加。 |
| P1 | [party_popularity_stability_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4378>)<br>党派支持度对稳定度修正 | 118／30 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [economy_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>经济法案花费 | 158／37 | 未选 | 经济法案费用修正，经济制度切换的重要成本。 |
| P1 | [surrender_limit](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4981>)<br>投降界限 | 101／33 | 未选 | 投降阈值，战略价值高但并非各局都有非零修正。 |
| P1 | [compliance_growth](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2262>)<br>顺从度增长速度 | 113／27 | 未选 | 顺从度增长相关修正，与当前顺从度和其他增长项区分。 |
| P1 | [resistance_damage_to_garrison](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4610>)<br>驻军所受伤害 | 105／29 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [trade_laws_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>贸易法案花费 | 130／33 | 未选 | 贸易法案费用修正，关联政治点数支出与资源政策。 |
| P1 | [compliance_gain](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2257>)<br>每日顺从度增长 | 95／24 | 未选 | 占领治理的顺从度相关修正，国家读数不等于各州当前顺从度。 |
| P1 | [send_volunteer_size](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4720>)<br>志愿军陆军师数量上限 | 88／43 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [generate_wargoal_tension](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2842>)<br>名称待核验 | 67／26 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [resistance_growth_on_our_occupied_states](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4640>)<br>我们被敌人占领地区的抵抗增长速度 | 67／26 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [lend_lease_tension](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3042>)<br>租借法案的紧张度限制 | 54／28 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [trade_opinion_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5034>)<br>贸易影响力系数 | 84／22 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [join_faction_tension](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2992>)<br>加入阵营的紧张度限制 | 54／24 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [resistance_growth](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4635>)<br>抵抗增长速度 | 80／23 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [war_support_weekly](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5125>)<br>每周战争支持度 | 53／28 | 未选 | 战争支持度每周变化，和当前最终值及总修正分列。 |

### 工业

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P1 | [production_speed_infrastructure_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>基础设施建设速度 | 213／54 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [production_speed_dockyard_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>海军船坞建设速度 | 167／36 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [global_building_slots_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2857>)<br>地区最大工厂数 | 59／22 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [civilian_factory_use](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2202>)<br>民用工厂占用 | 370／40 | 未选 | 占用民用工厂数量，可解释决议等持续效果占用民工；不是消费品比例。 |
| P1 | [factory_energy_consumption](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2737>)<br>工厂能源消耗 | 61／9 | 决议、UI | 当前版本能源机制重点候选，源文件频次低不等于无用。 |
| P1 | [production_speed_synthetic_refinery_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>合成炼油厂建设速度 | 40／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [fuel_gain_factor_from_states](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2832>)<br>从炼油厂获得的燃油 | 21／7 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [production_speed_bunker_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>陆上要塞建设速度 | 100／35 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [production_speed_rail_way_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>铁路建设速度 | 98／35 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [industry_free_repair_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2937>)<br>免费维修 | 21／11 | 决议、UI | 免费建筑修复修正，与投入工厂修复不同。 |
| P1 | [production_lack_of_resource_penalty_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4474>)<br>缺乏战略资源惩罚 | 115／28 | 未选 | 缺资源惩罚修正可解释工厂产出为何低于预期。 |
| P1 | [production_speed_supply_node_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>补给中心建设速度 | 72／33 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [production_factory_start_efficiency_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4469>)<br>基础生产效率 | 71／24 | 未选 | 新生产线的起始效率，和效率上限、增长率分列。 |
| P1 | [line_change_production_efficiency_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3152>)<br>生产效率保持 | 67／25 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [industry_repair_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2942>)<br>工厂修复速度 | 54／24 | 未选 | 建筑工厂修复相关项；应取代两个BUFF模组误标为工厂修理的船只修理键。 |
| P1 | [production_speed_coastal_bunker_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>海岸要塞建设速度 | 71／24 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [min_export](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3410>)<br>出口资源 | 55／20 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [industrial_capacity_dockyard_powered](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2912>)<br>已供能的船坞产出 | 1／1 | 未选 | 供能条件下的船坞产出，必须说明条件。 |
| P1 | [industrial_capacity_factory_powered](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2922>)<br>已供能的工厂产出 | 1／1 | 未选 | 供能条件下的军工产出，必须说明条件而不能合并为无条件产出。 |
| P1 | [production_speed_buildings_powered_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4497>)<br>已供能的建设速度 | 0／0 | 未选 | 供能条件下的建设速度，必须说明条件。 |

### 陆军

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P1 | [army_core_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1837>)<br>陆军师核心领土防御 | 414／74 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [army_core_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1832>)<br>陆军师核心领土攻击 | 209／56 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [training_time_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5049>)<br>训练时间 | 183／55 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [special_forces_cap](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4765>)<br>特种部队容量上限乘数 | 81／27 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [acclimatization_hot_climate_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1397>)<br>炎热适应度增长率 | 45／18 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [acclimatization_cold_climate_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1392>)<br>寒冷适应度增长率 | 40／19 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [army_org_regain](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1957>)<br>陆军组织度恢复 | 53／25 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [experience_loss_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2692>)<br>有经验的士兵的损失 | 46／16 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [coordination_bonus](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2322>)<br>协同性 | 36／19 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [army_armor_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1762>)<br>装甲师攻击 | 49／19 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [training_time_army_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5044>)<br>陆军师训练时间 | 34／22 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [cas_damage_reduction](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2152>)<br>承受密接支援伤害减免 | 26／14 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [minimum_training_level](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3435>)<br>最低训练程度 | 31／11 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [attack_bonus_against](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1992>)<br>我国对该国进攻加成 | 392／45 | 未选 | 针对指定对象的攻击修正，高频但必须保留目标；不合并为国家无条件攻击。 |
| P1 | [army_infantry_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1872>)<br>步兵师攻击 | 34／11 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [army_artillery_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1777>)<br>炮兵攻击 | 33／11 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [special_forces_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4760>)<br>特种攻击 | 19／8 | 决议、UI | 特种部队攻击专项项，采用当前文档的小写规范键。 |
| P1 | [defense_bonus_against](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2383>)<br>名称待核验 | 299／38 | 未选 | 针对指定对象的防御修正，高频但必须保留目标。 |
| P1 | [army_armor_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1767>)<br>装甲师防御 | 26／10 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [experience_gain_army_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2652>)<br>陆军经验增长 | 120／40 | 未选 | 陆军经验获取系数，关系学说与设计。 |
| P1 | [command_power_gain_mult](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2247>)<br>每日指挥点数增长乘数 | 112／41 | 未选 | 指挥点数获取系数，影响指挥能力使用节奏。 |
| P1 | [experience_gain_army](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2647>)<br>陆军经验增长 | 133／34 | 未选 | 陆军经验固定增量，须与获取系数和部队经验区分。 |
| P1 | [planning_speed](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4398>)<br>计划速度 | 112／34 | 未选 | 计划准备速度，适合使用作战计划的陆军。 |
| P1 | [special_forces_training_time_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4800>)<br>特种部队训练时间 | 15／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [army_artillery_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1782>)<br>炮兵防御 | 24／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [org_loss_at_low_org_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4293>)<br>组织度低于25%时的损失 | 12／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [send_volunteer_divisions_required](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4710>)<br>派遣志愿军需要的陆军师数量 | 94／46 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [breakthrough_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2102>)<br>突破 | 80／30 | 未选 | 突破修正，是进攻时的重要生存属性维度。 |
| P1 | [experience_gain_army_unit_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2662>)<br>陆军师经验增长 | 8／6 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [max_command_power](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3270>)<br>最大指挥点数提高 | 75／31 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [command_power_gain](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2242>)<br>每日指挥点数增长 | 94／24 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [army_infantry_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1877>)<br>步兵师防御 | 12／7 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [army_strength_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1977>)<br>名称待核验 | 20／5 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [max_dig_in_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3290>)<br>堑壕上限 | 62／22 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [attrition](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2002>)<br>陆军师损耗 | 52／26 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [out_of_supply_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4308>)<br>非战斗补给耗尽惩罚 | 54／22 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [dig_in_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2403>)<br>堑壕速度 | 58／20 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [org_loss_when_moving](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4298>)<br>移动中组织度损失 | 53／21 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [special_forces_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4775>)<br>特种防御 | 11／6 | 决议、UI | 特种部队防御专项项，采用当前文档的小写规范键。 |
| P1 | [max_planning](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3315>)<br>计划加成上限 | 57／15 | 未选 | 计划加成上限增量，与计划速度和系数分开。 |
| P1 | [land_doctrine_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3012>)<br>陆军学说花费 | 62／23 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [max_dig_in](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3285>)<br>堑壕上限 | 32／14 | 未选 | 堑壕上限增量，与堑壕速度和系数分开。 |
| P1 | [initiative_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2947>)<br>主动性 | 21／8 | UI | 当前文档登记的主动性系数；不要直接沿用普通版initiative字符串。 |
| P1 | [army_fuel_consumption_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1867>)<br>陆军燃料消耗 | 15／7 | 未选 | 陆军燃油消耗，和供油补给一起解释。 |
| P1 | [army_non_core_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1942>)<br>陆军师非核心领土防御 | 4／3 | UI | 非核心领土防御条件修正，不能标为攻击。 |
| P1 | [army_non_core_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1937>)<br>陆军师非核心领土攻击 | 4／3 | 未选 | 非核心领土攻击条件修正；UI版对应标签误读defence键，需更正。 |
| P1 | [combat_width_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2232>)<br>己方战场宽度 | 0／0 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |

### 海军

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P1 | [naval_coordination](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3758>)<br>舰队协同性 | 109／24 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [spotting_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4815>)<br>索敌速度 | 58／26 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [convoy_retreat_speed](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2317>)<br>撤退时运输船速度 | 32／11 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_critical_score_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3768>)<br>打出致命一击的几率 | 32／8 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_capital_ship_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4033>)<br>主力舰装甲 | 24／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_capital_ship_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4023>)<br>主力舰攻击 | 24／8 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_retreat_speed](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3928>)<br>撤退时的舰队速度 | 24／7 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_light_gun_hit_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3878>)<br>轻型火炮命中率 | 16／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_submarine_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4158>)<br>潜艇攻击 | 17／8 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [critical_receive_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2343>)<br>名称待核验 | 14／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_visibility](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4183>)<br>名称待核验 | 19／6 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_torpedo_hit_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3993>)<br>鱼雷命中几率 | 16／7 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_torpedo_reveal_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3998>)<br>鱼雷暴露几率 | 10／7 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [ships_at_battle_start](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4730>)<br>名称待核验 | 17／6 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_critical_effect_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3763>)<br>持续致命一击的效果 | 11／5 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_screen_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4148>)<br>屏卫舰防御 | 23／7 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_heavy_gun_hit_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3828>)<br>重型火炮命中率 | 12／6 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [experience_gain_navy](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2672>)<br>海军经验增长 | 75／23 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [navy_screen_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4138>)<br>屏卫舰攻击 | 18／6 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_carrier_air_targetting_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4053>)<br>名称待核验 | 7／5 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_torpedo_screen_penetration_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4003>)<br>鱼雷穿透屏卫舰 | 6／5 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_carrier_air_agility_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4043>)<br>名称待核验 | 8／5 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_org_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4133>)<br>海军组织度 | 53／11 | 未选 | 海军组织度系数，补充持续作战维度。 |
| P1 | [navy_fuel_consumption_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4068>)<br>海军燃料消耗 | 42／12 | 未选 | 海军燃油消耗，连接舰队活动和燃油预算。 |
| P1 | [experience_gain_navy_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2677>)<br>海军经验增长 | 45／19 | 未选 | 海军经验获取系数，关系学说与设计。 |
| P1 | [navy_carrier_air_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4048>)<br>名称待核验 | 6／4 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_submarine_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4168>)<br>潜艇防御 | 6／4 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_night_attack](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3913>)<br>夜间攻击 | 4／4 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [carrier_capacity_penalty_reduction](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2132>)<br>航母超载 | 5／5 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [fighter_sortie_efficiency](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2777>)<br>名称待核验 | 10／7 | UI | 舰载战斗机出击效率，表示航母给舰载战斗机加油载弹的速度，须与陆基任务效率区分。 |
| P1 | [naval_torpedo_damage_reduction_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3983>)<br>敌军鱼雷伤害降低 | 5／3 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3948>)<br>海军速度 | 19／7 | 未选 | 海军速度修正，影响部署作战，不是具体舰队最终航速。 |
| P1 | [naval_torpedo_enemy_critical_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3988>)<br>敌军鱼雷致命一击率 | 5／3 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_weather_penalty](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4188>)<br>恶劣天气惩罚 | 2／2 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_torpedo_cooldown_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3978>)<br>鱼雷冷却 | 1／1 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [night_spotting_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4198>)<br>夜间索敌 | 1／1 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |

### 空军

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P1 | [air_cas_present_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1542>)<br>地面支援 | 34／15 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_training_xp_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1687>)<br>空军联队训练经验增长 | 35／16 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_mission_xp_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1632>)<br>空军联队任务经验增长 | 34／13 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_strike_targetting_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3968>)<br>对海瞄准 | 22／10 | 决议、UI | 对海打击瞄准，虽含naval仍应归航空兵对海打击。 |
| P1 | [air_nav_efficiency](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1637>)<br>对海任务效率 | 28／11 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_untrained_pilots_penalty_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1692>)<br>新空军联队未经训练的飞行员惩罚 | 16／12 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_wing_xp_loss_when_killed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1707>)<br>空军联队受损时失去的经验 | 17／10 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_accidents_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1497>)<br>空军事故几率 | 68／21 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [air_bombing_targetting](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1527>)<br>对地轰炸瞄准 | 11／6 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_ace_generation_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1507>)<br>王牌飞行员产生几率 | 60／28 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [air_superiority_detect_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1677>)<br>战斗机探测 | 8／7 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_strategic_bomber_bombing_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1657>)<br>战略轰炸 | 46／17 | 未选 | 战略轰炸专项修正，适合空军分类页。 |
| P1 | [experience_gain_air_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2642>)<br>空军经验增长 | 48／19 | 未选 | 空军经验获取系数，关系学说设计。 |
| P1 | [air_fuel_consumption_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1577>)<br>空军燃料消耗 | 32／14 | 未选 | 空军燃油消耗，与工业供油关联。 |
| P1 | [air_ace_bonuses_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1502>)<br>空军王牌加成 | 4／3 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_maximum_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1622>)<br>名称待核验 | 4／2 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [air_close_air_support_org_damage_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1547>)<br>近距支援机组织度伤害系数 | 3／2 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [naval_strike_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3963>)<br>对海轰炸 | 13／6 | 未选 | 航空兵对海打击攻击修正，空军主类并关联海军。 |
| P1 | [air_detection](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1557>)<br>对空探测 | 13／6 | 未选 | 对空探测，与任务专项探测分列。 |

### 情报

| 优先级 | 修正键和名称 | 定义次数／文件数 | 两模组选取 | 作用或选择理由 |
|---|---|---:|---|---|
| P1 | [civilian_intel_to_others](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2217>)<br>泄露给他国的民政情报 | 60／21 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [army_intel_to_others](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1892>)<br>泄露给他国的陆军情报 | 39／18 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [enemy_operative_capture_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2498>)<br>敌方特工被捕几率 | 29／15 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [airforce_intel_to_others](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1722>)<br>泄露给他国的空军情报 | 26／14 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [navy_intel_to_others](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4083>)<br>泄露给他国的海军情报 | 23／13 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [intel_network_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2967>)<br>情报网强度增长率 | 34／8 | 决议、UI | 情报网增长系数，不能与增量项直接相加。 |
| P1 | [enemy_operative_intel_extraction_rate](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2533>)<br>敌方特工情报获取率 | 14／9 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [enemy_operative_detection_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2508>)<br>敌方特工被发现几率系数 | 13／6 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [decryption_power](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2368>)<br>破译能力 | 10／4 | 决议、UI | 固定破译能力，和系数分开显示。 |
| P1 | [foreign_subversive_activites](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2802>)<br>名称待核验 | 72／23 | 未选 | 原版跨文件使用较广，建议作为分类页候选复核 |
| P1 | [enemy_operative_detection_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2503>)<br>敌方特工被发现几率补正 | 12／3 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [new_operative_slot_bonus](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4193>)<br>特工招募选项 | 9／4 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [own_operative_detection_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4338>)<br>我方特工被发现几率系数 | 5／3 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [intel_network_gain](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2962>)<br>情报网强度增长 | 4／3 | 决议、UI | 情报网增长增量，与系数分列；具体网络受目标地区条件影响。 |
| P1 | [operation_cost](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4243>)<br>行动花费 | 2／2 | 决议、UI | 情报行动成本修正，实际费用取决于行动类型。 |
| P1 | [operation_outcome](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4253>)<br>行动效率 | 2／2 | 决议、UI | 行动结果修正，具体效果取决于行动类型。 |
| P1 | [crypto_strength](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2353>)<br>加密等级 | 6／1 | 决议、UI | 密码强度，区别于本国主动破译能力。 |
| P1 | [own_operative_capture_chance_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4328>)<br>我方特工被捕几率 | 1／1 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [own_operative_detection_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4333>)<br>我方特工被发现几率补正 | 1／1 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [operation_risk](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1360>)<br>行动风险 | 0／0 | 决议、UI | 行动风险修正，最终风险不只由此项决定。 |
| P1 | [own_operative_intel_extraction_rate](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4353>)<br>情报获取率 | 0／0 | 决议、UI | UI版已选择的候选项，可进入所属分类页；模组采纳不保证读值作用域和标签正确。 |
| P1 | [intelligence_operation_speed](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2977>)<br>情报行动速度系数 | 0／0 | 未选 | 情报行动速度，关系任务周转。 |

## 关联解读

政治点固定增量与获取系数、征兵比例与征兵系数、工厂产出与效率上限／增长／保持、陆军攻击与核心／非核心条件、国家修正与目标国家修正应分别显示。同族名称和共同出现不构成计算公式。完整数据的 related_keys 是人工或同族命名关联；cooccurring_keys 是同一脚本定义块中共同出现的统计关联，均不能直接当作因果或相加／连乘关系。
