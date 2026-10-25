# 03 从零做一个小模组

目标：用控制台打开一个事件，点击选项后获得政治点数和一个民族精神；同一国家再次触发时不重复发放奖励。这个小例子能同时验证加载、本地化、事件、条件、效果、修正和 flag。

**本例仅做了文件层面的检查，没有在本机启动游戏测试。** 第一次实践应使用单独 playset 和新存档。

## 1. 准备编辑环境

推荐 VS Code + [CWTools](https://github.com/cwtools/cwtools-vscode)。用 [HOI4 Mod Utilities](https://github.com/herbix/hoi4modutilities) 辅助预览国策、事件图、科技、地图、GUI、GFX；预览不能替代引擎验证。配置它们时分别选择真实的 HOI4 安装目录。

CWTools 配置仓库说明支持 `cwtools.rules_version = manual` 与 `cwtools.rules_folder` 指向手动规则目录。若使用本包快照，可指向 `references/cwtools-hoi4-config`；是否采用手动规则、何时更新由项目决定。游戏更新后重建 vanilla cache；不要把旧缓存误报当作新语法一定错误。[配置说明](references/cwtools-hoi4-config/README.md)

打开实际模组根目录作为编辑器项目。识别失败时检查扩展的游戏识别与路径提示，不要只打开一两个散落的 `.txt` 文件。

## 2. 创建并定位模组

通过启动器的创建模组入口建立本地模组。Wiki 记录的菜单路径是 “All installed mods → Upload mod → Create a mod”；启动器版本不同，标签可能变化。随后检查两份描述符的真实位置。

可以将教学模组目录放在 `D:/projects/hoi4_mod/1/h4guide_demo/`，再让用户数据目录里的 `mod/h4guide_demo.mod` 指向它。不要把整个 `hoi4-modding-guide` 文档目录作为模组。

从 [examples/minimal_mod](examples/README.md) 复制内容；把 `descriptor.mod.template` 改名为 `descriptor.mod`，填入实际验证版本。将 [h4guide_demo.mod.template](examples/h4guide_demo.mod.template) 改好路径和版本后放到用户数据 `mod/` 目录。也可以保留启动器生成的两份描述符，只复制内容文件。

```text
h4guide_demo/
├── descriptor.mod
├── events/h4guide_events.txt
├── common/ideas/h4guide_ideas.txt
├── common/scripted_effects/h4guide_effects.txt
├── common/scripted_triggers/h4guide_triggers.txt
└── localisation/
    ├── english/h4guide_l_english.yml
    └── simp_chinese/h4guide_l_simp_chinese.yml
```

本例无需 `replace_path`，也不需要改原版文件。仅在 playset 中启用教学模组，避免同名订阅版参与测试。[加载和描述符依据](https://hoi4.paradoxwikis.com/Modding)

## 3. 先看四个脚本文件如何配合

事件定义的关键部分：

```text
add_namespace = h4guide

country_event = {
    id = h4guide.1
    title = h4guide.1.t
    desc = h4guide.1.d
    is_triggered_only = yes

    option = {
        name = h4guide.1.a
        if = {
            limit = { h4guide_can_receive_reward = yes }
            h4guide_grant_reward = yes
        }
    }
}
```

`is_triggered_only = yes` 表示此教学事件通过其他调用入口触发，本例使用控制台。显示的标题、说明和按钮都引用本地化 key。条件和效果抽到了另外两个文件：

```text
# common/scripted_triggers/h4guide_triggers.txt
# Requires country scope.
h4guide_can_receive_reward = {
    NOT = { has_country_flag = h4guide_reward_received }
}
```

```text
# common/scripted_effects/h4guide_effects.txt
# Requires country scope.
h4guide_grant_reward = {
    add_political_power = 25
    add_ideas = h4guide_training_spirit
    set_country_flag = h4guide_reward_received
    log = "H4GUIDE: reward granted"
}
```

民族精神文件的定义如下：

```text
ideas = {
    country = {
        h4guide_training_spirit = {
            allowed = { always = yes }
            removal_cost = -1
            modifier = {
                political_power_gain = 0.10
            }
        }
    }
}
```

`add_political_power` 是一次性效果，`political_power_gain` 是民族精神持续提供的日增益修正。为减少资源依赖，示例没有指定自定义图片；完成基本验证后再参照目标版本原版配置图片与 sprite。

对应结构已经对照 [events.cwt](references/cwtools-hoi4-config/Config/events.cwt)、[ideas.cwt](references/cwtools-hoi4-config/Config/common/ideas.cwt)、[scripted 规则](references/cwtools-hoi4-config/Config/common/scripted_effects_locs_and_triggers.cwt) 与 [effects.cwt](references/cwtools-hoi4-config/Config/effects.cwt)。这是结构核对，不等同于运行证明。

## 4. 本地化必须单独检查

简中本地化文件需要 **UTF-8 BOM**；内容形如：

```yaml
l_simp_chinese:
 h4guide.1.t:0 "模组加载测试"
 h4guide.1.d:0 "这是一个用于验证事件、条件与民族精神的教学事件。"
 h4guide.1.a:0 "领取一次性奖励"
 h4guide_training_spirit:0 "训练计划"
 h4guide_training_spirit_desc:0 "教学民族精神：每日政治点数增加。"
```

示例包中的中英文 `.yml` 已写入 BOM。代码块本身不能表达 BOM，手动复制代码时仍需在编辑器中选择正确编码。[Wiki 本地化概述](https://hoi4.paradoxwikis.com/Modding#Localisation)

## 5. 在游戏中验收

1. 启动参数加入 `-debug`，启动单独 playset。
2. 查看主菜单和日志，确认模组确实加载；开始非铁人模式新游戏，暂停时间。
3. 记录当前政治点数，然后打开控制台输入 `event h4guide.1`，使用当前玩家国家作为目标。
4. 检查标题、正文和按钮是否显示文字；点击后政治点数应增加 25，并出现教学民族精神。
5. 检查政治点数日增益 tooltip 中民族精神贡献；不只看最终总值，因为它还受其他修正影响。
6. 再次执行同一事件并点击选项；应因 flag 条件不再增加政治点数，也不应重复执行奖励日志。
7. 在 `logs/game.log` 中搜索 `H4GUIDE`；在 `logs/error.log` 中检查本例相关新增报错。
8. 保存、退出、读档，再验证 flag 与民族精神是否符合预期；最后不带 `-debug` 正常启动检查一次。

`event` 和 `reload loc` 等命令的说明见 [离线控制台指南](references/wiki/Console_commands.txt)。控制台强制触发可以验证效果，但不能证明自然触发、AI 选择或完整游戏流程正确。

## 6. 下一步练习

| 练习 | 改动 | 应验收 |
|---|---|---|
| 给事件加使用条件 | 修改 scripted trigger | 满足和不满足条件的国家都测试 |
| 用决议触发事件 | 增加 category 与 decision；在 `complete_effect` 调用事件 | 可见性、可用性、成本、重复点击 |
| 用国策调用奖励 | 在国策 `completion_reward` 调用同一 scripted effect，并按需要加防重条件 | 奖励对象、前置关系、已完成状态 |
| 添加图标 | `gfx/` 纹理与 `interface/*.gfx` sprite | 图片路径、大小写、透明度和 sprite 名一致 |
| 改为定时或历史事件 | 使用有明确作用域的入口 | 发生频率、日期、存读档后行为、AI 情况 |

决定扩大范围前，先完成本章的验证记录，再阅读 [专题路线](04-topic-guides.md) 和 [调试发布清单](05-debug-release.md)。
