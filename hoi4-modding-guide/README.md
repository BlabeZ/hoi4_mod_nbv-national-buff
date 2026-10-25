# 钢铁雄心 IV 模组制作指南与离线参考

整理日期：**2026-10-24（Asia/Singapore）**。面向 Windows、本地开发、中文内容模组。所有链接和判断均对应本次检索，不能代替未来游戏版本的复核。

HOI4 模组的主要制作方法是：建立独立模组目录，按游戏目录组织数据文件，使用游戏支持的脚本、资源和本地化格式，通过启动器加载，再用游戏日志和实际运行验收。这里的“接口”主要是 **scope、trigger、effect、modifier、on_action 和各类数据定义**，不是一个统一的 HTTP API 或可任意执行的插件 SDK。[Wiki：Modding](https://hoi4.paradoxwikis.com/Modding)

## 阅读顺序

| 文档 | 解决的问题 |
|---|---|
| [BUFF 修正清单与统计模组需求](buff-statistics-mod/README.md) | 当前确认的 559 项最终清单、配套数据，以及统计模组的范围、界面、刷新与验收建议 |
| [01 制作标准与目录](01-standards.md) | 目录、描述符、覆盖规则、编码、命名与版本 |
| [02 脚本接口与查阅方法](02-scripting-api.md) | 条件、效果、作用域、修正、钩子、变量如何配合 |
| [03 从零做一个小模组](03-first-mod.md) | 创建、放置文件、触发事件、观察效果、排错 |
| [04 专题制作路线](04-topic-guides.md) | 国策、决议、国家、人物、科技、装备、地图、UI、音效 |
| [05 调试、兼容与发布](05-debug-release.md) | 日志、最小复现、性能、补丁迁移、发布验收 |
| [06 来源与核验记录](06-sources.md) | 官网、论坛、Wiki、GitHub、官方教程及访问状态 |
| [07 Kaiserreich 中欧同盟 GUI 源码分析](07-kaiserreich-mitteleuropa-gui.md) | 本机截图对应代码、右侧按钮挂载、独立窗口开关及议程交互 |
| [08 BUFF 数值可视化两版源码分析](08-buff-visualization-mods.md) | 模组目录、国家修正读取、覆盖范围、刷新条件及独立统计页面 |
| [原版修正完整目录与重要词条](vanilla-modifier-catalog/README.md) | 4,484 个具体修正键、六类归档、源码频次、模组覆盖与重要候选 |
| [国家全局 BUFF 二次筛选](vanilla-modifier-catalog/global-buff-review/README.md) | 国策／精神来源追踪、全局展示白名单、其他全国来源、排除项目及原因 |
| [2026-10-25 展示名单修订](vanilla-modifier-catalog/global-buff-review/user-revision-2026-10-25.md) | 无名隐藏、指定增删、同名词条区分，以及设计商与天气的国家分量边界 |
| [示例文件](examples/README.md) | 事件、民族精神、可复用条件和效果、中英本地化 |
| [检查结果](VERIFICATION.md) | 本地资料与示例实际做过哪些检查 |

## 离线参考

| 资料 | 本地位置 | 说明 |
|---|---|---|
| Wiki 模组总指南 | [Modding.txt](references/wiki/Modding.txt) | 正文快照，修订号 105601，页面最后修改 2026-10-17 |
| Wiki 控制台命令 | [Console_commands.txt](references/wiki/Console_commands.txt) | 正文快照，修订号与时间见文件头 |
| Effects | [effects.md](references/api/effects.md) | 上游文档中的 553 个条目 |
| Triggers | [triggers.md](references/api/triggers.md) | 上游文档中的 598 个条目 |
| Modifiers | [modifiers.md](references/api/modifiers.md) | 上游文档中的 764 个条目 |
| 进阶接口 | [advanced.md](references/api/advanced.md) | 上游的数学表达式、集合、常量、本地化等文档 |
| 机器可读索引 | [inventory.json](references/api/inventory.json) | 三大类共 1,915 条文档记录，不代表引擎接口总数 |
| CWTools 配置 | [上游 README](references/cwtools-hoi4-config/README.md)、[别名位置索引](references/api/cwt-alias-index.json) | 固定提交的 Config、README、LICENSE，共 116 个文件 |

CWTools 快照提交：`297dd69c42aabe10078a8b7ab7f2d07ee631d4ef`。这是社区维护的校验规则和文档快照，其精确目标游戏版本没有在本次检索中确认。规则通过不等于游戏运行通过，规则报错也可能是误报。[上游项目](https://github.com/cwtools/cwtools-hoi4-config)

## 核验边界

- **已核验**：官网入口、上述两个 Wiki 正文、固定提交的 CWTools 规则和项目说明，以及部分官方开发日志的搜索索引正文、官方视频标题与播放列表入口。
- **仅保留导航**：多数专题 Wiki 和部分论坛正文受到 Client Challenge / 访问限制，未伪装成已经逐页读过；每条状态见来源记录。
- **本机源码补充核验**：已确认安装版本 v1.19.3.0，并完成修正目录、国策／民族精神和模组源码分析。
- **尚未执行**：启动 HOI4、运行示例、逐项验证修正读数、验证 DLC 组合、发布到创意工坊。示例是供实践验证的教学模板。
- **标准的含义**：将“格式约束”“社区工具规则”“工程建议”分开使用。本资料不自称 Paradox 发布的统一认证标准，也不声称覆盖所有引擎接口。

## 查找与维护

在本目录执行以下只读查询即可定位接口：

```powershell
rg -n 'add_political_power|has_country_flag' references/api
rg -n -B 3 -A 10 'alias\[effect:country_event\]' references/cwtools-hoi4-config/Config
rg -n 'replace_path|supported_version|UTF-8' references/wiki/Modding.txt
```

`tools/build_reference.py` 可从已保存的配置重建接口 Markdown 和索引；只使用 Python 标准库。`tools/fetch_wiki.py` 需要 `requests`，显式运行时才会联网刷新 Wiki，并记录失败页面。刷新前先备份已有资料，避免覆盖本次取证记录。

## 署名与许可

Wiki 正文由 HOI4 Wiki 社区贡献者编写，按页面声明使用 **CC BY-SA 3.0**；每份快照头部包含原文、固定修订和贡献历史链接。快照经过 HTML → 纯文本转换，图片、导航和脚本已移除，复杂表格应回到原页面核对。中文指南中对 Wiki 的改写部分同样按 CC BY-SA 3.0 提供，变更形式为中文整理、解释与重组。[许可说明](https://creativecommons.org/licenses/by-sa/3.0/)

CWTools 文件及其重排输出保留上游 [MIT LICENSE](references/cwtools-hoi4-config/LICENSE)。本包原创教学代码和辅助脚本使用 [MIT LICENSE](examples/LICENSE)。官网、视频和论坛仅提供链接及简短研究笔记，未整页转载。
