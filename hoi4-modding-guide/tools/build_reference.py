"""Build offline reference pages from the pinned MIT-licensed CWTools snapshot."""
from pathlib import Path
from collections import Counter
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "references/cwtools-hoi4-config/Config"
OUT = ROOT / "references/api"
COMMIT = "297dd69c42aabe10078a8b7ab7f2d07ee631d4ef"


def header(title):
    return (f"# {title}\n\n"
            f"来源：[CWTools HOI4 配置固定提交](https://github.com/cwtools/cwtools-hoi4-config/tree/{COMMIT})。\n\n"
            "上游版权：Copyright (c) 2018 tboby；适用 [MIT 许可](../cwtools-hoi4-config/LICENSE)。"
            "本文件由上游 `Config/script_documentation.json` 重新排版生成，未独立验证引擎行为。"
            "快照取得日期：2026-10-24；其对应的精确游戏版本未知。条目数量不代表引擎接口总量。\n\n"
            "描述中的数值、示例和作用域均来自上游，可能存在遗漏或错误；实际开发须以目标游戏版本文档和运行结果复核。\n\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads((CONFIG / "script_documentation.json").read_text(encoding="utf-8-sig"))
    inventory = []
    for family in ("effects", "triggers"):
        rows = [header(f"{family} 离线参考（{len(data[family])} 条）")]
        for name, item in sorted(data[family].items()):
            rows += [f"## {name}\n\n", f"Scope: `{', '.join(item.get('supported_scope', []))}`  \n",
                     f"Target: `{', '.join(item.get('supported_target', []))}`\n\n",
                     "```text\n" + item.get("description", "").replace("```", "''' ") + "\n```\n\n"]
            inventory.append({"family": family, "name": name, **item})
        (OUT / f"{family}.md").write_text("".join(rows), encoding="utf-8")
    rows = [header(f"modifiers 离线参考（{len(data['modifiers'])} 条）"),
            "条目包含固定名称和动态名称组；动态组的成员清单保留在 inventory.json。上游字段 type / decimal_places 反映文档元数据，不能仅据此推断脚本参数的倍率或数值单位。\n\n",
            "| 名称 | type | decimal_places | IsDynamic | categories |\n|---|---|---:|---|---|\n"]
    for item in sorted(data["modifiers"], key=lambda x: x.get("name", x.get("groupname", ""))):
        name = item.get("name", item.get("groupname", ""))
        rows.append(f"| `{name}` | {item.get('type','')} | {item.get('decimal_places','')} | {item.get('IsDynamic','')} | {', '.join(item.get('categories',[]))} |\n")
        inventory.append({"family": "modifiers", "name": name, **item})
    (OUT / "modifiers.md").write_text("".join(rows), encoding="utf-8")
    rows = [header("进阶脚本概念与格式参考")]
    for group, values in data.items():
        if group in ("effects", "triggers", "modifiers"):
            continue
        rows.append(f"## {group}\n\n")
        for name, item in values.items():
            rows.append(f"### {name}\n\n")
            rows.append((item if isinstance(item, str) else json.dumps(item, ensure_ascii=False, indent=2)) + "\n\n")
    (OUT / "advanced.md").write_text("".join(rows), encoding="utf-8")
    (OUT / "inventory.json").write_text(json.dumps({"source_commit": COMMIT, "target_game_version": None, "license": "MIT", "entries": inventory}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    aliases = []
    for path in sorted(CONFIG.rglob("*.cwt")):
        comments = []
        for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                comments.append(stripped)
                continue
            match = re.match(r"alias\[(effect|trigger):([^\]]+)\]\s*=\s*(.*)", stripped)
            if match:
                aliases.append({"family": match[1], "name": match[2], "declaration": match[3],
                                "file": path.relative_to(ROOT).as_posix(), "line": number, "comments": comments})
            comments = []
    (OUT / "cwt-alias-index.json").write_text(json.dumps({"source_commit": COMMIT, "note": "Lexical declaration index, not a complete CWT parser or engine API catalogue. Overloads and generic aliases remain separate.", "entries": aliases}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"documentation_entries": dict(Counter(x['family'] for x in inventory)), "cwt_alias_declarations": len(aliases)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
