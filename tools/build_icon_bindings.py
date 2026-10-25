"""Port Modifier Icons CN text icons without overriding vanilla localisation.

The source mod's localisation is evidence for icon choice, not copied UI text.
Every non-exact choice is enumerated below; no keyword/category guessing is used.
Only Workshop-owned DDS files are copied; native DDS references stay native.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path(r"E:\Steam\steamapps\workshop\content\394360\2671396187")
DEFAULT_GAME = Path(r"E:\Steam\steamapps\common\Hearts of Iron IV")
LOC_RE = re.compile(r'^\s*([^\s:#]+):(?:\d+)?\s*"(.*)$')
ICON_RE = re.compile(r"£([A-Za-z0-9_]+)")

# Exact old names are distinguished from visual analogies. A visual analogy
# changes the decorative icon only, never the metric key, text, value or scope.
OVERRIDES = {
    "autonomy_gain_global_factor": ("MODIFIER_AUTONOMY_GAIN", "semantic_analogy", "同属自治度获取；使用自治度图标。"),
    "autonomy_manpower_share_from_subjects": ("MODIFIER_AUTONOMY_MANPOWER_SHARE", "semantic_analogy", "同属附属国人力要求；使用原模组同名图标。"),
    "faction_influence_contribution_factor": ("@ai_join_faction_texticon", "semantic_analogy", "原模组未覆盖阵营影响贡献；复用阵营关系图标。"),
    "faction_influence_war_score_factor": ("@ai_join_faction_texticon", "semantic_analogy", "原模组未覆盖阵营影响战争分数；复用阵营关系图标。"),
    "repair_speed_bunker_factor": ("MODIFIER_INDUSTRY_FREE_REPAIR_FACTOR", "semantic_analogy", "原模组要塞维修图标引用的 repair_bunker_texticon.dds 未提供；使用有效的通用维修图标。"),
    "repair_speed_rail_way_factor": ("modifier_repair_speed_infrastructure_factor", "semantic_analogy", "铁路维修复用基础设施维修图标。"),
    "research_sharing_per_country_bonus_factor": ("EFFECT_ADD_TECH_BONUS_BONUS_ONLY", "semantic_analogy", "科技共享加成复用科研加成图标。"),
    "resources_to_overlord_factor": ("MODIFIER_LOCAL_RESOURCES_FACTOR", "semantic_analogy", "向宗主国提供资源复用资源图标。"),
    "army_non_core_attack_factor": ("MODIFIERS_ARMY_ATTACK_FACTOR", "semantic_analogy", "非核心领土攻击使用通用陆军攻击图标。"),
    "army_non_core_defence_factor": ("MODIFIERS_ARMY_DEFENCE_FACTOR", "semantic_analogy", "非核心领土防御使用通用陆军防御图标。"),
    "army_claim_attack_factor": ("MODIFIERS_ARMY_ATTACK_FACTOR", "semantic_analogy", "宣称领土攻击使用通用陆军攻击图标。"),
    "army_claim_defence_factor": ("MODIFIERS_ARMY_DEFENCE_FACTOR", "semantic_analogy", "宣称领土防御使用通用陆军防御图标。"),
    "army_retreat_speed_factor": ("MODIFIER_NAVAL_RETREAT_SPEED", "semantic_analogy", "陆军撤退复用通用撤退图标。"),
    "modifier_army_sub_unit_marine_attack_factor": ("modifier_army_sub_unit_marines_attack_factor", "legacy_key_alias", "原模组使用 marines 旧拼写，原版当前单位键为 marine。"),
    "modifier_army_sub_unit_marine_defence_factor": ("modifier_army_sub_unit_marines_defence_factor", "legacy_key_alias", "原模组使用 marines 旧拼写，原版当前单位键为 marine。"),
    "modifier_army_sub_unit_marine_max_org_factor": ("modifier_army_sub_unit_marines_max_org_factor", "legacy_key_alias", "原模组使用 marines 旧拼写，原版当前单位键为 marine。"),
    "rangers_special_forces_contribution_factor": ("modifier_unit_rangers_support_design_cost_factor", "semantic_analogy", "游骑兵上限贡献使用游骑兵图标。"),
    "special_forces_doctrine_cost_factor": ("MODIFIER_LAND_DOCTRINE_COST_FACTOR", "semantic_analogy", "特种部队战术消耗复用陆军学说消耗图标。"),
    "air_invasion_division_cap": ("MODIFIER_UNIT_SIZE_FACTOR_FOR_PARADROP", "semantic_analogy", "空降计划容量使用空降兵图标。"),
    "air_invasion_plan_cap": ("MODIFIER_UNIT_SIZE_FACTOR_FOR_PARADROP", "semantic_analogy", "空降计划上限使用空降兵图标。"),
    "naval_general_support_factor": ("@naval_capacity_texticon", "semantic_analogy", "支援舰最大支援效果复用海军舰队图标。"),
    "naval_general_support_value_factor": ("@naval_capacity_texticon", "semantic_analogy", "支援舰支援值复用海军舰队图标。"),
    "naval_invasion_division_cap": ("MODIFIER_NAVAL_INVASION_CAPACITY", "semantic_analogy", "登陆计划容量复用登陆作战上限图标。"),
    "naval_invasion_plan_cap": ("MODIFIER_NAVAL_INVASION_CAPACITY", "semantic_analogy", "登陆计划上限复用登陆作战上限图标。"),
    "naval_repair_support_factor": ("MODIFIER_REPAIR_SPEED_FACTOR", "semantic_analogy", "维修舰最大维修效果使用舰船维修图标。"),
    "naval_repair_support_value_factor": ("MODIFIER_REPAIR_SPEED_FACTOR", "semantic_analogy", "维修舰维修值使用舰船维修图标。"),
    "naval_ship_recovery_chance": ("MODIFIER_ARMY_ORG_REGAIN", "semantic_analogy", "舰船组织度恢复使用组织度恢复图标。"),
    "naval_supply_consumption_factor": ("MODIFIER_SUPPLY_CONSUMPTION_FACTOR", "semantic_analogy", "海军补给消耗使用补给消耗图标。"),
    "air_close_air_support_org_damage_factor": ("MODIFIER_CAS_ATTACK_FACTOR", "semantic_analogy", "近距支援机组织度伤害使用近距支援攻击图标。"),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_localisation(source):
    result = {}
    for path in sorted((source / "localisation/replace/vanilla").glob("*.yml")):
        for line, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            match = LOC_RE.match(raw)
            if not match:
                continue
            key, value = match.groups()
            closing_quote = re.search(r'(?<!\\)"', value)
            literal = value[:closing_quote.start()] if closing_quote else value.rstrip()
            icon = ICON_RE.search(literal)
            if not icon:
                continue
            # One source line lacks its closing quote. Recover just its literal
            # icon token, record the defect, and never copy the malformed YAML.
            result[key] = {
                "key": key, "file": path.relative_to(source).as_posix(),
                "line": line, "text": literal, "icon": icon.group(1),
                "source_line_missing_closing_quote": closing_quote is None,
            }
    return result


def read_sprites(source):
    result = {}
    for path in sorted((source / "interface").glob("*.gfx")):
        text = path.read_text(encoding="utf-8-sig")
        for match in re.finditer(r"spriteType\s*=\s*\{(.*?)\}", text, re.S | re.I):
            body = match.group(1)
            name = re.search(r'name\s*=\s*"([^"]+)"', body, re.I)
            texture = re.search(r'texturefile\s*=\s*"([^"]+)"', body, re.I)
            frames = re.search(r"noOfFrames\s*=\s*(\d+)", body, re.I)
            if name and texture:
                result[name.group(1)] = {
                    "file": path.relative_to(source).as_posix(),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "sprite": name.group(1), "texture": texture.group(1),
                    "frames": int(frames.group(1)) if frames else 1,
                }
    return result


def build(source=DEFAULT_SOURCE, game=DEFAULT_GAME):
    records = json.loads((ROOT / "tools/data/metric-index.json").read_text(encoding="utf-8"))["records"]
    loc = read_localisation(source)
    sprites = {k: {**v, "origin": "vanilla_game"} for k, v in read_sprites(game).items()}
    sprites.update({k: {**v, "origin": "workshop_mod"} for k, v in read_sprites(source).items()})
    bindings = []
    for metric in records:
        key = metric["key"]
        # Name evidence takes precedence over mechanically derived candidates.
        candidates = [x["key"] for x in metric.get("name_origin", {}).get("sources", []) if "key" in x]
        candidates += [key, "MODIFIER_" + key.upper(), key + "_tt"]
        selected = next((x for x in candidates if x in loc), None)
        method = "exact_localisation"
        note = "原模组同一修正名称或同一修正工具提示图标。"
        if selected is None:
            if key not in OVERRIDES:
                raise ValueError("Missing explicit icon mapping: " + key)
            selected, method, note = OVERRIDES[key]
        evidence = []
        if selected.startswith("@"):
            icon = selected[1:]
        else:
            entry = loc[selected]
            icon = entry["icon"]
            evidence.append({"kind": "source_localisation", **{k: v for k, v in entry.items() if k != "icon"}})
        if icon == "speed_infantry_texticon" and "GFX_" + icon not in sprites:
            evidence.append({"kind": "source_defect", "missing_sprite": "GFX_" + icon})
            replacement = loc["MODIFIER_ARMY_SPEED_FACTOR"]
            icon = replacement["icon"]
            evidence.append({"kind": "replacement_localisation", **{k: v for k, v in replacement.items() if k != "icon"}})
            method = "source_sprite_repair"
            note = "原模组步兵速度引用未定义图标；改用其有效的陆军速度图标。"
        sprite = sprites.get("GFX_" + icon)
        if not sprite:
            raise ValueError("Missing sprite for " + key + ": " + icon)
        evidence.append({"kind": "source_sprite", "file": sprite["file"], "line": sprite["line"], "sprite": sprite["sprite"], "origin": sprite["origin"]})
        bindings.append({
            "id": metric["id"], "key": key, "name": metric["name"], "category": metric["category"],
            "icon_token": "nbv_mi_" + icon, "source_icon_token": icon,
            "method": method, "note": note, "evidence": evidence,
        })

    resources = []
    gfx = ["# Generated by tools/build_icon_bindings.py; private aliases only.", "spriteTypes = {"]
    for icon in sorted({x["source_icon_token"] for x in bindings}):
        sprite = sprites["GFX_" + icon]
        native_texture = sprite["texture"]
        source_file = source / native_texture
        if source_file.is_file():
            origin = "workshop_mod"
            destination = "gfx/nbv_modifier_icons/" + Path(native_texture).name
            target = ROOT / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, target)
        else:
            origin = "vanilla_game"
            source_file = game / native_texture
            if not source_file.is_file():
                raise FileNotFoundError(source_file)
            destination = native_texture
        data = source_file.read_bytes()
        if data[:4] != b"DDS ":
            raise ValueError("Not a DDS: " + str(source_file))
        height, width = struct.unpack_from("<II", data, 12)
        frames = sprite["frames"]
        if width % frames or height > 20:
            raise ValueError("Text icon does not fit row: " + str(source_file))
        token = "nbv_mi_" + icon
        resources.append({
            "token": token, "sprite": "GFX_" + token, "texture_file": destination,
            "sha256": sha256(source_file), "width": width, "height": height,
            "frames": frames, "frame_width": width // frames,
            "source": {"origin": origin, "file": str(source_file), "texture_file": native_texture,
                       "sha256": sha256(source_file), "gfx_file": sprite["file"], "gfx_line": sprite["line"], "gfx_origin": sprite["origin"],
                       "sprite": sprite["sprite"], "frames": frames},
        })
        gfx += ["  spriteType = {", f'    name = "GFX_{token}"',
                f'    texturefile = "{destination}"', f"    noOfFrames = {frames}",
                "    legacy_lazy_load = no", "  }"]
    gfx.append("}")
    with (ROOT / "interface/nbv_modifier_icons.gfx").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(gfx) + "\n")
    methods = dict(Counter(x["method"] for x in bindings))
    manifest = {
        "schema_version": 1,
        "source_mod": {"title": "Modifier Icons 汉化版（数据图标）", "descriptor_name": "Modifier Icons CN ver.",
                       "workshop_id": "2671396187", "author": "1+1=⑨", "root": str(source),
                       "url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2671396187",
                       "original_mod_id": "2668048070", "original_author": "truck gaming",
                       "original_url": "https://steamcommunity.com/sharedfiles/filedetails/?id=2668048070"},
        "policy": {"scope": "NBV metric row names and tooltip headings only; no global localisation overrides.",
                   "method": "Literal icon choices from source localisation, then explicit reviewed per-key aliases/analogies.",
                   "asset_copy": "Byte-identical Workshop DDS; native game DDS remain native references.",
                   "fallback": "No generic silent fallback; unknown metric or unresolved sprite is a build error."},
        "statistics": {"total": len(bindings), "mapped": len(bindings), "methods": methods,
                       "unique_icons": len(resources), "copied_textures": len({x["texture_file"] for x in resources if x["source"]["origin"] == "workshop_mod"}),
                       "vanilla_texture_references": sum(x["source"]["origin"] == "vanilla_game" for x in resources),
                       "categories": dict(Counter(x["category"] for x in bindings))},
        "records": bindings, "resources": resources,
    }
    with (ROOT / "tools/data/modifier-icon-bindings.json").open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--game", type=Path, default=DEFAULT_GAME)
    args = parser.parse_args()
    print(json.dumps(build(args.source, args.game)["statistics"], ensure_ascii=False, indent=2))
