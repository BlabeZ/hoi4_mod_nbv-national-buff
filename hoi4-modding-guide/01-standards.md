# 01 制作标准与目录

本章的“格式约束”来自已取得的 [Wiki Modding 正文](references/wiki/Modding.txt)；“工程建议”是便于维护的项目约定；CWTools 规则只作静态校验参考。它们不是同一层级的保证。

## 1. 先确定目标环境

开始开发时记录：游戏完整版本、分支（正式或测试）、checksum、启用的 DLC、语言、启动器 playset、依赖模组及版本。**不要用资料日期推定游戏版本，也不要把 `supported_version` 当成兼容性测试结果。**

建议优先级：目标版本实际运行结果与随游戏分发的文档/原版用法 → 对应版本官方开发日志 → Wiki 的具体条目与版本提示 → CWTools 和第三方教程。原版脚本是参考样例，也可能有错误；出现冲突时用小模组复现。

## 2. 三个目录必须分清

| 目录 | 用途 | 做法 |
|---|---|---|
| 游戏安装目录 | 原版脚本、资源、游戏程序、随版本分发的文档 | 查阅、比对；在独立模组中实现改动 |
| 用户数据目录 | `mod/`、`logs/`、存档、Nudger 输出 | 实际位置可能被 OneDrive 或游戏设置改写 |
| 模组根目录 | `descriptor.mod` 与模组内容 | 可放在本项目内，由用户描述符指向 |

Windows 用户数据目录通常为 `%USERPROFILE%/Documents/Paradox Interactive/Hearts of Iron IV/`，但应按实际“文档”目录和 `gameDataPath` 判断。Wiki 特别提醒模组所在路径的非 ASCII 字符可能导致加载问题；本项目的 `D:/projects/hoi4_mod/1/` 路径适合使用。[来源：用户目录与路径](https://hoi4.paradoxwikis.com/Modding#User_directory)

推荐内容布局（只创建实际需要的目录）：

```text
my_mod/
├── descriptor.mod
├── common/
│   ├── national_focus/
│   ├── decisions/categories/
│   ├── ideas/
│   ├── characters/
│   ├── scripted_effects/
│   ├── scripted_triggers/
│   └── on_actions/
├── events/
├── history/
│   ├── countries/
│   ├── states/
│   └── units/
├── localisation/
│   ├── english/
│   └── simp_chinese/
├── interface/
├── gfx/
└── map/
```

**格式约束**：模组根目录对应游戏根目录。`my_mod/common/national_focus/` 能被按国策读取；多套一层 `my_mod/something/common/` 就不是同一位置。`interface/` 放 `.gfx`、`.gui` 定义，`gfx/` 放图像资源，两者职责不同。[来源：文件加载和目录](https://hoi4.paradoxwikis.com/Modding#Loading_files)

## 3. 两份描述符

| 文件 | 放置位置 | 特有内容 |
|---|---|---|
| `<mod_name>.mod` | 用户数据目录的 `mod/` 下 | `path` 指向本机模组根目录 |
| `descriptor.mod` | 模组根目录内 | 随模组分发的元数据，不放本机绝对路径 |

共同字段示意：

```text
name = "My HOI4 Mod"
version = "0.1.0"
supported_version = "<实际验证过的主版本.次版本.*>"
tags = { "Events" }
```

`<...>` 是教学占位符，实际使用前必须替换；例如只有在确实针对 `1.19.x` 验证时才写 `1.19.*`。外部 `<mod_name>.mod` 额外写：

```text
path = "D:/projects/hoi4_mod/1/my_mod"
```

- `version` 是模组自身版本；`supported_version` 用于启动器的游戏版本提示。
- `dependencies = { "父模组显示名" }` 用来调整依赖模组之间的加载顺序，不会自动安装父模组，也不是依赖存在性的完整保证。
- `remote_file_id` 关联已发布条目；新模组不要继承别人的发布 ID。
- 如使用 `replace_path`，Wiki 要求两份描述符都维护该字段，不能假设启动器会自动复制。
- 本地测试版和订阅版同名可能造成加载混淆；使用不同显示名，并确认实际启用项。

来源：[描述符和属性](https://hoi4.paradoxwikis.com/Modding#Mod_structure)，离线可搜索 `There are two descriptor files`。

## 4. 文件覆盖、对象定义与加载顺序

**格式规则**：同一相对路径、同一文件名的模组文件会替代较早加载的文件。新增不同名文件通常与原版同目录文件一起读取；这不等于其中的重复 ID 会自动合并。

需要特别区分两件事：

1. **文件选择**：两个来源都提供 `events/Generic.txt` 时只选一个文件。
2. **对象解释**：两个不同文件都定义同一个国策或 state ID 时，各系统的处理可能不同，不能概括为“后者总是覆盖前者”。

Wiki 还区分加载顺序与解析顺序，并记录文件名、`dependencies` 和不同数据库的行为。因此不要仅凭启动器列表的视觉上下顺序或 `zzz_` 文件名，声称任意冲突已解决。[来源：Loading files](https://hoi4.paradoxwikis.com/Modding#Loading_files)

`replace_path = "history/states"` 会卸载该目录中此前加载的索引文件，通常用于大范围替换。它并不是通用“提高优先级”开关，不能递归替换所有子目录，也不适用于所有按文件名直接加载的内容。新手的小事件模组通常无需它。[来源：replace_path](https://hoi4.paradoxwikis.com/Modding#replace_path)

**工程建议**：新增内容尽量独立文件；确需覆盖原版文件时，记录上游版本、覆盖原因和补丁比对项。只改一个条目却复制整个大目录，会放大兼容与维护成本。

## 5. 编码和语法

| 对象 | 规则/建议 |
|---|---|
| 普通脚本 `.txt`、`.gfx`、`.gui` | 按 Wiki 通用指南使用 UTF-8 无 BOM；个别特殊格式以该格式规则为准 |
| 本地化 `.yml` | 使用 UTF-8 **带 BOM**；文件名语言后缀和首行语言标识必须一致 |
| 本地化条目 | 例如 `demo.1.t:0 "标题"`；数字是版本注记，不能用普通 YAML 解析器的通过与否证明游戏可读 |
| 脚本块 | `key = value` 与 `{ ... }`，部分条件使用比较运算符；使用 `#` 注释 |
| 文件名与路径 | 显示扩展名，避免 `file.txt.txt`；游戏脚本内路径优先使用 `/` |
| 图像 | 后缀不能替代实际格式转换；纹理、旗帜、地图分别遵守各自格式 |

英文示例：`localisation/english/demo_l_english.yml` 首行是 `l_english:`。简中示例：`localisation/simp_chinese/demo_l_simp_chinese.yml` 首行是 `l_simp_chinese:`。把中文放入简中语言文件，显示文字用 localisation key 引用。[来源：Localisation 概述](https://hoi4.paradoxwikis.com/Modding#Localisation)

Wiki 对普通 UI 图像、旗帜、地图明确区分：例如国旗使用特定 TGA 格式要求，不能把普通 UI 的 DDS 建议套到旗帜或地图。地图像素、位深、调色板、尺寸应查目标版本专题和原版文件后再改。[来源：GFX](https://hoi4.paradoxwikis.com/Modding#GFX)

## 6. 推荐项目规范（不是引擎强制标准）

- 为事件 namespace、国策 ID、决议、idea、flag、变量、本地化 key、GFX 名称使用一致的项目短前缀，例如 `h4guide_`。
- 事件使用 `add_namespace = h4guide` 和 `h4guide.1` 等 ID；项目维护一个 ID 清单，避免重复。
- 统一用四空格或 Tab；缩进只提高可读性，不会修复错误的括号结构。
- 中文用于本地化和文档；脚本 ID、文件名尽量用可移植的 ASCII 字符。
- 用 Git 保存可回退的变更；将日志、个人路径、缓存、临时导出排除出发布包。
- 每次只引入一条可观察的行为；写清触发条件、作用对象、预期效果、重复触发行为。
- 不把参考资料、CWTools 的 `Config/` 或文档包整体塞入发布模组根目录。

资料依据：[Wiki Guidelines](https://hoi4.paradoxwikis.com/Modding#Guidelines)、[CWTools 事件结构](references/cwtools-hoi4-config/Config/events.cwt)。
