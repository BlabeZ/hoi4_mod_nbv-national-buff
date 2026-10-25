# 国家全局范围与统计方法

本轮按用户确认保留国家持有的地区条件加成，只排除州／地方对象自身分量。2026-10-25的新要求覆盖此前天气、设计商和外交接纳度的整类排除：指定的天气相关国家分量、四种主义接纳度、六项设计商费用/经费纳入；无已确认名称项一律不展示。

领袖、法案／法律、顾问授予国家的修正与国策、民族精神等国家来源同样统计；只排除领袖本人技能和仅作用于其麾下单位的局部分量。运行页面只读取当前玩家国家，切换tag时重新绑定并刷新；不按来源类别扣掉国家合计。

当前有效规则：[用户覆盖规则](../../tools/global_buff_user_overrides.json)。[旧人工策略](../../tools/global_buff_review_policy.json)和[旧范围取证](../../tools/global_buff_scope_notes.json)保留为历史依据，冲突处以本轮覆盖规则为准。[本轮调整清单](user-revision-2026-10-25.md)逐项列出选择与同名边界。

## storage_not_directory

按存储对象和父块判定，不按文件夹、key前缀或engine_categories单独判定。

- [country的modifier：a modifier stored in country scope](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:496>)
- [state的modifier：该state中存储的值，例123.modifier@local_manpower](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1136>)
- [unit_leader的leader_modifier](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1230>)
- [unit_leader的unit_modifier，示例unit_modifier@army_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1379>)

## no_idea_is_not_exclusion

没有common/ideas国家精神定义不是排除条件；科技、学说和情报升级等可提供国家持有修正。零静态定义也只表示此次扫描无命中，不能单独证明不可读或无用。

- [科技antiair2顶层static_anti_air_damage_factor=0.1](<E:/Steam/steamapps/common/Hearts of Iron IV/common/technologies/artillery.txt:811>)
- [升级level.modifier同时提供crypto_strength=1与decryption_power=25](<E:/Steam/steamapps/common/Hearts of Iron IV/common/intelligence_agency_upgrades/intelligence_agency_upgrades.txt:419>)
- [学说奖励naval_invasion_plan_cap=2](<E:/Steam/steamapps/common/Hearts of Iron IV/common/doctrines/subdoctrines/special_forces/special_forces_subdoctrines.txt:285>)

## idea_is_not_sufficient

出现在国家idea文件仍不足以作为ROOT.modifier@候选：必须区分modifier、targeted_modifier、equipment_bonus及其他带对象的嵌套载荷。

- [同一idea的普通modifier含war_support_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/japan.txt:527>)
- [同一idea的targeted_modifier指定tag=MAN后才设attack_bonus_against和defense_bonus_against](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/japan.txt:531>)
- [equipment_bonus按small_plane_cas_airframe/medium_plane_airframe设置build_cost_ic](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/japan.txt:1362>)
- [equipment_bonus按convoy_1设置build_cost_ic=-0.15](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/japan.txt:4619>)

## country_army_air_navy

国家持有的army/air/navy系数可作为ROOT.modifier@候选；不能因engine_categories只有army/air/naval就排除，也不能将同key的王牌、领袖、地形等局部分量并入国家读数。

- [army_attack_factor分类army, aggressive；分类不是严格country读取白名单](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1797>)
- [普通国家idea.modifier含air_agility_factor与air_attack_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/siam.txt:1600>)
- [普通海军精神modifier含navy_visibility=-0.05](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/navy_spirits.txt:492>)
- [concealment_expert海军领袖特质modifier也使用navy_visibility=-0.1](<E:/Steam/steamapps/common/Hearts of Iron IV/common/unit_leader/00_traits.txt:2155>)
- [sub_unit_modifiers.destroyer也使用navy_visibility=-0.1](<E:/Steam/steamapps/common/Hearts of Iron IV/common/unit_leader/00_traits.txt:2258>)
- [王牌effect使用air_attack_factor，属于额外局部来源](<E:/Steam/steamapps/common/Hearts of Iron IV/common/aces/00_aces.txt:9>)

## core_noncore_are_retained

保留国家持有的核心、非核心、宣称、敌国等级等条件系数；名称中有地区条件不等于该值存储于州。展示时保留条件标签，不能标成所有战斗统一生效。

- [同一普通国家modifier并列army_core_attack_factor、army_core_defence_factor与army_defence_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/GER.txt:2168>)
- [普通国家modifier并列核心攻防与稳定/战争支持](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/GER.txt:3783>)

## local_does_not_always_mean_state_only

local_resources_factor保留国家分量，不能用local_前缀或state类别一刀切。具体州最终资源、州附加值与占领法造成的各州最终收益不纳入国家数值表。

- [国家idea ARG_resource_extration_focus普通modifier设置local_resources_factor=0.15](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/argentina.txt:250>)
- [local_resources_factor标签为state,war_production，但原版国家idea仍使用](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3230>)
- [sultana国家领袖特质compliance_gain=0.01](<E:/Steam/steamapps/common/Hearts of Iron IV/common/country_leader/00_traits.txt:3161>)
- [compliance_gain标签同时含country,state](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2257>)
- [读取特定州分量应进入state scope，不可与国家分量混称](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1136>)

## target_country_needs_target

targeted_modifier必须保留目标国家维度；attack_bonus_against/defense_bonus_against不能用无目标的单行国家总值表示“对全部国家加成”。本轮应移出普通全局表，留给未来目标国家详情。

- [tag=MAN，attack_bonus_against=0.15、defense_bonus_against=0.1](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/japan.txt:531>)
- [tag=JAP.JAP_first_strike_principle_target_1，运行时目标国变量](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/japan.txt:4762>)
- [公开country.modifier说明没有按目标国家聚合或选择参数](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:496>)

## same_name_different_storage

max_organisation等同名属性需逐父块审计，不能按裸key总频次直接升级为国家BUFF。装备设计统计中的armor_value/soft_attack/build_cost_ic等也不是ROOT的同名最终值。

- [category_special_forces中max_organisation=5，与soft_attack并列，是兵种属性奖励](<E:/Steam/steamapps/common/Hearts of Iron IV/common/doctrines/subdoctrines/special_forces/special_forces_subdoctrines.txt:58>)
- [max_organisation在修正注册文档中同时列为naval](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3310>)
- [STAT_COMMON_MAX_ORG及其说明是单位组织度属性](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/english/stats_l_english.yml:12>)
- [equipment_bonus含armor_value/defense/build_cost_ic](<E:/Steam/steamapps/common/Hearts of Iron IV/common/military_industrial_organization/organizations/00_generic_organization.txt:130>)

## ai_and_boolean

AI行为权重移出玩家BUFF数值表；Boolean不按百分比统计，可另做规则状态徽章。它们即使可读也不等于适合统计页，且排除理由不是没有国家来源。

- [ai_desired_divisions_factor分类ai](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1427>)
- [dictator国家领袖特质确实可带ai_desired_divisions_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/common/country_leader/00_traits.txt:50>)
- [can_guarantee_other_ideologies为Boolean且分类country](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2107>)
- [cannot_retreat_while_attacking为Boolean](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2117>)

## 设计商与MIO的实现边界

五类设计商/工业企业聘用费用、国家持有的军工机构经费获取纳入；具体MIO、装备、模块、单位、生产线对象属性继续排除。军工机构研究加成按本次“不包括科技修正”继续排除，普通国家科研修正不受此限定影响。七项当前目录无已确认名称的MIO管理键仍不展示；原版存在候选本地化标签不等于本目录已确认对应映射，本轮不以猜测补名绕过隐藏规则。

国家ROOT.modifier@只读取该国家存储的合计，没有按来源扣除的现成参数。如果工业企业的普通国家modifier已经汇入同一国家总值，不能据“排除对象局部值”声称已从总量扣除该来源。纳入设计商国家管理修正也不等于把具体机构的局部值加入国家总值。

- [equipment_bonus说明：trait解锁且MIO分配给装备变体](<E:/Steam/steamapps/common/Hearts of Iron IV/common/military_industrial_organization/organizations/_documentation.md:156>)
- [production_bonus说明：trait解锁且MIO分配给生产线](<E:/Steam/steamapps/common/Hearts of Iron IV/common/military_industrial_organization/organizations/_documentation.md:162>)
- [organization_modifier说明：作用在组织本身](<E:/Steam/steamapps/common/Hearts of Iron IV/common/military_industrial_organization/organizations/_documentation.md:169>)
- [policy bonuses only applies to equipment variant or production line assigned](<E:/Steam/steamapps/common/Hearts of Iron IV/common/military_industrial_organization/policies/_documentation.md:4>)
- [MIO也有独立modifier动态变量](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1066>)
- [工业企业类别industrial_concern](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/argentina.txt:1297>)
- [ARG央行工业企业的普通modifier包含consumer_goods_factor=-0.05](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/argentina.txt:1325>)
- [country.modifier只描述国家存储值，没有来源过滤参数](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:496>)

## 来源追踪的覆盖边界

- 统计的是本机原版静态可达/定义证据，不代表所有分支同局同时生效或当前国家数值。
- ideas.country仅作为国家精神定义；hidden_ideas独立列出；法律、顾问、设计商、军种spirit等其他组不混入。
- 国家精神直属modifier与equipment_bonus、targeted_modifier、state/unit等嵌套载荷分别统计。
- dynamic_modifiers可应用于国家/地区/单位将领/特殊项目，common/modifiers还包含天气战斗等静态机制，定义文件不等于国家作用域。
- 国策从completion_reward、completion_reward_joint_originator、completion_reward_joint_member、select_effect追踪静态对象引用。联合国策两入口按CWTools规则root=this=country。
- 仅展开无参数块的scripted_effect调用，最多16层；同一国策到同一定义保留第一条可达调用链，不把多次路径数作为触发次数。
- 参数化效果、事件后续链、复杂变量/事件目标/数组表达式未求值；未命中不代表原版绝对从未间接使用。
- effect_tooltip仅用于显示，不执行；已从国策实际可达链中排除。精神on_add/on_remove/on_update回调未递归执行，定义位置单列。
- debug来源保留辅助证据但不进入主摘要。common/modifiers静态天气/战斗等对象仅凭定义不进入国策国家候选。
- focus_country_global_candidate_count与link_count均为对象引用链接数；unique_focus_count按candidate加direct来源的focus_uid去重，focus_ids为对应ID集合；不将多链接称为多个国策。
- 动态变量链只作精确裸变量名的文本数据依赖；同一国策可达应用另标记，未模拟变量作用域或证明本局激活。
- 直接赋值依赖完整第一轮definition分类，避免把set_variable等同名变量操作误计为修正定义。
- 多定义同名对象全部保留，不猜测引擎最终覆盖顺序；所有结果保留文件行号。

## 计数与推荐规则

国家精神直属定义、独立国策关联、动态变量弱链、全语料频次分别保留，不能相加作为“生效次数”。仅修改变量不等于直接授予同名修正；去掉民族精神也不记为新增BUFF。A/B/C覆盖原4484个键，不删除原全量目录。

国家来源与展示资格分开判断：排除对象局部载荷、无名称及用户指定项，再应用明确纳入需求和人工白名单。仅注册但无原版赋值的明确指定项可作为待验证候选；已知只在地方使用的同名项不以地方数值充当国家值。当前规则由旧人工策略与优先级更高的用户覆盖文件共同生成。

“国家持有”不等于“无条件生效”；核心领土、特定兵种、海军任务、占领治理等保留条件说明。当前只提出读取候选，所有数值仍须逐项校验单位、基值、叠加和刷新。不能从国家总量推导具体师、舰、飞机、州或装备的最终属性。

## 人工补齐的国家动态精神来源

### air_equipment_upgrade_xp_cost

埃塞俄比亚与意大利的国家历史文件在国家作用域添加工业动态民族精神；精神直属字段分别读取ETH_air_equipment_upgrade_xp_cost与ITA_military_industry_air_equipment_upgrade_xp_cost。ETH_adapt_and_improve和ITA_standardization等国策在同一国家奖励作用域直接改变这些变量，构成初始化—国家动态精神—国策变量修改的完整静态链，非跨作用域同名猜测。

- 各分支与DLC条件决定具体生效时机，不表示两国效果叠加到同一国家。
- [ETH_industrialization_dynamic_modifier定义，原版注释标明NATIONAL SPIRIT](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/bba_dynamic_modifiers.txt:220>)
- [air_equipment_upgrade_xp_cost读取ETH_air_equipment_upgrade_xp_cost](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/bba_dynamic_modifiers.txt:234>)
- [国家历史初始化添加ETH_industrialization_dynamic_modifier](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/ETH - Ethiopia.txt:75>)
- [国策ID ETH_adapt_and_improve](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/ethiopia.txt:1811>)
- [国家completion_reward将ETH_air_equipment_upgrade_xp_cost减少0.25](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/ethiopia.txt:1836>)
- [意大利工业动态精神读取ITA_military_industry_air_equipment_upgrade_xp_cost](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/bba_dynamic_modifiers.txt:416>)
- [意大利国家变量初始化为0](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/ITA - Italy.txt:220>)
- [同一国家添加ITA_military_industry_dynamic_modifier](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/ITA - Italy.txt:222>)
- [ITA_standardization的国家奖励将该变量增加0.25](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/italy.txt:5300>)
- [ITA_specialization继续修改同一国家变量](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/italy.txt:5357>)
- [ITA_multirole_aircraft继续修改同一国家变量](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/italy.txt:5546>)

### autonomy_gain_warscore

INS_dutch_east_indies是国家历史在Thunder at Our Gates条件下添加的国家动态精神，其直属autonomy_gain_warscore读取国家变量。国策INS_the_declaration_of_independence调用indonesia_form_other_indies_effect；该效果以create_dynamic_country创建国家并保存为INS_dutch_indonesia，因此随后向该event_target添加动态精神可确认为国家作用域，补足自动trace的unknown。

- 本机common/events/history对INS_dutch_east_indies_autonomy_gain_warscore的精确文本检索仅发现有效的初始0赋值；拟增加1.5的联合国策代码已全部注释。
- 因此可确认国家精神字段来源，不能声称该版本存在已确认的非零国策加成。归A若依据‘来源出现’成立；展示时宜隐藏零值或标为预留字段。
- [INS_dutch_east_indies定义；enable要求DLC与original_tag=INS](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:2>)
- [autonomy_gain_warscore直属字段读取INS_dutch_east_indies_autonomy_gain_warscore](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:23>)
- [国家变量初始化为0](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/INS - Indonesia.txt:131>)
- [DLC条件下向印度尼西亚国家添加动态精神](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/INS - Indonesia.txt:464>)
- [独立宣言国策在completion_reward内调用indonesia_form_other_indies_effect](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/indonesia.txt:560>)
- [create_dynamic_country证明新建对象为国家](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_effects/INS_scripted_effects.txt:781>)
- [将新建国家保存为INS_dutch_indonesia全局事件目标](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_effects/INS_scripted_effects.txt:786>)
- [在已证明为国家的event_target上添加INS_dutch_east_indies](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_effects/INS_scripted_effects.txt:842>)
- [增加1.5的代码前有#注释，不构成有效非零修改证据](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/indonesia_joint.txt:10311>)

### consumer_goods_expected_value

德国国家历史初始化GER_industrial_consumer_goods_expected_value并添加MEFO动态精神；MEFO及征服经济的直属consumer_goods_expected_value读取这一国家变量。GER_establish_the_reichswerke等国策在国家作用域检查已持有这两种精神后调用GER_add_mefo_bills_penalty，效果改变该同国变量。链路包含真实非零惩罚值0.1，可证明不是仅靠同名变量猜测。

- 变量修改具有消费品阈值与国家标记条件；来源证明不等于所有国策完成后都无条件产生同一数值。
- [MEFO动态精神的consumer_goods_expected_value读取国家变量](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/wuw_dynamic_modifiers.txt:491>)
- [征服经济动态精神读取同一国家变量](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/wuw_dynamic_modifiers.txt:528>)
- [GER_expected_consumer_goods_penalty初始化为0.1](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/GER - Germany.txt:190>)
- [德国国家变量GER_industrial_consumer_goods_expected_value初始化为0](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/GER - Germany.txt:221>)
- [德国国家历史添加MEFO动态精神](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/GER - Germany.txt:223>)
- [国策奖励检查国家已持有MEFO或征服经济精神](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/germany.txt:1825>)
- [同一国家作用域调用GER_add_mefo_bills_penalty](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/germany.txt:1829>)
- [惩罚效果定义，后续检查消费品变量阈值与国家标记](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_effects/GER_scripted_effects.txt:818>)
- [将国家动态精神读取变量增加GER_expected_consumer_goods_penalty，即0.1](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_effects/GER_scripted_effects.txt:829>)
- [国家事件将MEFO替换成征服经济动态精神](<E:/Steam/steamapps/common/Hearts of Iron IV/events/WUW_Germany.txt:66>)

### opinion_gain_monthly

SSB_saadabad_pact是向协定成员国家添加的动态民族精神。联合国策SSB_the_saadabad_pact在completion_reward_joint_originator入口初始化SSB_opinion_gain_monthly并添加该精神；加入协定的country_event及1939国家历史也有国家级添加证据。上一版自动扫描漏掉联合国策奖励入口，本次已将joint_originator/member入口补入主扫描；这里保留人工确认及零值路径证据。

- 本机common/events/history对SSB_opinion_gain_monthly的精确文本检索只发现联合国策及加入协定事件中的0初始化，未找到有效非零赋值或增减。
- 可确认国家动态精神字段存在，不能将其描述为已确认会产生非零月度关系收益；宜隐藏零值或标为预留字段。
- 主扫描已扩展原版实际存在的joint_originator/member奖励入口，但未扩展全部事件调用图。
- [SSB_saadabad_pact动态精神定义](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/GoE_dynamic_modifiers.txt:986>)
- [opinion_gain_monthly直属字段读取SSB_opinion_gain_monthly](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/GoE_dynamic_modifiers.txt:1012>)
- [联合国策ID SSB_the_saadabad_pact](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/goe_shared_saadabad_branch.txt:2>)
- [completion_reward_joint_originator奖励入口，作用于联合国策发起国](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/goe_shared_saadabad_branch.txt:136>)
- [发起国变量SSB_opinion_gain_monthly初始化为0](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/goe_shared_saadabad_branch.txt:161>)
- [向联合国策发起国添加SSB_saadabad_pact](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/goe_shared_saadabad_branch.txt:167>)
- [PER_imperial_events.200为country_event](<E:/Steam/steamapps/common/Hearts of Iron IV/events/GOE_Persia.txt:2070>)
- [加入协定事件将国家变量初始化为0](<E:/Steam/steamapps/common/Hearts of Iron IV/events/GOE_Persia.txt:2121>)
- [同一国家事件选项添加SSB_saadabad_pact](<E:/Steam/steamapps/common/Hearts of Iron IV/events/GOE_Persia.txt:2127>)
- [波斯1939国家历史分支添加协定动态精神](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/PER - Persia.txt:273>)

