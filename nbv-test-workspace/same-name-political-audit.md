# 政治／工业／情报同名修正核查

核查原版 1.19.3.0 与本模组 559 键注册表。共 10 个同名组、11 个此前未显示键。

其中 8 个是明确不同的全局词条（含本轮新增固定建筑位），2 个键的具体公式仍待验证，1 个仅属于州对象应继续排除。

| 页面 | 中文名 | 已显示键 | 此前遗漏键 | 判断 |
|---|---|---|---|---|
| 政治 | 可征募人口 | `conscription` | `conscription_factor` | 国家的征募人口比例乘数；conscription 是征募人口基础比例的直接增量。两者都显示百分号，但不能合并。 |
| 政治 | 可征募人口 | `conscription` | `recruitable_population_factor` | 州对象的可征募人口系数。注册类别只有 state；原版用于州动态修正、顺从度等。按用户排除州／地方对象规则继续排除，不能作为国家遗漏补入。 |
| 政治 | 志愿军陆军师数量上限 | `send_volunteer_size` | `send_volunteer_factor` | 志愿军可派遣师数的比例加成；已显示的 size 是额外师数固定值。实际原版赋值分别有 2.0 比例与 3 个师。精确取整顺序未做引擎测试。 |
| 政治 | 战争贡献度自治度增长 | `autonomy_gain_warscore` | `autonomy_gain_warscore_factor` | 两个独立已注册键，原版都在使用且都显示百分比；不能称为固定值／百分比配对。当前源码证据不足以确认两者在自治度增长计算中的相加／相乘顺序，需保留独立键并在接入前进一步验证。 |
| 政治 | 附属国人力要求 | `autonomy_manpower_share` | `autonomy_manpower_share_from_subjects` | 宗主国对附属国人力要求的修正，区别于附属国自身提供人力份额的修正。英文名称和描述不同，日方共荣圈与领袖使用 from_subjects，自治等级对附属国设置 share。两者均为比例。 |
| 政治 | 改善关系获得的评价 | `opinion_gain_monthly` | `opinion_gain_monthly_factor` | 改善关系获得评价的比例加成；已显示键为每月评价固定点数。原版分别赋值 -0.15 与 0.25，描述明确 factor 改善增长效率。 |
| 政治 | 相同意识形态每月评价 | `opinion_gain_monthly_same_ideology` | `opinion_gain_monthly_same_ideology_factor` | 相同意识形态每月评价的比例加成；已显示键为固定评价点。原版精确模板明确百分比，固定键在里宾特洛甫特质中赋值 5。 |
| 工业 | 地区最大工厂数 | `global_building_slots_factor` | `global_building_slots` | 所有州共享建筑位上限的固定数量加成；已显示键为百分比加成。原版精确模板分别 +=0 与 +=%1，实际 fixed 赋值含 2。 |
| 情报 | 加强抵抗组织效率 | `boost_resistance_factor` | `operation_boost_resistance_outcome` | 两个单独赋值的修正键，英文也区分 effectiveness 与 efficiency；但当前行动配置的 outcome_modifiers 显式列出 boost_resistance_factor，未列出 operation_boost_resistance_outcome。后者是否由引擎自动接入、是否与前者处于同一计算通道未验证，不能仅凭中文同名断言别名或已覆盖。 |
| 情报 | 解密 | `decryption` | `decryption_factor` | 旧式解密数值的比例加成；已显示键为解密等级／点数固定增量。基础科技为 decryption=1，且受未启用 La Resistance 条件限制；不是新版 decryption_power。 |
| 情报 | 加密 | `encryption` | `encryption_factor` | 旧式加密数值的比例加成；已显示键为加密等级／点数固定增量。基础科技为 encryption=1；不是新版密码强度系数。 |

## 原版证据

### conscription_factor

国家的征募人口比例乘数；conscription 是征募人口基础比例的直接增量。两者都显示百分号，但不能合并。

- [modifiers_l_english.yml:678](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:678>)
- [chile.txt:525](<E:\Steam\steamapps\common\Hearts of Iron IV\common\ideas\chile.txt:525>)
- [modifiers_documentation.md:2272](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:2272>)

### recruitable_population_factor

州对象的可征募人口系数。注册类别只有 state；原版用于州动态修正、顺从度等。按用户排除州／地方对象规则继续排除，不能作为国家遗漏补入。

- [modifiers_documentation.md:4552](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:4552>)
- [bba_dynamic_modifiers.txt:269](<E:\Steam\steamapps\common\Hearts of Iron IV\common\dynamic_modifiers\bba_dynamic_modifiers.txt:269>)
- [compliance_modifiers.txt:39](<E:\Steam\steamapps\common\Hearts of Iron IV\common\resistance_compliance_modifiers\compliance_modifiers.txt:39>)

### send_volunteer_factor

志愿军可派遣师数的比例加成；已显示的 size 是额外师数固定值。实际原版赋值分别有 2.0 比例与 3 个师。精确取整顺序未做引擎测试。

- [modifiers_l_english.yml:731](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:731>)
- [taog_traits.txt:272](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\taog_traits.txt:272>)
- [taog_traits.txt:478](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\taog_traits.txt:478>)
- [modifiers_documentation.md:4715](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:4715>)

### autonomy_gain_warscore_factor

两个独立已注册键，原版都在使用且都显示百分比；不能称为固定值／百分比配对。当前源码证据不足以确认两者在自治度增长计算中的相加／相乘顺序，需保留独立键并在接入前进一步验证。

- [modifiers_documentation.md:2057](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:2057>)
- [modifiers_l_english.yml:922](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:922>)
- [modifiers_l_english.yml:1055](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:1055>)
- [00_traits.txt:13038](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\00_traits.txt:13038>)
- [faction_manifests.txt:565](<E:\Steam\steamapps\common\Hearts of Iron IV\common\factions\goals\faction_manifests.txt:565>)

### autonomy_manpower_share_from_subjects

宗主国对附属国人力要求的修正，区别于附属国自身提供人力份额的修正。英文名称和描述不同，日方共荣圈与领袖使用 from_subjects，自治等级对附属国设置 share。两者均为比例。

- [modifiers_l_english.yml:892](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:892>)
- [modifiers_l_english.yml:2605](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:2605>)
- [00_traits.txt:1552](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\00_traits.txt:1552>)
- [SEA_dynamic_modifiers.txt:441](<E:\Steam\steamapps\common\Hearts of Iron IV\common\dynamic_modifiers\SEA_dynamic_modifiers.txt:441>)
- [puppet.txt:17](<E:\Steam\steamapps\common\Hearts of Iron IV\common\autonomous_states\puppet.txt:17>)

### opinion_gain_monthly_factor

改善关系获得评价的比例加成；已显示键为每月评价固定点数。原版分别赋值 -0.15 与 0.25，描述明确 factor 改善增长效率。

- [modifiers_l_english.yml:426](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:426>)
- [modifiers_documentation.md:4268](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:4268>)
- [00_traits.txt:2634](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\00_traits.txt:2634>)
- [00_traits.txt:6070](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\00_traits.txt:6070>)

### opinion_gain_monthly_same_ideology_factor

相同意识形态每月评价的比例加成；已显示键为固定评价点。原版精确模板明确百分比，固定键在里宾特洛甫特质中赋值 5。

- [modifiers_l_english.yml:429](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:429>)
- [00_traits.txt:13377](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\00_traits.txt:13377>)
- [chile.txt:710](<E:\Steam\steamapps\common\Hearts of Iron IV\common\ideas\chile.txt:710>)

### global_building_slots

所有州共享建筑位上限的固定数量加成；已显示键为百分比加成。原版精确模板分别 +=0 与 +=%1，实际 fixed 赋值含 2。

- [modifiers_l_english.yml:9](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:9>)
- [british_raj_goe.txt:1873](<E:\Steam\steamapps\common\Hearts of Iron IV\common\ideas\british_raj_goe.txt:1873>)
- [modifiers_documentation.md:2852](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:2852>)

### operation_boost_resistance_outcome

两个单独赋值的修正键，英文也区分 effectiveness 与 efficiency；但当前行动配置的 outcome_modifiers 显式列出 boost_resistance_factor，未列出 operation_boost_resistance_outcome。后者是否由引擎自动接入、是否与前者处于同一计算通道未验证，不能仅凭中文同名断言别名或已覆盖。

- [modifiers_l_english.yml:1457](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:1457>)
- [modifiers_l_english.yml:1747](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:1747>)
- [00_traits.txt:6078](<E:\Steam\steamapps\common\Hearts of Iron IV\common\country_leader\00_traits.txt:6078>)
- [intelligence_agency_upgrades.txt:247](<E:\Steam\steamapps\common\Hearts of Iron IV\common\intelligence_agency_upgrades\intelligence_agency_upgrades.txt:247>)
- [00_operations.txt:1390](<E:\Steam\steamapps\common\Hearts of Iron IV\common\operations\00_operations.txt:1390>)

### decryption_factor

旧式解密数值的比例加成；已显示键为解密等级／点数固定增量。基础科技为 decryption=1，且受未启用 La Resistance 条件限制；不是新版 decryption_power。

- [modifiers_l_english.yml:651](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:651>)
- [electronic_mechanical_engineering.txt:857](<E:\Steam\steamapps\common\Hearts of Iron IV\common\technologies\electronic_mechanical_engineering.txt:857>)
- [modifiers_documentation.md:2358](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:2358>)

### encryption_factor

旧式加密数值的比例加成；已显示键为加密等级／点数固定增量。基础科技为 encryption=1；不是新版密码强度系数。

- [modifiers_l_english.yml:647](<E:\Steam\steamapps\common\Hearts of Iron IV\localisation\english\modifiers_l_english.yml:647>)
- [electronic_mechanical_engineering.txt:728](<E:\Steam\steamapps\common\Hearts of Iron IV\common\technologies\electronic_mechanical_engineering.txt:728>)
- [modifiers_documentation.md:2453](<E:\Steam\steamapps\common\Hearts of Iron IV\documentation\modifiers_documentation.md:2453>)

未修改生产文件；除用户明确要求的固定建筑位，其余不在本审计中自动增补。
