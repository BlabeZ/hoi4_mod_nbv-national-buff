# 用户指定的 BUFF 展示名单修订

日期：2026-10-25。修订前 562 项，新增 26 项，移出 29 项，修订后 **559 项**（A 521、B 38）。完整目录仍为 4484 项，未入选的 3925 项仅保留审计记录。

移出项包括 **25 个原已选无名词条和4个指定B档词条**。全目录共 79 个未确认名称的键，均为C；不会以技术键或占位名称进入BUFF界面。此次指定词条中 7 项原已选入，继续保留，不重复计数。

## 按用户清单对应到修正键

| 用户要求 | 采用的键与本轮结果 |
|---|---|
| 设计商修正（不包括具体对象/科技修正） | `aircraft_manufacturer_cost_factor`：C → A<br>`industrial_concern_cost_factor`：C → A<br>`naval_manufacturer_cost_factor`：C → A<br>`tank_manufacturer_cost_factor`：C → A<br>`materiel_manufacturer_cost_factor`：C → A<br>`military_industrial_organization_funds_gain`：C → A |
| 所有主义外交接纳度 | `communism_acceptance`：C → A<br>`democratic_acceptance`：C → A<br>`fascism_acceptance`：C → A<br>`neutrality_acceptance`：C → A |
| 冬季损耗、炎热损耗 | `winter_attrition`：C → A<br>`winter_attrition_factor`：C → A<br>`heat_attrition_factor`：C → A |
| 炎热适应度增长率、寒冷适应度增长率 | `acclimatization_hot_climate_gain_factor`：C → A<br>`acclimatization_cold_climate_gain_factor`：C → A |
| 恶劣天气惩罚（空军） | `air_weather_penalty`：C → A |
| 恶劣天气惩罚（海军） | `navy_weather_penalty`：C → A |
| 投降界限 | `surrender_limit`：保留 A<br>`forced_surrender_limit`：C → A |
| 跨空域力量投射修正系数 | `air_power_projection_factor`：C → B |
| 每项空降入侵计划的陆军师容量、空降作战计划上限 | `air_invasion_division_cap`：C → B<br>`air_invasion_plan_cap`：C → B |
| 陆军师损耗 | `attrition`：保留 A |
| 己方战场宽度 | `combat_width_factor`：C → B |
| 军用/民用工厂/船坞捐赠 | `military_factory_donations`：C → B<br>`industrial_factory_donations`：C → B<br>`dockyard_donations`：C → B |
| 军用/民用工厂/船坞/基础设施建设速度 | `production_speed_arms_factory_factor`：保留 A<br>`production_speed_industrial_complex_factor`：保留 A<br>`production_speed_dockyard_factor`：保留 A<br>`production_speed_infrastructure_factor`：保留 A |
| 陆军师训练时间 | `training_time_army`：C → B<br>`training_time_army_factor`：保留 A |

## 同名、对象与科技边界

- 四种主义指原版顶层的共产主义、民主主义、法西斯主义、中立主义；子意识形态不另外生成修正键。
- 冬季损耗基础项与比例项分列；空军、海军恶劣天气惩罚分列；训练时间基础项与比例项分列。它们不是重复键，不能仅凭同名相加。
- `forced_surrender_limit` 标注“强制阈值”，与常规 `surrender_limit` 分列。
- 军用工厂、民用工厂、船坞、基础设施四种建设速度使用原有国家键；四个同名 `state_` 键继续排除。
- 设计商增加五类国家聘用费用及军工机构经费获取，共6项。无名称MIO管理项、具体机构/装备/模块/生产线属性不加入。
- `heat_attrition`：炎热损耗基础项本次只检出Province天气对象赋值，未检出国家来源；国家炎热损耗使用heat_attrition_factor。不能把地方基础损耗值并入全局BUFF；不据此断言引擎禁止国家使用此键。
- `attrition_for_controller`：中文同为陆军师损耗，但当前证据指向state_modifier及地区动态修正，不能作为已确认国家全局值；使用国家attrition满足损耗展示需求。
- `military_industrial_organization_research_bonus`：军工机构研究加成属于设计商相关科研修正，按本次“不包括科技修正”的口径继续排除；不影响其他普通国家科研加成。

仅发现地方来源并不证明引擎拒绝国家使用；本轮依据已确认存储对象选择同名的国家版本。空降容量/计划上限、己方战场宽度等用户明确指定而无赋值记录的键，则保留注册候选标记，不能声称其国家读数已验证。

## 新增进入展示库

| 修正键／名称 | 国家精神定义 | 国策关联 | 分类理由及条件 |
|---|---:|---:|---|
| [acclimatization_cold_climate_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1392>)<br>寒冷适应度增长率 | 8 | 31 | 用户指定保留国家持有的炎热/寒冷适应度增长修正。；条件：展示国家增长率修正，不展示各部队当前适应度或当地温度。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:1457>) |
| [acclimatization_hot_climate_gain_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1397>)<br>炎热适应度增长率 | 9 | 47 | 用户指定保留国家持有的炎热/寒冷适应度增长修正。；条件：展示国家增长率修正，不展示各部队当前适应度或当地温度。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/britain.txt:1350>) |
| [air_invasion_division_cap](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1597>)<br>每项空降入侵计划的陆军师容量 | 0 | 0 | 用户指定展示空降师容量与计划上限；注册表中存在，但本次未检出原版定义赋值，按明确需求加入待运行核验候选。；条件：容量项与计划数上限分列；未确认基值，不把修正分量直接标为最终容量。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。；本次原版扫描未检出定义赋值；不能将仅注册解释为当前国家必有非零值，也不能将修正分量当作最终上限。 |
| [air_invasion_plan_cap](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1602>)<br>空降作战计划上限 | 0 | 0 | 用户指定展示空降师容量与计划上限；注册表中存在，但本次未检出原版定义赋值，按明确需求加入待运行核验候选。；条件：容量项与计划数上限分列；未确认基值，不把修正分量直接标为最终容量。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。；本次原版扫描未检出定义赋值；不能将仅注册解释为当前国家必有非零值，也不能将修正分量当作最终上限。 |
| [air_power_projection_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1647>)<br>跨空域力量投射修正系数 | 0 | 0 | 用户指定展示国家持有的跨空域力量投射修正系数。；条件：展示国家系数，不读取某一空域的实际投射力量。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/china_nationalist_sea.txt:11845>) |
| [air_weather_penalty](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1702>)<br>恶劣天气惩罚（空军） | 2 | 28 | 用户指定保留国家持有的空军恶劣天气惩罚修正。；条件：与海军天气惩罚分列，不加入实际空域天气惩罚值。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/finland.txt:174>) |
| [aircraft_manufacturer_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>飞机设计商花费 | 4 | 9 | 用户指定加入国家面向设计商的通用管理修正：五类聘用费用及军工机构经费获取；有国家精神来源。；条件：只读国家持有的费用/经费修正，不读取具体MIO、装备或生产线对象；旧设计商机制受DLC分支影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:3034>) |
| [combat_width_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2232>)<br>己方战场宽度 | 0 | 0 | 用户指定展示己方战场宽度修正；本次未检出原版定义赋值，保留国家读取待实测标记。；条件：仅为修正候选，不等于单个师或某次战斗的最终战场宽度。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。；本次原版扫描未检出定义赋值；不能将仅注册解释为当前国家必有非零值，也不能将修正分量当作最终上限。 |
| [communism_acceptance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1304>)<br>共产主义外交接纳度 | 16 | 18 | 用户指定展示原版四种意识形态的外交接纳度；本轮覆盖旧的外交接受倾向排除规则。；条件：按对方意识形态分列，不汇总为一个外交接纳度；接纳度不等于外交行动成功概率。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:194>) |
| [democratic_acceptance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1304>)<br>民主主义外交接纳度 | 16 | 25 | 用户指定展示原版四种意识形态的外交接纳度；本轮覆盖旧的外交接受倾向排除规则。；条件：按对方意识形态分列，不汇总为一个外交接纳度；接纳度不等于外交行动成功概率。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:222>) |
| [dockyard_donations](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2428>)<br>海军船坞捐赠 | 0 | 0 | 用户指定展示军用工厂、民用工厂和海军船坞捐赠的国家修正。；条件：按三种工业设施分别显示修正分量，不与地图上实际设施总数混算。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。；本次原版扫描未检出定义赋值；不能将仅注册解释为当前国家必有非零值，也不能将修正分量当作最终上限。 |
| [fascism_acceptance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1304>)<br>法西斯主义外交接纳度 | 20 | 30 | 用户指定展示原版四种意识形态的外交接纳度；本轮覆盖旧的外交接受倾向排除规则。；条件：按对方意识形态分列，不汇总为一个外交接纳度；接纳度不等于外交行动成功概率。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/_event.txt:211>) |
| [forced_surrender_limit](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2797>)<br>投降界限（强制阈值） | 1 | 1 | 用户指定展示投降界限，保留常规项并补入有国家精神来源的强制投降阈值项。；条件：常规surrender_limit与forced_surrender_limit分列，后者标注强制阈值；不能相加或互相替代。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/japan.txt:2242>) |
| [heat_attrition_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2897>)<br>炎热损耗（比例项） | 5 | 7 | 用户指定恢复天气损耗词条，仅纳入国家持有分量的展示候选，不累计地图天气对象的数值。；条件：冬季损耗基础项与_factor比例项分列，不直接相加；炎热损耗只纳入有国家来源的比例项，基础项仅检出地方天气来源。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/aussa.txt:4>) |
| [industrial_concern_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>工业企业花费 | 8 | 13 | 用户指定加入国家面向设计商的通用管理修正：五类聘用费用及军工机构经费获取；有国家精神来源。；条件：只读国家持有的费用/经费修正，不读取具体MIO、装备或生产线对象；旧设计商机制受DLC分支影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:1050>) |
| [industrial_factory_donations](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2927>)<br>民用工厂捐赠 | 0 | 0 | 用户指定展示军用工厂、民用工厂和海军船坞捐赠的国家修正。；条件：按三种工业设施分别显示修正分量，不与地图上实际设施总数混算。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。 |
| [materiel_manufacturer_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>军需品设计花费 | 5 | 10 | 用户指定加入国家面向设计商的通用管理修正：五类聘用费用及军工机构经费获取；有国家精神来源。；条件：只读国家持有的费用/经费修正，不读取具体MIO、装备或生产线对象；旧设计商机制受DLC分支影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:3034>) |
| [military_factory_donations](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3355>)<br>军用工厂捐赠 | 0 | 0 | 用户指定展示军用工厂、民用工厂和海军船坞捐赠的国家修正。；条件：按三种工业设施分别显示修正分量，不与地图上实际设施总数混算。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。 |
| [military_industrial_organization_funds_gain](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3370>)<br>军工机构经费获取 | 7 | 13 | 用户指定加入国家面向设计商的通用管理修正：五类聘用费用及军工机构经费获取；有国家精神来源。；条件：只读国家持有的费用/经费修正，不读取具体MIO、装备或生产线对象；旧设计商机制受DLC分支影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:3010>) |
| [naval_manufacturer_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>海军设计商花费 | 3 | 7 | 用户指定加入国家面向设计商的通用管理修正：五类聘用费用及军工机构经费获取；有国家精神来源。；条件：只读国家持有的费用/经费修正，不读取具体MIO、装备或生产线对象；旧设计商机制受DLC分支影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:3034>) |
| [navy_weather_penalty](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4188>)<br>恶劣天气惩罚（海军） | 0 | 1 | 用户指定保留国家持有的海军恶劣天气惩罚修正。；条件：与空军天气惩罚分列，不加入实际海域天气惩罚值。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/australia_taog.txt:12366>) |
| [neutrality_acceptance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1304>)<br>中立主义外交接纳度 | 11 | 9 | 用户指定展示原版四种意识形态的外交接纳度；本轮覆盖旧的外交接受倾向排除规则。；条件：按对方意识形态分列，不汇总为一个外交接纳度；接纳度不等于外交行动成功概率。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:267>) |
| [tank_manufacturer_cost_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1296>)<br>坦克设计商花费 | 9 | 13 | 用户指定加入国家面向设计商的通用管理修正：五类聘用费用及军工机构经费获取；有国家精神来源。；条件：只读国家持有的费用/经费修正，不读取具体MIO、装备或生产线对象；旧设计商机制受DLC分支影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:3034>) |
| [training_time_army](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5039>)<br>陆军师训练时间（基础项） | 0 | 0 | 用户指定展示陆军师训练时间；保留已有比例项，补入已注册的基础项读取候选。；条件：基础项与比例项分列，不直接相加；基础项本次未检出定义赋值，单位与读取须实测。；注意：按用户指定加入展示候选；未检出可信国策/国家精神来源，国家读取与实际刷新仍待实测。；本次原版扫描未检出定义赋值；不能将仅注册解释为当前国家必有非零值，也不能将修正分量当作最终上限。 |
| [winter_attrition](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5155>)<br>冬季损耗（基础项） | 1 | 1 | 用户指定恢复天气损耗词条，仅纳入国家持有分量的展示候选，不累计地图天气对象的数值。；条件：冬季损耗基础项与_factor比例项分列，不直接相加；炎热损耗只纳入有国家来源的比例项，基础项仅检出地方天气来源。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/hungary.txt:845>) |
| [winter_attrition_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5160>)<br>冬季损耗（比例项） | 12 | 8 | 用户指定恢复天气损耗词条，仅纳入国家持有分量的展示候选，不累计地图天气对象的数值。；条件：冬季损耗基础项与_factor比例项分列，不直接相加；炎热损耗只纳入有国家来源的比例项，基础项仅检出地方天气来源。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/czechoslovakia.txt:1322>) |

## 从原展示库移出

| 修正键／名称 | 国家精神定义 | 国策关联 | 分类理由及条件 |
|---|---:|---:|---|
| [additional_brigade_column_size](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1407>)<br>名称待核验 | 0 | 0 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/doctrines/grand_doctrines/land_grand_doctrines.txt:78>) |
| [air_maximum_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1622>)<br>名称待核验 | 1 | 0 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/SOV.txt:402>) |
| [air_strategic_bomber_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1662>)<br>名称待核验 | 0 | 0 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/country_leader/00_traits.txt:16437>) |
| [air_strategic_bomber_night_penalty](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1667>)<br>名称待核验 | 1 | 2 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；条件：夜间；全国相应作战行为；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/GER.txt:2176>) |
| [amphibious_invasion_defence](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1737>)<br>名称待核验 | 1 | 1 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/bulgaria.txt:1056>) |
| [army_strength_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1977>)<br>名称待核验 | 11 | 11 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj_goe.txt:37>) |
| [civil_war_involvement_tension](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2197>)<br>介入内战造成紧张度 | 0 | 0 | 用户在本轮明确指定不加入BUFF统计，覆盖此前B档推荐。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/bop/ITA.txt:793>) |
| [control_trade_mission_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2292>)<br>控制贸易任务成果 | 0 | 0 | 用户在本轮明确指定不加入BUFF统计，覆盖此前B档推荐。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt:367>) |
| [critical_receive_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2343>)<br>名称待核验 | 4 | 2 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/SOV.txt:334>) |
| [diplomatic_pressure_mission_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2408>)<br>外交施压任务成果 | 0 | 0 | 用户在本轮明确指定不加入BUFF统计，覆盖此前B档推荐。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/country_leader/00_traits.txt:7995>) |
| [enemy_operative_recruitment_chance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2538>)<br>敌国国籍特工招募几率 | 0 | 0 | 用户在本轮明确指定不加入BUFF统计，覆盖此前B档推荐。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt:297>) |
| [fighter_sortie_efficiency](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2777>)<br>名称待核验 | 4 | 4 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/denmark.txt:422>) |
| [foreign_subversive_activites](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2802>)<br>名称待核验 | 36 | 40 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/australia.txt:1637>) |
| [generate_wargoal_tension](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2842>)<br>名称待核验 | 36 | 34 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/aussa.txt:357>) |
| [invasion_preparation](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2982>)<br>名称待核验 | 4 | 23 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/bulgaria.txt:1056>) |
| [naval_attrition](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3748>)<br>名称待核验 | 2 | 1 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/denmark.txt:254>) |
| [naval_invasion_planning_bonus_speed](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3863>)<br>名称待核验 | 2 | 2 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/british_raj.txt:495>) |
| [naval_invasion_prep_days](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3868>)<br>名称待核验 | 0 | 0 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/doctrines/subdoctrines/special_forces/special_forces_subdoctrines.txt:367>) |
| [navy_carrier_air_agility_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4043>)<br>名称待核验 | 2 | 4 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/denmark.txt:422>) |
| [navy_carrier_air_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4048>)<br>名称待核验 | 2 | 2 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/denmark.txt:422>) |
| [navy_carrier_air_targetting_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4053>)<br>名称待核验 | 2 | 2 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/denmark.txt:422>) |
| [navy_visibility](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4183>)<br>名称待核验 | 0 | 5 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/soviet.txt:3321>) |
| [request_lease_tension](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4580>)<br>名称待核验 | 4 | 4 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/czechoslovakia.txt:306>) |
| [resistance_damage_to_garrison_on_our_occupied_states](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4615>)<br>名称待核验 | 10 | 13 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；条件：相应占领地区；只取国家持有分量；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/czechoslovakia.txt:2792>) |
| [river_crossing_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4665>)<br>名称待核验 | 1 | 2 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/paraguay_uruguay_shared_ideas.txt:237>) |
| [ships_at_battle_start](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4730>)<br>名称待核验 | 2 | 13 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/siam.txt:1412>) |
| [starting_compliance](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4840>)<br>名称待核验 | 2 | 1 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；条件：相应占领地区；只取国家持有分量；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/czechoslovakia.txt:1139>) |
| [strategic_bomb_visibility](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4931>)<br>名称待核验 | 1 | 10 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/GER.txt:2176>) |
| [strike_force_movement_org_loss](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4936>)<br>名称待核验 | 0 | 11 | 当前目录无已确认显示名称，按用户要求不进入BUFF展示；原始注册键与来源只保留在审计目录。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/italy.txt:4304>) |

## 本轮明确要求且已在展示库的项目

| 修正键／名称 | 国家精神定义 | 国策关联 | 分类理由及条件 |
|---|---:|---:|---|
| [attrition](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2002>)<br>陆军师损耗 | 32 | 46 | 用户指定展示陆军师损耗，使用已有国家来源的全局attrition；同名attrition_for_controller的州/地方对象值仍排除。；条件：只读国家attrition，不将州或具体部队实际损耗混入。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/argentina.txt:388>) |
| [production_speed_arms_factory_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>军用工厂建设速度 | 168 | 205 | 用户确认保留四种设施的国家建设速度；这些词条已在A档，无需重复新增，同名state_版本仍排除。；条件：全国修正分量，不含某州的建设速度、地形或建筑槽位影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:426>) |
| [production_speed_dockyard_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>海军船坞建设速度 | 77 | 96 | 用户确认保留四种设施的国家建设速度；这些词条已在A档，无需重复新增，同名state_版本仍排除。；条件：全国修正分量，不含某州的建设速度、地形或建筑槽位影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:282>) |
| [production_speed_industrial_complex_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>民用工厂建设速度 | 160 | 247 | 用户确认保留四种设施的国家建设速度；这些词条已在A档，无需重复新增，同名state_版本仍排除。；条件：全国修正分量，不含某州的建设速度、地形或建筑槽位影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:1043>) |
| [production_speed_infrastructure_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4484>)<br>基础设施建设速度 | 93 | 168 | 用户确认保留四种设施的国家建设速度；这些词条已在A档，无需重复新增，同名state_版本仍排除。；条件：全国修正分量，不含某州的建设速度、地形或建筑槽位影响。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:282>) |
| [surrender_limit](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4981>)<br>投降界限 | 37 | 31 | 用户指定展示投降界限，保留常规项并补入有国家精神来源的强制投降阈值项。；条件：常规surrender_limit与forced_surrender_limit分列，后者标注强制阈值；不能相加或互相替代。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/belgium.txt:122>) |
| [training_time_army_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:5044>)<br>陆军师训练时间（比例项） | 26 | 25 | 用户指定展示陆军师训练时间；保留已有比例项，补入已注册的基础项读取候选。；条件：基础项与比例项分列，不直接相加；基础项本次未检出定义赋值，单位与读取须实测。；[来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/afghanistan.txt:426>) |

完整结果：[A档](A-focus-spirit-required.md) · [B档](B-other-global-required.md) · [C档审计](C-not-displayed.md) · [离线检索](catalog.html)。规则：[用户覆盖文件](../../tools/global_buff_user_overrides.json)；设计商取证：[候选审查](../../tools/user_revision_designer_candidates.json)；修订前名单：[快照](data/before-user-revision-2026-10-25.json)。
