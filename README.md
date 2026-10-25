# HOI4 模组制作资料

[GitHub 仓库](https://github.com/BlabeZ/hoi4_mod_nbv-national-buff) · [Steam 创意工坊](https://steamcommunity.com/sharedfiles/filedetails/?id=3826858105)

Git 管理范围是整个工作区根目录，本机位置为 `D:\projects\hoi4_mod\1`。仓库包括 `nbv-national-buff/` 模组源码、`hoi4-modding-guide/` 研究资料、`outputs/` 排序文档、`nbv-test-workspace/` 测试脚本和证据、`dist/` 发布包及根目录图片。依赖缓存、隔离游戏运行目录和本机启动器数据库由 `.gitignore` 排除，保留在本机。

大型研究 JSON 与 `dist/` 中的 ZIP 使用 Git LFS。完整获取工作区时，在安装 Git LFS 后执行：

```powershell
git lfs install
git clone https://github.com/BlabeZ/hoi4_mod_nbv-national-buff.git
cd hoi4_mod_nbv-national-buff
git lfs pull
```

模组安装和打包命令从工作区根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\nbv-national-buff\install-local.ps1
python .\nbv-national-buff\tools\package_mod.py
```

本地整理入口：[HOI4 模组制作指南](hoi4-modding-guide/README.md)。

当前模组：[国家 BUFF 统计 UI](nbv-national-buff/README.md)，当前展示 528 项修正，基础注册表保留 559 项；提供右侧独立窗口、六页导航、常用三列／其他四列布局和国家页面记忆。源码目录固定为 `nbv-national-buff`。运行安装脚本后，启动器使用游戏文档 `mod` 目录中的独立副本；启动器重命名会同步改安装副本及外部 `.mod` 名称，不影响项目源码。更新源码后需重新安装。安装、源码和验证边界见模组说明与测试报告。

需求与研究依据：[BUFF 修正清单与统计模组需求](hoi4-modding-guide/buff-statistics-mod/README.md)，包括最终 559 项六类清单、配套 JSON，以及统计取数、刷新与验收要求。

检索与整理日期：2026-10-24。包括中文制作规范、脚本接口、入门示例、专题导航、调试发布流程、来源核验记录，以及可离线检索的 Wiki 正文与 CWTools 规则快照。

本机 Kaiserreich 截图对应的 [中欧同盟 GUI 源码分析](hoi4-modding-guide/07-kaiserreich-mitteleuropa-gui.md)：右侧入口挂载、独立窗口开关、动态列表和议程交互的源码位置及调用链。

[BUFF 数值可视化两版源码分析](hoi4-modding-guide/08-buff-visualization-mods.md)：普通版与 UI 版目录、修正读取方式、指标覆盖和刷新边界，以及政治界面入口与独立统计页面的实现。

[原版修正完整目录与重要词条分析](hoi4-modding-guide/vanilla-modifier-catalog/README.md)：本机原版 4,484 个具体修正键、政治／工业／陆军／海军／空军／情报六类目录、静态源码使用频次，以及结合两种 BUFF 模组的重点候选。可使用[离线检索页](hoi4-modding-guide/vanilla-modifier-catalog/catalog.html)搜索和筛选。

[国家全局 BUFF 二次筛选](hoi4-modding-guide/vanilla-modifier-catalog/global-buff-review/README.md)：按国策／国家民族精神来源、其他全国来源及用户指定候选、不展示项目分为 A／B／C。已按 [2026-10-25 增删要求](hoi4-modding-guide/vanilla-modifier-catalog/global-buff-review/user-revision-2026-10-25.md)修订：隐藏全部无名词条，纳入指定的天气、主义接纳度、设计商国家费用/经费等项目；持续排除州／地方对象与具体单位属性。后续 BUFF UI 词条选择以当前白名单为准。
