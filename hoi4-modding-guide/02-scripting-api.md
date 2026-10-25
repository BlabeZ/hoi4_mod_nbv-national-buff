# 02 脚本接口与查阅方法

HOI4 的常规模组接口是一组引擎解释的数据和脚本入口。`common/defines/` 的配置与 Lua 文件另有用途，不能据此把事件、国策代码当成 Lua；其他 Paradox 游戏的新语法也不能未经验证直接移植。[脚本结构说明](https://hoi4.paradoxwikis.com/Modding#Code_structure)

## 1. 六类最重要的接口

| 类别 | 回答的问题 | 例子 | 常见位置 |
|---|---|---|---|
| Scope 作用域 | 对谁检查/修改？ | 国家、州、人物；`capital_scope`、`owner` | 条件块、效果块中的作用域切换 |
| Trigger 条件 | 是否满足？ | `has_war = no`、`has_country_flag = h4guide_done` | `trigger`、`available`、`limit` |
| Effect 效果 | 立即发生什么？ | `add_political_power = 25`、`add_ideas = h4guide_spirit` | 事件选项、国策奖励、决议效果 |
| Modifier 修正 | 持续改变哪个数值？ | `political_power_gain = 0.10` | idea 的 `modifier` 等 |
| On action 钩子 | 在哪个引擎时机运行？ | `on_startup`、`on_daily`、`on_capitulation` | `common/on_actions/` |
| 数据定义 | 创建何种游戏对象？ | `country_event`、`focus_tree`、`characters` | 对应 `events/`、`common/` 等目录 |

依据：[Wiki 概念区分](https://hoi4.paradoxwikis.com/Modding#Code_structure)、[作用域规则](references/cwtools-hoi4-config/Config/scopes.cwt)、[钩子规则](references/cwtools-hoi4-config/Config/on_actions.cwt)。

把 `add_political_power` 放进 `trigger` 不会变成“政治点数条件”；把 `political_power_gain` 直接当事件效果也不是同一用途。字段是否合法取决于它所在的块和当前作用域。

## 2. 作用域优先于命令名称

`THIS` 表示当前对象；`ROOT` 表示当前脚本上下文的根对象；`PREV` 跟踪作用域切换的前一层；`FROM` 的含义由事件或钩子的调用上下文决定。不要把 `ROOT` 固定理解成玩家，也不要把 `FROM` 固定理解成敌国。具体入口要检查其作用域约定。[Wiki 导航：Scopes](https://hoi4.paradoxwikis.com/Scopes)、[本地 scope 规则](references/cwtools-hoi4-config/Config/scopes.cwt)

**在 country 作用域内**，可以这样理解一次切换：

```text
capital_scope = {
    # THIS is now a state.
    owner = {
        # THIS is now the owner country of that state.
        add_political_power = 25
    }
}
```

`capital_scope` 的输出是州，`owner` 的输出是国家；返回国家作用域后才使用国家效果。示例只是说明作用域，并不承诺任意上下文都有有效的首都或所有者。[链接定义](references/cwtools-hoi4-config/Config/links.cwt)

典型陷阱：`on_startup` 在本次规则快照中初始作用域是 invalid，而 `on_daily` 是 country。不能不看定义就把需要国家作用域的奖励直接塞进所有钩子。[on_actions.cwt](references/cwtools-hoi4-config/Config/on_actions.cwt)

## 3. 条件和执行块

```text
if = {
    limit = {
        has_war = no
        NOT = { has_country_flag = h4guide_rewarded }
    }
    add_political_power = 25
    set_country_flag = h4guide_rewarded
}
```

这里 `limit` 包含条件，后面的两行是效果。`if` 本身必须位于允许效果的地方，例如事件 `option`。需要替代分支时查阅 `else_if` / `else` 对应规则；复杂条件用显式 `AND`、`OR`、`NOT` 表达，避免照搬其他游戏的逻辑关键字。

检查参数时至少记录：名称、允许作用域、参数类型、可选字段、数值单位、游戏版本、产生的副作用、重复调用是否安全。不要因为字段是浮点数就推断 `5` 代表 5%：上游生成文档也可能留下简化或过时示例。

依据：[效果规则](references/cwtools-hoi4-config/Config/effects.cwt)、[条件规则](references/cwtools-hoi4-config/Config/triggers.cwt)。

## 4. 复用、自定义状态与钩子

| 需求 | 机制 | 约定 |
|---|---|---|
| 多处复用一段效果 | `common/scripted_effects/` | 用项目名前缀，注明要求的作用域 |
| 多处复用一组条件 | `common/scripted_triggers/` | 条件命名体现含义，避免把效果写入条件 |
| 记住一次性状态 | country/state/global 等 flag | 状态属于哪个对象要明确；设定、检查、清除应一致 |
| 计数与计算 | variables / temporary variables | 区分对象范围和存活期，显式初始化 |
| 保存多个值 | arrays / 新版本 collections | 先确认目标版本支持；旧教程和新语法不能混用 |
| 定期或系统时机执行 | on_actions | 查清 ROOT/FROM/THIS；优先短条件过滤，避免频繁全世界扫描 |

保存变量、事件目标和集合的能力不等于普通编程语言中的任意对象指针；参考 [variables.cwt](references/cwtools-hoi4-config/Config/variables.cwt)、[arrays.cwt](references/cwtools-hoi4-config/Config/arrays.cwt)、[进阶文档](references/api/advanced.md)。这些进阶接口的最低游戏版本本次未逐项确认。

可复用逻辑的定义格式见 [scripted_effects_locs_and_triggers.cwt](references/cwtools-hoi4-config/Config/common/scripted_effects_locs_and_triggers.cwt)，完整小示例在 [03 入门](03-first-mod.md)。

## 5. 怎样查“接口手册”

1. **确认目标版本**。优先检查游戏安装目录里的 `documentation/`；常见文件有 `effects_documentation.html` / `.md` 和 `triggers_documentation.html` / `.md`，以实际安装内容为准。本次没有读取本机游戏文档。[工具维护者的路径说明](https://github.com/Anatoli27149/hoi4-ai-modding-kit/blob/main/docs/setup.md)
2. **查用途和例子**。Wiki 的 [Effect](https://hoi4.paradoxwikis.com/Effect)、[Triggers](https://hoi4.paradoxwikis.com/Triggers)、[Modifiers](https://hoi4.paradoxwikis.com/Modifiers) 是常用导航，本次这些专题正文受访问限制。
3. **离线查字段与作用域**。本包保存了 [effects](references/api/effects.md)、[triggers](references/api/triggers.md)、[modifiers](references/api/modifiers.md) 及完整相关 CWT 文件。
4. **查当前原版使用方式**。在游戏目录搜索同名字段，观察它处于哪个顶层对象、作用域和 DLC 条件下。
5. **做最小运行实验**。日志无新增相关错误、对象确实变化、重复触发与存读档符合预期，才算对目标版本确认。

离线查询例子：

```powershell
rg -n '^## (country_event|add_political_power)$' references/api/effects.md
rg -n 'has_country_flag' references/cwtools-hoi4-config/Config -g 'triggers*.cwt'
rg -n 'on_startup|on_daily|on_capitulation' references/cwtools-hoi4-config/Config/on_actions.cwt
```

## 6. 如何读 CWT

以下是 **编辑器校验语言**，不是直接放入游戏的脚本：

```text
## scope = country
alias[effect:add_political_power] = variable_field
```

它表示 CWTools 规则认为此效果适用于 country，并接受其 `variable_field` 类型。`cardinality` 表示允许出现的数量，`push_scope` / `replace_scope` 描述作用域变化，`<event>` 等引用类型用于交叉检查对象是否存在。应打开整个块阅读，不能只复制首行。

上游明确记录了变量、数组、部分字符和原版校验的误报限制。**不要为消除编辑器红线随意修改已经验证正确的脚本。** 同时也不要因某字段不在 CWT 中就断言游戏不存在该字段。[上游说明](references/cwtools-hoi4-config/README.md)
