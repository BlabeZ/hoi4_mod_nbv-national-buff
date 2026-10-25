# 06 来源与核验记录

检索日期：**2026-10-24**。检索渠道包含公开网页搜索、官网/官方公告、Wiki 页面直接读取、GitHub 网页、Git 远端提交查询和原始文件下载。

## 1. 如何理解证据状态

| 状态 | 含义 |
|---|---|
| 正文已读 | 得到了实际页面/文件内容，能够支撑本资料的归纳 |
| 固定快照 | 额外保存了修订号或 Git commit，可定位本次依据 |
| 索引正文 | 搜索服务返回了文章正文片段；未声称整篇直读或离线保存 |
| 入口已核验 | 确认官网链接、视频标题、项目存在等，不代表已观看完整课程 |
| 受限/待复核 | 返回访问挑战、401 或受限内容，未获得正文 |

可信度需结合问题判断：Paradox 官方内容用于了解产品入口和版本变化；Wiki 是**社区维护的参考**；CWTools 是**社区静态规则**，都不能代替用户目标版本的运行结果。专题 Wiki 页面受限时，本资料用已读总览与原始规则文件确认基础结构，不用搜索摘要猜完整参数。

## 2. Paradox 官网与官方发布

| 编号 | 来源 | 本次确认的内容 | 状态 |
|---|---|---|---|
| P01 | [HOI4 官网](https://www.paradoxinteractive.com/games/hearts-of-iron-iv/about) | 官方页面提供 Forums、Community Wiki、Mods 入口；官网本身不是完整脚本手册 | 正文已读 |
| P02 | [HOI4 官方论坛入口](https://forum.paradoxplaza.com/forum/forums/hearts-of-iron-iv.844/) | 官网关联的论坛入口 | 入口；未全面读取论坛 |
| P03 | [Developer Diary: Modding!，2023-09-13，官方 Steam 公告](https://steamcommunity.com/games/394360/announcements/detail/3648531811786549063) | joint focus 和部分脚本能力随版本扩展 | 索引正文；直接页面正文受限 |
| P04 | [P03 的 Paradox 论坛原帖](https://forum.paradoxplaza.com/forum/developer-diary/developer-diary-modding.1598797/) | 保留官方原帖以供后续复核 | Client Challenge |
| P05 | [Developer Diary: Performance and Modding，2024，官方 Steam 公告](https://steamcommunity.com/games/394360/announcements/detail/4445708897933590809) | 开发者讨论性能与新的 tooltip 能力 | 索引正文；直接页面正文受限 |
| P06 | [HOI4 Dev Diary: Modding Changes，1.11 时代](https://forum.paradoxplaza.com/forum/developer-diary/hoi4-dev-diary-modding-changes.1495215/) | 历史版本变更查阅入口 | 受限，仅作导航 |
| P07 | [Developer Diary: Modding，1.12 时代](https://forum.paradoxplaza.com/forum/developer-diary/developer-diary-modding.1540232/) | 历史版本变更查阅入口 | 受限，仅作导航 |
| P08 | [Mods won't load / Mod load order failed](https://support.paradoxplaza.com/hc/en-us/articles/360019724999-Mods-won-t-load-Mod-load-order-failed) | 官方启动器加载故障排查；不能直接当一般开发步骤执行 | 搜索索引正文已读 |
| P09 | [Paradox Mods](https://mods.paradoxplaza.com/Any) | 官方模组平台入口 | 搜索索引与官网链接 |

本资料没有确认“截至今天的最新稳定补丁号”，也没有把 2023/2024 年日志当成当前版本的完整 API 规范。开发日志说明某功能被引入，不代表后续行为永远不变。

## 3. 官方教程

播放列表链接同时出现在已读的 Wiki Modding 总览中，单集标题通过网页搜索核验。这里只做学习路线整理，未下载视频、逐帧观看或转录全部课程。

| 入口 | 用途 |
|---|---|
| [Beginner's Modding Guide 播放列表](https://www.youtube.com/playlist?list=PL6EAZcF5cWbg57Srq6BTVvguMl6YfP9pG) | 从建立模组开始 |
| [Part 1 — Getting Started](https://www.youtube.com/watch?v=E7zIU3L2eUs) | 基础环境与入门，搜索记录显示发布于 2024-08-20 |
| [Part 2 — Events & National Spirits](https://www.youtube.com/watch?v=BuIycVRxrO4) | 事件、民族精神与本地化 |
| [Intermediate Modding Guide 播放列表](https://www.youtube.com/playlist?list=PL6EAZcF5cWbiwdGsdZs-C3o6-uwgD4RKs) | 地图及其他进阶专题 |
| [Intermediate Part 1 — Map modding](https://www.youtube.com/watch?v=vU4_5X1JEbM) | 地图、州与关联数据的学习入口 |

视频内 UI、安装路径、原版文件名或接口可能对应拍摄时的版本，实践时应核对当前安装内容。

## 4. Wiki 正文快照

| 来源 | 核验与本地文件 |
|---|---|
| [Modding](https://hoi4.paradoxwikis.com/Modding) | **全文取得**；修订号 `105601`；页面最后修改 2026-10-17；[离线正文](references/wiki/Modding.txt) |
| [Console commands](https://hoi4.paradoxwikis.com/Console_commands) | **全文取得**；修订号和修改时间见 [离线正文头部](references/wiki/Console_commands.txt) |

两个页面均从官方域名直接取得，不是 GitHub 镜像。页面声明 CC BY-SA 3.0；每份快照保存原始 URL、固定 oldid、贡献者历史、取得时间和转换说明。HTML 转换保留正文和代码文本，表格使用制表符分列，未保留图片和交互布局。

网页搜索工具最初对 Wiki 返回 401；直接 HTTP 读取上述两个页面成功。其他请求虽然部分返回 HTTP 200，但内容是 **Client Challenge**，没有将它们误判为已读取。完整请求记录见 [sources-wiki.json](sources-wiki.json)，其中失败 URL 只是尝试记录，不能证明候选页面一定存在。

## 5. Wiki 专题导航（正文待复核）

以下是进一步查阅入口。大多数已由 Modding 总页的链接确认导航位置，但本次未取得专题正文；没有离线全文文件。

| 主题 | 链接 |
|---|---|
| 基础接口 | [Scopes](https://hoi4.paradoxwikis.com/Scopes)、[Triggers](https://hoi4.paradoxwikis.com/Triggers)、[Effect](https://hoi4.paradoxwikis.com/Effect)、[Modifiers](https://hoi4.paradoxwikis.com/Modifiers) |
| 编码与文本 | [Localisation](https://hoi4.paradoxwikis.com/Localisation)、[Scripted localisation](https://hoi4.paradoxwikis.com/Scripted_localisation) |
| 复用与状态 | [Scripted trigger](https://hoi4.paradoxwikis.com/Scripted_trigger)、[On actions](https://hoi4.paradoxwikis.com/On_actions)、[Data structures](https://hoi4.paradoxwikis.com/Data_structures) |
| 事件与决议 | [Event modding](https://hoi4.paradoxwikis.com/Event_modding)、[Decision modding](https://hoi4.paradoxwikis.com/Decision_modding) |
| 国策与理念 | [National focus modding](https://hoi4.paradoxwikis.com/National_focus_modding)、[Idea modding](https://hoi4.paradoxwikis.com/Idea_modding) |
| 国家和人物 | [Country creation](https://hoi4.paradoxwikis.com/Country_creation)、[Character modding](https://hoi4.paradoxwikis.com/Character_modding) |
| 科技和装备 | [Technology modding](https://hoi4.paradoxwikis.com/Technology_modding)、[Equipment modding](https://hoi4.paradoxwikis.com/Equipment_modding)、[Unit modding](https://hoi4.paradoxwikis.com/Unit_modding)、[Division modding](https://hoi4.paradoxwikis.com/Division_modding) |
| 地图和州 | [Map modding](https://hoi4.paradoxwikis.com/Map_modding)、[State modding](https://hoi4.paradoxwikis.com/State_modding)、[Strategic region modding](https://hoi4.paradoxwikis.com/Strategic_region_modding) |
| 图形和交互 | [Interface modding](https://hoi4.paradoxwikis.com/Interface_modding)、[Scripted GUI modding](https://hoi4.paradoxwikis.com/Scripted_GUI_modding)、[Graphical asset modding](https://hoi4.paradoxwikis.com/Graphical_asset_modding) |
| AI 和常量 | [AI modding](https://hoi4.paradoxwikis.com/AI_modding)、[Defines](https://hoi4.paradoxwikis.com/Defines) |
| 音频 | [Music modding](https://hoi4.paradoxwikis.com/Music_modding)、[Sound modding](https://hoi4.paradoxwikis.com/Sound_modding) |
| 其他系统 | [Military industrial organization modding](https://hoi4.paradoxwikis.com/Military_industrial_organization_modding)、[Balance of power modding](https://hoi4.paradoxwikis.com/Balance_of_power_modding)、[Doctrine modding](https://hoi4.paradoxwikis.com/Doctrine_modding) |

`Mod structure` 在已读总览中是 [Modding 页内章节](https://hoi4.paradoxwikis.com/Modding#Mod_structure)。本次早期也尝试了独立 URL，它只保留在请求日志中，不作为已确认的独立页面推荐。

## 6. GitHub 原始项目

| 编号 | 项目 | 查阅结果与用途 | 保存情况 |
|---|---|---|---|
| G01 | [cwtools/cwtools-hoi4-config](https://github.com/cwtools/cwtools-hoi4-config) | `.cwt` 语法/作用域/引用规则；维护者说明配置方式和误报边界 | 保存 Config、README、MIT LICENSE，固定 commit |
| G02 | [cwtools/cwtools-vscode](https://github.com/cwtools/cwtools-vscode) | 语言服务、补全、定义跳转、作用域和本地化检查 | 读 README；远端 HEAD 为 `364beae5e3c1edfd6fe2f7e5701e8df93c9e45c5` |
| G03 | [herbix/hoi4modutilities](https://github.com/herbix/hoi4modutilities) | 地图、国策、事件、科技、MIO、GUI、GFX 及图像预览 | 读项目说明；远端 HEAD 为 `1fcd19944d5a6940c53e3dac34ed6e1b5e403dab` |
| G04 | [cwtools/cwtools-action](https://github.com/cwtools/cwtools-action) | CI 静态检查的候选方案 | 项目说明/索引已读；未配置或运行 |
| G05 | [MillenniumDawn/Millennium-Dawn](https://github.com/MillenniumDawn/Millennium-Dawn) | 大型真实模组仓库与其维护文档入口 | 仅仓库级查阅；未全面审计代码，未复制资源 |
| G06 | [hoi4-ai-modding-kit setup 文档](https://github.com/Anatoli27149/hoi4-ai-modding-kit/blob/main/docs/setup.md) | 补充定位游戏 `documentation/` 的说明 | 搜索索引正文已读；未安装该工具 |

G01 的固定来源：[commit 297dd69c42aabe10078a8b7ab7f2d07ee631d4ef](https://github.com/cwtools/cwtools-hoi4-config/tree/297dd69c42aabe10078a8b7ab7f2d07ee631d4ef)。GitHub API 请求遇到匿名限流，因此改用 `git ls-remote` 确认提交，并从该提交下载公开源文件。没有把 API 限流错误解释为仓库不存在。

下载存储的是数据与文本，不运行仓库程序。`references/github-snapshot.json` 记录范围；`references/api/` 由上游 `script_documentation.json` 重排，原始数据仍保留。

## 7. 关键结论到证据的对应

| 结论 | 直接依据 |
|---|---|
| 模组目录对应原版目录，外部描述符指定根目录 | Wiki Modding：Loading files / Mod structure |
| 同路径文件替换与重复对象 ID 的解释不是一回事 | Wiki Modding：Loading files |
| localisation 需要 BOM、语言后缀和首行标识 | Wiki Modding：Guidelines / Localisation |
| trigger、effect、scope、modifier 各有用途 | Wiki Modding：Code structure；CWT scope 与 alias 定义 |
| on_action 的作用域随钩子而异 | G01 `Config/on_actions.cwt` |
| CWTools 并非引擎官方完整规范 | G01 README 的工具定位与限制 |
| 新版本会增加和改变脚本能力 | P03、P05 官方开发日志 |
| 游戏测试不能被静态检查替代 | 本资料的工程验收建议；已明确和引擎规则区分 |

## 8. 后续复核办法

每次升级游戏时补记版本、DLC、分支、checksum、随游戏文档文件名；比对被覆盖的原版文件；重新检查官方变更日志；对关键接口做最小实验。如果刷新本包来源，请保留旧的修订号/commit 与日期，再生成新快照，避免把不同版本的证据混为一套。
