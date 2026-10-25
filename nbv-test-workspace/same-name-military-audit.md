# 军事页面同中文名遗漏复核

核查日期：2026-10-25。范围：当前原始 559 键登记表与页面同名去重记录，游戏 1.19.3.0。本轮只读核查，未更改页面。

共发现 12 组、12 个军事修正键因“同名保留首次绑定”未展示。5 组有原版精确模板确认固定值/百分比区别；海军组织度固定项另有原版 +5 赋值支持。其余独立键不能视作别名，但完整单位或计算层仍需核验。

本地发行文件不包含原生 C++ 计算代码。本轮没有运行战斗属性差分测试；源码中的注册键、赋值和本地化格式不等于最终引擎计算公式。以下明确区分可确认内容与待核实内容。

| 页面 | 同名 | 当前显示键 | 遗漏键 | 建议区分名称 |
|---|---|---|---|---|
| 陆军 | 陆军师组织度恢复速率 | `army_morale_factor` | `army_morale` | 陆军师组织度恢复速率（基础项，单位待核实） |
| 陆军 | 陆军师组织度 | `army_org_factor` | `army_org` | 陆军师组织度（固定值） |
| 陆军 | 陆军经验增长 | `experience_gain_army` | `experience_gain_army_factor` | 陆军经验增长（百分比） |
| 陆军 | 堑壕上限 | `max_dig_in` | `max_dig_in_factor` | 堑壕上限（百分比） |
| 陆军 | 堑壕速度 | `dig_in_speed_factor` | `dig_in_speed` | 堑壕速度（基础项，单位待核实） |
| 陆军 | 骑兵攻击 | `cavalry_attack_factor` | `modifier_army_sub_unit_cavalry_attack_factor` | 骑兵攻击（骑兵营修正） |
| 陆军 | 骑兵防御 | `cavalry_defence_factor` | `modifier_army_sub_unit_cavalry_defence_factor` | 骑兵防御（骑兵营修正） |
| 海军 | 海军经验增长 | `experience_gain_navy` | `experience_gain_navy_factor` | 海军经验增长（百分比） |
| 海军 | 海军组织度 | `navy_org_factor` | `navy_org` | 海军组织度（固定值） |
| 海军 | 海军组织度恢复速率 | `naval_morale` | `naval_morale_factor` | 海军组织度恢复速率（百分比） |
| 空军 | 空军事故几率 | `air_accidents_factor` | `air_accidents` | 空军事故几率（基础项，单位待核实） |
| 空军 | 空军经验增长 | `experience_gain_air_factor` | `experience_gain_air` | 空军经验增长（固定值） |

## 陆军：陆军师组织度恢复速率

army_morale_factor 有精确百分比模板；army_morale 是独立注册键，原版大型部队战术分支奖励直接赋值 0.1。基础恢复率增量的具体计量和最终计算层尚未通过引擎差分确认，不能直接套用百分比。

已有国家来源候选绑定：1 条。该数量不是当前存档的生效来源数。

证据：

- [infantry_subdoctrines.txt:230](<E:/Steam/steamapps/common/Hearts of Iron IV/common/doctrines/subdoctrines/land/infantry_subdoctrines.txt:230>)：`army_morale = 0.1`
- [modifiers_l_simp_chinese.yml:297](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:297>)：`army_morale_factor_tt: " $MODIFIER_ARMY_MORALE_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_documentation.md:1932](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1932>)：`## army_morale_factor`
- [modifiers_documentation.md:1927](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1927>)：`## army_morale`

## 陆军：陆军师组织度

army_org_tt 明确使用未缩放数值 +=1，army_org_factor_tt 使用 +=%1。分别为固定组织度增量与比例加成；不能合并为一个读数。日本、法国、中共及暹罗国家精神使用固定项，澳大利亚国家动态精神也使用固定项。

已有国家来源候选绑定：5 条。该数量不是当前存档的生效来源数。

证据：

- [modifiers_l_simp_chinese.yml:284](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:284>)：`army_org_factor_tt: "$MODIFIER_ARMY_ORG_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_l_simp_chinese.yml:285](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:285>)：`army_org_tt: " $MODIFIER_ARMY_ORG$：$RIGHT|+=1$"`
- [comchina.txt:240](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/comchina.txt:240>)：`army_org = 5`
- [TAOG_dynamic_modifiers.txt:984](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/TAOG_dynamic_modifiers.txt:984>)：`army_org = AST_australian_military_forces_spirit_army_org`
- [modifiers_documentation.md:1952](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1952>)：`## army_org_factor`
- [modifiers_documentation.md:1947](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1947>)：`## army_org`

## 陆军：陆军经验增长

experience_gain_army_tt 使用 +=2 固定值模板，experience_gain_army_factor_tt 使用 +=%1 百分比模板。当前只显示固定值，比例加成漏展示。

已有国家来源候选绑定：148 条。该数量不是当前存档的生效来源数。

证据：

- [modifiers_l_simp_chinese.yml:253](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:253>)：`experience_gain_army_tt: "$MODIFIER_XP_GAIN_ARMY$：$RIGHT|+=2$"`
- [modifiers_l_simp_chinese.yml:255](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:255>)：`experience_gain_army_factor_tt: "$MODIFIER_XP_GAIN_ARMY_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_documentation.md:2647](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2647>)：`## experience_gain_army`
- [modifiers_documentation.md:2652](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2652>)：`## experience_gain_army_factor`

## 陆军：堑壕上限

max_dig_in_tt 为 +=1 固定堑壕增量，max_dig_in_factor_tt 为 +=%1 比例加成。当前显示固定项，比例项漏展示。

已有国家来源候选绑定：39 条。该数量不是当前存档的生效来源数。

证据：

- [modifiers_l_simp_chinese.yml:765](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:765>)：`max_dig_in_factor_tt: "$MODIFIER_MAX_DIG_IN_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_l_simp_chinese.yml:766](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:766>)：`max_dig_in_tt: "$MODIFIER_MAX_DIG_IN$：$RIGHT|+=1$"`
- [switzerland.txt:626](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/switzerland.txt:626>)：`max_dig_in_factor = 0.5`
- [modifiers_documentation.md:3285](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3285>)：`## max_dig_in`
- [modifiers_documentation.md:3290](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3290>)：`## max_dig_in_factor`

## 陆军：堑壕速度

两个键均独立注册且实际赋值。国家精神 SWI_spirit_of_helvetia_defensive_war 使用 dig_in_speed=0.3；领袖能力另有 6.0。dig_in_speed_factor 有百分比模板，但 dig_in_speed 的原版精确模板和计算层未确认。现有格式表按同名类比为百分比，不足以证明单位或两键等价。只列国家持有贡献，领袖能力的单位对象贡献仍排除。

已有国家来源候选绑定：1 条。该数量不是当前存档的生效来源数。

证据：

- [switzerland.txt:625](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/switzerland.txt:625>)：`dig_in_speed = 0.3`
- [generic_leader_abilities.txt:379](<E:/Steam/steamapps/common/Hearts of Iron IV/common/abilities/generic_leader_abilities.txt:379>)：`dig_in_speed = 6.0`
- [modifiers_l_simp_chinese.yml:343](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:343>)：`dig_in_speed_factor_tt: "$MODIFIER_DIG_IN_SPEED_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_documentation.md:2403](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2403>)：`## dig_in_speed_factor`
- [modifiers_documentation.md:2398](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2398>)：`## dig_in_speed`

## 陆军：骑兵攻击

与 cavalry_attack_factor 是两个独立注册键。unit_modifiers.txt 明确将长键注册为指定 sub_unit cavalry 的修正；短键为原生 cavalry 修正。两者都可由国家精神持有，前者已见军阀政府和意大利/阿富汗动态精神，不能因含 sub_unit 就当作单个单位对象排除。短键针对何种师分类、长键对营贡献如何聚合及二者叠加公式尚未做引擎战斗差分，不断言互为别名或给出完整公式。

已有国家来源候选绑定：11 条。该数量不是当前存档的生效来源数。

证据：

- [unit_modifiers.txt:1](<E:/Steam/steamapps/common/Hearts of Iron IV/common/units/unit_modifiers/unit_modifiers.txt:1>)：`#list all modifiers that will be used for specific sub unit or sub unit categories`
- [unit_modifiers.txt:23](<E:/Steam/steamapps/common/Hearts of Iron IV/common/units/unit_modifiers/unit_modifiers.txt:23>)：`modifier_army_sub_unit_cavalry_attack_factor`
- [china_warlord.txt:111](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/china_warlord.txt:111>)：`modifier_army_sub_unit_cavalry_attack_factor = 0.1`
- [poland.txt:1891](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/poland.txt:1891>)：`cavalry_attack_factor = 0.1`
- [bba_dynamic_modifiers.txt:440](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/bba_dynamic_modifiers.txt:440>)：`modifier_army_sub_unit_cavalry_attack_factor = ITA_re_modifier_army_sub_unit_cavalry_attack_factor #0.03`
- [modifiers_documentation.md:2162](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2162>)：`## cavalry_attack_factor`
- [modifiers_documentation.md:3530](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3530>)：`## modifier_army_sub_unit_cavalry_attack_factor`

## 陆军：骑兵防御

与 cavalry_defence_factor 是两个独立注册键。长键在 unit_modifiers.txt 明确注册为 sub_unit cavalry 防御；短键为原生 cavalry 防御。军阀政府及意大利/阿富汗动态精神对国家提供长键，不能用短键替代读取。准确战斗计算层仍待引擎差分，不能按同中文名合并。

已有国家来源候选绑定：11 条。该数量不是当前存档的生效来源数。

证据：

- [unit_modifiers.txt:4](<E:/Steam/steamapps/common/Hearts of Iron IV/common/units/unit_modifiers/unit_modifiers.txt:4>)：`# modifier_army_sub_unit_[sub_unit or sub_unit_category]_defence_factor`
- [unit_modifiers.txt:24](<E:/Steam/steamapps/common/Hearts of Iron IV/common/units/unit_modifiers/unit_modifiers.txt:24>)：`modifier_army_sub_unit_cavalry_defence_factor`
- [china_warlord.txt:110](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/china_warlord.txt:110>)：`modifier_army_sub_unit_cavalry_defence_factor = 0.05`
- [poland.txt:1892](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/poland.txt:1892>)：`cavalry_defence_factor = 0.1`
- [bba_dynamic_modifiers.txt:459](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/bba_dynamic_modifiers.txt:459>)：`modifier_army_sub_unit_cavalry_defence_factor = ITA_re_modifier_army_sub_unit_cavalry_defence_factor #0.05`
- [modifiers_documentation.md:2167](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2167>)：`## cavalry_defence_factor`
- [modifiers_documentation.md:3535](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3535>)：`## modifier_army_sub_unit_cavalry_defence_factor`

## 海军：海军经验增长

experience_gain_navy_tt 使用 +=2 固定值模板，experience_gain_navy_factor_tt 使用 +=%1 百分比模板。当前只显示固定值，比例加成漏展示。

已有国家来源候选绑定：113 条。该数量不是当前存档的生效来源数。

证据：

- [modifiers_l_simp_chinese.yml:257](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:257>)：`experience_gain_navy_tt: "$MODIFIER_XP_GAIN_NAVY$：$RIGHT|+=2$"`
- [modifiers_l_simp_chinese.yml:259](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:259>)：`experience_gain_navy_factor_tt: " $MODIFIER_XP_GAIN_NAVY_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_documentation.md:2672](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2672>)：`## experience_gain_navy`
- [modifiers_documentation.md:2677](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2677>)：`## experience_gain_navy_factor`

## 海军：海军组织度

中央军事委员会国家精神直接赋值 navy_org=5，原版 navy_org_factor 使用百分比模板。这强烈支持前者是未缩放固定组织度、后者为比例项；前者尚无精确 RIGHT 模板或本轮引擎差分，单位结论标为源码支持的推断。

已有国家来源候选绑定：1 条。该数量不是当前存档的生效来源数。

证据：

- [comchina.txt:243](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/comchina.txt:243>)：`navy_org = 5`
- [modifiers_l_simp_chinese.yml:286](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:286>)：`MODIFIER_NAVY_ORG: "海军组织度"`
- [modifiers_l_simp_chinese.yml:288](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:288>)：`navy_org_factor_tt: "$MODIFIER_NAVY_ORG_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_documentation.md:4133](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4133>)：`## navy_org_factor`
- [modifiers_documentation.md:4128](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4128>)：`## navy_org`

## 海军：海军组织度恢复速率

遗漏的 naval_morale_factor 有精确 +=%1 模板，是确定的百分比项。已显示 naval_morale 的单位却未确认：现有格式表引用 ITA_supermarina_rm_tt 的 MODIFIER_NAVAL_MORALE +10%，但实际国策修改 ITA_rm_naval_morale_factor，动态表写入 naval_morale_factor，不能据同名提示证明 naval_morale 的单位。比利时国家精神确实另用 naval_morale=0.15。应独立保留键并核实当前已显示项单位。

已有国家来源候选绑定：41 条。该数量不是当前存档的生效来源数。

证据：

- [modifiers_l_simp_chinese.yml:302](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:302>)：`naval_morale_factor_tt: " $MODIFIER_NAVAL_MORALE_FACTOR$：$RIGHT|+=%1$"`
- [belgium.txt:373](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/belgium.txt:373>)：`naval_morale = 0.15`
- [bba_focus_l_english.yml:1406](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/english/bba_focus_l_english.yml:1406>)：`ITA_supermarina_rm_tt: "$ITA_modify_regia_marina_dynamic_modifier_ns_intro$ \n$MODIFIER_NAVAL_MORALE$: §G+10.0%§! \n$MODIFIER_STRIKE_FORCE_MOVING_ORG$: §G-5.00%§! \n$MODIFIER_NAVAL_DOCTRINE_COST_FACTOR$: §G-10.00%§! \n\n"`
- [italy.txt:6276](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/italy.txt:6276>)：`add_to_variable = { ITA_rm_naval_morale_factor = 0.1 }`
- [bba_dynamic_modifiers.txt:1039](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/bba_dynamic_modifiers.txt:1039>)：`naval_morale_factor = ITA_rm_naval_morale_factor #0.1`
- [modifiers_documentation.md:3903](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3903>)：`## naval_morale`
- [modifiers_documentation.md:3908](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:3908>)：`## naval_morale_factor`

## 空军：空军事故几率

air_accidents_factor 有精确百分比模板。独立的 air_accidents 被暹罗国家精神气象广播赋值 -0.1，天气静态块也用该键；本页面只能读取国家持有部分。现有格式表援引 ETH_bring_in_foreign_advisors_tt 的 MODIFIER_AIR_ACCIDENTS -15%，但对应国策和动态表实际修改 air_accidents_factor。不能把该提示用来确认无 factor 项的单位、是否为百分点或二者计算层，更不能称两者是别名。

已有国家来源候选绑定：1 条。该数量不是当前存档的生效来源数。

证据：

- [modifiers_l_simp_chinese.yml:73](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:73>)：`air_accidents_factor_tt: "$MODIFIER_AIR_ACCIDENTS_FACTOR$：$RIGHT|-=%1$"`
- [siam.txt:1428](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideas/siam.txt:1428>)：`air_accidents = -0.1`
- [bba_focus_l_english.yml:116](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/english/bba_focus_l_english.yml:116>)：`ETH_bring_in_foreign_advisors_tt: "Modify §Y[GetEthiopianAirforceSpiritName]§! by:\n $MODIFIER_ENEMY_ARMY_BONUS_AIR_SUPERIORITY_FACTOR$: §G-5%§!\n $MODIFIER_AIR_DOCTRINE_COST_FACTOR$: §G-5%§!\n $MODIFIER_AIR_ACCIDENTS$: §G-15%§!  "`
- [ethiopia.txt:1218](<E:/Steam/steamapps/common/Hearts of Iron IV/common/national_focus/ethiopia.txt:1218>)：`add_to_variable = {	ETH_airforce_air_accidents_factor = -0.15 }`
- [bba_dynamic_modifiers.txt:180](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/bba_dynamic_modifiers.txt:180>)：`air_accidents_factor = ETH_airforce_air_accidents_factor`
- [modifiers_documentation.md:1497](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1497>)：`## air_accidents_factor`
- [modifiers_documentation.md:1492](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:1492>)：`## air_accidents`

## 空军：空军经验增长

experience_gain_air_tt 使用 +=2 固定值模板，experience_gain_air_factor_tt 使用 +=%1 百分比模板。当前只显示百分比，固定经验增量漏展示。

已有国家来源候选绑定：593 条。该数量不是当前存档的生效来源数。

证据：

- [modifiers_l_simp_chinese.yml:261](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:261>)：`experience_gain_air_tt: "$MODIFIER_XP_GAIN_AIR$：$RIGHT|+=2$"`
- [modifiers_l_simp_chinese.yml:263](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:263>)：`experience_gain_air_factor_tt: " $MODIFIER_XP_GAIN_AIR_FACTOR$：$RIGHT|+=%1$"`
- [modifiers_documentation.md:2642](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2642>)：`## experience_gain_air_factor`
- [modifiers_documentation.md:2637](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2637>)：`## experience_gain_air`

## 对现有格式表的两项警示

- `naval_morale` 的百分比推断引用了意大利提示，但实际赋值键是 `naval_morale_factor`，不能据此确认前者单位。
- `air_accidents` 的百分比推断引用了埃塞俄比亚提示，但实际赋值键是 `air_accidents_factor`，不能据此确认前者单位。

上述证据不足项已保留为待核实；没有将任何一组断言为别名，也没有未经确认批量补入页面。
