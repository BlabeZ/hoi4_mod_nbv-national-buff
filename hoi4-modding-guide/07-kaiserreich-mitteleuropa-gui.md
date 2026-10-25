# Kaiserreich 中欧同盟 GUI 源码分析

截图中的功能是 **中欧同盟（Mitteleuropa）会议系统**。窗口标题、主席、下次会议、议程分数和议程列表，与本机 Kaiserreich 的 `mitteleuropa` 界面及汉化键逐一对应。其入口采用 HOI4 的 **Scripted GUI**：将一个小型按钮容器挂到原版右侧 HUD，另行定义主窗口，用国家标记控制窗口显隐，用脚本效果处理页面操作。

分析日期：2026-10-24。对象是本机已安装源码；核心模组 `descriptor.mod` 声明版本 `1.7`、支持游戏版本 `1.19.3.*`。以下行号对应本次读取文件，后续 Workshop 更新可能改变行号。此次核验为截图与静态源码对照，未启动游戏验证操作。

| 对象 | 本机位置 |
|---|---|
| 截图中的右侧入口 | [截图1.png](D:/projects/hoi4_mod/1/截图1.png) |
| 截图中的主窗口 | [截图2.png](D:/projects/hoi4_mod/1/截图2.png) |
| Kaiserreich 核心模组 | `E:\Steam\steamapps\workshop\content\394360\1521695605` |
| Kaiserreich 汉化 | `E:\Steam\steamapps\workshop\content\394360\2946487287` |
| 原版游戏 | `E:\Steam\steamapps\common\Hearts of Iron IV` |

中文标题来自 [MIT 汉化文件第 2 行](<E:/Steam/steamapps/workshop/content/394360/2946487287/localisation/simp_chinese/KR_country_specific/MIT - Mitteleuropa l_simp_chinese.yml:2>)。第 5、7、12、30、34 行分别对应主席、下次会议、议程分数、可选议程、支持度最高的议程。代码搜索宜使用 `mitteleuropa` 或 `MIT_`。

## 核心源码位置

| 文件 | 关键代码段 | 职责 |
|---|---|---|
| [gui_mitteleuropa.gui](E:/Steam/steamapps/workshop/content/394360/1521695605/interface/kaiserreich/gui_mitteleuropa.gui:12) | 13–37；39–87；169–454 | 入口按钮、主窗口、关闭按钮、网格及条目模板的布局 |
| [germany_mitteleuropa.txt](E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_guis/germany_mitteleuropa.txt:5) | 6–52；55–80；317–555 | 绑定窗口、显示条件、点击回调、动态列表、图标和选中状态 |
| [MIT triggers](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_triggers/MIT triggers (Mitteleuropa).txt:1>) | 1–6；43–45 | 系统是否激活、窗口是否打开 |
| [MIT effects](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_effects/MIT effects (Mitteleuropa).txt:819>) | 819–869；981–1100 | 刷新、投入政治点数、生成列表、开关窗口、支持议程 |
| [原版 country_raids_view.gui](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/military_raids/country_raids_view.gui:1018>) | 1018–1029 | 右侧 HUD 父容器 `raid_filter` 的位置与锚点 |
| [MIT events](<E:/Steam/steamapps/workshop/content/394360/1521695605/events/MIT events (Mitteleuropa).txt:1052>) | 1052–1075；8–30；804–874 | 首次说明、正式会议开始和结束流程 |
| [MIT scripted localisation](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_localisation/MIT scripted_loc (Mitteleuropa).txt:30>) | 30–48；63–72 | 剩余天数、分数的动态文字 |

## 右侧按钮如何出现

入口由三个部分连接起来：**原版父容器 → 模组按钮容器 → 按钮控件**。

原版 `country_raids_view.gui` 第 1018 行定义 `raid_filter`，其中有：

```text
name = "raid_filter"
position = { x = -76 y = -235 }
size = { width = 78 height = 0 }
clipping = no
orientation = lower_right
```

`lower_right` 将父容器锚定到界面右下方；其高度由引擎随网格项目数动态确定。`clipping = no` 允许子控件画到父容器矩形以外。这解释了截图按钮为什么能够位于右侧现有控件上方。

Kaiserreich 的 `.gui` 第 13–37 行定义一个新的容器。下面摘录其布局和按钮，省略了背景、声音与提示字段：

```text
containerWindowType = {
    name = "mitteleuropa_open_button_window"
    position = { x = 0 y = -115 }
    size = { width = 77 height = 77 }

    buttonType = {
        name = "mitteleuropa_open_button"
        position = { x = 8 y = 4 }
        quadTextureSprite = "GFX_idea_ger_revive_the_kaiserreich"
    }
}
```

容器相对父容器向上移动 115 个 GUI 坐标单位，内部按钮再偏移 `(8, 4)`。鹰徽使用已有 sprite，其定义位于 [ideas.gfx 第 179 行](E:/Steam/steamapps/workshop/content/394360/1521695605/interface/ideas.gfx:179)，指向 `gfx/interface/ideas/idea_ger_revive_the_kaiserreich.dds`。

真正把这个容器接到游戏 HUD 的是 `common/scripted_guis/germany_mitteleuropa.txt` 第 6–14 行：

```text
mitteleuropa_button = {
    parent_window_name = raid_filter
    context_type = player_context
    window_name = "mitteleuropa_open_button_window"
    dirty = global.MIT_update

    visible = {
        GER_is_in_mitteleuropa = yes
    }
    # 后续还有 triggers、effects 和 AI 配置
}
```

`parent_window_name` 指明要附着的原版容器；`window_name` 必须匹配 `.gui` 中的容器 `name`。`player_context` 使条件和效果以操作界面的玩家国家为上下文。因此，这套实现可以在模组自身的 `.gui` 和 `scripted_guis` 文件中增加入口，并复用原版 `raid_filter`，无需改写其整份布局文件。

入口出现与能够点击分别判断：

| 条件 | 实际检查 |
|---|---|
| 显示入口 | `GER_is_in_mitteleuropa`；定义在 [GER triggers 第 95 行](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_triggers/GER triggers (Germany).txt:95>)，检查国家拥有 `MIT_mitteleuropa_modifier` 动态修正 |
| 允许点击 | Scripted GUI 第 22–25 行要求 `MIT_is_active = yes`，并且不存在全局标记 `MIT_event_chain_ongoing` |
| 系统激活 | `MIT_is_active` 检查德国拥有 `MIT_election` 国家标记 |

成员资格在这里由动态修正判断，不能直接用“属于帝国公约军事阵营”替代。父容器名称、右侧空间和 UI 缩放是迁移到其他游戏版本或其他界面模组时需要复核的依赖。

## 主窗口如何成为独立浮动页面

`.gui` 第 39 行另行定义 `mitteleuropa_window`。它的主要属性是：

```text
containerWindowType = {
    name = "mitteleuropa_window"
    position = { x = -500 y = -250 }
    size = { width = @window_width height = 530 }

    hide_position = { x = 1000 y = -250 }
    show_animation_type = decelerated
    hide_animation_type = accelerated
    animation_time = 300

    moveable = yes
    show_sound = menu_open_window
    hide_sound = menu_close_window
    click_to_front = yes
    orientation = center
    # 后续是背景、标题、关闭按钮、内容区域
}
```

文件第 1 行设定 `@window_width = 850`，因此主页面为 850 × 530。`orientation = center` 配合负偏移决定其屏幕位置；此处横向偏移是 `-500`，不能简单理解为严格水平居中。`moveable = yes` 声明可拖动，`click_to_front = yes` 声明点击时前置；显示、隐藏另有位置动画及声音。

对应 Scripted GUI 第 55–62 行：

```text
mitteleuropa_window = {
    context_type = player_context
    window_name = "mitteleuropa_window"
    dirty = global.MIT_update

    visible = {
        MIT_interface_is_open = yes
    }
    # 后续是数据列表、交互、属性和 AI 配置
}
```

这一块独立绑定主页面，没有入口所用的 `parent_window_name = raid_filter`，所以主窗口位置不跟随右侧按钮。`.gui` 负责“长什么样”，Scripted GUI 的 `visible` 负责“何时显示”。截图中的页面由这个容器呈现；首次说明另有普通国家事件。

## 点击如何打开和关闭

按钮与回调通过名字对应：`.gui` 中 `name = "mitteleuropa_open_button"`，在 Scripted GUI 的 `effects` 下对应 `mitteleuropa_open_button_click`；可点击条件对应 `mitteleuropa_open_button_click_enabled`。

第 29–46 行的入口回调分三种情况：

1. 窗口未打开，且真人国家从未看过介绍：触发 `germany_mitteleuropa_events.1001`。该事件先设置 `MIT_opened_panel_once`，玩家选择选项后调用打开效果。
2. 窗口未打开，已完成上述介绍：直接调用 `MIT_open_mitteleuropa_panel`。
3. 窗口已经打开：调用 `MIT_close_mitteleuropa_panel`。

打开效果原文见 [MIT effects 第 1064 行](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_effects/MIT effects (Mitteleuropa).txt:1064>)：

```text
MIT_open_mitteleuropa_panel = {
    if = {
        limit = { MIT_interface_is_open = no }
        hidden_effect = { MIT_update_agenda_list = yes }
        set_country_flag = mitteleuropa_window_open
        MIT_update_gui = yes
    }
}
```

它先准备当前国家的候选议程数组，再设置国家标记并触发刷新。判断是否打开的条件在 [MIT triggers 第 43 行](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_triggers/MIT triggers (Mitteleuropa).txt:43>)：

```text
MIT_interface_is_open = {
    has_country_flag = mitteleuropa_window_open
}
```

这里的开关属于**当前国家的脚本状态**，使用 `country_flag`。它不是全局开关，也不能被当作纯客户端临时变量。

关闭效果位于 effects 第 1074–1081 行，在已打开时执行：

```text
clr_country_flag = mitteleuropa_window_open
clear_array = MIT_agenda_list_for_ui
MIT_update_gui = yes
```

页面右上角 X 是 `.gui` 第 79–87 行的 `button_close`，带有 `shortcut = "ESCAPE"`。Scripted GUI 第 376–378 行把 `button_close_click` 绑定到同一关闭效果，因此 X、Esc、再次点击侧边入口都具备关闭路径。关闭清理显示标记和候选 UI 数组，保留国家此前的议程支持与政治点数投入。

开关链可以写成：

```text
右侧按钮 mitteleuropa_open_button
  → mitteleuropa_open_button_click
  → 首次使用时先完成说明事件
  → MIT_open_mitteleuropa_panel
  → 建立 MIT_agenda_list_for_ui
  → 设置国家标记 mitteleuropa_window_open
  → 改变 global.MIT_update
  → 主窗口 visible 判断成立
  → 显示 mitteleuropa_window

X / Esc / 再次点击入口
  → MIT_close_mitteleuropa_panel
  → 清除国家标记和候选 UI 数组
  → 改变 global.MIT_update
  → visible 判断不成立，隐藏窗口
```

## 数据改变后怎样更新画面

入口和主窗口均声明 `dirty = global.MIT_update`。刷新效果位于 [MIT effects 第 819 行](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_effects/MIT effects (Mitteleuropa).txt:819>)：

```text
MIT_update_gui = {
    set_variable_to_random = global.MIT_update
}
```

改变这个变量使依赖它的 Scripted GUI 重新求值，更新显隐、列表与属性。两种状态各有用途：`mitteleuropa_window_open` 表示某个国家是否打开窗口；`global.MIT_update` 是共用的刷新信号。议程投票关系会影响多个成员国家，共用刷新信号让这些界面重新读取同一组会议数据。

除了点击后的主动刷新，[on_actions_Germany.txt 第 532 行](E:/Steam/steamapps/workshop/content/394360/1521695605/common/on_actions/on_actions_Germany.txt:532) 的每日逻辑还会重算议程分数、重新排序并更新 GUI。

## 窗口中的列表和按钮怎样操作游戏数据

主窗口由标题、主席旗帜、成员国网格、议程分数加减按钮、前三项议程、候选议程滚动列表等控件组成。`.gui` 定义这些控件及单条记录的模板；Scripted GUI 的 `dynamic_lists` 将数组展开为条目。

| 截图内容 | GUI 容器与模板 | Scripted GUI 数据绑定 |
|---|---|---|
| 成员国旗 | `countries_list_grid`、`member_entry` | 第 71–75 行，`MIT.economic_sphere:members` |
| 可选议程 | `agenda_list_grid`、`agenda_entry` | 第 77–80 行，`MIT_agenda_list_for_ui`，`value = agenda` |
| 支持度最高的议程 | `top_agendas_grid`、`top_agenda_entry` | 第 317–321 行，`global.MIT_sorted_voted_agendas`，`value = top_agenda` |
| 某议程的支持国旗 | `supporters_list_grid`、`top_agenda_supporter_entry` | 第 322–326 行，`top_agenda:agenda_supporters` |

成员和支持国列表使用 `change_scope = yes`，每条记录把当前作用域切到对应国家，因此属性 `image = "[THIS.GetFlag]"` 能显示各国国旗。议程列表使用 `value = agenda`，当前行的议程对象引用可通过 `agenda` 取得；它不是议程数组下标。

议程行的 `.gui` 模板在 [第 405 行](E:/Steam/steamapps/workshop/content/394360/1521695605/interface/kaiserreich/gui_mitteleuropa.gui:405)，其中的可点击按钮叫 `agenda_button`。其回调 `agenda_button_click` 在 Scripted GUI 第 422–497 行：首次支持、取消原支持或切换支持，最后重算所有议程分数、排序并刷新。支持效果见 [MIT effects 第 1089 行](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_effects/MIT effects (Mitteleuropa).txt:1089>)：

```text
# 调用者先用 var:agenda = { ... } 切到议程对象
MIT_support_agenda = {
    add_to_array = { agenda_supporters = PREV }
    set_variable = { frame@PREV = 2 }
    set_variable = { PREV.MIT_supported_agenda = THIS }
}
```

此时 `THIS` 是议程，`PREV` 是投票国家。脚本把该国加入议程的支持者数组，记录该国支持的议程，并为该国保存选中帧。Scripted GUI 第 541–543 行随后用 `agenda_checkbox = { frame = agenda:frame@ROOT }` 回显玩家国家的选择。第 364–372 行的 enabled 条件检查投票冷却；实际冷却效果在 effects 第 1084 行，设置 30 日国家标记。

议程分数旁的加减按钮也遵循同样模式：Scripted GUI 第 329–362 行检查政治点数或可回收投入，第 380–419 行执行加减及重算。普通、Ctrl、Shift、Ctrl+Shift 点击分别传入 1、5、10、50。effects 第 823–869 行修改 `MIT_agenda_investment`，按成本修正扣除或返还政治点数。

主席旗帜通过 `image = "[MIT.GetFlag]"` 读取。[tag_aliases.txt 第 151 行](E:/Steam/steamapps/workshop/content/394360/1521695605/common/country_tag_aliases/tag_aliases.txt:151) 将 `MIT` 定义为 `GER.economic_sphere:members^0`，即成员数组第一项。更换主席时，effects 第 883–907 行调整该数组第一项，旗帜也随新的主席国更新。

候选议程的数据对象在 [MIT characters.txt](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/characters/MIT characters.txt:2>) 中定义。德国历史文件 [GER - Germany.txt 第 1069 行](<E:/Steam/steamapps/workshop/content/394360/1521695605/history/countries/GER - Germany.txt:1069>) 初始化这些对象及其字段、加入全局议程数组。打开窗口时，`MIT_update_agenda_list`（effects 第 981–1006 行）按可用条件筛选出本国候选数组。因此，布局模板可以重复使用，议程内容及支持状态由游戏数据驱动。

## 截图文字和正式会议流程

“180 日”由 scripted localisation 第 30–48 行计算：180 减去德国 `MIT_election` 标记已存在天数；剩余时间不为正时显示“即将”。“24 分”来自 `[GetMitteleuropaAgendaScore]`：有支持议程时显示该议程总分，否则显示本国分数计算结果，并非写死的界面文字。对应的权重公式在 [GER_mtth.txt 第 5 行](E:/Steam/steamapps/workshop/content/394360/1521695605/common/mtth/GER_mtth.txt:5)。

正式会议开始事件在 MIT events 第 8–30 行设置 `MIT_event_chain_ongoing` 并关闭成员面板，入口的 enabled 条件据此暂时禁用点击。结束事件第 804–874 行解除锁定、重置议程数据，并重新设置 `GER.MIT_election` 开始下一轮。

`.gui` 第 360–379 行还有三个 `hide = yes` 的辅助按钮，名字包含 `agenda_reward_loc_button` 等。它们配合本地化中的 `[!…_click]` 生成效果说明。真正点击议程修改的是支持关系；奖励由会议事件调用 `MIT_add_agenda_reward` 发放，不是这些隐藏辅助按钮供玩家即时领取。

## 制作同类功能时需要复用的结构

若目标是制作自己的“右侧入口加独立功能页面”，可以沿用以下对应关系：

| 层次 | 需要定义的内容 | Kaiserreich 对照 |
|---|---|---|
| 布局 | 一个入口容器、一个主页面容器、关闭及业务按钮 | `gui_mitteleuropa.gui` |
| HUD 挂载 | 入口的 `parent_window_name`、匹配布局的 `window_name` | `mitteleuropa_button` |
| 显隐 | 当前国家开关标记、主窗口 `visible`、入口点击切换 | `mitteleuropa_window_open` |
| 交互 | `控件名_click_enabled` 与 `控件名_click` | `button_close_click`、`agenda_button_click` |
| 刷新 | 数据变化后修改与 `dirty` 绑定的变量 | `global.MIT_update` |
| 页面数据 | 变量、数组、动态列表与 `properties` | 候选议程数组、成员列表、旗帜及选中帧 |
| 资源和文字 | `.gfx` sprite、纹理、本地化、动态文本 | 鹰徽、窗口标题、分数、tooltip |

仅实现空白页面的打开和关闭，主要需要前五层；会议、议程 character 对象、AI 投票和政治点数逻辑属于这一具体玩法的扩展。新功能应给容器、控件、标记、变量和本地化键使用自己的命名前缀，同时保证布局名、绑定名和回调名一致。

若要修改这套现有功能，布局先看 `.gui`，按钮行为先看 `germany_mitteleuropa.txt`，状态和数据处理再进入 effects。这样可以保持“显示、交互、业务规则”各自的职责清楚。

源文件路径、行数、SHA-256 和关键符号位置记录在 [源码索引](D:/projects/hoi4_mod/1/hoi4-modding-guide/references/kaiserreich-mitteleuropa-source-index.json)，用于在 Workshop 更新后复核本分析。
