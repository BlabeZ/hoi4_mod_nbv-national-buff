# 源码参考与移植改造说明

记录日期：2026-10-25。项目：**国家修正统计 UI 0.1.11**。本说明记录源码参考关系与实现边界，不代替游戏内测试记录。

## 0.1.11 指定同名键加入其他修正

新增 8 个显示 ID：2 `conscription_factor`、43 `autonomy_manpower_share_from_subjects`、275 `army_org`、234 `experience_gain_army_factor`、241 `max_dig_in_factor`、379 `experience_gain_navy_factor`、544 `encryption_factor`、542 `decryption_factor`。它们追加到对应页面的“其他修正”末尾。已有 ID484 `experience_gain_air_factor` 由空军“常用”移到“其他修正”末尾，并改为明确的百分比名称，没有重复添加。组织度固定项按上轮已确认的陆军师组织度接入；海军固定组织度仍保留待核状态。

当前共 528 项（常用 176、其他 352），9 个指定词条均采用四列。8 个新增显示键已有精确原版格式与来源绑定，此次只更新显示名称和选择名单，559 项基础注册表、数值格式、来源与图标绑定保持不变。新增选择使候选来源覆盖达到 514/528、28931 条；这不代表全部生效来源都已拆分。用户 Markdown 中旧“空军经验增长”的两次出现一起替换，防止首次去重使其仍留在常用区。

## 0.1.10 固定建筑位与同名词条

新增 ID142 `global_building_slots`，位于工业“其他修正”第 77 项，显示名“地区最大工厂数（固定值）”。原有 ID109 `global_building_slots_factor` 保留在原位置；本机原版 `global_building_slots_tt` 使用 `+=0`，比例项模板使用 `+=%1`。本次添加的是所有州共享建筑位上限的国家固定加成，不是已建工厂数。

当前页面共 520 项（常用 177、其他 343）；工业 99 项。通过 `display_names.py` 设置独立 UI 别名，先解析名称再按技术键去重。其余 519 项次序、基础 559 项注册表及数值、图标、来源绑定保持一致。原版未区分名称仍沿用首次绑定，其他同名项目没有批量恢复。候选来源覆盖随新增选择变为 506/520、27965 条；来源定义本身不变。

完整同名审计保存在 `tools/data/same-name-modifier-audit.json`。它区分已确认不同的国家键、具体单位或计算层待核的键，以及应继续排除的州对象；不能把全部同名遗漏直接视为应加入页面的修正。

## 0.1.9 入口图标与已知侧栏布局

原版 `interface/topbar.gfx` 的 `GFX_ledger_button` 使用 110×41、2 帧贴图，单帧为 55×41。入口容器 77×77，按钮从 (3,3) 开始、尺寸 71×71。图标改为 (11,18)，两者中心均为 (38.5,38.5)；不再为已删除的文字保留下方空位。没有修改原版贴图。

`sidebar_placement.py` 在构建 `.gui` 时对已登记的占位计算间距，发生接近或相交时只向上移动，每次移动后重新检查全部占位。该过程只发生在构建工具中；发布模组使用已生成的固定位置，正常从 Steam 或启动器启动即可。没有离线启动扫描器、外部后台程序、运行时碰撞探测或对其他模组文件的修改。

| 已核实布局 | 结论 |
|---|---|
| KR 中欧同盟 | 同挂 `raid_filter`，其容器 (0,-115,77,77)，本入口 (0,-202,77,77)，间隔 10；父容器位置和动态高度同时影响两者，相对间距不变 |
| EAW 侧边 lore 入口 | 父锚点改为右下 (-76,-300)；lore 背景及按钮在独立右下锚点。按袭击容器高度为零计算最近边界，背景间隔仍为 121；正高度只会让本入口更靠上 |
| TFR | 已检查入口在顶栏，没有在相同侧栏区域发现功能入口 |
| BUFF UI | 入口在政治页面，不占这个右侧位置 |

因此当前构建的向上移动次数为零，位置保持不变。此结论只涉及已核实的永久入口，不能推广到任意临时弹窗、任意 GUI 缩放或后续更新后的布局。TNO 及其子模组按用户要求不适配。四项几何回归检查覆盖连续碰撞、间距边界、水平分离和居中计算；不把它们表述成大型模组实机合用验收。

## 0.1.8 民族精神遗漏与特殊国家来源

原版 `common/ideas/SOV.txt`、`persia.txt`、`switzerland.txt` 和 `common/doctrines/subdoctrines/sea/navy_submarine_doctrines.txt` 缺少末尾闭合。来源扫描现仅对核实过的文件 SHA256 做内存恢复，保持严格通用解析器和原版文件不变；恢复证据分别写入 `source-bindings.json` 与 `doctrine-technology-source-bindings.json` 的 `parse_recoveries`。匿名对象解析修复后重新扫描暹罗角色事件，补回顾问绑定。

`build_special_source_bindings.py` 接入 15 条国家状态贡献，读取原版 `common/modifiers/00_static_modifiers.txt`，使用文档明确的 `ROOT.has_stability` 和 `ROOT.has_war_support` 实时输入及和平条件。奇观 `country_modifiers/modifiers` 的 26 条候选只保留研究记录，不生成来源行；`state_modifiers` 始终排除。三轮引擎测试否定了已尝试的省级奇观健康度查询，包括“国家无任何受损建筑”门槛，因此不能声称完好状态已得到保证。所有已接入来源仍显示“来源名称 数值”，不增加类别前缀或残差。

`special_source_smoke_probes.py` 只在外部隔离 addon 中建立真实 SOV／GER／LIB 国家事件，检查原生精神生命周期、原版状态曲线，以及国会建筑状态变化时合计增减 0.05 且不输出未经核实的奇观来源。`landmark_unavailable` 检查来源省略与真实合计，不表示奇观已接入。舰队荣耀及沿岸保护未找到可核实当前状态的公开脚本查询，记在 `special-source-bindings.json/unavailable_sources`；沿岸保护是否进入 `modifier@stability_factor` 尚未单独实测，没有把固定最大值或合计差额冒充实时来源。

## 0.1.7 页面名单与排序

以用户编辑的 Markdown 为页面名单：519 项分为常用 177 项、其他修正 342 项。导入忽略 111 个空条目，对 16 次重复出现保留首次位置；用户确认粘连的两个情报词条在原位置拆开。`display-order.md` 保留输入快照，`display-layout.json` 记录实际顺序、去重位置、同名绑定选择和排除项。

布局与 559 项基础注册表分离，原始 ID、数值格式、来源映射和图标绑定保持稳定；只将选中的 ID 按新顺序写入实时与后备列表。`display_layout.py` 导入名单，`build_backend.py` 生成列表和最大滚动行数。静态验证独立解析 Markdown 对照，隔离引擎逐个核对 519 个单元格及顺序摘要，同时保留 559 项读数回归。

## 0.1.6 数据图标

本机“Modifier Icons 汉化版（数据图标）”对应目录为 `E:\Steam\steamapps\workshop\content\394360\2671396187`。其 `description.mod` 声明名称 `Modifier Icons CN ver.`、版本 1.1、支持 1.19.*。汉化版作者为 **1+1=⑨**，原版作者为 **truck gaming**。来源：[汉化版创意工坊](https://steamcommunity.com/sharedfiles/filedetails/?id=2671396187)、[原版 Modifier Icons](https://steamcommunity.com/sharedfiles/filedetails/?id=2668048070)。原作者页面允许其他模组使用并希望署名，本项目在此保留出处。

原模组在 `localisation/replace/vanilla/` 的修正名称前加入 `£图标名`，由 `interface/modifiericons_texticons.gfx` 和 `modifiericons_texticons_for_cn_ver.gfx` 中的 `GFX_图标名` 解析至 DDS 贴图。中文专用图标还通过透明边距调整文本对齐。

本项目提取词条与图标的对应关系，只在自身 `nbv_row_name_*` 和 `nbv_row_tooltip_*` 标题中加入图标。所有精灵改名为 `GFX_nbv_mi_*`，所需模组贴图复制至 `gfx/nbv_modifier_icons/`，不安装源模组的全局本地化覆盖。原版已有素材由独立精灵引用原版路径。名称、数值和来源仍使用本项目的既有数据；图标不参与取数，也不改变筛选、排序、三列／四列布局和来源判定。16 像素图标在现有 20 像素高名称框中显示，名称过长仍截断，悬停保留完整名称。

构建脚本为 `tools/build_icon_bindings.py`，逐项依据及贴图 SHA-256 保存于 `tools/data/modifier-icon-bindings.json`。自动映射优先使用修正键对应的原版本地化名及已核实名称引用；缺少直接映射的项目逐键选择同类图标并记录理由，不按关键词批量猜测。素材按需复制，启动本模组不依赖创意工坊图标模组。

559 项全部有图标：529 项直接对应原模组本地化，3 项适配海军陆战队的旧键名，26 项逐键选择同类图标，1 项修复源模组未定义的步兵速度图标。共使用 352 种图标，其中 343 张源模组 DDS 原样复制（合计 438,320 字节），9 项引用原版贴图。所有图标均单帧，高度为 16–20 像素。要塞维修的源 DDS 缺失，改用其通用维修图标；反坦克许可生产的源本地化缺少结束引号，只提取有效图标标记，不复制错误文本。两处处理均保留逐项证据。

## 0.1.5 动态民族精神来源修复与领袖姓名

0.1.4 已接入变量型动态修正，但旧解析器不支持原版 `optional_assets = { { icon = ... model = ... } }` 的匿名嵌套块。苏联、日本等国家历史文件因此整文件解析失败；作用域审计对这些文件出现的动态修正采用保守排除，造成实际国家民族精神来源遗漏。0.1.5 在 [validate_mod.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/validate_mod.py) 中保留匿名节点及其行号、顺序，后续 `add_dynamic_modifier` 可以继续正常解析，再重新扫描来源。六条有针对性的解析回归见 [test_script_parser.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/test_script_parser.py)。

本版同时按当前国家上下文求值原版 `enable`，保留经过核对的原版国家动态名称。领袖来源改为“领袖名：特质名：数值”，姓名用 `[ROOT.GetLeader]` 在显示时读取；其他来源继续显示“修正名 数值”，不加领袖、民族精神、科技等类别前缀。常用区标题、排序和三列／四列结构保持现有要求。

变量型动态来源显示原版当前输入变量值，并非逐来源引擎缓存的导出。原版每日更新修正缓存前，输入值、当前启用条件与国家合计可能暂时不同；正式模组不强制刷新游戏缓存、不写原版输入变量。新增来源的运行验证范围以 [TEST-REPORT.md](D:/projects/hoi4_mod/1/nbv-national-buff/TEST-REPORT.md) 为准，不由生成成功或本说明推定通过。

## 0.1.2 滚动及拖动修复

用户截图已验证 0.1.1 不再堆叠，但滚动条未出现、词条溢出窗口，且标题栏无法拖动。此前结构检查只核验了滚动条资源存在，未覆盖视口自身必须有背景的条件，不能据此认定实际滚动正常。

- 滚动：对照 [原版情报视图](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/countryintelligenceagencyview.gui:644>)、[BUFF UI](E:/Steam/steamapps/workshop/content/394360/3795966002/interface/BDUI_gui_tools.gui:125) 和 [KR 中欧同盟](E:/Steam/steamapps/workshop/content/394360/1521695605/interface/kaiserreich/gui_mitteleuropa.gui:333)，补齐视口 `background`，使用 `GFX_tiled_window_transparent`，设置 `clipping=yes`。背景不能换成带输入穿透的 `GFX_tiled_window_transparent_transparent`。保留 34 高的动态 grid，原 BUFF UI 的动态 grid 同样只有单行初始高度。
- 滚动条：沿用原版 `right_vertical_slider_intel`，按 [原版音乐窗口](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/musicplayer.gui:90>) 设置 `autohide_scrollbars=no`，在短列表时也保留滚动条。
- 拖动：对照 [KR 根级标题结构](E:/Steam/steamapps/workshop/content/394360/1521695605/interface/kaiserreich/gui_mitteleuropa.gui:49) 和 [原版成就窗口](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/achievements.gui:8>)，去掉带背景的子标题容器，将装饰、标题、关闭按钮提升到主窗直属层；装饰和文字设置 `alwaystransparent=yes`，由可移动主窗接收标题处拖动。
- 标题装饰：`GFX_nbv_header_background` 是 [原版 core.gfx](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core.gfx:269>) 的 `GFX_tiled_header_1` 纹理与九宫格参数的私有尺寸定义，984×44；没有复制原版图片。

这些是已实施的源码修复及参考依据。0.1.2 未替代用户执行游戏内拖动、滚轮和拖动滑块的验证；报告明确区分静态结构、隔离引擎加载与实际鼠标操作。

本项目综合参考了普通 BUFF 模组的国家修正读取、BUFF UI 版的编号分发与列表、Kaiserreich 的右侧入口与独立窗口，以及 TNO 的透明计算控件。这些模组提供接口与结构参考；窗口纹理、字体、关闭按钮和滚动条使用 HOI4 原版资源。0.1.6 另行移植 Modifier Icons 汉化版的部分图标素材，具体范围记录于上文与图标清单。运行不依赖这些参考模组。

本机来源文件的 SHA-256、字节数和关键行号保存在 [source-manifest.json](D:/projects/hoi4_mod/1/nbv-national-buff/source-manifest.json)。Workshop 更新可能使行号和文件内容变化；应先核对哈希，再使用本说明中的行号。哈希用于溯源，不代表授权证明或运行测试结果。

## 来源与职责

| 来源 | Steam 页面 | 本机目录 | 参考内容 |
|---|---|---|---|
| BUFF数值可视化 | [Workshop 3440479297](https://steamcommunity.com/sharedfiles/filedetails/?id=3440479297) | `E:\Steam\steamapps\workshop\content\394360\3440479297` | 动态本地化直接读取国家 `modifier@` 值 |
| BUFF数值可视化 UI 版本，描述符名 `buff display ui` | [Workshop 3795966002](https://steamcommunity.com/sharedfiles/filedetails/?id=3795966002) | `E:\Steam\steamapps\workshop\content\394360\3795966002` | 编号数组、动态列表、模板、分类按钮、本地化分发 |
| Kaiserreich | [Workshop 1521695605](https://steamcommunity.com/sharedfiles/filedetails/?id=1521695605) | `E:\Steam\steamapps\workshop\content\394360\1521695605` | 挂载 `raid_filter`、独立浮动窗口、统一开关效果 |
| The New Order: Last Days of Europe | [Workshop 2438003901](https://steamcommunity.com/sharedfiles/filedetails/?id=2438003901) | `E:\Steam\steamapps\workshop\content\394360\2438003901` | 透明 calculator 控件先创建临时数组，动态列表随后消费 |
| TNO: 2WRW-TNO | [Workshop 3449417512](https://steamcommunity.com/sharedfiles/filedetails/?id=3449417512) | `E:\Steam\steamapps\workshop\content\394360\3449417512` | 最初定位 calculator 模式的本机副本；随后在 TNO 本体核对了同构实现 |
| Hearts of Iron IV 原版 | [Steam 394360](https://store.steampowered.com/app/394360/Hearts_of_Iron_IV/) | `E:\Steam\steamapps\common\Hearts of Iron IV` | Scripted GUI 接口、动态变量文档、基础 UI 资源 |

参考某模组的结构不表示本项目依赖该模组，也不表示已经证明与该模组共同加载兼容。原版父容器、同名资源覆盖、`replace_path` 和加载顺序仍可能影响结果。

## 普通 BUFF 版：读取引擎已有国家修正

普通版 [we_l_simp_chinese.yml 第 4 行](E:/Steam/steamapps/workshop/content/394360/3440479297/localisation/simp_chinese/we_l_simp_chinese.yml:4) 的决议分类说明使用 `[?This.modifier@political_power_gain|+]` 一类动态表达式；第 6、8 行分别补充其他分类。决议分类定义见 [common_dicision_categories.txt 第 1 行](E:/Steam/steamapps/workshop/content/394360/3440479297/common/decisions/categories/common_dicision_categories.txt:1)，显示/隐藏动作见 [we_common.txt 第 45 行](E:/Steam/steamapps/workshop/content/394360/3440479297/common/decisions/we_common.txt:45)。

本项目沿用“显示时读取引擎已经维护的国家值”这一取数基础，统一明确为 `ROOT.modifier@<key>`。0.1.1 增加的来源明细仅提供提示文字；合计始终由引擎读取，来源表不参与合计运算。

目标位置：

- [nbv_l_simp_chinese.yml](D:/projects/hoi4_mod/1/nbv-national-buff/localisation/simp_chinese/nbv_l_simp_chinese.yml)：名称、国家修正合计和来源提示的生成表达式。
- [build_mod.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_mod.py)：从统一展示名单生成名称、数值和提示。
- [modifier-format-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/modifier-format-bindings.json)：每项对应的原版格式资料。

本项目没有移入普通版的长字符串排版、决议分类、全局展开 flag 或外部图标引用。读取表达式的存在只能证明采用了该接口；读数作用域、单位、利弊配色和已知变化量仍需逐项核验。国家修正分量也不能直接当成部队最终属性或某次战斗的全部加成。

## BUFF UI 版：编号数组到可重复的界面条目

原 UI 版的调用链为：分类按钮建立编号数组 → `dynamic_lists` 为每个编号创建模板 → `GETBUFFName` 拼出本地化键 → 文字读取国家修正。

| 来源证据 | 原实现 | 本项目目标及改造 |
|---|---|---|
| [BDUI_scripted_gui.txt 第 43–50 行](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_guis/BDUI_scripted_gui.txt:43) | 一个数组绑定一个 grid，条目值写入 `v` | [nbv_scripted_gui.txt](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_guis/nbv_scripted_gui.txt)：将统一行数组 `nbv_display_rows` 绑定到一个 grid；行编号为 `nbv_row_id`，单元格再解析为 `nbv_entry_id` |
| [BDUI_scripted_localisation.txt 第 14–24 行](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_localisation/BDUI_scripted_localisation.txt:14) | 根据编号拼接 `FE_tool_show_buff_name_text_<编号>` | [nbv_scripted_localisation.txt](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_localisation/nbv_scripted_localisation.txt)：按行选择模板，再分别分发每格名称、数值和 tooltip |
| [BDUI_gui_tools.gui 第 124–144 行](E:/Steam/steamapps/workshop/content/394360/3795966002/interface/BDUI_gui_tools.gui:124) | 可滚动的三列列表 | [nbv.gui 第 153 行](D:/projects/hoi4_mod/1/nbv-national-buff/interface/nbv.gui:153)：单个滚动容器与单列外层 grid，每个行模板内部为“常用”三列或“其他修正”四列 |
| [BDUI_gui_tools.gui 第 190–209 行](E:/Steam/steamapps/workshop/content/394360/3795966002/interface/BDUI_gui_tools.gui:190) | 一个文本模板 | [nbv.gui 第 213 行](D:/projects/hoi4_mod/1/nbv-national-buff/interface/nbv.gui:213)：两种行模板；每格名称和数值在同一行的独立区域，整格悬停显示完整文字 |
| [BDUI_scripted_gui.txt 第 63–132 行](E:/Steam/steamapps/workshop/content/394360/3795966002/common/scripted_guis/BDUI_scripted_gui.txt:63) | 五类固定编号区间 | [nbv_scripted_gui.txt](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_guis/nbv_scripted_gui.txt)：政治、工业、陆军、海军、空军、情报六页；采用本项目 559 项名单与稳定排序 |

原版文档说明，`change_scope = yes` 会把当前作用域切到数组元素。原 UI 版虽设置它，实际数组装的是展示编号。本项目明确使用 `change_scope = no`，保留根玩家国家作为取数对象，编号仅用于查找展示项。

原 UI 版把入口挂到 `politics_tab`，主窗口挂到 `top_bar`；本项目改用下面的 KR 右侧入口结构。原版 [Scripted GUI 文档第 102–105 行](<E:/Steam/steamapps/common/Hearts of Iron IV/common/scripted_guis/_documentation.md:102>) 说明 `dirty` 声明会限制 GUI 更新；本项目没有照搬只在开窗和切类时翻转 dirty 的策略，而是使用默认 GUI 更新与 calculator 重建当前页展示数组。默认更新的实际时机及暂停表现由运行测试确认，不能据此承诺逐帧刷新。

## Kaiserreich：右侧独立入口和浮动主窗口

KR 的中欧同盟入口不是原版按钮重命名，而是新的 Scripted GUI 附着到既有 HUD 容器：

- [germany_mitteleuropa.txt 第 6–14 行](E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_guis/germany_mitteleuropa.txt:6)：入口 `parent_window_name = raid_filter`，并绑定独立入口容器。
- [gui_mitteleuropa.gui 第 13–37 行](E:/Steam/steamapps/workshop/content/394360/1521695605/interface/kaiserreich/gui_mitteleuropa.gui:13)：入口布局。
- [gui_mitteleuropa.gui 第 39–87 行](E:/Steam/steamapps/workshop/content/394360/1521695605/interface/kaiserreich/gui_mitteleuropa.gui:39)：独立主窗口、`moveable = yes`、`click_to_front = yes`、关闭按钮与 Esc。
- [MIT effects 第 1064–1081 行](<E:/Steam/steamapps/workshop/content/394360/1521695605/common/scripted_effects/MIT effects (Mitteleuropa).txt:1064>)：统一打开、关闭效果。
- 原版 [country_raids_view.gui 第 1018–1029 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/military_raids/country_raids_view.gui:1018>)：`raid_filter` 的右下锚点、位置及 `clipping = no`。

本项目对应 [nbv_scripted_gui.txt 第 11–25 行](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_guis/nbv_scripted_gui.txt:11) 与 [nbv.gui 第 6–89 行](D:/projects/hoi4_mod/1/nbv-national-buff/interface/nbv.gui:6)。入口和主窗口独立绑定；移动主窗不会移动入口。窗口为 1000×650，入口偏移为 `y = -202`，与所参考 KR 入口的 `-115` 有所区分。这是当前布局选择，不是与所有 HUD 模组无重叠的保证。

[nbv_effects.txt 第 22 行](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_effects/nbv_effects.txt:22) 实现本项目的开关。X、Esc 和入口切换关闭都使用同一关闭效果，保留当前 `nbv_page`。没有移入 KR 的成员国、会议、投票、议程、AI 点击或政治点数操作，也没有使用其鹰徽与会议美术。

## TNO：透明 calculator 与临时显示数组

原先在整个窗口的 `visible` 中准备数组存在跨求值阶段生命周期疑问。后来在本机 TNO 系列源码找到了更接近目标的用法：**先更新透明控件的可见条件，在该条件中准备临时数据，随后动态列表消费同一组数据**。

TNO 本体证据：

1. [TNO_Politics.txt 第 1005–1012 行](E:/Steam/steamapps/workshop/content/394360/2438003901/common/scripted_guis/TNO_Politics.txt:1005)：`assorted_laws_calculator_visible` 调用 `add_to_temp_array`。
2. [同文件第 1023–1028 行](E:/Steam/steamapps/workshop/content/394360/2438003901/common/scripted_guis/TNO_Politics.txt:1023)：`dynamic_lists` 使用 `TNO_assorted_laws_display_temp`。
3. [TNO_SG_Politics_Misc.gui 第 46–57 行](E:/Steam/steamapps/workshop/content/394360/2438003901/interface/TNO_SG_Politics_Misc.gui:46)：透明 `assorted_laws_calculator` 位于列表 grid 之前。

最初定位的 `TNO: 2WRW-TNO` 副本对应 [TNO_Politics.txt 第 1025–1049 行](E:/Steam/steamapps/workshop/content/394360/3449417512/common/scripted_guis/TNO_Politics.txt:1025) 和 [TNO_SG_Politics_Misc.gui 第 73–82 行](E:/Steam/steamapps/workshop/content/394360/3449417512/interface/TNO_SG_Politics_Misc.gui:73)。两个 Workshop ID 在本说明中分别列出，避免将副本当成本体。

本项目采用 [nbv.gui 第 51 行](D:/projects/hoi4_mod/1/nbv-national-buff/interface/nbv.gui:51) 的 `nbv_calculator` 和 [nbv_scripted_gui.txt](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_guis/nbv_scripted_gui.txt) 的 `nbv_calculator_visible`。主窗口 `visible` 只检查开窗状态；[nbv_triggers.txt](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_triggers/nbv_triggers.txt) 的 `nbv_prepare_view` 负责生成当前页高低数组及计数，再将分区标题和内容行依次写入 `nbv_display_rows`。它不缓存国家修正合计，文字仍直接读取当前根国家。

原版 [triggers_documentation.md 第 698 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:698>) 与 [第 2154 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:2154>) 分别记录 `add_to_temp_array` 和 `clear_temp_array`。这些文档和模组例证支持选用该模式，但不能代替本项目当前版本的列表生命周期、求值顺序及刷新测试。

## 原版图形、字体与样式

本项目 [nbv.gfx](D:/projects/hoi4_mod/1/nbv-national-buff/interface/nbv.gfx) 定义三个窗口 sprite 名：`GFX_nbv_tab_normal`、`GFX_nbv_tab_selected` 引用原版普通／浅色按钮纹理，`GFX_nbv_header_background` 引用原版标题纹理并按本窗口尺寸定义九宫格；这些窗口 DDS 不随包复制。0.1.6 的数据图标单独定义在 `nbv_modifier_icons.gfx`，其中来自 Modifier Icons 的贴图随包提供。

| 用途 | 原版定义 | 本项目使用 |
|---|---|---|
| 标签普通／选中背景 | [core.gfx 第 525 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core.gfx:525>)、[第 539 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core.gfx:539>) | [nbv.gfx](D:/projects/hoi4_mod/1/nbv-national-buff/interface/nbv.gfx)：`button_148x34.dds`、`button_148x34_light.dds` 的私有别名 |
| 入口统计图标 | [topbar.gfx 第 357 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/topbar.gfx:357>) | `GFX_ledger_button`，仅保留图标，悬停提示“修正统计” |
| 透明计算控件 | [core.gfx 第 138–145 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core.gfx:138>) | `GFX_tiled_window_transparent_transparent` |
| 主窗、标题和条目背景 | [countrytechtreeview.gfx 第 253 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/countrytechtreeview.gfx:253>)、[core.gfx 第 177 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core.gfx:177>)、[第 269 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core.gfx:269>) | `GFX_tiled_window`、`GFX_tiled_window_small_small`，以及基于 `GFX_tiled_header_1` 的私有标题定义 `GFX_nbv_header_background` |
| 关闭按钮 | [general_stuff.gfx 第 202 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/general_stuff.gfx:202>) | `GFX_closebutton` |
| 滚动条 | [countryintelligenceagencyview.gui 第 1428 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/countryintelligenceagencyview.gui:1428>) | `right_vertical_slider_intel`，与原 BUFF UI 列表使用的滚动条名称一致 |
| 中文字体 | [core_chinese.gfx 第 158 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core_chinese.gfx:158>)、[第 191 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core_chinese.gfx:191>)、[第 279 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/core_chinese.gfx:279>) | `hoi_16mbs`、`hoi_18mbs`、`hoi_24header`；文字颜色使用原版格式规则 |

## 需要保留的实现边界

### 国家切换与页面记忆

开关和页面记录属于国家脚本状态，不是纯客户端偏好。`player_context` 改变后，界面绑定新国家的 flag、变量和 `ROOT`。本项目当前结构可以保留同一国家的页面；新国家没有开窗标记时会关闭，不能据此声称已经实现“切 tag 后保持原窗口及原页面”。曾打开过的新国家则有它自己的记录。

本轮没有在原版公开 Scripted GUI 接口中找到可写的客户端持久开关或稳定玩家 ID，也没有找到公开的 tag 切换回调。原版虽有 [career_profile_has_player_flag](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:2025>)，其实际使用在 [00_ribbons.txt 第 178 行](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ribbons/00_ribbons.txt:178>) 标注为引擎代码设置，不能把它当作已找到的自定义 UI setter。

因此，跨 tag 连续打开、暂停切 tag、多人共同控制同国及观察者行为都必须单列验收。不要改用一个共享全局开关来掩盖这个边界，也不要把国家变量说成客户端隔离状态。

### 0.1.1 统一行列表与紧凑排版

用户提供的 0.1.0 截图证明两组网格发生覆盖，且没有可用滚动条。旧结构使用临时计算的 Y 值移动低优先级标题和网格，其滚动范围没有得到视觉验收。0.1.1 已替换这一实现：`nbv_rows_grid` 是外层唯一动态网格，`max_slots_horizontal = 1`，每个条目占一整行；`NBVRowContainer` 根据行编号选择标题、高优先级三格或低优先级四格模板。所有行按数组顺序排布，不再通过单独移动低网格来拼接高度。

当前滚动区为 970×486，外层行宽 944、行步长 34；“常用”每格 306×30，“其他修正”每格 227×30。名称和数值采用互不重叠的单行文字区域，名称左对齐、数值右对齐，超长名称在格内裁切。原版 `right_vertical_slider_intel` 负责滚动条；分区没有条目时，不加入其标题行。代码见 [build_interface.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_interface.py)、[build_backend.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_backend.py)。网格保留已核对的 `format = UPPER_LEFT` 大小写。

该结构沿用原 BUFF UI 的“一个数组、一个动态 grid、一个滚动容器”基础，并将每个列表元素由一个词条改为一行词条。原版存在多个 grid 共用滚动区的界面，但这些界面可能有专门引擎逻辑，不能用来证明旧版动态 Y 方案正确。新实现仍须检查最长分类底部可达、筛选后滚动范围收缩、切页、拖动和不同缩放；目前不声称已完成鼠标视觉验收。

同一版本还删除页面上下说明文字、筛选与刷新按钮的解释 tooltip，将“隐藏已验零值”改为“隐藏词条”，并把词条提示缩减为名称、合计及非零已知来源。使用限制保留在本文和 README 中，不塞入游戏页面。

### 来源提示接口及适配范围

本机原版 [dynamic_variables_documentation.md 第 496 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:496>) 提供国家 `modifier` 总值读取。[loc_formatter_documentation.md](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/loc_formatter_documentation.md>) 提供 `idea_desc`、`idea_name`、`advisor_desc`、`country_leader_desc`、`tech_effect` 等针对已知对象的文字格式器；它们不是“输入任意修正键，枚举该修正全部来源和贡献”的接口。

原版 [countryarmyview.gui 第 129 行](<E:/Steam/steamapps/common/Hearts of Iron IV/interface/countryarmyview.gui:129>) 有 `modifier_entry`／`modifier_value` 模板，但仅复制这些控件名称，不能给 Scripted GUI 的 559 个修正键自动建立底层来源绑定。当前公开文档与本机参考代码中未找到已验证可用于本项目的通用来源拆分 API。因此 `pdx_tooltip` 绑定本项目生成的文本，按来源定义与当前激活条件输出明细；不假装调用了原生完整来源列表。

0.1.8 由**九张来源表**生成 **31803 条候选来源绑定**，联合覆盖完整注册表中的 **545/559** 个修正键；0.1.8 时的 519 项页面名单中有 505 项、27954 条候选贡献。0.1.5–0.1.7 的八表历史数量为 31012 条。这里的覆盖表示该键至少有一个已适配定义，不表示该键的全部来源均已拆分，也不表示每个候选定义已经逐一通过引擎生命周期测试。运行时变量绑定记录输入表达式和系数，不把表中的系数冒充当前贡献值。

| 来源表 | 适配内容 | 候选贡献数 | 当前激活判断 |
|---|---|---:|---|
| [source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/source-bindings.json) | 法案、民族精神、军种精神等 idea 直接修正 | 11365 | 当前国家 `has_idea = <id>` |
| [leader-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/leader-source-bindings.json) | 执政领袖的国家特质直接修正 | 5362 | `has_country_leader_with_trait = <id>` |
| [advisor-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/advisor-source-bindings.json) | 政治顾问、陆海空军部长、最高统帅部及理论家特质 | 9231 | 人物存在、对应职位实际任职、当前特质存在且该职位的 idea token 已生效 |
| [doctrine-technology-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/doctrine-technology-source-bindings.json) | 当前学说、已达到的精通奖励和完成的路线里程碑；已研发科技 | 学说 379；科技 173 | 学说用 `has_doctrine`，奖励额外核对 `has_mastery_level`，里程碑额外核对 `has_completed_track`；科技核对当前已研发状态 |
| [dynamic-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/dynamic-source-bindings.json) | 国家动态修正常量；正在执行决议的直接修正 | 动态修正 200；决议 872 | 当前国家 `has_dynamic_modifier` 且当前原版 `enable` 成立／缺省；活动决议用 `has_decision` |
| [dynamic-spirit-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/dynamic-spirit-source-bindings.json) | 变量型国家动态修正／民族精神的当前输入 | 4045 | 当前国家持有，当前原版 `enable` 成立／缺省，原版直接引用的输入值非零 |
| [ideology-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/ideology-source-bindings.json) | 当前执政意识形态组的国家修正，包括隐藏国家修正 | 34 | `has_government = <ideology>` |
| [faction-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/faction-source-bindings.json) | 当前阵营章程、宗旨比例及宗旨阶段的国家修正 | 127 | 已在阵营内，章程／宗旨当前生效，并核对原版完成度和阶段区间 |
| [special-source-bindings.json](D:/projects/hoi4_mod/1/nbv-national-buff/tools/data/special-source-bindings.json) | 国家稳定度／战争支持度曲线和和平状态 | 15 | 当前有效状态及原版条件；奇观候选未接入 |

idea 生成器 [build_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_source_bindings.py) 仅提取直接 `modifier` 中非零数值常量，尊重 `name =` 的名称覆盖；整个 idea 含 `do_effect`、traits 或不明确字段时排除，重复来源 ID、重复修正键、变量数值、缺失或歧义中文名也不采用。`allowed`、`available` 和 `cancel` 是选择／移除规则，不替代当前持有判断；法案的 `level` 也不作为数值乘数。0.1.7 及之前，`persia.txt`、`SOV.txt`、`switzerland.txt` 因缺少外层闭合而整文件排除；0.1.8 仅对已核实的文件内容 SHA256 恢复 EOF 闭合，新增 755 条绑定，其他解析失败仍拒绝接入。

领袖生成器 [build_leader_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_leader_source_bindings.py) 只扫描国家领袖特质，不扫描将领个人属性。条件、嵌套、隐藏／指定目标、非数值常量或重复定义等不明确特质被排除。显示格式为 `[ROOT.GetLeader]：特质名：数值`，不缓存人名；英文使用 `: ` 分隔，特质自身换行仍合并为空格。当前执政领袖判断的原版文档见 [triggers_documentation.md 第 3664 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:3664>)；`has_idea` 文档见 [第 4034 行](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:4034>)。

顾问生成器 [build_advisor_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_advisor_source_bindings.py) 建立“人物—职位—特质—国家修正”的绑定。仅招募人物或拥有可选顾问角色不足以显示贡献：先以 `has_character` 保护人物作用域，再检查 `has_advisor_role`、对应 `is_political_advisor`／`is_army_chief`／`is_navy_chief`／`is_air_chief`／`is_high_command`，理论家使用 `is_hired_as_advisor` 并核对角色；同时要求人物当前 `has_trait` 且该角色的 `has_idea` 生效。条件触发器延后读取尚未创建的角色 token，避免对不存在的 token 直接查询。显示名只保留特质名，静态别名展开为单行；不明确角色、跨角色归属不清的特质、动态名称或条件效果排除。接口依据见 [has_advisor_role](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:3064>)、[has_character](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:3410>)、[has_trait](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:4951>) 和 [is_hired_as_advisor](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:5645>)。

学说／科技生成器 [build_doctrine_technology_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_doctrine_technology_source_bindings.py) 仅取国家层直接修正。学说必须当前生效，不能用历史研究或解锁替代；奖励需要达到对应精通等级，里程碑需要完成对应路线，尚未获得的后续奖励不显示。科技只列已研发项目的直接国家贡献，装备、单位类别、州／地方修正以及 `on_research_complete` 等一次性效果不在此处重复统计。依据见 [has_doctrine](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:3748>)、[has_mastery_level](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:4181>)、[has_completed_track](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:3541>)、[has_tech](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:4882>) 和原版 [researched_techs 数组](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:767>)。控制台撤销科技等生命周期行为仍须单独进行引擎验证，不能仅由静态条件推出。

动态修正／决议生成器 [build_dynamic_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_dynamic_source_bindings.py) 将来源绑定到当前国家，排除仅有州／人物添加点的定义；目标决议和带 `scope` 的动态修正也保守排除，因为一个布尔持有条件无法计算同 ID 同时作用于多个目标的实例数。原版 `enable` 的语法树按原有逻辑序列化，并与当前国家持有条件一起求值；缺省视为启用，依赖 `FROM`／`PREV`／`THIS` 等无法保留调用上下文的条件仍排除。原版 [has_dynamic_modifier](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:3775>) 区分普通与目标实例；[has_decision](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:3693>) 明确检查正在执行的已选决议，不能用可见、可选或曾经完成来替代。

静态来源名继续展开别名并合并换行。动态修正名称还接受当前国家／明确国家的 `GetAdjective` 和三个核实过的原版国家名称函数：`NORDIC_get_adjective`、`NORDIC_get_alliance_name`、`IRQ_navy_modifier_key`。这些条目记录 `native_dynamic_name = true`、保留原 `name_loc_key`，通过原版名称键在当前国家上下文求值；不把动态表达式预先写死成另一国家的名称。任意未知函数、州／单位名称、`FROM`／`PREV` 等调用上下文、缺失或歧义中英名称仍省略。此扩展针对动态修正名称，不放宽顾问／决议等其他来源的名称限制。

重建后的作用域审计中，涉及动态修正添加点的文件解析失败数由 5 降为 0，未解决的参数化添加 ID 为 0。固定动态表包含 200 条绑定、90 个来源；变量动态表包含 4045 条绑定、380 个来源、2332 个不同输入变量。合并去重为 445 个动态来源、4245 条贡献映射，其中非恒定当前启用条件 223 条，原版动态名称 116 条绑定、17 个不同来源。这些是源码审计统计，不能代替引擎运行结果。

固定数值和变量型动态来源分别由两张表承担，没有重复绑定。[build_dynamic_spirit_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_dynamic_spirit_source_bindings.py) 复用国家作用域审计与原版启用条件，只接入当前国家持有且原版直接引用标量变量的定义。它按原版明确写出的国家或全局引用取当前输入值，未持有、当前启用条件不成立或输入为零时不显示，不能根据总值残差反推来源。例证为 [wuw_dynamic_modifiers.txt 第 592 行](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/wuw_dynamic_modifiers.txt:592>) 的 `GER_army_modifier`，以及 [德国历史初始化第 262 行](<E:/Steam/steamapps/common/Hearts of Iron IV/history/countries/GER - Germany.txt:262>) 的组织度 0.05、计划速度 0.25、补给消耗 0.15 输入；这只是示例，来源表并非按德国专用名单生成。

原版 [0_dynamic_modifiers.txt 第 27 行](<E:/Steam/steamapps/common/Hearts of Iron IV/common/dynamic_modifiers/0_dynamic_modifiers.txt:27>) 说明动态效果通常每日更新。因此这些来源行表示**当前输入值与当前启用条件，不是已经缓存的逐来源贡献和启用状态**；输入或条件改变后、下一次每日刷新前，来源行之和可能与国家引擎合计不同。正式模组不调用 `force_update_dynamic_modifier`，不修改输入变量，不改变游戏运算时机；无法保留调用上下文的条件仍不输出来源。0.1.8 的稳定度／战争支持度分段来源由单独的状态表承担。

[build_ideology_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_ideology_source_bindings.py) 读取 [00_ideologies.txt](<E:/Steam/steamapps/common/Hearts of Iron IV/common/ideologies/00_ideologies.txt>) 中各意识形态组的国家 `modifiers`，只显式展开同作用域的 `hidden_modifier`。`has_government` 的 [原版文档](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/triggers_documentation.md:4007>) 明确检查当前执政意识形态组，因此不会把党派支持率或领袖子意识形态当成生效条件。法西斯主义的租借紧张度、战时正当化时间、情报泄露和禁运费用由其原版名称标识；`faction_modifiers` 不属于这个国家块，不在此表混入。

[build_faction_source_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_faction_source_bindings.py) 读取 `common/factions` 中的章程与宗旨，要求当前国家在阵营内，并检查 `has_active_rule` 或 `has_faction_goal`。宗旨的比例及反向比例以原版 [faction_manifest_fulfillment](<E:/Steam/steamapps/common/Hearts of Iron IV/documentation/dynamic_variables_documentation.md:346>) 为输入，按定义的系数计算，不重建领土／成员等进度收集算法；阶段奖励额外核对定义区间。阵营目标授予的 idea 或动态修正由实际持有对象显示，避免历史目标重复计数。战区指挥官的部队属性、共享人力池、研究对象和和谈费用对象不纳入。民主政体的 `faction_modifiers` 贸易加成经隔离测试确认：由领袖政体决定并传递给全体成员，已通过 `faction_leader = { has_government = democratic }` 接入。

决议只读取自身直接 `modifier`。若决议、国策或事件授予民族精神／动态修正，明细由实际持有的修正对象提供一次；不会再把授予动作作为另一份相同加成。多个历史途径可能授予同一对象，当前持有状态不能证明最初通过哪次决议或国策获得，因此不反推历史授予者，也不据此补出无法核实的来源名称。

九张来源表记录定义文件、行号、数值原文或输入表达式、激活表达式、SHA-256 和排除原因。[build_mod.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_mod.py) 将它们生成为 [nbv_source_localisation.txt](D:/projects/hoi4_mod/1/nbv-national-buff/common/scripted_localisation/nbv_source_localisation.txt)：来源当前有效且数值非零时输出一行，领袖来源为“领袖名：特质名：数值”，其他来源为“修正名 数值”，否则输出空文本；不加“领袖”“科技”“民族精神”等来源类别前缀。零值和无法拆分的差额完全省略，不生成“其他来源”行。来源行可能无法解释合计全部变化；合计始终直接使用 `ROOT.modifier@<key>`，不会按有限来源表重新求和。

这些明细只适用于扫描的原版来源定义。如果其他模组改写同名 idea、角色、特质、学说、科技、动态修正、决议、意识形态或阵营条款，激活判断不能发现定义内容已经被覆盖，已有贡献值或输入表达式便可能失配。大型模组需要独立来源适配和测试；原版或参考定义更新后应重新生成并核验。来源定义核查、来源显示运行测试、国家合计读取测试必须分别报告；具体已测试样本和未通过项以 [TEST-REPORT.md](D:/projects/hoi4_mod/1/nbv-national-buff/TEST-REPORT.md) 为准，不能把样本通过或候选覆盖等同于全部来源实时拆分通过。

### 0.1.4 原生百分点格式

原格式生成器将 `%` 和 `%%` 都归一为 `%`，会丢失原版“原值附加百分号”的语义。本版 [build_format_bindings.py](D:/projects/hoi4_mod/1/nbv-national-buff/tools/build_format_bindings.py) 保留两种标记：普通 `%` 的显示乘数为 100，`%%` 的显示乘数为 1；原始合计和来源输入均不改写。受影响的五项是 `civilian_intel_to_others`、`army_intel_to_others`、`navy_intel_to_others`、`airforce_intel_to_others` 与 `subjects_autonomy_gain`，在绑定表中单列为 `percentage_points`，其余 554 项格式代码保持不变。

原版模板证据见 [情报泄露第 1712 行](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/english/modifiers_l_english.yml:1712>) 的 `$RIGHT|-=%%1$` 和 [自治增长第 931 行](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/english/modifiers_l_english.yml:931>) 的 `$RIGHT|+=%%1$`。原版直接变量也使用 `%%`，例如 [印度国策第 992 行](<E:/Steam/steamapps/common/Hearts of Iron IV/localisation/english/goe_focus_l_english.yml:992>) 的 `[?RAJ_the_government_of_india_act_pp_bonus_based_on_compliance|+=%%0]`；旧 [BUFF UI 第 143 行](E:/Steam/steamapps/workshop/content/394360/3795966002/localisation/simp_chinese/BDUI_l_simp_chinese.yml:143) 则用原值数字后接字面 `%`。本版采用原生双百分号格式，具体正负数与小数显示的运行验证见测试报告。

0.1.3 的科技撤销样例验证了一个引擎边界：撤销后 `has_tech` 仍可能返回真，而 `researched_techs` 已移除该科技。实现同时核对两者，测试中的来源行已随实际贡献消失，重新研究后恢复。顾问还排除了 15 组已核实的动态领袖／顾问特质交集，避免同一人物的特质跨职位误归因；排除证据保存在顾问来源表中。未知动态作用域仍不宣称已穷尽。

以上边界和参考关系在本文件中保留；最终运行测试情况、通过范围和未通过项应由独立测试记录说明。
