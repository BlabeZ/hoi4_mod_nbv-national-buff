# 本地资料核验记录

整理日期：2026-10-24。

## 已完成的检查

- 自编指南中的本地 Markdown 链接目标存在。
- 4 个教学脚本以 UTF-8 无 BOM 保存，字符串与括号结构检查通过。
- 2 个中英本地化文件含 UTF-8 BOM，语言目录、文件名后缀和首行语言一致；所需 5 个 key 齐全且无重复。
- 教学示例使用的基础 effect、trigger、modifier 名称在固定提交的上游文档中存在；自定义 scripted effect / trigger / idea 引用有对应定义。
- 两个 Wiki 正文快照与保存时的 SHA-256 一致。
- 上游快照范围为 116 个文件，包含 Config、README 与 MIT LICENSE。
- 从原始 JSON 重建出 effects 553 条、triggers 598 条、modifiers 764 条（含动态名称组），合计 1,915 条文档记录；另有 1,610 条 CWT effect/trigger 别名声明位置记录。

机器结果见 [verification-results.json](verification-results.json)。可在本目录用 `python -B tools/verify_bundle.py` 重复这些检查。

## 检查没有覆盖的内容

**未启动 HOI4，未运行 CWTools 校验器，也未验证本机游戏版本、DLC、实际图形显示、自然触发、AI、存读档或联机行为。** 括号/引用检查只验证文件层面的一部分问题，不是完整 Clausewitz 解析器，更不能证明模组可发布。

两份描述符仍保留 `REPLACE_WITH_TESTED_MAJOR_MINOR.*` 教学占位符，需要按实际目标版本填写。示例没有安装或启用。

## 来源核验的限制

官网入口和两份 Wiki 正文已取得；CWT 使用固定 Git commit。多数专题 Wiki、部分官方论坛页面正文受访问限制；官方视频仅核验入口和标题。全部这些限制已在 [来源记录](06-sources.md) 中说明，没有把受限网页或 HTTP 200 挑战页当成正文。
