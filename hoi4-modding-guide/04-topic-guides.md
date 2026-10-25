# 04 专题制作路线

下表是制作路径与核验要点。目录/字段对照依据是本地 CWTools 规则和 Wiki Modding 总页；链接到专题 Wiki 是继续查阅入口，**本次多数专题正文因访问挑战未能读取**。因此地图二进制格式、复杂系统的所有参数和最低版本不在本章冒充已确认。

## 1. 内容模组

| 专题 | 主要目录/定义 | 最小制作路线 | 验收重点 | 参考 |
|---|---|---|---|---|
| 事件 | `events/`、`country_event` | namespace → ID → title/desc → option → effect → localisation | 触发对象、条件、重复发放、延迟、选项文字 | [Wiki](https://hoi4.paradoxwikis.com/Event_modding) · [规则](references/cwtools-hoi4-config/Config/events.cwt) |
| 民族精神/理念 | `common/ideas/` | 定义 idea → modifier → 使用效果授予/移除 → 本地化 | 持续数值、适用对象、取消条件、重复添加 | [Wiki](https://hoi4.paradoxwikis.com/Idea_modding) · [规则](references/cwtools-hoi4-config/Config/common/ideas.cwt) |
| 决议 | `common/decisions/categories/`、`common/decisions/` | category → decision → visible/available → cost → complete_effect | 分类与决议都可见、成本、任务期限、AI 权重 | [Wiki](https://hoi4.paradoxwikis.com/Decision_modding) · [规则](references/cwtools-hoi4-config/Config/common/decisions.cwt) |
| 国策 | `common/national_focus/` | focus_tree 选择 → focus ID/位置 → 前置/互斥 → reward → 图标/文本 | 选对国家、前置无环、互斥、奖励 scope、布局 | [Wiki](https://hoi4.paradoxwikis.com/National_focus_modding) · [规则](references/cwtools-hoi4-config/Config/common/national_focus.cwt) |
| 国家 | `common/country_tags/`、`common/countries/`、`history/countries/` | 注册 TAG → 外观/名字 → 历史政治/首都 → 领土 → 人物/部队 | tag 唯一、首都与州合法、控制权/所有权/核心关系、旗帜 | [Wiki](https://hoi4.paradoxwikis.com/Country_creation) · [国家规则](references/cwtools-hoi4-config/Config/common/countries.cwt) |
| 人物/顾问/将领 | `common/characters/`、国家历史或相关效果 | 定义人物 → 角色与肖像 → 正确招募/启用入口 | 定义存在不等于国家已拥有；任职条件、角色与肖像 | [Wiki](https://hoi4.paradoxwikis.com/Character_modding) · [规则](references/cwtools-hoi4-config/Config/common/characters.cwt) |
| 科技 | `common/technologies/` 等 | 科技定义 → 解锁/效果 → 前置 → UI/本地化 | 年份、依赖、实际解锁、AI 研究、UI 布局 | [Wiki](https://hoi4.paradoxwikis.com/Technology_modding) · [规则](references/cwtools-hoi4-config/Config/common/technologies.cwt) |
| 装备与单位 | `common/units/`、装备相关子目录、`history/units/` | 装备原型 → 具体型号/模块 → 科技解锁 → 部队编制与库存 | archetype 先存在、类型引用、生产、运输/补给、实际作战 | [装备 Wiki](https://hoi4.paradoxwikis.com/Equipment_modding) · [装备规则](references/cwtools-hoi4-config/Config/common/equipment.cwt) |

国家历史、州历史和部队部署相互引用。读取 [country_history.cwt](references/cwtools-hoi4-config/Config/history/country_history.cwt)、[states.cwt](references/cwtools-hoi4-config/Config/history/states.cwt)、[oobs.cwt](references/cwtools-hoi4-config/Config/history/oobs.cwt) 时，应沿着引用关系检查，而不只检查单个文件是否括号配对。

国策的 `shared_focus` 与 `joint_focus` 不应混为一谈。官方 2023 年开发日志介绍了 joint focus 的新增行为；复杂功能按目标游戏版本阅读说明与原版用例。[官方开发日志](https://steamcommunity.com/games/394360/announcements/detail/3648531811786549063)

## 2. 地图与历史数据

**先分清 province（省份）、state（州）和 strategic region（战略区域）。** 地图通常在 `map/`，州归属和州内省份集合在 `history/states/`，开局部队在 `history/units/`。补给点和铁路也有 `map/` 下的独立数据，不能以为改完州历史就全部完成。[Wiki 目录说明](https://hoi4.paradoxwikis.com/Modding#Folder_structure)

推荐顺序：

1. 保留干净基线，先做“把现有省份划入一个新州”的小实验。
2. 核对所有 ID 与引用，避免同一省份在冲突的州定义中出现。
3. 对照原版和当前教程，核对战略区域、地形、建筑位置、港口、补给节点、铁路、相邻关系等关联数据。
4. 使用 Nudger 时确认输出实际落在**用户数据目录**，再把需要的文件归入模组。
5. 单独检查 `MAP_ERROR`，并在不带 `-debug` 的正常启动中复测；调试模式容忍某些地图错误，不能因此判定发布版正常。

新建省份、替换整张世界地图、改变尺寸都比改州复杂。请逐文件核对 `provinces.bmp`、`definition.csv`、地形/高度/河流等资源的目标版本要求；本包没有在未读到专题正文的情况下给出通用位深、尺寸或调色板“万能配置”。[地图 Wiki](https://hoi4.paradoxwikis.com/Map_modding) · [州 Wiki](https://hoi4.paradoxwikis.com/State_modding) · [本地地图规则](references/cwtools-hoi4-config/Config/map/map_consolidated.cwt)

官方进阶教程从地图入门：[Intermediate Part 1](https://www.youtube.com/watch?v=vU4_5X1JEbM)。本次核验了标题和入口，没有下载或逐帧观看视频。

## 3. UI、图片和声音

| 需求 | 连接关系 | 检查点 |
|---|---|---|
| 显示一个图标 | `gfx/` 图片 → `interface/*.gfx` 的 sprite → 使用该 sprite 的对象 | `GFX_` 名、路径、大小写、文件实际格式 |
| 调整界面布局 | `interface/*.gui` → container/button/text 等元素 | 原版控件层级、锚点、分辨率、重叠与文字溢出 |
| 做交互界面 | `.gui` 的表现 + `common/scripted_guis/` 的脚本 | context、可见条件、可点击条件、效果作用域与刷新 |
| 国家旗帜 | `gfx/flags/` 及对应变体/尺寸目录 | 国家/意识形态/外观 tag 的命名匹配和 TGA 要求 |
| 音乐 | `music/` 的资源与播放定义 | 格式、引用、播放条件与电台规则 |
| 音效 | `sound/` 的资源与定义 | 名称、触发入口、循环/音量及素材授权 |

`.gfx` 和 `.gui` 是文本定义，DDS/TGA 才是资源文件。添加一张图片通常不意味着游戏自动使用它。[Wiki GFX](https://hoi4.paradoxwikis.com/Modding#GFX)

详查：[GUI 规则](references/cwtools-hoi4-config/Config/interface/gui.cwt)、[GFX 规则](references/cwtools-hoi4-config/Config/interface/gfx.cwt)、[scripted GUI 规则](references/cwtools-hoi4-config/Config/common/scripted_guis.cwt)、[音乐规则](references/cwtools-hoi4-config/Config/music.cwt)、[声音规则](references/cwtools-hoi4-config/Config/sound.cwt)。

官方 2024 年 Performance and Modding 日志介绍了更复杂的 GUI/脚本 tooltip 能力。此类功能应对照目标版本，不能从旧教程推断所有参数仍相同。[官方日志](https://steamcommunity.com/games/394360/announcements/detail/4445708897933590809)

## 4. AI 和较新的系统

AI 不只是为选项写一个很大的 `ai_will_do`。需要检查可用条件、权重、计划/策略、资源成本和实际长期行为。观察者模式可以辅助测试，但 Wiki 提醒它会影响 AI 表现，不能代替常规玩家国家运行。[控制台参考](references/wiki/Console_commands.txt)

| 系统 | 本地规则入口 | 使用前确认 |
|---|---|---|
| AI 策略 | [ai_strategy.cwt](references/cwtools-hoi4-config/Config/common/ai_strategy.cwt) | 策略类型、目标 scope、启用/撤销条件 |
| 军工组织 MIO | [military_industrial_organizations.cwt](references/cwtools-hoi4-config/Config/common/military_industrial_organizations.cwt) | 游戏版本、组织解锁、特质树、装备匹配 |
| 权力平衡 BOP | [bop.cwt](references/cwtools-hoi4-config/Config/common/bop.cwt) | 区间、方向、阈值效果、移除与恢复 |
| 特别计划 | [special_projects.cwt](references/cwtools-hoi4-config/Config/common/special_projects.cwt) | 设施、项目引用、阶段/效果和目标版本 |
| 突袭 | [raids.cwt](references/cwtools-hoi4-config/Config/common/raids.cwt) | 目标、行动条件、资源和结果 |
| 学说扩展 | [doctrine_tracks.cwt](references/cwtools-hoi4-config/Config/common/doctrine_tracks.cwt) | 新旧版本数据结构差异 |
| 集合与数学函数 | [进阶接口文档](references/api/advanced.md) | 支持版本、表达式类型和上下文 |

这些文件表明**本次取得的社区规则覆盖了相应系统**，不证明用户安装的任意版本或 DLC 组合都能使用全部功能。

## 5. 推荐学习顺序

事件与本地化 → 民族精神 → 决议 → 小型国策分支 → 人物/国家历史 → 科技/装备 → 地图 → scripted GUI 与复杂系统。每一步保留一个能独立复现、能通过日志和游戏表现检查的小模组。

官方 [初学者播放列表](https://www.youtube.com/playlist?list=PL6EAZcF5cWbg57Srq6BTVvguMl6YfP9pG) 和 [进阶播放列表](https://www.youtube.com/playlist?list=PL6EAZcF5cWbiwdGsdZs-C3o6-uwgD4RKs) 是课程路线；本地规则与目标游戏文档是编码时的查阅工具。
