# -*- coding: utf-8 -*-
from pathlib import Path
import json
from collections import defaultdict, Counter
root=Path(__file__).resolve().parent
d=json.loads((root/'static-idea-coverage-audit-v018.json').read_text(encoding='utf-8'))
missing=d['missing_direct_displayed']
conditional=[r for r in missing if r['safe_category'] and r['rejections'][0]['reason']=='conditional_or_unknown_idea_fields']
no_name=[r for r in missing if r['safe_category'] and r['rejections'][0]['reason']=='missing_or_ambiguous_chinese_name']
trait=[r for r in d['trait_candidates'] if r['displayed'] and r['safe_category']]
advcats={'political_advisor','army_chief','navy_chief','air_chief','high_command','theorist'}
adv=[r for r in d['trait_candidates'] if r['displayed'] and r['category'] in advcats]
designer=[r for r in missing if not r['safe_category']]
designer_traits=[r for r in d['trait_candidates'] if r['displayed'] and r['category'] not in advcats and not r['safe_category']]
lines=['# 原版普通／旧式民族精神来源独立覆盖审计（0.1.8）','','审计日期：2026-10-25。只读审计；未改动生产模组或原版。结论范围为本机原版 1.19.3 文件与当前 519 个页面词条，不包括第三方重写的同名精神。',
'','**结论：文件扫描完整，但不能确认民族精神的悬停来源已经全部覆盖。** 页面合计读取 `ROOT.modifier@key`，不依赖下面的来源映射；“没有来源”不能等同于“合计漏加”。',
'','本报告使用独立 lexer/tree scanner 重新读原版，未调用生产生成器的 parser 或接受其“已覆盖”计数。JSON 保留全部定义、行号、直接值、traits 引用及遗漏清单。DLC 路径完整性由主审计单独核验。',
'','## 范围与计数','','| 项目 | 结果 |','|---|---:|',
f"| ideas 文件 / 定义 | {d['statistics']['files']} / {d['statistics']['ideas']} |",
f"| 独立解析失败 | {d['statistics']['parse_failures']} |",
'| EOF 不闭合但可读取的外层 ideas | SOV、persia、switzerland 共 3 文件 |',
'| 当前页面词条 / 基础注册词条 | 519 / 559 |',
f"| 普通／隐藏精神、法案、军种精神：非零直接修正，落在当前页面键 | {d['statistics']['safe_category_displayed_candidates']} |",
f"| 上述已有来源绑定 | {d['statistics']['safe_category_displayed_covered']} |",
f"| 有中文名、do_effect 未适配 | {len(conditional)} 条 / {len(set(r['idea'] for r in conditional))} 个精神 |",
f"| traits 承载的国家精神未适配 | {len(trait)} 条 / {len(set(r['idea'] for r in trait))} 个精神 |",
f"| 无中文来源名，被当前显示策略排除 | {len(no_name)} 条 / {len(set(r['idea'] for r in no_name))} 个精神 |",
f"| 当前页面键中的非字面量直接 modifier 值 | {len(d.get('nonliteral_displayed_direct_values',[]))} |",
'','已对全部 9 张现行来源表交叉核验：下文 36 个 do_effect 精神的 246 条贡献及 4 个 traits 精神的 7 条贡献，在对应修正键的 activation_script 中均无该精神 ID 的持有适配。合计 **40 个具名国家精神、253 条当前页面来源贡献明确未适配**；并非被另一来源表补齐。',
'','“条”指一个来源组件对一个当前页面修正键的贡献，不是缺失的页面词条数量。不能用 6508 减去已绑定精神数作为遗漏数量，因为其中包含法案、顾问、设计商、无所选修正及用户不展示项目。',
'','## 明确仍未适配的普通民族精神','','### 条件生效 do_effect','','当前代码整项排除带 `do_effect` 的精神。要补齐应在 `has_idea` 之外原样核验其生效条件，不能仅以持有精神推断有贡献。斯柯达的条件是仍控制至少一个核心州；意大利科研合作有阵营条件。CZE 外包武器生产虽然也带 do_effect，但在当前范围只有 targeted_modifier，不计入本节246条。',
'','| 精神 ID | 名称 | 当前页面贡献数 | 原版位置 |','|---|---|---:|---|']
def group(rows):
    out=defaultdict(list)
    for r in rows:out[r['idea']].append(r)
    return out
for key,rs in group(conditional).items():
    r=rs[0];lines.append(f"| `{key}` | {' / '.join(r['names_zh'])} | {len(rs)} | `{r['file']}:{r['line']}` |")
lines += ['','### traits 承载的精神','','下列精神本身未绑定；领袖表或其他国家顾问表出现同名 trait，并不能覆盖这些精神，因为各自的持有触发器不同。','','| 精神 | trait | 词条 | 值 | 原版位置 |','|---|---|---|---:|---|']
for r in trait:lines.append(f"| {' / '.join(r['names_zh'])} (`{r['idea']}`) | `{r['trait']}` | {r['modifier_name']} | {r['value_literal']} | `{r['file']}:{r['line']}` |")
lines += ['','## 旧式顾问与设计商','','这些数据确实存在于 `common/ideas`，没有被现代 character/advisor 适配表自动覆盖。以下是定义层面的候选，不是“所有这些旧式人物在当前局一定能聘用”的运行时结论；仍需核验 DLC、allowed/available/do_effect 与实际聘用接口。',
f"","- 旧式顾问的 traits：{len(adv)} 条当前页面键贡献候选；其中有明确中文名的 {sum(bool(r['names_zh']) for r in adv)} 条，涉及 {len(set(r['idea'] for r in adv if r['names_zh']))} 个顾问，集中在白俄罗斯、克罗地亚、维希法国。没有任何同 idea_token 的现行顾问来源绑定。",
f"- 其余 {sum(not r['names_zh'] for r in adv)} 条来自无静态中文名／通用旧式人物；不能直接输出原始 ID，需先解决原版运行时人物名称。",
f"- 旧式设计商有 {len(designer)} 条直接 modifier 和 {len(designer_traits)} 条 traits 候选落在页面键；均没有旧式设计商持有适配。这里不包括 equipment_bonus／research_bonus 嵌套对象。用户允许设计商提供的国家修正，故它们应单列待适配。",
'','### 有中文名的旧式顾问清单','','| 顾问 ID | 名称 | 贡献数 | 原版位置 |','|---|---|---:|---|']
for key,rs in group([r for r in adv if r['names_zh']]).items():
    r=rs[0];lines.append(f"| `{key}` | {' / '.join(r['names_zh'])} | {len(rs)} | `{r['file']}:{r['line']}` |")
lines += ['','## 与遗漏区分的项目','','- 当前 40 个主动移出页面的 registry 键不在审计缺口分母内。','- 零值不显示。','- 77 条无中文来源名的条目单列，不以英文 ID 冒充名称，也不直接归为已经确认应展示的来源。','- targeted_modifier 中有 40 个当前页面键的出现，但它们带特定对象上下文，不能并入无目标的国家全局值。','- equipment_bonus／research_bonus、on_add／on_remove 不是持有时可直接相加的国家 modifier；前者是对象/科技效果，后者可能产生其他精神或动态修正，应沿实际来源体系跟踪，不能重复计入。','- 本报告只核查 ideas；dynamic_modifiers 的完整性与运行时数值表达式由独立动态审计处理。',
'','## 复核文件','','- `audit_static_ideas_v018.py`：独立读取脚本。','- `static-idea-coverage-audit-v018.json`：完整机器可读清单，含每项源码位置。','- `summarize_static_ideas_v018.py`：本报告生成器。',
'','建议依次补齐：36 个 do_effect 精神 → 4 个 traits 精神 → 可用的旧式顾问/国家设计商来源。每类验证添加、移除、条件失效和切换国家后的来源，保持合计直接读取引擎、不制造差额。']
(root/'static-idea-coverage-audit-v018.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(str(root/'static-idea-coverage-audit-v018.md'))
