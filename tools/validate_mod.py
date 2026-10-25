#!/usr/bin/env python3
"""Independent static checks for NBV; this does not run or emulate the game UI.

Run: python tools/validate_mod.py [--game-root PATH] [--report PATH]
Only the JSON report is written. Game files and production mod files are read-only.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
from display_names import metric_display_name


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME = Path(r"E:\Steam\steamapps\common\Hearts of Iron IV")
PAGES = ["政治", "工业", "陆军", "海军", "空军", "情报"]
EXPECTED_COUNTS = [94, 109, 166, 92, 51, 47]
SOURCE_INPUT_TABLES = ("source-bindings.json", "leader-source-bindings.json", "advisor-source-bindings.json",
                       "doctrine-technology-source-bindings.json", "dynamic-source-bindings.json",
                       "ideology-source-bindings.json", "faction-source-bindings.json", "dynamic-spirit-source-bindings.json",
                       "special-source-bindings.json")


@dataclass
class Token:
    value: str
    line: int
    kind: str


@dataclass
class Entry:
    key: str | None
    op: str | None
    value: object
    line: int


class ParseError(ValueError):
    pass


TOKEN = re.compile(
    r'(?P<space>\s+)|(?P<comment>\#[^\n]*)|(?P<string>"(?:[^"\\]|\\.)*")'
    r'|(?P<brace>[{}])|(?P<op><=|>=|!=|=|<|>)|(?P<atom>[^\s{}=<>!"#]+)'
)


def parse_script(text, filename="<text>"):
    """Parse assignments, comparisons, ordered blocks and bare list values.

    Repeated keys remain ordered entries; they are not silently overwritten.
    Bare list values can themselves be anonymous blocks, as in vanilla
    optional_assets = { { icon = ... model = ... } } definitions.
    This is a syntax parser for the subset used by the mod, not an engine validator.
    """
    tokens = []
    offset, line = 0, 1
    while offset < len(text):
        match = TOKEN.match(text, offset)
        if not match:
            raise ParseError(f"{filename}:{line}: unexpected token {text[offset:offset+30]!r}")
        kind, value = match.lastgroup, match.group()
        if kind not in ("space", "comment"):
            if kind == "string":
                value = value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
            tokens.append(Token(value, line, kind))
        line += match.group().count("\n")
        offset = match.end()
    cursor = 0

    def block(nested=False):
        nonlocal cursor
        result = []
        while cursor < len(tokens):
            first = tokens[cursor]
            if first.value == "}" and first.kind == "brace":
                if not nested:
                    raise ParseError(f"{filename}:{first.line}: unexpected closing brace")
                cursor += 1
                return result
            if first.value == "{" and first.kind == "brace":
                cursor += 1
                result.append(Entry(None, None, block(True), first.line))
                continue
            if first.kind not in ("atom", "string"):
                raise ParseError(f"{filename}:{first.line}: expected key or scalar, got {first.value!r}")
            cursor += 1
            if cursor < len(tokens) and tokens[cursor].kind == "op":
                op = tokens[cursor].value
                cursor += 1
                if cursor == len(tokens):
                    raise ParseError(f"{filename}:{first.line}: missing assignment value")
                value_token = tokens[cursor]
                cursor += 1
                if value_token.value == "{" and value_token.kind == "brace":
                    if op != "=":
                        raise ParseError(f"{filename}:{first.line}: block needs assignment operator")
                    value = block(True)
                elif value_token.kind in ("atom", "string"):
                    value = value_token.value
                else:
                    raise ParseError(f"{filename}:{value_token.line}: invalid assignment value")
                result.append(Entry(first.value, op, value, first.line))
            else:
                result.append(Entry(None, None, first.value, first.line))
        if nested:
            raise ParseError(f"{filename}: unclosed block")
        return result

    return block()


def walk(entries):
    for entry in entries:
        yield entry
        if isinstance(entry.value, list):
            yield from walk(entry.value)


def children(entries, key):
    return [e for e in entries if e.key == key]


def one(entries, key):
    matches = children(entries, key)
    if len(matches) != 1:
        raise ValueError(f"Expected one {key}, found {len(matches)}")
    return matches[0]


def scalar(entries, key, default=None):
    matches = children(entries, key)
    return matches[0].value if matches else default


def resource_scalar(entries, key, default=None):
    """Native graphics files use both texturefile and textureFile spellings."""
    matches = [e for e in entries if e.key and e.key.lower() == key.lower()]
    return matches[0].value if matches else default


def script_signature(entry):
    """Compare Clausewitz semantics without source-file line numbers."""
    return (entry.key, entry.op, tuple(script_signature(child) for child in entry.value)
            if isinstance(entry.value, list) else entry.value)


def variable_check_parts(entries):
    """Decode only check_variable forms supported by the installed HOI4 engine.

    The generic script parser accepts >=/<=/!= for other syntaxes. HOI4's
    check_variable specifically requires named `compare` values for those
    operators; accepting them here would mask a real engine parser failure.
    """
    if not isinstance(entries, list) or any(item.op not in ("=", "<", ">") for item in entries):
        raise ValueError("check_variable does not accept inline >=, <= or !=")
    comparisons = children(entries, "compare")
    tooltips = children(entries, "tooltip")
    if len(comparisons) > 1 or len(tooltips) > 1:
        raise ValueError("check_variable has duplicate metadata")
    if any(item.op != "=" for item in comparisons + tooltips):
        raise ValueError("check_variable metadata must use assignment")
    compare_map = {"equals": "=", "not_equals": "!=", "less_than": "<",
                   "less_than_or_equals": "<=", "greater_than": ">", "greater_than_or_equals": ">="}
    if comparisons and comparisons[0].value not in compare_map:
        raise ValueError("check_variable has unsupported compare value")
    operands = [item for item in entries if item.key not in ("compare", "tooltip")]
    if len(operands) == 2 and {item.key for item in operands} == {"var", "value"}:
        if any(item.op != "=" or not isinstance(item.value, str) for item in operands):
            raise ValueError("check_variable long-form operands must be scalar assignments")
        return (scalar(operands, "var"), compare_map[comparisons[0].value] if comparisons else "=",
                scalar(operands, "value"))
    if len(operands) != 1 or not operands[0].key or not isinstance(operands[0].value, str):
        raise ValueError("check_variable needs one short comparison or a var/value pair")
    item = operands[0]
    if comparisons and item.op != "=":
        raise ValueError("check_variable cannot combine shorthand comparison with compare metadata")
    return item.key, compare_map[comparisons[0].value] if comparisons else item.op, item.value


def named_blocks(entries):
    result = {}
    for entry in walk(entries):
        if isinstance(entry.value, list):
            name = scalar(entry.value, "name")
            if isinstance(name, str):
                result.setdefault(name, []).append(entry)
    return result


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_loc(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    rows, duplicates, invalid = {}, [], []
    header = None
    pattern = re.compile(r'^\s*([A-Za-z0-9_.-]+):(?:\d+)?\s+"((?:[^"\\]|\\.)*)"\s*(?:#.*)?$')
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.fullmatch(r"l_[a-z_]+:\s*", line.strip()):
            header = line.strip()[:-1]
            continue
        match = pattern.fullmatch(line)
        if not match:
            invalid.append(line_number)
            continue
        key, value = match.groups()
        if key in rows:
            duplicates.append(key)
        rows[key] = value
    return rows, header, raw.startswith(b"\xef\xbb\xbf"), duplicates, invalid


def expected_display_layout(text, registry):
    """Independently recover the first occurrence of every requested name.

    Do not use the importer here: a shared ordering/deduplication mistake would
    otherwise make the generator and its validation agree on the wrong layout.
    """
    first_binding = {}
    for record in registry:
        first_binding.setdefault(record["name"], record)
        first_binding.setdefault(metric_display_name(record), record)
    band_names = {"常用": "high", "其他修正": "low"}
    confirmed_splits = {"敌方特工情报获取率加强意识形态任务成果":
                        ("敌方特工情报获取率", "加强意识形态任务成果")}
    result, duplicates, section_order, page_order = [], [], [], []
    seen, section_counts = {}, Counter()
    page = band = None
    ignored_empty_bullets = 0
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        heading = re.fullmatch(r"(#{1,2})\s+(.+)", line)
        if heading:
            level, title = heading.groups()
            if level == "#":
                if title not in PAGES:
                    raise ValueError(f"Unknown page at line {number}: {title}")
                page, band = title, None
                page_order.append(title)
            else:
                if page is None or title not in band_names:
                    raise ValueError(f"Unknown section at line {number}: {title}")
                band = band_names[title]
                section_order.append((page, band))
            continue
        bullet = re.fullmatch(r"-\s*(.*)", line)
        if not bullet:
            raise ValueError(f"Unexpected Markdown at line {number}: {line}")
        name = bullet.group(1).strip()
        if not name:
            ignored_empty_bullets += 1
            continue
        if page is None or band is None:
            raise ValueError(f"Metric outside a page/section at line {number}")
        for name in confirmed_splits.get(name, (name,)):
            if name not in first_binding:
                raise ValueError(f"Unknown modifier at line {number}: {name}")
            original = first_binding[name]
            identity = original["key"]
            if identity in seen:
                duplicates.append({"name": name, "source_line": number,
                                   "first_source_line": seen[identity]["source_line"],
                                   "retained_id": seen[identity]["id"]})
                continue
            section_counts[(page, band)] += 1
            row = {key: original[key] for key in ("id", "key", "name")}
            row["name"] = metric_display_name(original)
            row.update(category=page, display_priority_band=band,
                       grid_columns=3 if band == "high" else 4,
                       display_order=section_counts[(page, band)], source_line=number)
            seen[identity] = row
            result.append(row)
    if page_order != PAGES or section_order != [(page, band) for page in PAGES for band in ("high", "low")]:
        raise ValueError("The Markdown must contain the six pages and two bands once in GUI order")
    return result, duplicates, ignored_empty_bullets


class ScriptModel:
    """Interpret this mod's state effects and arithmetic for static invariants only.

    This deliberately does not claim to model GUI lifetime, engine ROOT rebinding,
    modifier validity, caching, rendering, network state or actual refresh timing.
    """
    def __init__(self, effects, triggers, modifiers=None):
        self.effects = {e.key: e.value for e in effects}
        self.triggers = {e.key: e.value for e in triggers}
        self.vars, self.flags, self.arrays = {}, set(), {}
        self.temp, self.temp_arrays = {}, {}
        self.modifiers = modifiers or {}

    def value(self, name):
        try:
            return float(name)
        except ValueError:
            pass
        if name.startswith("ROOT.modifier@"):
            return self.modifiers.get(name.split("@", 1)[1], 0)
        name = name.removeprefix("ROOT.")
        if name.endswith("^num"):
            key = name[:-4]
            return len(self.temp_arrays.get(key, self.arrays.get(key, [])))
        if "^" in name:
            key, index = name.split("^", 1)
            items = self.temp_arrays.get(key, self.arrays.get(key, []))
            offset = int(self.value(index))
            # The generated resolver must guard invalid indices. Treat an
            # out-of-range model lookup as an error, not a fabricated zero.
            if offset < 0 or offset >= len(items):
                raise IndexError(f"Array lookup outside bounds: {name} -> {offset}/{len(items)}")
            return items[offset]
        return self.temp.get(name, self.vars.get(name, 0))

    def arithmetic(self, entry):
        name = entry.key
        target = self.temp if "temp" in name else self.vars
        assert isinstance(entry.value, list) and len(entry.value) == 1
        item = entry.value[0]
        key, value = item.key, self.value(item.value)
        old = target.get(key, 0)
        if name.startswith("set_"):
            target[key] = value
        elif name.startswith("add_to_"):
            target[key] = old + value
        elif name.startswith("subtract_from_"):
            target[key] = old - value
        elif name.startswith("multiply_"):
            target[key] = old * value
        elif name.startswith("divide_"):
            target[key] = old / value
        elif name.startswith("modulo_"):
            target[key] = old % value
        else:
            raise ValueError(f"Unknown arithmetic {name}")

    def check(self, entries):
        result = True
        for entry in entries:
            key, val = entry.key, entry.value
            if key == "always":
                passed = val == "yes"
            elif key == "OR":
                passed = any(self.check([item]) for item in val)
            elif key in ("AND", "hidden_trigger"):
                passed = self.check(val)
            elif key == "NOT":
                passed = not self.check(val)
            elif key == "has_country_flag":
                passed = val in self.flags
            elif key == "check_variable":
                left_name, operator, right_name = variable_check_parts(val)
                left, right = self.value(left_name), self.value(right_name)
                passed = {"=": left == right, ">": left > right, "<": left < right,
                          ">=": left >= right, "<=": left <= right, "!=": left != right}[operator]
            elif key == "if":
                passed = True
                if self.check(one(val, "limit").value):
                    passed = self.check([item for item in val if item.key != "limit"])
            elif key == "clear_temp_array":
                self.temp_arrays[val] = []
                passed = True
            elif key == "add_to_temp_array":
                item = val[0]
                self.temp_arrays.setdefault(item.key, []).append(int(self.value(item.value)))
                passed = True
            elif key.endswith("_temp_variable"):
                self.arithmetic(entry)
                passed = True
            elif key in self.triggers:
                passed = self.check(self.triggers[key]) == (val == "yes")
            else:
                raise ValueError(f"Unsupported static-model trigger {key}")
            result = result and passed
        return result

    def run(self, name):
        self.execute(self.effects[name])

    def execute(self, entries):
        last_if = None
        for entry in entries:
            key, val = entry.key, entry.value
            if key == "if":
                last_if = self.check(one(val, "limit").value)
                if last_if:
                    self.execute([item for item in val if item.key != "limit"])
            elif key == "else":
                if last_if is False:
                    self.execute(val)
            elif key in self.effects:
                self.run(key)
            elif key == "set_country_flag":
                self.flags.add(val)
            elif key == "clr_country_flag":
                self.flags.discard(val)
            elif key == "clear_array":
                self.arrays[val] = []
            elif key == "add_to_array":
                item = val[0]
                self.arrays.setdefault(item.key, []).append(int(self.value(item.value)))
            elif key.endswith("_variable"):
                self.arithmetic(entry)
            else:
                raise ValueError(f"Unsupported static-model effect {key}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    cli.add_argument("--report", type=Path, default=ROOT / "tools/data/static-validation.json")
    args = cli.parse_args()
    checks, warnings, resources = [], [], []
    parsed, source_text, file_fingerprints = {}, {}, {}

    def check(name, passed, detail=None):
        checks.append({"检查": name, "通过": bool(passed), "详情": detail})

    def rel(path):
        try:
            return path.relative_to(ROOT).as_posix()
        except ValueError:
            return str(path)

    def guarded(label, function):
        try:
            function()
        except Exception as exc:
            check(label, False, f"{type(exc).__name__}: {exc}")

    script_paths = sorted((ROOT / "common").rglob("*.txt"))
    script_paths += sorted((ROOT / "interface").rglob("*.gui"))
    script_paths += sorted((ROOT / "interface").rglob("*.gfx"))
    script_paths += [ROOT / "descriptor.mod"]
    for path in script_paths:
        try:
            check("非本地化脚本不含 UTF-8 BOM：" + rel(path), not path.read_bytes().startswith(b"\xef\xbb\xbf"))
            text = path.read_text(encoding="utf-8-sig")
            parsed[rel(path)] = parse_script(text, rel(path))
            source_text[rel(path)] = text
            file_fingerprints[rel(path)] = sha256(path)
            check("脚本结构解析：" + rel(path), True)
            if rel(path).startswith("common/scripted_"):
                check("common 脚本无孤立标量：" + rel(path), all(e.key is not None for e in walk(parsed[rel(path)])))
        except Exception as exc:
            check("脚本结构解析：" + rel(path), False, str(exc))
    check_variable_errors, check_variable_count = [], 0
    for relative, tree in parsed.items():
        if not relative.startswith("common/"):
            continue
        for node in walk(tree):
            if node.key != "check_variable":
                continue
            check_variable_count += 1
            try:
                variable_check_parts(node.value)
            except (ValueError, TypeError) as exc:
                check_variable_errors.append({"文件": relative, "行": node.line, "原因": str(exc)})
    check("check_variable 使用引擎支持的比较语法且禁止大于等于等简写", not check_variable_errors,
          {"比较数量": check_variable_count, "错误数量": len(check_variable_errors), "错误": check_variable_errors[:30]})
    for path in sorted((ROOT / "tools").glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            file_fingerprints[rel(path)] = sha256(path)
            check("Python 语法：" + path.name, True)
        except Exception as exc:
            check("Python 语法：" + path.name, False, str(exc))

    index_path = ROOT / "tools/data/metric-index.json"
    binding_path = ROOT / "tools/data/modifier-format-bindings.json"
    manifest_path = ROOT / "tools/data/build-manifest.json"
    index = json.loads(index_path.read_text(encoding="utf-8-sig"))
    bindings = json.loads(binding_path.read_text(encoding="utf-8-sig"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    for path in (index_path, binding_path, manifest_path):
        file_fingerprints[rel(path)] = sha256(path)
    records = index["records"]
    lookup = {row["id"]: row for row in records}
    binding_map = {row["key"]: row for row in bindings["records"]}
    manifest_map = {row["id"]: row for row in manifest["records"]}
    expected_ids = set(range(1, 560))
    check("559 个连续唯一 ID 与唯一键", len(records) == 559 and set(lookup) == expected_ids
          and len({row["key"] for row in records}) == 559)
    counts = [sum(row["category"] == category for row in records) for category in PAGES]
    check("完整注册表六类数量保持不变", counts == EXPECTED_COUNTS, dict(zip(PAGES, counts)))
    ordered = sorted(records, key=lambda row: (PAGES.index(row["category"]), row["priority"], row["key"]))
    check("分类、优先级、技术键稳定顺序", [r["id"] for r in records] == [r["id"] for r in ordered])
    band_counts = Counter(row["display_priority_band"] for row in records)
    check("完整注册表原始优先级保持不变", band_counts == {"high": 198, "low": 361}, dict(band_counts))
    display_records = []
    display_counts = [0] * len(PAGES)

    def inspect_display_selection():
        nonlocal display_records, display_counts
        layout_path = ROOT / "tools/data/display-layout.json"
        layout = json.loads(layout_path.read_text(encoding="utf-8-sig"))
        snapshot_path = layout_path.parent / layout["source_markdown"]
        snapshot = snapshot_path.read_text(encoding="utf-8-sig")
        for path in (layout_path, snapshot_path):
            file_fingerprints[rel(path)] = sha256(path)
        check("展示布局使用当前 Markdown 快照和稳定注册表", layout.get("source_sha256") == sha256(snapshot_path)
              and layout.get("registry_sha256") == sha256(index_path)
              and layout.get("display_names_sha256") == sha256(ROOT / "tools/display_names.py")
              and layout.get("registry_count") == len(records))
        expected, duplicates, empty_bullets = expected_display_layout(snapshot, records)
        selection = layout["records"]
        selection_ids = [row["id"] for row in selection]
        check("展示名单按 Markdown 分类和顺序，空行忽略，同一修正键仅保留首次位置",
              selection == expected and layout.get("duplicates") == duplicates
              and layout.get("ignored_empty_bullets") == empty_bullets,
              {"展示数": len(expected), "删除重复数": len(duplicates), "忽略空词条数": empty_bullets})
        check("展示名单只引用稳定 ID 且名字与修正键唯一",
              bool(selection) and len(set(selection_ids)) == len(selection_ids)
              and set(selection_ids) <= expected_ids
              and len({row["key"] for row in selection}) == len(selection)
              and len({row["name"] for row in selection}) == len(selection)
              and all(all(row[field] == lookup[row["id"]][field] for field in ("id", "key"))
                      and row["name"] == metric_display_name(lookup[row["id"]])
                      for row in selection if row["id"] in lookup))
        # All GUI expectations below come from the independent Markdown result,
        # not from the generated manifest or backend's display-layout loader.
        display_records = [{**lookup[row["id"]], **row} for row in expected]
        display_counts = [sum(row["category"] == category for row in display_records) for category in PAGES]
        expected_page_bands = {page: {band: sum(row["category"] == page and row["display_priority_band"] == band
                                              for row in expected) for band in ("high", "low")} for page in PAGES}
        excluded = [{field: row[field] for field in ("id", "key", "name", "category")}
                    for row in records if row["id"] not in set(selection_ids)]
        check("展示分页、分组及排除清单与 Markdown 完全一致",
              layout.get("record_count") == len(expected)
              and layout.get("categories") == dict(zip(PAGES, display_counts))
              and layout.get("bands") == dict(Counter(row["display_priority_band"] for row in expected))
              and layout.get("page_bands") == expected_page_bands
              and layout.get("excluded_records") == excluded,
              {"分页数量": dict(zip(PAGES, display_counts)), "排除数量": len(excluded)})

    guarded("展示 Markdown 的独立分类、首次去重及顺序审查正常执行", inspect_display_selection)
    check("清单与当前格式绑定相同键集", set(binding_map) == {row["key"] for row in records})
    source_tokens = set(re.findall(r'\btoken:([A-Za-z0-9_]+)', source_text.get('common/scripted_localisation/nbv_source_localisation.txt', '')))
    required_modifier_tokens = set(json.loads((ROOT / 'tools/data/synchronized-tokens.json').read_text(encoding='utf-8'))['tokens'])
    for path, tree in parsed.items():
        if path.startswith("common/synchronized_dynamic_tokens/"):
            tokens = [e.value for e in tree]
            check("动态 token 列表格式、唯一性及名单归属：" + path,
                  all(e.key is None and isinstance(e.value, str) for e in tree)
                  and len(tokens) == len(set(tokens)) and set(tokens) == required_modifier_tokens | source_tokens,
                  {"数量": len(tokens)})
    check("构建清单输入 SHA256", manifest.get("index_sha256") == sha256(index_path)
          and manifest.get("bindings_sha256") == sha256(binding_path))
    manifest_errors = []
    for row in records:
        built = manifest_map.get(row["id"], {})
        bound = binding_map.get(row["key"], {})
        expected = f"[?ROOT.modifier@{row['key']}|{bound.get('format_code', '')}]"
        if any((built.get("key") != row["key"], built.get("category") != row["category"],
                built.get("priority") != row["priority"], built.get("expression") != expected,
                built.get("columns") != (3 if row["display_priority_band"] == "high" else 4))):
            manifest_errors.append(row["id"])
    check("559 构建记录对应最新指标、格式及列数", not manifest_errors, manifest_errors[:30])

    locs = {}
    for language in ("simp_chinese", "english"):
        path = ROOT / f"localisation/{language}/nbv_l_{language}.yml"
        values, header, bom, duplicates, invalid = read_loc(path)
        locs[language] = values
        file_fingerprints[rel(path)] = sha256(path)
        check(f"{language} 本地化编码、语法和唯一键", bom and header == "l_" + language and not duplicates and not invalid,
              {"UTF8_BOM": bom, "重复键": duplicates, "不合规范行": invalid})
        missing, wrong = [], []
        for row in records:
            ident = row["id"]
            for kind in ("name", "value", "tooltip"):
                if not values.get(f"nbv_row_{kind}_{ident}"):
                    missing.append(f"{kind}:{ident}")
            expected = manifest_map.get(ident, {}).get("expression")
            value = values.get(f"nbv_row_value_{ident}", "")
            tooltip = values.get(f"nbv_row_tooltip_{ident}", "")
            extracted = re.findall(r"\[\?ROOT\.modifier@([a-z0-9_]+)(?:\|[^\]]*)?\]", value)
            if extracted != [row["key"]] or value != expected or not expected or expected not in tooltip:
                wrong.append(ident)
        actual_ids = {int(m.group(1)) for key in values if (m := re.fullmatch(r"nbv_row_name_(\d+)", key))}
        check(f"{language} 559 行名称、数值、提示齐全", not missing and actual_ids == expected_ids, missing[:30])
        check(f"{language} 数值表达式与修正键准确映射", not wrong, wrong[:30])
    check("两种语言键集一致", set(locs["simp_chinese"]) == set(locs["english"]))
    check("筛选按钮中文名称按用户要求简化", locs["simp_chinese"].get("nbv_filter_active") == "隐藏词条"
          and locs["simp_chinese"].get("nbv_filter_all") == "全部词条")
    check("高优先级区标题按用户要求显示常用", locs["simp_chinese"].get("nbv_high_title") == "常用")
    explanations = ("作用项：", "公式说明", "国家修正不等于单位最终属性", "此项的精确数值格式", "数值格式尚待核验")
    check("559 个中文词条悬停不再附加作用、公式或开发解释", not any(
        term in value for key, value in locs["simp_chinese"].items()
        if re.fullmatch(r"nbv_row_tooltip_\d+", key) for term in explanations))

    def inspect_modifier_icons():
        """Check the imported text-icon chain without trusting generated names."""
        path = ROOT / "tools/data/modifier-icon-bindings.json"
        icon_manifest = json.loads(path.read_text(encoding="utf-8"))
        file_fingerprints[rel(path)] = sha256(path)
        icon_rows = icon_manifest["records"]
        icon_map = {row["id"]: row for row in icon_rows}
        check("559 个图标映射完整且保持原指标 ID、键、名称和分类",
              len(icon_rows) == len(icon_map) == 559 and set(icon_map) == expected_ids
              and all(all(icon_map[row["id"]].get(field) == row[field]
                          for field in ("id", "key", "name", "category")) for row in records))
        icon_resources = icon_manifest["resources"]
        resource_map = {row["token"]: row for row in icon_resources}
        used_tokens = {row["icon_token"].split("|", 1)[0] for row in icon_rows}
        frame_errors = []
        for row in icon_rows:
            parts = row["icon_token"].split("|", 1)
            frames = resource_map.get(parts[0], {}).get("frames", 0)
            if (not re.fullmatch(r"nbv_mi_[A-Za-z0-9_]+(?:\|[1-9][0-9]*)?", row["icon_token"])
                    or (len(parts) == 2 and not 1 <= int(parts[1]) <= frames)):
                frame_errors.append(row["id"])
        check("图标资源和词条引用一一覆盖且只使用私有命名空间及有效帧",
              len(resource_map) == len(icon_resources) and set(resource_map) == used_tokens and not frame_errors,
              {"帧引用错误": frame_errors})
        english_path = ROOT.parent / "hoi4-modding-guide/vanilla-modifier-catalog/data/catalog.json"
        english = {}
        if english_path.exists():
            english = {r["key"]: r for r in json.loads(english_path.read_text(encoding="utf-8"))["records"]}
            file_fingerprints[str(english_path)] = sha256(english_path)
        name_errors, misplaced_icons = [], []
        for language, values in locs.items():
            for row in records:
                ident = row["id"]
                token = icon_map.get(ident, {}).get("icon_token", "")
                name = metric_display_name(row, language, english.get(row["key"], {}).get("name_en") if language == "english" else None)
                original_name = name.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", r"\n")
                actual = values.get(f"nbv_row_name_{ident}", "")
                tooltip = values.get(f"nbv_row_tooltip_{ident}", "")
                if (actual != "£" + token + " " + original_name
                        or re.findall(r"£([A-Za-z0-9_]+(?:\|[0-9]+)?)", actual) != [token]
                        or re.findall(r"£(nbv_mi_[A-Za-z0-9_]+(?:\|[0-9]+)?)", tooltip) != [token]):
                    name_errors.append({"语言": language, "编号": ident, "实际名称": actual})
            for key, value in values.items():
                if "£nbv_mi_" in value and not re.fullmatch(r"nbv_row_(?:name|tooltip)_\d+", key):
                    misplaced_icons.append({"语言": language, "键": key})
        check("中英词条及标题各加一个正确图标，原名称保持不变", not name_errors, name_errors[:30])
        check("新图标仅出现在词条名和悬停标题，未污染来源及数值", not misplaced_icons, misplaced_icons[:30])
        check("图标移植不覆盖原版或第三方本地化键", all(key.startswith("nbv_") for values in locs.values() for key in values))
        gfx_path = "interface/nbv_modifier_icons.gfx"
        icon_sprites = named_blocks(parsed[gfx_path])
        expected_sprites = {"GFX_" + token for token in used_tokens}
        all_gfx_names = Counter(name for relative, tree in parsed.items() if relative.endswith(".gfx")
                                for name, definitions in named_blocks(tree).items() for _ in definitions)
        check("所有图标 sprite 私有且唯一，无原版 sprite 覆盖",
              set(icon_sprites) == expected_sprites
              and all(all_gfx_names[name] == 1 for name in expected_sprites)
              and all(name.startswith("GFX_nbv_") for name in all_gfx_names)
              and all(len(nodes) == 1 and nodes[0].key.lower() == "spritetype" for nodes in icon_sprites.values()))
        asset_errors, asset_details, copied_paths = [], [], set()
        for token, record in resource_map.items():
            sprite = "GFX_" + token
            definitions = icon_sprites.get(sprite, [])
            nodes = definitions[0].value if len(definitions) == 1 else []
            texture = record["texture_file"]
            origin = record["source"]["origin"]
            texture_path = Path(texture)
            path_is_safe = not texture_path.is_absolute() and ".." not in texture_path.parts and texture_path.suffix.lower() == ".dds"
            if origin == "workshop_mod":
                path_is_safe &= texture_path.as_posix().startswith("gfx/nbv_modifier_icons/")
                asset = ROOT / texture_path
                copied_paths.add(texture_path.as_posix())
            else:
                path_is_safe &= origin == "vanilla_game" and texture_path.as_posix().startswith("gfx/texticons/")
                asset = args.game_root / texture_path
            data = asset.read_bytes() if path_is_safe and asset.is_file() else b""
            valid_dds = len(data) >= 128 and data[:4] == b"DDS " and struct.unpack_from("<I", data, 4)[0] == 124
            width, height = ((struct.unpack_from("<I", data, 16)[0], struct.unpack_from("<I", data, 12)[0])
                             if valid_dds else (0, 0))
            frames = record["frames"]
            frames_valid = isinstance(frames, int) and frames > 0 and width > 0 and width % frames == 0
            correct = (path_is_safe and valid_dds and frames_valid and 0 < height <= 20
                       and width == record["width"] and height == record["height"]
                       and hashlib.sha256(data).hexdigest() == record["sha256"]
                       and record["sprite"] == sprite and scalar(nodes, "name") == sprite
                       and Path(resource_scalar(nodes, "texturefile", "")) == texture_path
                       and int(resource_scalar(nodes, "noOfFrames", "1")) == frames)
            detail = {"图标": token, "文件": str(asset), "尺寸": [width, height], "帧数": frames, "来源": origin}
            asset_details.append(detail)
            if not correct:
                asset_errors.append(detail)
            if path_is_safe and asset.is_file():
                file_fingerprints[rel(asset)] = sha256(asset)
        actual_copied_paths = {rel(path) for path in (ROOT / "gfx/nbv_modifier_icons").rglob("*") if path.is_file()}
        check("图标 DDS 文件、哈希、尺寸及帧数与 sprite 完整对应且容纳于 20 像素文本行",
              not asset_errors, {"资源数": len(asset_details), "错误": asset_errors[:30]})
        check("移植贴图目录仅包含已使用的私有图标素材", actual_copied_paths == copied_paths,
              {"文件数": len(actual_copied_paths), "额外": sorted(actual_copied_paths - copied_paths),
               "缺失": sorted(copied_paths - actual_copied_paths)})
        resources.extend({"类型": "词条文本图标", **detail} for detail in asset_details)

    guarded("移植图标映射、本地化及资源审查正常执行", inspect_modifier_icons)

    def inspect_source_tree():
        """Validate generated source branches independently of build_mod.py.

        This traverses EVERY leaf, including inactive branches.  Decimal
        projection checks display precision only, not engine modifier math.
        """
        path = ROOT / "tools/data/source-display-manifest.json"
        source_manifest = json.loads(path.read_text(encoding="utf-8"))
        file_fingerprints[rel(path)] = sha256(path)
        source_rows = source_manifest["records"]
        source_indices = [row["index"] for row in source_rows]
        check("来源清单连续唯一编号与声明数量一致",
              source_indices == list(range(1, len(source_rows) + 1))
              and source_manifest["record_count"] == len(source_rows), {"来源条数": len(source_rows)})
        expected_by_metric = {ident: [] for ident in expected_ids}
        for row in source_rows:
            expected_by_metric[row["metric_id"]].append(row["index"])
        original_by_id = {}
        input_hash_ok = True
        expected_bindings = []
        for filename in SOURCE_INPUT_TABLES:
            source_path = ROOT / "tools/data" / filename
            if not source_path.exists():
                continue
            table = json.loads(source_path.read_text(encoding="utf-8"))
            file_fingerprints[rel(source_path)] = sha256(source_path)
            input_hash_ok &= source_manifest["input_hashes"].get(filename) == sha256(source_path)
            if filename == "source-bindings.json":
                check("民族精神来源扫描没有整文件解析遗漏", not table.get("parse_failures"),
                      table.get("parse_failures", []))
                regressions = {
                    "trotskyite_plot_nsb": {"stability_factor", "political_power_factor"},
                    "SOV_politicized_military": {"command_abilities_cost_factor", "land_doctrine_cost_factor",
                        "naval_doctrine_cost_factor", "air_doctrine_cost_factor", "drift_defence_factor", "army_core_defence_factor"},
                }
                actual = {source: {key for key, entries in table["by_modifier"].items()
                                   if any(entry["source_id"] == source for entry in entries)} for source in regressions}
                check("苏联开局两个民族精神的八项直接来源完整保留", actual == regressions,
                      {source: sorted(keys) for source, keys in actual.items()})
            if filename == "special-source-bindings.json":
                candidates = table.get("unavailable_landmark_candidates", [])
                check("未能可靠查询健康的奇观候选不进入生产来源", len(candidates) == 26
                      and all(not binding.get("production_eligible", True) for binding in candidates)
                      and not any(binding.get("source_type") == "landmark"
                                  for entries in table["by_modifier"].values() for binding in entries),
                      {"未启用奇观候选": len(candidates)})
                invalid_landmarks = []
                for entries in table["by_modifier"].values():
                    for binding in entries:
                        if binding.get("source_type") != "landmark":
                            continue
                        nodes = list(walk(parse_script(binding["activation_script"])))
                        counts = [node for node in nodes if node.key == binding["source_id"]]
                        if ([(node.op, node.value) for node in counts] != [(">", "0"), ("<", "2"), (">", "0")]
                                or not any(node.key == "has_damaged_buildings" and node.value == "no" for node in nodes)
                                or any(node.key == "non_damaged_building_level" for node in nodes)
                                or "building_level@" in binding["activation_script"]):
                            invalid_landmarks.append(binding["id"])
                check("省级奇观使用原生计数与国家无损坏建筑的保守门槛", not invalid_landmarks, invalid_landmarks)
            for key, entries in table["by_modifier"].items():
                for entry in entries:
                    if entry.get("value_kind", "literal") == "literal" and Decimal(entry["value_literal"]) == 0:
                        continue
                    identity = (key, entry["source_category"], entry["source_id"])
                    expected_bindings.append(identity)
                    original_by_id[identity] = entry
        generated_bindings = [(row["key"], row["source_category"], row["source_id"]) for row in source_rows]
        check("来源清单覆盖全部可信输入且没有额外或重复来源", input_hash_ok
              and Counter(generated_bindings) == Counter(expected_bindings)
              and all(count == 1 for count in Counter(generated_bindings).values()),
              {"来源条数": len(source_rows), "输入条数": len(expected_bindings), "输入哈希一致": input_hash_ok})
        tree = parsed["common/scripted_localisation/nbv_source_localisation.txt"]
        definitions = {}
        for entry in tree:
            if entry.key == "defined_text":
                name = scalar(entry.value, "name")
                if name in definitions:
                    raise ValueError("Duplicate source function: " + name)
                definitions[name] = entry.value
        leaf_names = {name for name in definitions if re.fullmatch(r"NBVSource\d+", name)}
        check("来源叶函数与清单一一对应", leaf_names == {f"NBVSource{i}" for i in source_indices})
        activation_errors, format_errors, alias_errors = [], [], []
        runtime_errors, runtime_count = [], 0
        for row in source_rows:
            ident = row["index"]
            identity = (row["key"], row["source_category"], row["source_id"])
            original = original_by_id[identity]
            texts = children(definitions[f"NBVSource{ident}"], "text")
            expected_activation = parse_script(original["activation_script"])
            kind = original.get("value_kind", "literal")
            if (len(expected_activation) != 1
                    or expected_activation[0].key not in ("has_idea", "has_country_leader_with_trait", "has_tech",
                        "has_doctrine", "has_dynamic_modifier", "has_decision", "has_completed_track", "has_government", "AND")
                    or row["activation_script"] != original["activation_script"]
                    or row["value_literal"] != original["value_literal"]
                    or row.get("value_kind", "literal") != kind
                    or row.get("value_expression") != original.get("value_expression")):
                activation_errors.append(ident)
            base_format = binding_map[row["key"]]["format_code"]
            source_format = row["source_format_code"]
            base_precision = int(re.search(r"\d+$", base_format).group())
            # %% appends a percentage sign to raw percentage points. Only a
            # single % scales the number by 100 in Clausewitz localisation.
            scale = Decimal(100 if "%" in base_format and "%%" not in base_format else 1)
            formats = row.get("display_formats", [source_format])
            variable = f"nbv_source_value_{ident}"
            if kind == "runtime":
                runtime_count += 1
                expression = original["value_expression"]
                expected_formats = [re.sub(r"\d+$", str(precision), base_format)
                                    for precision in range(base_precision, max(base_precision, 3 if scale == 100 else 5) + 1)]
                if (set(expression) != {"variable", "coefficient", "offset"}
                        or not re.fullmatch(r"(?:ROOT|global|[A-Z]{3})\.[A-Za-z_][A-Za-z_0-9]*", expression["variable"])
                        or formats != expected_formats or source_format != expected_formats[0]):
                    runtime_errors.append({"编号": ident, "原因": "运行输入表达式或精度序列不一致"})
                expected_steps = list(expected_activation)
                calculation = f"set_temp_variable = {{ {variable} = {expression['variable']} }}"
                if Decimal(expression["coefficient"]) != 1:
                    calculation += f" multiply_temp_variable = {{ {variable} = {expression['coefficient']} }}"
                if Decimal(expression["offset"]) != 0:
                    calculation += f" add_to_temp_variable = {{ {variable} = {expression['offset']} }}"
                expected_steps += parse_script(calculation)
                if len(texts) != len(expected_formats) + 1:
                    runtime_errors.append({"编号": ident, "原因": "运行值精度分支数量不一致"})
                for position, code in enumerate(expected_formats):
                    if position >= len(texts) - 1:
                        break
                    precision = int(re.search(r"\d+$", code).group())
                    threshold = Decimal(1).scaleb(-precision) / scale
                    gate = parse_script(f"OR = {{ check_variable = {{ {variable} = {threshold:f} compare = greater_than_or_equals }} "
                                        f"check_variable = {{ {variable} = {-threshold:f} compare = less_than_or_equals }} }}")
                    actual_steps = one(texts[position].value, "trigger").value
                    if [script_signature(item) for item in actual_steps] != [
                            script_signature(item) for item in expected_steps + gate]:
                        runtime_errors.append({"编号": ident, "分支": precision,
                                               "原因": "来源输入、系数、偏移、门槛或计算顺序不一致"})
            elif kind == "literal":
                decimal_places = int(re.search(r"\d+$", source_format).group())
                value = Decimal(original["value_literal"]) * scale
                rendered = value.quantize(Decimal(1).scaleb(-decimal_places), rounding=ROUND_HALF_UP)
                expected_steps = expected_activation + parse_script(
                    f"set_temp_variable = {{ {variable} = {original['value_literal']} }}")
                actual_steps = one(texts[0].value, "trigger").value
                if (len(texts) != 2 or [script_signature(item) for item in actual_steps] != [
                        script_signature(item) for item in expected_steps]):
                    activation_errors.append(ident)
                if (formats != [source_format]
                        or re.sub(r"\d+", "", base_format) != re.sub(r"\d+", "", source_format)
                        or not re.fullmatch(r"[+\-=%0-9YGRWH.?]+", source_format) or rendered == 0
                        # Require one whole visible least-significant unit;
                        # half-unit engine rounding can otherwise display zero.
                        or abs(value) * (Decimal(10) ** decimal_places) < 1):
                    format_errors.append({"编号": ident, "键": row["key"], "值": original["value_literal"], "格式": source_format})
            else:
                activation_errors.append(ident)
            if (not texts or len(texts[-1].value) != 1
                    or scalar(texts[-1].value, "localization_key") != "nbv_empty_text"):
                activation_errors.append(ident)
            for language, values in locs.items():
                for position, code in enumerate(formats):
                    precision = int(re.search(r"\d+$", code).group())
                    suffix = "" if position == 0 else f"_p{precision}"
                    loc_key = f"nbv_source_line_{ident}{suffix}"
                    expected_name = "$" + row["name_loc_key"] + "$"
                    if original.get("source_type") == "country_leader_trait":
                        separator = "：" if language == "simp_chinese" else ": "
                        expected_name = "[ROOT.GetLeader]" + separator + expected_name + separator
                    else:
                        expected_name += " "
                    expected_line = r"\n" + expected_name + "[?" + variable + "|" + code + "]"
                    if (values.get(loc_key) != expected_line or position >= len(texts) - 1
                            or scalar(texts[position].value, "localization_key") != loc_key):
                        format_errors.append({"编号": ident, "语言": language, "原因": "领袖行姓名特质数值、其他来源名称数值或精度分支不一致"})
                if original.get("display_name_zh") or original.get("requires_single_line_alias"):
                    key = row["name_loc_key"]
                    alias = values.get(key, "")
                    if original.get('display_name_zh'):
                        expected_alias = re.sub(r'(?:\\n|[\r\n])+', ' ', original.get(
                            'display_name_zh' if language == 'simp_chinese' else 'display_name_en') or original['display_name_zh'])
                    else:
                        expected_alias = original["name_single_line_zh" if language == "simp_chinese" else "name_single_line_en"]
                    if (not key.startswith("nbv_source_name_") or alias != expected_alias
                            or not alias.strip() or any(c in alias for c in (r"\n", "\n", "\r"))):
                        alias_errors.append({"编号": ident, "语言": language, "名称键": key})
        check("来源叶仅按可信原始激活条件读取定义且未激活为空", not activation_errors, activation_errors[:30])
        check("运行来源逐分支读取原版输入并按原系数偏移计算且零值不显示", not runtime_errors,
              {"运行来源数": runtime_count, "错误": runtime_errors[:30]})
        check("来源值保留原符号单位颜色且静态精度投影非零", not format_errors, format_errors[:30])
        check("原版换行名称具有完整的单行中英文来源别名", not alias_errors, alias_errors[:30])
        expected_activations = {row["index"]: row["activation_script"] for row in source_rows}
        language_details, tree_errors = [], []
        for language, values in locs.items():
            maximum_calls, maximum_depth, visited = 0, 0, set()
            cache = {}

            def expand_localisation(key, ancestry=()):
                nonlocal maximum_calls, maximum_depth
                if key in ancestry:
                    raise ValueError("Source localisation cycle: " + key)
                maximum_depth = max(maximum_depth, len(ancestry))
                refs = re.findall(r"\[(NBVSource\w+)\]", values[key])
                if values[key] != "".join("[" + function + "]" for function in refs):
                    raise ValueError("Unexpected source text/residual in " + key)
                maximum_calls = max(maximum_calls, len(refs))
                if len(refs) > 8:
                    raise ValueError("Source expansion exceeds eight calls: " + key)
                leaves = []
                for function in refs:
                    if function not in definitions:
                        raise ValueError("Missing source function: " + function)
                    visited.add(function)
                    if re.fullmatch(r"NBVSource\d+", function):
                        leaves.append(int(function[9:]))
                        continue
                    if function not in cache:
                        texts = children(definitions[function], "text")
                        descendants = expand_localisation(scalar(texts[0].value, "localization_key"), ancestry + (key,))
                        trigger = one(texts[0].value, "trigger").value
                        gate = one(trigger, "OR").value
                        actual = list(dict.fromkeys(script_signature(entry) for entry in gate))
                        expected = list(dict.fromkeys(script_signature(parse_script(expected_activations[index])[0]) for index in descendants))
                        if (len(trigger) != 1 or actual != expected or len(texts) != 2
                                or scalar(texts[1].value, "localization_key") != "nbv_empty_text"):
                            raise ValueError("Incorrect active-source group gate: " + function)
                        cache[function] = descendants
                    leaves.extend(cache[function])
                return leaves

            for row in records:
                ident = row["id"]
                found = expand_localisation(f"nbv_sources_{ident}")
                if found != expected_by_metric[ident] or len(found) != len(set(found)):
                    tree_errors.append({"语言": language, "指标": ident, "实际数": len(found),
                                        "期望数": len(expected_by_metric[ident])})
                expected_title = ("§Y" + values[f"nbv_row_name_{ident}"] + "§!  "
                                  + values[f"nbv_row_value_{ident}"] + f"$nbv_sources_{ident}$")
                if values[f"nbv_row_tooltip_{ident}"] != expected_title:
                    tree_errors.append({"语言": language, "指标": ident, "原因": "标题、总值或来源根引用不一致"})
            if visited != set(definitions):
                tree_errors.append({"语言": language, "原因": "存在孤立或缺失来源函数"})
            language_details.append({"语言": language, "指标数": len(records), "来源叶数": len(source_rows),
                                     "单层最大调用数": maximum_calls, "最大分组深度": maximum_depth})
        check("完整来源树无缺漏重复循环且顺序正确、每层至多八调用", not tree_errors,
              {"树": language_details, "错误": tree_errors[:30]})
        check("来源标题仅完整名称和引擎总值、各来源独行且无残差", not tree_errors and not format_errors,
              {"指标数": len(records), "来源数": len(source_rows)})

    guarded("完整来源树与来源呈现审查正常执行", inspect_source_tree)

    def inspect_structure():
        gui_ast = parsed["interface/nbv.gui"]
        gfx_ast = parsed["interface/nbv.gfx"]
        sgui = parsed["common/scripted_guis/nbv_scripted_gui.txt"]
        effects = parsed["common/scripted_effects/nbv_effects.txt"]
        triggers = parsed["common/scripted_triggers/nbv_triggers.txt"]
        sloc = [entry for path, tree in parsed.items() if path.startswith("common/scripted_localisation/")
                for entry in tree]
        gui_names = named_blocks(gui_ast)
        gui_definitions = one(sgui, "scripted_gui").value
        main_gui = one(gui_definitions, "nbv_main").value
        entry_gui = one(gui_definitions, "nbv_entry").value
        effect_map = {e.key: e for e in effects}
        trigger_map = {e.key: e for e in triggers}
        dynamic_texts = named_blocks(sloc)
        check("所有脚本本地化函数名称唯一", all(len(definitions) == 1 for definitions in dynamic_texts.values()))
        sprites = named_blocks(gfx_ast)
        from build_interface import build as build_interface
        check("界面文件与单列表生成器一致", source_text["interface/nbv.gui"] == build_interface())
        check("两个 GUI 均绑定当前玩家", all(scalar(e.value, "context_type") == "player_context" for e in gui_definitions))
        check("独立入口挂载与主窗分离", scalar(entry_gui, "parent_window_name") == "raid_filter"
              and scalar(main_gui, "parent_window_name") is None and scalar(main_gui, "parent_window_token") is None)
        window = gui_names["nbv_window"][0].value
        direct_window = {scalar(e.value, "name"): e for e in window
                         if isinstance(e.value, list) and scalar(e.value, "name")}
        check("主窗声明可拖动、点击置前并裁剪边界", scalar(window, "moveable") == "yes"
              and scalar(window, "click_to_front") == "yes" and scalar(window, "clipping") == "yes")
        header_icon = direct_window.get("nbv_header_background")
        title_node = direct_window.get("nbv_title")
        close_node = direct_window.get("nbv_close_button")
        check("标题装饰和文字直接归属可拖动主窗且鼠标穿透", "nbv_header" not in gui_names
              and header_icon is not None and header_icon.key == "iconType"
              and scalar(header_icon.value, "spriteType") == "GFX_nbv_header_background"
              and scalar(header_icon.value, "alwaystransparent") == "yes"
              and title_node is not None and title_node.key == "instantTextboxType"
              and scalar(title_node.value, "alwaystransparent") == "yes"
              and close_node is not None and close_node.key == "buttonType")
        check("中文窗口标题和侧边悬停提示使用修正统计名称", locs["simp_chinese"].get("nbv_entry_tooltip") == "修正统计"
              and locs["simp_chinese"].get("nbv_window_title") == "[ROOT.GetName] · 国家修正统计")
        check("侧边入口无可见文字并保留悬停提示", "nbv_entry_text" not in gui_names
              and all("nbv_entry_label" not in values for values in locs.values())
              and scalar(gui_names["nbv_open_button"][0].value, "pdx_tooltip") == "nbv_entry_tooltip"
              and scalar(gui_names["nbv_open_button"][0].value, "buttonText") is None)
        check("不绑定 dirty 或 AI 点击", not any(e.key in ("dirty", "ai_enabled") for e in walk(sgui)))
        from sidebar_placement import placement, Rect, too_close
        sidebar = placement()
        check("已知侧栏占位与生成记录一致", json.loads((ROOT / 'tools/data/sidebar-placement.json').read_text(encoding='utf-8')) == sidebar)
        selected = Rect(**sidebar['position'])
        check("已知侧栏入口保留间距且排除TNO适配", all(not too_close(selected, Rect(**{k: r[k] for k in ('x', 'y', 'width', 'height')}), sidebar['gap']) for r in sidebar['reservations'])
              and sidebar['excluded_families'] == ['TNO and its submods'] and not sidebar['runtime_collision_detection'])
        icon_pos = one(gui_names['nbv_entry_icon'][0].value, 'position').value
        button = gui_names['nbv_open_button'][0].value
        button_pos, button_size = one(button, 'position').value, one(button, 'size').value
        check("入口图标水平垂直居中", all(float(scalar(icon_pos, axis)) + extent / 2 == float(scalar(button_pos, axis)) + float(scalar(button_size, axis)) / 2 for axis, extent in (('x', 55), ('y', 41))))
        check("窗口绑定存在", all(scalar(e.value, "window_name") in gui_names for e in gui_definitions))
        callbacks = [e for e in walk(sgui) if e.key and e.key.endswith("_click")]
        callback_names = {e.key.removesuffix("_click") for e in callbacks}
        expected_buttons = {"nbv_open_button", "nbv_close_button", "nbv_filter_button", "nbv_refresh_button"}
        expected_buttons.update(f"nbv_tab_{i}" for i in range(1, 7))
        check("10 个点击回调与控件匹配", callback_names == expected_buttons and len(callbacks) == 10
              and all(name in gui_names and any(e.key == "buttonType" for e in gui_names[name]) for name in callback_names), sorted(callback_names))
        check("所有点击回调调用已声明效果", all(e.key in effect_map for cb in callbacks for e in cb.value))
        tab_positions = [one(gui_names[f"nbv_tab_{i}"][0].value, "position").value for i in range(1, 7)]
        tab_x = [float(scalar(p, "x")) for p in tab_positions]
        check("六个页签顶部横排顺序一致", tab_x == sorted(tab_x) and len(set(tab_x)) == 6
              and len({scalar(p, "y") for p in tab_positions}) == 1
              and all(scalar(gui_names[f"nbv_tab_{i}"][0].value, "buttonText") == f"nbv_page_{i}" for i in range(1, 7)))
        close_button = gui_names["nbv_close_button"][0].value
        check("Esc 与 X 使用同一关闭按钮", scalar(close_button, "shortcut") == "ESCAPE"
              and any(e.key == "nbv_close" for e in one(one(main_gui, "effects").value, "nbv_close_button_click").value))
        close = effect_map["nbv_close"].value
        check("关闭不清除或重置页面", len(close) == 1 and close[0].key == "clr_country_flag" and close[0].value == "nbv_window_open")
        grid = gui_names["nbv_rows_grid"][0].value
        grid_nodes = [e for e in walk(gui_ast) if e.key == "gridBoxType"]
        check("全部内容只使用一个纵向网格", len(grid_nodes) == 1
              and scalar(grid_nodes[0].value, "name") == "nbv_rows_grid"
              and scalar(grid, "max_slots_horizontal") == "1"
              and scalar(grid, "add_horizontal") != "yes")
        check("纵向网格 format 使用引擎大写枚举", scalar(grid, "format") == "UPPER_LEFT")
        check("纵向网格固定 34 高行距", scalar(one(grid, "slotsize").value, "height") == "34")
        lists = one(main_gui, "dynamic_lists").value
        check("单个编号列表不切换国家作用域", len(lists) == 1 and lists[0].key == "nbv_rows_grid"
              and scalar(lists[0].value, "change_scope") == "no"
              and scalar(lists[0].value, "array") == "nbv_display_rows"
              and scalar(lists[0].value, "value") == "nbv_row_id"
              and scalar(lists[0].value, "entry_container") == "[NBVRowContainer]")
        row_templates = {"nbv_high_heading_row", "nbv_low_heading_row", "nbv_high_row", "nbv_low_row"}
        container_dispatch = dynamic_texts["NBVRowContainer"][0].value
        container_targets = {e.value for e in walk(container_dispatch) if e.key == "localization_key"}
        check("动态行容器分发仅引用四种已定义模板", container_targets == row_templates <= set(gui_names))
        scroll_area = gui_names["nbv_scroll_area"][0].value
        scroll_children = named_blocks(scroll_area)
        check("高低优先级共用唯一滚动列表", "nbv_rows_grid" in scroll_children
              and not {"nbv_high_grid", "nbv_low_grid", "nbv_content_end"} & set(gui_names))
        scroll_backgrounds = children(scroll_area, "background")
        check("滚动视口显式裁剪、保留滚动条并提供鼠标接收背景", scalar(scroll_area, "clipping") == "yes"
              and scalar(scroll_area, "autohide_scrollbars") == "no"
              and scalar(scroll_area, "verticalScrollbar") == "right_vertical_slider_intel"
              and scalar(scroll_area, "scroll_wheel_factor") == "34"
              and scalar(scroll_area, "smooth_scrolling") == "yes"
              and len(scroll_backgrounds) == 1
              and scalar(scroll_backgrounds[0].value, "name") == "nbv_scroll_background"
              and scalar(scroll_backgrounds[0].value, "quadTextureSprite") == "GFX_tiled_window_transparent"
              and scalar(scroll_backgrounds[0].value, "alwaystransparent") != "yes")
        scroll_position, scroll_size = one(scroll_area, "position").value, one(scroll_area, "size").value
        window_size = one(window, "size").value
        check("滚动视口完整位于主窗边界内", all(
              0 <= float(scalar(scroll_position, axis))
              and float(scalar(scroll_position, axis)) + float(scalar(scroll_size, dim)) <= float(scalar(window_size, dim))
              for axis, dim in (("x", "width"), ("y", "height"))))
        check("删除顶部及底部说明控件", not {"nbv_subtitle", "nbv_footer_text"} & set(gui_names)
              and not any(e.key == "text" and e.value in ("nbv_window_subtitle", "nbv_footer") for e in walk(gui_ast)))
        check("筛选与刷新按钮没有悬停解释框", all(not any(e.key in ("pdx_tooltip", "tooltip", "tooltipText")
              for e in gui_names[name][0].value) for name in ("nbv_filter_button", "nbv_refresh_button")))
        cell_details = []
        for band, columns in (("high", 3), ("low", 4)):
            template = gui_names[f"nbv_{band}_row"][0].value
            direct_cells = [e for e in template if e.key == "containerWindowType"]
            row_width = float(scalar(one(template, "size").value, "width"))
            row_height = float(scalar(one(template, "size").value, "height"))
            check(f"{band} 行模板的固定列数及高度", len(direct_cells) == columns and row_height == 34)
            previous_right = 0
            for slot in range(1, columns + 1):
                cell = gui_names[f"nbv_{band}_cell_{slot}"][0].value
                name = gui_names[f"nbv_{band}_name_{slot}"][0].value
                value = gui_names[f"nbv_{band}_value_{slot}"][0].value
                hitbox = gui_names[f"nbv_{band}_hitbox_{slot}"][0].value
                cx = float(scalar(one(cell, "position").value, "x"))
                cw = float(scalar(one(cell, "size").value, "width"))
                ch = float(scalar(one(cell, "size").value, "height"))
                np, vp = one(name, "position").value, one(value, "position").value
                nx, ny = float(scalar(np, "x")), float(scalar(np, "y"))
                vx, vy = float(scalar(vp, "x")), float(scalar(vp, "y"))
                nw, nh = float(scalar(name, "maxWidth")), float(scalar(name, "maxHeight"))
                vw, vh = float(scalar(value, "maxWidth")), float(scalar(value, "maxHeight"))
                valid = (ny == vy and ny >= 0 and ny + max(nh, vh) <= ch < row_height
                         and 0 <= nx < nx + nw < vx < vx + vw <= cw
                         and previous_right <= cx and cx + cw <= row_width
                         and scalar(name, "fixedsize") == scalar(value, "fixedsize") == "yes"
                         and scalar(name, "format") == "left" and scalar(value, "format") == "right"
                         and scalar(hitbox, "pdx_tooltip") == f"nbv_{band}_tooltip_{slot}")
                cell_details.append({"格": f"{band}_{slot}", "通过": valid,
                                     "名称范围": [nx, nx + nw], "数值范围": [vx, vx + vw], "高度": ch})
                previous_right = cx + cw
        check("七种词条单行名值不重叠且完整位于各自格内", all(row["通过"] for row in cell_details), cell_details)
        control_references = [e.key for e in one(main_gui, "properties").value]
        control_references += [e.key.removesuffix("_visible") for e in one(main_gui, "triggers").value if e.key.endswith("_visible")]
        check("所有动态属性与显隐回调控件存在", all(name in gui_names for name in control_references), control_references)
        window_children = [e for e in gui_names["nbv_window"][0].value if isinstance(e.value, list) and scalar(e.value, "name")]
        check("计算图标在主窗其余子控件之前", scalar(window_children[0].value, "name") == "nbv_calculator"
              and scalar(window_children[0].value, "hide") != "yes")
        calculator = one(one(main_gui, "triggers").value, "nbv_calculator_visible").value
        check("计算器负责临时列表准备", len(calculator) == 1 and calculator[0].key == "nbv_prepare_view"
              and not any(e.key == "nbv_prepare_view" for e in one(main_gui, "visible").value))
        for band, slots in (("high", 3), ("low", 4)):
            for slot in range(1, slots + 1):
                for suffix in ("name", "value", "tooltip"):
                    name = f"NBV{band.title()}{suffix.title()}{slot}"
                    node = dynamic_texts[name][0].value
                    key = f"nbv_row_{suffix}_[?nbv_entry_id]"
                    check(f"动态本地化分发 {name}", any(e.key == "localization_key" and e.value == key for e in walk(node))
                          and any(e.key == f"nbv_resolve_{band}_{slot}" and e.value == "yes" for e in walk(node)))

        bad_names, written = [], set()
        variable_commands = {"set_variable", "add_to_variable", "subtract_from_variable", "multiply_variable", "divide_variable", "modulo_variable",
                             "set_temp_variable", "add_to_temp_variable", "subtract_from_temp_variable", "multiply_temp_variable", "divide_temp_variable", "modulo_temp_variable"}
        array_commands = {"clear_array", "clear_temp_array", "add_to_array", "add_to_temp_array"}
        all_script_nodes = [e for path, tree in parsed.items() if path.startswith("common/") for e in walk(tree)]
        # Native researched_techs is read-only here. Do not allow it as a write
        # target merely because the same identifier is valid in is_in_array.
        native_array_reads = {id(field) for node in all_script_nodes
                              if node.key == "is_in_array" and isinstance(node.value, list)
                              for field in node.value if field.key == "array" and field.value == "researched_techs"}
        # Derive native reads from the audited INPUT tables, never from generated
        # production code. A permitted read never permits the same identifier as
        # a write target. The source-tree audit separately checks exact placement,
        # arithmetic order and activation for all generated source leaves.
        native_value_reads, native_flag_reads = set(), set()
        for filename in SOURCE_INPUT_TABLES:
            path = ROOT / "tools/data" / filename
            if not path.exists():
                continue
            table = json.loads(path.read_text(encoding="utf-8"))
            for entries in table["by_modifier"].values():
                for entry in entries:
                    expression = entry.get("value_expression")
                    if expression:
                        native_value_reads.add(expression["variable"])
                    for node in walk(parse_script(entry["activation_script"])):
                        if node.key == "check_variable" and isinstance(node.value, list):
                            left_name, _, right_name = variable_check_parts(node.value)
                            native_value_reads.update((left_name, right_name))
                        elif node.key == "has_country_flag":
                            native_flag_reads.add(node.value)
        def is_ui_value(value):
            try:
                float(value)
                return True
            except ValueError:
                return (value.startswith("nbv_") or value.startswith("ROOT.nbv_")
                        or value.startswith("ROOT.modifier@") or value in native_value_reads)
        for node in all_script_nodes:
            if node.key in variable_commands or node.key in array_commands:
                targets = [e.key for e in node.value] if isinstance(node.value, list) else [node.value]
                for target in targets:
                    written.add(target)
                    if not target.startswith("nbv_"):
                        bad_names.append(target)
                if isinstance(node.value, list):
                    for assignment in node.value:
                        if not is_ui_value(assignment.value):
                            bad_names.append(assignment.value)
            if node.key == "check_variable":
                left_name, _, right_name = variable_check_parts(node.value)
                if not is_ui_value(left_name):
                    bad_names.append(left_name)
                if not is_ui_value(right_name):
                    bad_names.append(right_name)
            if node.key in ("array", "index") and isinstance(node.value, str) and not is_ui_value(node.value) and id(node) not in native_array_reads:
                bad_names.append(node.value)
            if (node.key in ("set_country_flag", "clr_country_flag") and not node.value.startswith("nbv_")
                    or node.key == "has_country_flag" and not node.value.startswith("nbv_") and node.value not in native_flag_reads):
                bad_names.append(node.value)
            if node.key in ("set_global_flag", "clr_global_flag"):
                bad_names.append(node.key)
        check("所有写入变量、数组与 flag 使用 nbv 前缀且无全局开关", not bad_names, {"命名错误": bad_names, "写入对象": sorted(written)})
        native_effects = {"if", "else", "set_variable", "clr_country_flag", "set_country_flag", "clear_array", "add_to_array"}
        direct_native = set()
        def effect_commands(nodes):
            for node in nodes:
                direct_native.add(node.key)
                if node.key in ("if", "else"):
                    effect_commands([e for e in node.value if e.key != "limit"])
        for effect in effects:
            effect_commands(effect.value)
        check("效果仅修改本模组 UI 状态", direct_native <= native_effects | set(effect_map), sorted(direct_native))

        filter_mismatches = []
        for label, tree, command in (("实时", triggers, "add_to_temp_array"), ("后备", effects, "add_to_array")):
            ids = []
            for branch in walk(tree):
                if branch.key != "if" or not isinstance(branch.value, list):
                    continue
                additions = [e for e in branch.value if e.key == command]
                if not additions:
                    continue
                assert len(additions) == 1
                assignment = additions[0].value[0]
                if assignment.key not in ("nbv_high_entries", "nbv_low_entries",
                                           "nbv_high_entries_cache", "nbv_low_entries_cache"):
                    continue
                ident = int(assignment.value)
                ids.append(ident)
                keys = [e.key.split("@", 1)[1] for e in walk(one(branch.value, "limit").value)
                        if e.key and e.key.startswith("ROOT.modifier@")]
                selected = next((row for row in display_records if row["id"] == ident), None)
                expected_array = (f"nbv_{selected['display_priority_band']}_entries"
                                  + ("_cache" if label == "后备" else "")) if selected else None
                if not selected or keys != [selected["key"]] or assignment.key != expected_array:
                    filter_mismatches.append(f"{label}:{ident}")
            if ids != [row["id"] for row in display_records]:
                filter_mismatches.append(f"{label}:展示ID或完整遍历顺序错误")
        check("展示词条实时/后备筛选按 Markdown 顺序读取正确修正键和分组",
              not filter_mismatches, filter_mismatches[:30])

        model = ScriptModel(effects, triggers)
        model.run("nbv_open")
        check("模型：首次政治页并显示全部", model.vars.get("nbv_page") == 1 and {"nbv_window_open", "nbv_show_zero"} <= model.flags)
        page_results = []
        row_results = []

        def expected_row_ids(high_count, low_count):
            high = ([10000] + list(range(1, high_count + 1, 3))) if high_count else []
            low = ([20000] + [-i for i in range(1, low_count + 1, 4)]) if low_count else []
            return high + low

        def resolve_display_rows():
            seen = {"high": [], "low": []}
            empty_cells_ok = True
            for row_id in model.temp_arrays["nbv_display_rows"]:
                model.temp["nbv_row_id"] = row_id
                if row_id in (10000, 20000):
                    for band, slots in (("high", 3), ("low", 4)):
                        for slot in range(1, slots + 1):
                            empty_cells_ok &= not model.check(trigger_map[f"nbv_resolve_{band}_{slot}"].value)
                            empty_cells_ok &= model.temp["nbv_entry_id"] == 0
                    continue
                band, slots = ("high", 3) if row_id > 0 else ("low", 4)
                other, other_slots = ("low", 4) if row_id > 0 else ("high", 3)
                for slot in range(1, slots + 1):
                    index = abs(row_id) - 1 + slot - 1
                    shown = model.check(trigger_map[f"nbv_resolve_{band}_{slot}"].value)
                    expected = model.temp_arrays[f"nbv_{band}_entries"]
                    if index < len(expected):
                        empty_cells_ok &= shown and model.temp["nbv_entry_id"] == expected[index]
                        seen[band].append(model.temp["nbv_entry_id"])
                    else:
                        empty_cells_ok &= not shown and model.temp["nbv_entry_id"] == 0
                for slot in range(1, other_slots + 1):
                    empty_cells_ok &= not model.check(trigger_map[f"nbv_resolve_{other}_{slot}"].value)
                    empty_cells_ok &= model.temp["nbv_entry_id"] == 0
            return seen, empty_cells_ok

        for page, category in enumerate(PAGES, 1):
            model.run(f"nbv_select_page_{page}")
            model.check(trigger_map["nbv_prepare_view"].value)
            for band in ("high", "low"):
                expected = [r["id"] for r in display_records if r["category"] == category and r["display_priority_band"] == band]
                actual = model.temp_arrays[f"nbv_{band}_entries"]
                cached = model.arrays[f"nbv_{band}_entries_cache"]
                page_results.append({"页": category, "区": band, "数量": len(actual), "通过": actual == expected == cached})
            actual_rows = model.temp_arrays["nbv_display_rows"]
            high_count, low_count = len(model.temp_arrays["nbv_high_entries"]), len(model.temp_arrays["nbv_low_entries"])
            seen, hidden_ok = resolve_display_rows()
            row_results.append({"页": category, "行数": len(actual_rows), "通过":
                                actual_rows == expected_row_ids(high_count, low_count) and hidden_ok
                                and all(seen[band] == model.temp_arrays[f"nbv_{band}_entries"] for band in ("high", "low"))})
        check("模型：六页实时/后备数组与名单顺序完全一致", all(r["通过"] for r in page_results), page_results)
        check("模型：六页编码行与七格解析器展开后无缺漏、重复或空格显示", all(r["通过"] for r in row_results), row_results)
        model.run("nbv_select_page_4")
        model.run("nbv_close")
        closed = "nbv_window_open" not in model.flags and model.vars["nbv_page"] == 4
        model.run("nbv_open")
        check("模型：关闭重开恢复页面", closed and model.vars["nbv_page"] == 4)
        model.vars["nbv_page"] = 99
        model.run("nbv_open")
        check("模型：无效记录回退政治页", model.vars["nbv_page"] == 1)
        second_country = ScriptModel(effects, triggers)
        check("模型：不同国家状态不共享", "nbv_window_open" not in second_country.flags and second_country.vars.get("nbv_page", 0) == 0)
        model.flags.discard("nbv_show_zero")
        model.check(trigger_map["nbv_prepare_view"].value)
        pending_ids = {r["id"] for r in display_records if r["category"] == "政治" and not r.get("runtime_read_validated", False)}
        displayed = set(model.temp_arrays["nbv_high_entries"] + model.temp_arrays["nbv_low_entries"])
        check("模型：未验证零值保持可见", pending_ids <= displayed)
        model.flags.add("nbv_debug_filter_unverified")
        filter_examples = [row for row in display_records if row["category"] == "政治"][:2]
        model.modifiers = {row["key"]: value for row, value in zip(filter_examples, (0.001, -0.001))}
        model.check(trigger_map["nbv_prepare_view"].value)
        displayed = set(model.temp_arrays["nbv_high_entries"] + model.temp_arrays["nbv_low_entries"])
        check("模型：开发筛选保留正负微小非零值", len(filter_examples) == 2
              and displayed == {row["id"] for row in filter_examples})
        geometry_ok = True
        maximum = {band: max(sum(r["category"] == category and r["display_priority_band"] == band for r in display_records)
                            for category in PAGES) for band in ("high", "low")}
        count_pairs = {(high, low) for high in range(maximum["high"] + 1)
                       for low in (0, 1, 3, 4, 5, maximum["low"] - 1, maximum["low"])}
        count_pairs.update((high, low) for high in (0, 1, 2, 3, 4, maximum["high"])
                           for low in range(maximum["low"] + 1))
        for high, low in sorted(count_pairs):
            model.temp_arrays["nbv_high_entries"] = list(range(1, high + 1))
            model.temp_arrays["nbv_low_entries"] = list(range(301, 301 + low))
            model.temp.update(nbv_high_count=high, nbv_low_count=low)
            model.check(trigger_map["nbv_prepare_layout"].value)
            geometry_ok &= model.temp_arrays["nbv_display_rows"] == expected_row_ids(high, low)
            seen, hidden_ok = resolve_display_rows()
            geometry_ok &= hidden_ok and all(seen[band] == model.temp_arrays[f"nbv_{band}_entries"] for band in ("high", "low"))
        check("模型：单区、全空、末行不足三四格及所有计数边界", geometry_ok, {"计数组合数": len(count_pairs), "最大数": maximum})

        required = {"sprite": set(), "font": set(), "scrollbar": set(), "sound": set()}
        game_trees = {}
        def game_tree(relative):
            path = args.game_root / relative
            if path not in game_trees:
                game_trees[path] = parse_script(path.read_text(encoding="utf-8-sig"), str(path))
            return game_trees[path]

        local_keys = set()
        for node in walk(gui_ast):
            if node.key in ("quadTextureSprite", "spriteType"):
                required["sprite"].add(node.value)
            elif node.key in ("font", "buttonFont"):
                required["font"].add(node.value)
            elif node.key == "verticalScrollbar":
                required["scrollbar"].add(node.value)
            elif node.key in ("clicksound", "oversound", "show_sound", "hide_sound"):
                required["sound"].add(node.value)
            elif node.key in ("text", "buttonText", "pdx_tooltip") and isinstance(node.value, str) and node.value.startswith("nbv_"):
                local_keys.add(node.value)
        for node in walk(sloc):
            if node.key == "localization_key" and isinstance(node.value, str):
                if node.value.startswith("GFX_"):
                    required["sprite"].add(node.value)
                elif "[?" not in node.value and node.value not in row_templates:
                    local_keys.add(node.value)
        check("GUI 与脚本文本静态本地化引用完备", all(local_keys <= set(values) for values in locs.values()), sorted(local_keys))
        missing_functions = []
        for values in locs.values():
            for value in values.values():
                for function in re.findall(r"\[([A-Za-z_][A-Za-z0-9_]*)\]", value):
                    if function not in dynamic_texts:
                        missing_functions.append(function)
        for node in walk(sgui):
            if node.key in ("image", "entry_container") and isinstance(node.value, str) and node.value.startswith("["):
                function = node.value.strip("[]")
                if function not in dynamic_texts:
                    missing_functions.append(function)
        check("动态本地化函数引用存在", not missing_functions, sorted(set(missing_functions)))
        expected_sprite_types = {"GFX_nbv_tab_normal": {"textSpriteType", "spriteType"},
                                 "GFX_nbv_tab_selected": {"textSpriteType", "spriteType"},
                                 "GFX_nbv_header_background": {"corneredTileSpriteType"}}
        check("私有 sprite 名称唯一且按钮与标题类型适配", set(sprites) == set(expected_sprite_types)
              and all(len(entries) == 1 and entries[0].key in expected_sprite_types.get(name, set())
                      for name, entries in sprites.items()))
        native_core = named_blocks(game_tree("interface/core.gfx"))
        private_header = sprites["GFX_nbv_header_background"][0].value
        native_header = native_core["GFX_tiled_header_1"][0].value
        header_size, header_border = one(private_header, "size").value, one(private_header, "borderSize").value
        check("私有标题精灵仅按窗口尺寸复用原版贴图与效果", scalar(header_size, "x") == "984"
              and scalar(header_size, "y") == "44" and scalar(header_border, "x") == scalar(header_border, "y") == "8"
              and resource_scalar(private_header, "tilingCenter") == resource_scalar(native_header, "tilingCenter") == "yes"
              and resource_scalar(private_header, "effectFile") == resource_scalar(native_header, "effectFile")
              and resource_scalar(private_header, "effectFile") == "gfx/FX/buttonstate_nodowneffect.lua"
              and Path(resource_scalar(private_header, "texturefile")) == Path(resource_scalar(native_header, "texturefile"))
              and Path(resource_scalar(private_header, "texturefile")) == Path("gfx/interface/tiles/tiled_header_1.dds")
              and scalar(private_header, "noOfFrames") == "1",
              {"原版定义": "interface/core.gfx:GFX_tiled_header_1", "模组尺寸": [984, 44], "边框": [8, 8]})
        for name, entries in sprites.items():
            node = entries[0]
            details, ok = {}, True
            for field in ("texturefile", "effectFile"):
                value = scalar(node.value, field)
                candidates = [ROOT / value, args.game_root / value] if value else []
                found = next((p for p in candidates if p.is_file()), None)
                details[field] = str(found) if found else value
                if not found and field == "effectFile" and value and value.endswith(".lua"):
                    shader = (args.game_root / value).with_suffix(".shader")
                    same_vanilla = [name for name, definitions in native_core.items()
                                    if any(scalar(e.value, "effectFile") == value
                                           and Path(resource_scalar(e.value, "texturefile", "")) == Path(resource_scalar(node.value, "texturefile", "")) for e in definitions)]
                    if shader.is_file() and same_vanilla:
                        found = shader
                        details["effectFile_兼容引用"] = {"声明路径字面存在": False, "同名shader文件": str(shader),
                                                        "同贴图及效果的原版定义": same_vanilla}
                        warnings.append(f"{name} 的 {value} 字面路径不存在；与原版同款定义一致，且同名 .shader 存在。仅作为静态兼容证据，不声称字面 .lua 文件存在。")
                ok &= found is not None
                if field == "texturefile" and found:
                    header = found.read_bytes()[:128]
                    valid_dds = len(header) >= 128 and header[:4] == b"DDS " and struct.unpack_from("<I", header, 4)[0] == 124
                    ok &= valid_dds
                    if valid_dds:
                        details["DDS_宽高"] = [struct.unpack_from("<I", header, 16)[0], struct.unpack_from("<I", header, 12)[0]]
            ok &= scalar(node.value, "noOfFrames") == "1"
            check("私有 sprite 文件与 DDS 头：" + name, ok, details)
            resources.append({"类型": "私有 sprite", "名称": name, "定义": "interface/nbv.gfx", **details})

        # Include the scrollbar's own child sprites, rather than only its top-level name.
        scrollbar_definitions = {}
        for relative in ("interface/core.gui", "interface/countryintelligenceagencyview.gui"):
            for name, blocks in named_blocks(game_tree(relative)).items():
                if any(block.key == "extendedScrollbarType" for block in blocks):
                    scrollbar_definitions.setdefault(name, []).extend(blocks)
        for name in required["scrollbar"]:
            blocks = scrollbar_definitions.get(name, [])
            check("滚动条定义类型：" + name, len(blocks) == 1 and blocks[0].key == "extendedScrollbarType")
            for definition in blocks:
                required["sprite"].update(e.value for e in walk(definition.value) if e.key in ("quadTextureSprite", "spriteType"))

        wanted = set.union(*required.values()) - set(sprites)
        found = {}
        candidate_paths = list((args.game_root / "interface").rglob("*.gfx"))
        candidate_paths += list((args.game_root / "interface").rglob("*.gui"))
        candidate_paths += list((args.game_root / "sound").rglob("*.asset"))
        name_pattern = re.compile(r'\bname\s*=\s*(?:"([^"\n]+)"|([^\s{}#]+))')
        for path in sorted(candidate_paths):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if not any(name in text for name in wanted):
                continue
            for match in name_pattern.finditer(text):
                name = match.group(1) or match.group(2)
                if name in wanted and name not in found:
                    found[name] = {"文件": str(path), "行": text.count("\n", 0, match.start()) + 1}
        for kind, names in required.items():
            missing = sorted(names - set(found) - set(sprites))
            check(f"全部 {kind} 资源名可解析到模组或本机原版", not missing, {"数量": len(names), "缺失": missing})
            resources.extend({"类型": kind, "名称": name, **found[name]} for name in sorted(names) if name in found)

        vanilla_texture_errors, vanilla_texture_details = [], []
        for name in sorted(required["sprite"] - set(sprites)):
            if name not in found:
                continue
            path = Path(found[name]["文件"])
            definitions = named_blocks(game_tree(path.relative_to(args.game_root))).get(name, [])
            definitions = [d for d in definitions if d.key in ("spriteType", "textSpriteType", "corneredTileSpriteType")]
            if not definitions:
                vanilla_texture_errors.append(name + ":不是精灵定义")
                continue
            texture = resource_scalar(definitions[0].value, "texturefile")
            texture_path = args.game_root / texture if texture else None
            if not texture_path or not texture_path.is_file():
                vanilla_texture_errors.append(name + ":贴图文件缺失")
            vanilla_texture_details.append({"名称": name, "类型": definitions[0].key, "贴图": str(texture_path)})
        check("原版精灵及滚动条子精灵贴图存在", not vanilla_texture_errors,
              {"错误": vanilla_texture_errors, "贴图": vanilla_texture_details})

        font_errors, font_files = [], []
        for relative in ("interface/core.gfx", "interface/core_chinese.gfx"):
            native_fonts = named_blocks(game_tree(relative))
            for name in sorted(required["font"]):
                definitions = [d for d in native_fonts.get(name, []) if d.key in ("bitmapfont", "bitmapfont_override")]
                if not definitions:
                    font_errors.append(f"{relative}:{name}:定义缺失")
                for definition in definitions:
                    for base in one(definition.value, "fontfiles").value:
                        for suffix in (".fnt", ".dds"):
                            path = args.game_root / (base.value + suffix)
                            font_files.append(str(path))
                            if not path.is_file():
                                font_errors.append(str(path))
        check("默认及简体中文字体文件完整", not font_errors, {"文件数": len(font_files), "缺失": font_errors, "文件": font_files})

        sound_effects = named_blocks(game_tree("sound/gui/gui_sound_effects.asset"))
        sounds = named_blocks(game_tree("sound/sound.asset"))
        sound_errors, sound_files = [], []
        for name in sorted(required["sound"]):
            effect = [d for d in sound_effects.get(name, []) if d.key == "soundeffect"]
            if not effect:
                sound_errors.append(name + ":soundeffect缺失")
                continue
            sources = [e.value for e in walk(effect[0].value) if e.key == "sound" and isinstance(e.value, str)]
            for sound in sources:
                definitions = [d for d in sounds.get(sound, []) if d.key == "sound"]
                if not definitions:
                    sound_errors.append(sound + ":sound缺失")
                for definition in definitions:
                    audio = scalar(definition.value, "file")
                    audio_path = args.game_root / "sound" / audio if audio else None
                    sound_files.append(str(audio_path))
                    if not audio_path or not audio_path.is_file():
                        sound_errors.append(str(audio_path))
        check("六个声效的效果、声音和 WAV 文件链完整", not sound_errors, {"错误": sound_errors, "文件": sound_files})
        check("描述文件声明完整且没有 replace_path", all(scalar(parsed["descriptor.mod"], key) for key in ("name", "version", "supported_version"))
              and not children(parsed["descriptor.mod"], "replace_path"))

    guarded("结构、状态模型和资源审查正常执行", inspect_structure)
    warnings.append("仅完成静态语法、映射、文件存在性与脚本状态模型检查；不等于引擎成功加载、游戏内交互或数据读取验证。")
    warnings.append("临时数组、动态行模板与 GUI 更新生命周期、滚动边界、暂停刷新及 tag 切换仍需游戏内测试。")
    warnings.append("国家 flag/变量按国家共享；这里没有实现客户端独立偏好或跨 tag 强制保持窗口。")
    warnings.append(f"运行读取已验证项：{sum(bool(r.get('runtime_read_validated')) for r in records)}/559。")
    warnings.append("资源名检查证明定义存在；不证明与其他 UI 模组组合后的显示效果及资源覆盖顺序。")
    failures = [item for item in checks if not item["通过"]]
    report = {
        "schema_version": 1,
        "验证类型": "独立静态验证，非引擎验证",
        "生成时间": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "模组目录": str(ROOT), "原版目录": str(args.game_root),
        "通过": not failures, "检查数": len(checks), "失败数": len(failures),
        "指标数": len(records), "展示指标数": len(display_records),
        "分页数量": dict(zip(PAGES, display_counts)), "注册表分类数量": dict(zip(PAGES, counts)),
        "检查": checks, "限制": warnings, "资源证据": resources,
        "输入_SHA256": file_fingerprints,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"静态检查：{len(checks) - len(failures)}/{len(checks)} 通过；报告：{args.report}")
    for failure in failures:
        print("失败：", failure["检查"], str(failure["详情"])[:500])
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
