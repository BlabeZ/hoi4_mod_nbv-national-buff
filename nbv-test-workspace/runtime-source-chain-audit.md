# 来源渲染链与旧式精神审计（0.1.8）

本次只读核查，不修改生产模组。结论：已接入的来源表没有在生成页面时丢条；不能据此确认所有原版民族精神均已接入。

## 已确认的渲染链

- `tools/build_mod.py:146` 的页面合计为 `ROOT.modifier@key`，独立于来源表，不按民族精神 ID、国家或 DLC 白名单求和。页面仍限于用户选定的 519 个展示指标（注册表 559 项）。
- `common/scripted_guis/nbv_scripted_gui.txt:21` 使用 `player_context`，动态行 `change_scope = no`，来源谓词在当前玩家国家上下文评估。动态来源中显式 BEL/global 输入是原版变量所在位置，持有判定仍在当前国家；不能把显式变量作用域误认为按国家漏扫。
- 9 张输入表合计 31,803 条非零绑定，与生成 `source-display-manifest.json` 身份多重集逐项一致。连续编号、唯一性、输入哈希均通过。不存在新增适配表忘记拼接入页面的问题。
- 重新运行独立静态检查得到 179/179 通过，报告为 `runtime-source-audit-static.json`。中英来源树覆盖全部 31,803 个叶节点；没有缺失、重复、循环或孤立函数；每层至多 8 个引用，最大分组深度为 3。
- 来源生成字符串最长 192 字符，名称没有按字符数截断的生成规则。常用三列、其他四列限制的是页面单行单元格数，不是来源数。引擎在大量同时生效来源下的最终屏幕高度/长提示可读性并未穷举测试。
- 临时民族精神和永久民族精神都通过 `has_idea` 持有判定，不因授予手段是 `add_ideas` 或 `add_timed_idea` 区分。不过并未全量测试所有临时精神到期生命周期。

## 确定存在的旧式 traits 民族精神缺口

以下本体均被 `source-bindings.json` 的 `trait_contribution_not_adapted` 排除。领袖表只判断当前领袖特质，顾问表只扫描角色顾问，因此这两个表都不能替代“持有这个民族精神”的条件。

| 民族精神 ID | 定义位置 | trait 对应已选择修正 | 当前来源绑定 |
| --- | --- | --- | --- |
| `george_v` | `common/ideas/britain.txt:4` | `popular_figurehead`：稳定度 +15% | 缺失 |
| `ENG_george_vi` | `common/ideas/britain.txt:85` | `popular_figurehead`：稳定度 +15% | 缺失 |
| `HOL_wilhelmina` | `common/ideas/netherlands.txt:96` | `popular_figurehead`：稳定度 +15% | 缺失 |
| `SWE_gustaf_v_idea` | `common/ideas/sweden.txt:4` | `SWE_former_autocrat`：政治点数 -10%、法西斯/中立接纳度各 +20、中立支持率 +0.01、指挥点增长 +15% | 缺失 |

这些不是仅孤立定义：`history/countries/ENG - Britain.txt:241,351`、`HOL - Holland.txt:122`、`SWE - Sweden.txt:43` 存在授予引用，英国后续事件也添加 `ENG_george_vi`。其总值仍由引擎接口读出；缺失结论针对当前来源接口。

## 旧式顾问路径需要另行确认

六类旧顾问（政治顾问、陆海空军部长、总参谋、理论家）的 `common/ideas` 定义共 984 个。按 **559 项全注册表**统计，977 个含非零直接/特质贡献，共 **1,471 个候选贡献**；按 **519 项当前页面**统计，则为 **832 个旧顾问定义、1,324 个候选贡献**。当前生成来源不存在对应的 `has_idea = 旧 ID` 条件。

这一统计证明适配路径缺失，不代表 977 个在当前版本全部可选或生效；其中包含遗留或条件定义，需要检查引擎可达性。不能简单认为新的 `common/characters` 顾问表已经覆盖：例如 `common/ideas/andalusia.txt` 存在 ADU 旧顾问，而 `common/characters/ADU.txt` 不存在。原版无旧式 `event_modifiers` 内容可补扫：`common/event_modifiers.txt`、`common/triggered_modifiers.txt`、`common/modifiers/01_event_modifiers.txt` 在本机均为空文件。

## 现有引擎测试边界

- 动态来源实际逐绑定测试 3,936 项并通过，但另有 309 项未配置同类 fixture：223 项条件启用、86 项外部国家/全局输入。这些是测试未覆盖，不等同于生产未接入。
- 另有 51 阶段动态生命周期、9 阶段条件/错误国家检查；不能从抽样生命周期推导所有国家所有时点均无遗漏。
- 基础来源直接回归 4 组，扩展来源 16 组，以及 0.1.8 苏联与状态等新增回归。不存在逐个全量民族精神真实授予、移除的引擎测试。
- `ui_interaction_verified = false`、`cross_tag_tested = false`：真实鼠标界面及控制台 tag 切换未验证；已有错误 ROOT 的事件探针不能取代完整交互测试。
- 当前总值接口不会因名称不在来源表而少加，但没有被用户列入 519 项的指标本来就不展示；来源明细也有上游策略排除和适配缺口。两者必须分开说明。

机器可复核数据：`runtime-source-chain-audit.json`；读取脚本：`audit_runtime_source_chain.py`；本轮重跑静态报告：`runtime-source-audit-static.json`。
