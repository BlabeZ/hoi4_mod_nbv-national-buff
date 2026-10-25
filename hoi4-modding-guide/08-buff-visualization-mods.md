# BUFF 数值可视化两个版本的源码分析

两个模组都通过动态本地化中的 `modifier@修正键` 读取引擎保存的国家修正值。普通版将结果写进原版决议分类说明；UI 版将指标编号映射成文本，在独立 Scripted GUI 中分五类展示。两者都使用人工维护的指标清单，不能视为自动发现所有 BUFF、拆解所有来源或计算最终战斗属性的系统。

分析日期：2026-10-24。以下对应本机已安装文件，核验方式为只读源码、模组自带预览图和原版随游戏文档对照，未启动游戏做运行测试。指标计数是本地化中的读取表达式统计，不代表逐项验证了引擎返回值。

## 名称与文件夹

| 项目 | 普通版 | UI 版 |
|---|---|---|
| 工坊名称 | [BUFF数值可视化](https://steamcommunity.com/sharedfiles/filedetails/?id=3440479297) | [BUFF数值可视化 UI 版本 buff display ui](https://steamcommunity.com/sharedfiles/filedetails/?id=3795966002) |
| 启动器描述符中的名称 | `BUFF数值可视化` | `buff display ui` |
| Workshop ID | `3440479297` | `3795966002` |
| 本机目录 | `E:\Steam\steamapps\workshop\content\394360\3440479297` | `E:\Steam\steamapps\workshop\content\394360\3795966002` |
| 描述符版本 | `1.0` | `1.0` |
| 声明的游戏支持版本 | `1.*` | `1.19.2.0` |

核心名称和 ID 可直接在 [普通版 descriptor.mod](E:/Steam/steamapps/workshop/content/394360/3440479297/descriptor.mod:5) 与 [UI 版 descriptor.mod](E:/Steam/steamapps/workshop/content/394360/3795966002/descriptor.mod:5) 中复核。启动器外部描述符 [ugc_3440479297.mod](<C:/Users/1/Documents/Paradox Interactive/Hearts of Iron IV/mod/ugc_3440479297.mod:7>)、[ugc_3795966002.mod](<C:/Users/1/Documents/Paradox Interactive/Hearts of Iron IV/mod/ugc_3795966002.mod:10>) 的 `path` 也分别指向这两个目录。

UI 版的 [desc.txt](E:/Steam/steamapps/workshop/content/394360/3795966002/desc.txt:1) 明确写明它是普通版的 UI 改版，入口是政治界面上方的议会图标。它自身包含显示逻辑和数据本地化，描述符没有将普通版列为依赖。描述符列有 `Modifier Icons CN ver.`，作者说明则推荐搭配图标模组并称可单独使用；图标资源不负责修正数值的计算。

## 修正数值从哪里来

普通版的本地化直接使用：

```text
[?This.modifier@political_power_gain|+]
[?This.modifier@political_power_factor|%0+]
[?This.modifier@army_attack_factor|%0+]
```

见 [we_l_simp_chinese.yml 第 4 行](E:/Steam/steamapps/workshop/content/394360/3440479297/localisation/simp_chinese/we_l_simp_chinese.yml:4)。UI 版同一类表达式使用显式的根国家作用域，例如 [BDUI_l_simp_chinese.yml 第 33 行](E:/Steam/steamapps/workshop/content/394360/3795966002/localisation/simp_chinese/BDUI_l_simp_chinese.yml:33)：

```text
FE_tool_show_buff_name_text_101: "$MODIFIERS_ARMY_ATTACK_FACTOR$: [?ROOT.modifier@army_attack_factor|+=0%]"
```

其中 `$MODIFIERS_ARMY_ATTACK_FACTOR$` 复用游戏的修正名称；`[?…]` 读取数值；竖线后的格式控制百分比、精度、符号和颜色。普通版的 `This` 来自决议国家，UI 版的 `ROOT` 来自 `player_context` 的玩家国家。两者都没有把 BUFF 数值复制进一个定期更新的统计缓存。

原版 [dynamic_variables_documentation.md 第 496 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:496>) 将国家作用域的 `modifier` 定义为该国家保存的修正值。因而实际数据链是：

```text
民族精神、动态修正、科技等来源对某项国家修正产生作用
  → 游戏引擎维护该国家的修正值
  → 本地化读取 country.modifier@指定键
  → 格式化为文字
  → 决议说明或 GUI 文本控件显示
```

模组自身没有逐个搜索民族精神、科技或国策并相加。一个来源只有作用于所读的国家修正项时，才会体现在该值中。例如，科技直接修改某种装备或营属性，不能据此认定其所有影响都会出现在一个国家 `modifier@` 数字里。

国家总修正也不能直接替代某个师在某场战斗中的最终攻击、防御或伤害。原版文档另行定义 [州 modifier](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1136>)、[leader_modifier](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1230>) 和 [unit_modifier](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:1379>)；这两个模组没有遍历这些对象来汇总装备、将领、州、地形、天气等全部影响，也没有展示每个来源的贡献。

## 全面覆盖到什么程度

按简体中文本地化逐个抽取 `modifier@...`，得到以下计数。英文 UI 文件的取值表达式与中文对应一致。

| 分类 | 普通版读取次数 | UI 版读取次数 | UI 版总显示槽 |
|---|---:|---:|---:|
| 政治和工业 | 16 | 16 | 21 |
| 陆军 | 31 | 33 | 33 |
| 海军 | 34 | 34 | 51 |
| 空军 | 19 | 19 | 21 |
| 情报 | 27 | 28 | 36 |
| 合计 | **127** | **130** | **162** |

普通版共有 **126 个不同修正键字符串**；UI 版共有 **128 个**。重复读取会使表达式数大于键数。UI 版剩余 32 个槽是 27 个空白和 5 个小标题，用来排版。空白槽并非“修正为零所以隐藏”，源码没有按零值过滤指标。

这些数量体现的是预设表的大小，并非引擎支持的修正总量。例如，本机原版文档中的 [工厂产出 industrial_capacity_factory](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2917>) 和 [科研速度 research_speed_factor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4600>) 就没有被两份显示表引用。大模组新增的自定义修正也不会自动成为新显示行。

完整读取键、格式、源码行号、UI 槽位及两版差集保存在 [机器可读核验记录](D:/projects/hoi4_mod/1/hoi4-modding-guide/references/buff-visualization-audit.json)。其中包含可疑键与错配项，不能把键数当作有效指标认证。

## 普通版如何显示

普通版只有三份功能文件：

| 文件 | 职责 |
|---|---|
| [common_dicision_categories.txt](E:/Steam/steamapps/workshop/content/394360/3440479297/common/decisions/categories/common_dicision_categories.txt:1) | 定义三个决议分类，检查是否展开海空军和情报 |
| [we_common.txt](E:/Steam/steamapps/workshop/content/394360/3440479297/common/decisions/we_common.txt:1) | 一条提示决议、两条显示决议、两条隐藏决议 |
| [we_l_simp_chinese.yml](E:/Steam/steamapps/workshop/content/394360/3440479297/localisation/simp_chinese/we_l_simp_chinese.yml:3) | 分类标题、长说明文本及全部修正读取表达式 |

第 4、6、8 行的三个 `_desc` 分别显示政治工业与陆军、海空军、情报。它们是完整长字符串，用 `\n` 换行、固定空格排列、`§...§!` 着色和 `£...` 插入图标；全部借用原版决议界面的分类说明区域。源码没有为每项修正创建一个独立控件。

显示海空军的决议在 `we_common.txt` 第 45 行执行 `set_global_flag = show_air_and_nav_flag`，对应分类的 `visible` 在 categories 第 22–24 行检查它。情报同理，使用 `show_intel_flag`。隐藏决议分别在第 96、122 行清除标记。这些决议免费且 AI 权重为 0，主要用于改变显示范围。

展开状态使用 **global flag**，在多人游戏中属于共享脚本状态；各国看到的修正数值仍由各自的 `This` 国家决定。它没有实现每个客户端各自独立的展开偏好。

## 实时读取与界面刷新

动态表达式在本地化被重新求值时读取引擎当前值，因此没有模组自己保存旧采样值的问题。但“读取当前值”和“界面多久重新求值”是两件事。

普通版依赖原版决议界面的刷新。它没有事件、`on_actions` 或每日每小时统计任务；源码不足以证明文本每帧更新。隐藏决议的说明还写有“第二天 0 时生效”，实际脚本只是清除全局标记，没有设置次日定时事件，这应理解为作者对界面表现的提示，具体延迟需要运行测试。

UI 版在两个 Scripted GUI 中都写有：

```text
dirty = FE_statistics_tools_box_dirty_var
```

刷新函数位于 [BDUI_scripted_effects.txt 第 1 行](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_effects/BDUI_scripted_effects.txt:1)，把该变量在 0 和 1 之间切换。已接入交互的刷新调用发生在打开窗口和切换分类时；该目录没有周期任务。

原版 [Scripted GUI 文档第 102–105 行](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_guis/_documentation.md:102>) 说明，GUI 默认每 tick 更新，指定 `dirty` 后只在该变量变化时更新。因此，本机 UI 版源码不能支持“窗口持续打开时会完整、连续刷新全部数值”的保证。动态文字是否还有引擎独立重求值路径、实际可见延迟是多少，需要在游戏中改变一个已知修正并观察。

还有一个具体待测点：Scripted GUI 第 60–62 行的关闭回调，以及第 21 行入口的关闭分支，只修改开关数组，没有修改 `dirty`。按文档，这是可复用时应补齐的刷新路径；本次静态检查不据此断言当前游戏一定无法关闭。

多数读数显示整数百分比，较小变化也可能因显示精度被舍入。`modifier@` 能读到值，不自动保证指标选择、单位、舍入和刷新全部正确。

## UI 版如何创建独立页面

UI 版采用两套 Scripted GUI，入口与主页面分别挂到两个引擎界面节点。关键代码在 [BDUI_scripted_gui.txt 第 3 行](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_guis/BDUI_scripted_gui.txt:3)，以下仅摘录绑定字段：

```text
BDUI_tools_box = {
    context_type = player_context
    parent_window_token = politics_tab
    window_name = "BDUI_tools_box"
    dirty = FE_statistics_tools_box_dirty_var
    visible = { always = yes }
    # effects 中处理 tools_button_click
}

statistics_tool_show_buff = {
    context_type = player_context
    parent_window_token = top_bar
    window_name = "FE_statistics_tool_show_buff"
    dirty = FE_statistics_tools_box_dirty_var
    visible = {
        check_variable = { FE_statistics_tools_show_array^0 = 2 }
    }
    # 后续定义 properties、dynamic_lists 和 effects
}
```

`politics_tab` 与 `top_bar` 是原版公开的父界面 token，见 [原版文档第 25–30 行](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_guis/_documentation.md:25>)。因此无需替换原版整份政治布局文件，就可以附加入口和主页面。

入口布局见 [BDUI_gui_tools.gui 第 3–31 行](E:/Steam/steamapps/workshop/content/394360/3795966002/interface/BDUI_gui_tools.gui:3)。外层容器相对政治界面位置为 `(185,0)`，内层偏移 `(12,0)`，实际 `tools_button` 再偏移 `(10,7)`；图像 `GFX_BDUI_menu` 对应 `gfx/interface/BDUI/menu.dds`。入口由政治面板承载，位于其标题附近。

主窗口布局在同文件第 67–76 行：

```text
name = "FE_statistics_tool_show_buff"
position = { x = 0 y = 120 }
show_position = { x = 545 y = 120 }
size = { width = 720 height = 600 }
show_animation_type = decelerated
hide_animation_type = accelerated
animation_time = 300
```

它以独立容器显示在政治面板旁，主窗口的父节点是 `top_bar`。这个版本没有声明 `moveable = yes` 或 `click_to_front = yes`，不能照搬 Kaiserreich 的可拖动、点击前置结论。

模组附带的 UI 预览图如下，属于作者随模组提供的素材，不是本次运行测试截图：

![UI 版政治入口与独立修正窗口](E:/Steam/steamapps/workshop/content/394360/3795966002/thumbnail2.png)

## 页面开关与分类切换

入口 `tools_button_click`（Scripted GUI 第 13–22 行）检查 `FE_statistics_tools_show_array^0`：未打开时设为 `2` 并调用 `FE_tool_exec_1`，再次点击则设为 `1`。主页面的 `visible` 以第 0 项等于 `2` 为条件。

打开效果 [FE_tool_exec_1](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_effects/BDUI_scripted_effects.txt:25) 初始化五个分类标签状态，填入首页指标编号 1–21，并切换刷新变量。关闭按钮在 `.gui` 第 112–121 行，名字为 `close_button`，绑定 `ESCAPE` 快捷键；其回调将第 0 项设为 `1`。这些操作改变的是国家作用域的显示状态数组。

五个分类使用同一个网格，每次点击都会清空并重建编号数组：

| 分类 | 填入 `FE_tool_show_buff_array` 的编号 | Scripted GUI 回调起始行 |
|---|---|---:|
| 政治和工业 | 1–21 | 63 |
| 陆军 | 101–133 | 77 |
| 海军 | 201–251 | 91 |
| 空军 | 301–321 | 105 |
| 情报 | 401–436 | 119 |

这些编号只是作者自定义的显示索引，不是引擎自动枚举出的 modifier ID。`FE_show_buff_tab_array^1` 至 `^5` 控制标签图片帧：1 为选中，2 为未选中。对应 `.gfx` 的标签图片均声明两帧。

## 一项 BUFF 怎样变成页面上的一行

[Scripted GUI 第 43–50 行](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_guis/BDUI_scripted_gui.txt:43) 绑定动态列表：

```text
tool_show_buff_gridbox = {
    array = THIS.FE_tool_show_buff_array
    change_scope = yes
    value = v
    index = i
    entry_container = FE_tool_show_buff_window_container
}
```

数组装的是显示编号。`v` 保存当前条目的值，`i` 保存数组位置。虽然源文件设置了 `change_scope = yes`，这里仍不能解读成遍历所有国家；最终取数明确使用 `ROOT.modifier@...`，固定在 GUI 的根玩家国家。

每个编号生成一个 [条目模板](E:/Steam/steamapps/workshop/content/394360/3795966002/interface/BDUI_gui_tools.gui:190)，其中的文本控件使用 `tool_show_buff_name_text`。本地化第 11 行将它转发到 `[GETBUFFName]`；[scripted localisation 第 14–24 行](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_localisation/BDUI_scripted_localisation.txt:14) 把 `v` 存到临时变量 `buff_index`，拼出 `FE_tool_show_buff_name_text_[?buff_index]`。

例如陆军第一个条目的完整链路为：

```text
点击陆军标签
 → 数组填入 101…133
 → 为 v = 101 创建文本条目
 → tool_show_buff_name_text
 → GETBUFFName
 → FE_tool_show_buff_name_text_101
 → 名称 $MODIFIERS_ARMY_ATTACK_FACTOR$
 → 数值 [?ROOT.modifier@army_attack_factor|+=0%]
 → 显示玩家国家的陆军攻击修正
```

布局在 `.gui` 第 124–144 行设置高 475 的滚动内容区、垂直滚动条和平滑滚动；网格最多三列，槽位 `220 × 35`。因此整齐排列来自“编号数组、重复模板和三列网格”，内容较长时使用滚动区域。源码没有国家选择器、国家比较或逐项来源明细窗口。

## 已确认的错配和待测问题

| 状态 | 位置 | 问题 |
|---|---|---|
| 确认错配，两版都有 | 普通版本地化第 4 行；UI 本地化第 20 行，ID 9 | “工厂修复速度”读取 `repair_speed_factor`，而本机原版该键对应船只修理；工厂修复键是 `industry_repair_factor` |
| 确认错配，UI 版 | UI 本地化第 35 行，ID 103 | “非核心领土攻击”标签读取 `army_non_core_defence_factor`；第 38 行的防御条目再次读取它，真正攻击键没有被该条目读取 |
| 确认重复，普通版 | 本地化第 6 行 | “出击效率”和“舰载机起降能力”均读取 `sortie_efficiency` |
| 确认重复，UI 版 | 本地化第 167、170 行，ID 430、433 | 两项完全重复 `own_operative_detection_chance_factor` |
| 字段兼容疑点，普通版 | 本地化第 4 行 | 主动性读取 `initiative`；本机原版登记的修正键是 `initiative_factor`，UI 版已经改用后者 |
| 字段兼容疑点，两版都有 | 普通版第 4 行；UI 第 45、48 行 | 特殊部队攻防键使用大写 `SPECIAL_FORCES_*`，原版登记为小写；需核验该读取路径的大小写容忍情况 |
| 本轮全量目录已确认，两版都有 | 普通版第 8 行；UI 第 163 行 | `operation_risk` 来自原版修正文档第 1360 行的 `<Operation>_risk` 模板，第 1366 行参数列表包含 `operation`；此前仅查固定标题留下的疑点已消除，实际读数仍未运行验证 |
| 刷新待测，UI 版 | Scripted GUI 第 21、60–62 行 | 关闭路径没有改变 dirty；持续打开期间也没有显式周期刷新 |

工厂与船只修理名称可由原版 [modifiers_l_simp_chinese.yml 第 667 行](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:667>) 和 [第 1298 行](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/simp_chinese/modifiers_l_simp_chinese.yml:1298>) 复核。对应脚本键分别在 [修正文档第 2942 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:2942>) 与 [第 4575 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/modifiers_documentation.md:4575>)。这些错配使“读数实时”也不能等同于“标签与数值正确”。

## 与 Kaiserreich 中欧同盟界面的关系

| 机制 | Kaiserreich 中欧同盟 | BUFF UI 版 |
|---|---|---|
| 入口挂载 | `parent_window_name = raid_filter` | `parent_window_token = politics_tab` |
| 主窗口挂载 | 默认主界面 | `parent_window_token = top_bar` |
| 显隐状态 | 国家标记 `mitteleuropa_window_open` | 国家数组首项取值 1 或 2 |
| 刷新信号 | 全局变量 `global.MIT_update` | 国家变量 `FE_statistics_tools_box_dirty_var` |
| 主体内容 | 国家、议程对象与投票操作 | 固定显示编号对应的修正文本 |
| 已声明窗口能力 | 可拖动、点击前置 | 未声明这两项 |

两个案例共同展示了 HOI4 自定义页面的基本结构：独立布局容器、Scripted GUI 挂载、状态驱动显隐、点击回调和刷新信号。若在自己的模组中制作修正统计页，可以复用这套结构，再为指标目录明确作用域、单位、标签和来源范围，并在需要的时机刷新。仅复制 UI 版的布局无法自动获得完整指标覆盖或持续更新保证。
