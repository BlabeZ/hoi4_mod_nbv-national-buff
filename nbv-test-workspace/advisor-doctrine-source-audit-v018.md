# 顾问和学说剩余解析失败核查（只读研究）

本次没有修改生产表或共享解析器，重建输出仅放测试工作区。

## 顾问

旧表 `advisor-source-bindings.json` 的 `events/TAOG_Siam.txt:1752` 匿名块错误已被现行通用解析器支持。直接重建即可恢复，无需新代码。

- 绑定：9,219 → 9,231（增加 12）。
- 顾问人物／角色／特质各增加 3，现为 2,323／2,349／866。
- 覆盖修正键：251 → 252。
- 解析失败：1 → 0。
- 新增来源：`SIA_phraya_songsuradet` 高级军官领袖、`SIA_rambai_barni` 摄政王后、`SIA_rangsit_prayurasakdi` 猜纳亲王。
- 无既有绑定删除。
- 研究输出：`rebuilt-advisor-source-bindings.json`。

## 潜艇学说

`common/doctrines/subdoctrines/sea/navy_submarine_doctrines.txt` 目前仍真实缺少文件最后一个闭合花括号。未闭合的是第 297 行 `long_range_submarines = {`；前五个学说完整。严格解析整文件失败造成所有六个学说的候选来源丢失。

对该文件仅在内存补一个 EOF 闭合再重建：

- 绑定：543 → 552（增加 9）。
- 来源：368 → 377（增加 9）。
- 解析失败：1 → 0。
- 新增 9 个绑定全部位于当前 519 项展示名单。
- 文件 SHA256：`b0fe32ce5ca0d8e0efba38f747cb1aa0851f29664d6594197d00869fc43fad38`。
- 研究输出：`recovered-submarine-source-bindings.json`。

| 来源 | 修正 | 数值 |
|---|---|---:|
| 海岸布雷 · 有效布雷 | naval_mines_damage_factor | +0.25 |
| 海岸布雷 | naval_mines_effect_reduction | +0.10 |
| 狼群战术 | naval_retreat_speed_after_initial_combat | +0.15 |
| 远程潜艇 | naval_torpedo_hit_chance_factor | +0.10 |
| 主力舰猎手 | naval_torpedo_reveal_chance_factor | -0.10 |
| 对舰群作战 | naval_torpedo_screen_penetration_factor | +0.05 |
| 主力舰猎手 · 战列线优先 | naval_torpedo_screen_penetration_factor | +0.05 |
| 对舰群作战 · 伏击战术 | navy_submarine_attack_factor | +0.10 |
| 主力舰猎手 · 弹尽撤离 | sub_retreat_speed | +0.10 |

如纳入修复，建议沿用 ideas 的文件路径＋完整内容 SHA256 限定恢复策略，记录恢复，保持其他文档严格解析，并为学说启用／精通等级／替换关闭补充引擎验证。
