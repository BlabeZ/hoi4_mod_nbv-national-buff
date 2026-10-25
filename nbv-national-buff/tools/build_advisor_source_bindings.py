#!/usr/bin/env python3
"""Map verified active vanilla advisor-role traits to national modifiers.

The map is deliberately incomplete.  An idea token proves the precise role is
hired, and the character's current trait must still exist.  Never infer hiring
from a character being recruited or merely having an advisor role.  Only direct
national scalar values (including unambiguous file-local numeric constants) are
exposed.  Unknown, zero, local/unit, targeted and conditional values are omitted.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from validate_mod import ParseError, parse_script
from build_source_bindings import localizations, number

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GAME = Path(r"E:\Steam\steamapps\common\Hearts of Iron IV")
TOKEN = re.compile(r"[A-Za-z0-9_.-]+\Z")
SLOTS = {"political_advisor", "army_chief", "navy_chief", "air_chief", "high_command", "theorist"}
HIRE_TRIGGERS = {slot: "is_" + slot for slot in SLOTS - {"theorist"}}
ROLE_METADATA = {"slot", "idea_token", "traits", "allowed", "available", "visible", "cost",
                 "removal_cost", "ledger", "ai_will_do", "on_add", "on_remove", "can_be_fired",
                 "name", "research_bonus", "always_show_on_actions_tooltip"}
TRAIT_METADATA = {"random", "sprite", "name", "ai_will_do", "custom_modifier_tooltip",
                  "command_cap_increase", "command_power"}
IGNORED_TRAIT_BLOCKS = {"equipment_bonus", "targeted_modifier", "hidden_modifier"}
SAFE_SCOPE_WRAPPERS = {"if", "else_if", "else", "hidden_effect", "effect", "immediate", "option",
                       "complete_reward", "completion_reward", "on_add", "on_remove"}
# Reviewed vanilla effects that can give an advisor's trait to another role of
# the SAME character. has_trait does not select an advisor slot, so retaining the
# trait in that leader role could otherwise mask its removal from the advisor.
# Every evidence entry is revalidated against the AST and content fingerprint.
VERIFIED_NON_ADVISOR_TRAITS = (
    ("POL_walery_slawek", "left_sanationist_minister", "common/scripted_effects/POL_scripted_effects.txt", 202, "add_country_leader_role"),
    ("AUS_ernst_rudiger_starhemberg", "AUS_prince_of_starhemberg", "common/national_focus/austria.txt", 5220, "add_country_leader_trait"),
    ("GER_walter_ulbricht", "GER_inflexible_communist_organizer", "common/national_focus/germany.txt", 22642, "add_country_leader_role"),
    ("POL_edward_rydzsmigly", "sanation_militarist", "common/national_focus/poland.txt", 2735, "add_country_leader_role"),
    ("SWE_king_gustaf_v", "SWE_ardent_conservative", "common/national_focus/sweden.txt", 8241, "add_country_leader_role"),
    ("SWE_birger_furugard", "national_socialist_veterinarian", "events/AAT_Sweden.txt", 7016, "add_country_leader_role"),
    ("SWE_karl_kilbom", "anti_soviet_socialist", "events/AAT_Sweden.txt", 8234, "add_country_leader_role"),
    ("IRQ_abd_al_ilah", "IRQ_hashemite_regent", "events/GOE_Iraq.txt", 1806, "add_country_leader_role"),
    ("RAJ_GOE_muhammad_ali_jinnah", "all_india_muslim_league_leader", "events/GOE_Raj.txt", 4030, "add_country_leader_role"),
    ("JAP_yamakawa_kikue", "ARG_feminist_revolutionary", "events/SEA_Japan.txt", 11610, "add_country_leader_role"),
    ("BRA_anisio_teixeira", "BRA_education_pioneer", "events/TOA_Brazil.txt", 3421, "add_country_leader_role"),
    ("BRA_armando_de_sales_oliveira", "BRA_democratic_engineer", "events/TOA_Brazil.txt", 3451, "add_country_leader_role"),
    ("BRA_minervino_de_oliveira", "ICE_trade_unionist", "events/TOA_Brazil.txt", 3486, "add_country_leader_role"),
    ("BRA_lindolfo_collor", "BRA_anti_authoritarian", "events/TOA_Brazil.txt", 3514, "add_country_leader_role"),
    ("MAN_pujie", "JAP_militarist", "events/TSR_Manchukuo.txt", 72, "add_country_leader_role"),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def values(entries, key):
    return [entry.value for entry in entries if entry.key == key]


def scalar(entries, key, default=None):
    found = values(entries, key)
    return found[0] if len(found) == 1 and isinstance(found[0], str) else default


def bare_traits(entries):
    return {item.value for field in entries if field.key == "traits" and isinstance(field.value, list)
            for item in field.value if item.key is None and isinstance(item.value, str)}


def build(game, index_path):
    index = json.loads(index_path.read_text(encoding="utf-8"))
    selected = {row["key"] for row in index["records"]}
    registry_path = ROOT.parent / "hoi4-modding-guide/vanilla-modifier-catalog/data/catalog.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    modifier_keys = {row["key"].lower() for row in registry["records"]}
    canonical = {key.lower(): key for key in selected}
    names = localizations(game)
    files, failures, excluded = {}, [], []
    uncertain_ids = set()

    def read(path):
        rel = path.relative_to(game).as_posix()
        text = path.read_text(encoding="utf-8-sig")
        files[rel] = {"sha256": digest(path)}
        try:
            return rel, parse_script(text, rel)
        except ParseError as exc:
            failures.append({"file": rel, "reason": str(exc)})
            uncertain_ids.update(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=\s*\{", text))
            return rel, []

    def reject(source_id, file, line, reason, **extra):
        excluded.append({"source_id": source_id, "source_file": file,
                         "source_line": line, "reason": reason, **extra})

    def localized(key):
        if not isinstance(key, str) or not TOKEN.fullmatch(key):
            return None
        zh = {row["text"] for row in names["simp_chinese"].get(key, []) if row["text"].strip()}
        en = {row["text"] for row in names["english"].get(key, []) if row["text"].strip()}
        if len(zh) != 1:
            return None
        return next(iter(zh)), next(iter(en)) if len(en) == 1 else next(iter(zh))

    def expand_name(text, language, trail=()):
        """Resolve native label aliases and keep each source on one text row."""
        def replace(match):
            key = match.group(1)
            if key in trail:
                raise ValueError("cyclic localisation label")
            candidates = {row["text"] for row in names[language].get(key, []) if row["text"].strip()}
            if len(candidates) != 1:
                raise ValueError("missing or ambiguous localisation alias")
            return expand_name(next(iter(candidates)), language, trail + (key,))
        text = re.sub(r"\$([A-Za-z0-9_.-]+)\$", replace, text)
        # A label containing a dynamic formatter cannot be safely resolved by
        # a static map (the relevant character/event scope may differ).
        if "$" in text or "[" in text or "]" in text:
            raise ValueError("dynamic localisation label")
        return re.sub(r"\s+", " ", re.sub(r"(?:\\n|[\r\n])+", " ", text)).strip()

    characters = defaultdict(list)
    roles = []
    other_traits = defaultdict(set)
    for path in sorted((game / "common/characters").glob("*.txt")):
        rel, tree = read(path)
        for outer in tree:
            if outer.key != "characters" or not isinstance(outer.value, list):
                continue
            for char in outer.value:
                if not isinstance(char.value, list):
                    continue
                characters[char.key].append((char, rel))
                for role in char.value:
                    if not isinstance(role.value, list):
                        continue
                    if role.key == "advisor":
                        roles.append({"character": char.key, "entry": role, "file": rel,
                                      "traits": bare_traits(role.value), "origin": "character_definition"})
                    else:
                        other_traits[char.key].update(bare_traits(role.value))

    verified_cross_role = {}
    evidence_trees = {}
    for char_id, trait_id, file, line, effect in VERIFIED_NON_ADVISOR_TRAITS:
        if file not in evidence_trees:
            _, evidence_trees[file] = read(game / file)
        matches = []

        def verify_effect(entries, char_scope=None):
            for node in entries:
                if node.line == line and node.key == effect:
                    target = scalar(node.value, "character", char_scope) if isinstance(node.value, list) else char_scope
                    effect_traits = set()
                    if effect == "add_country_leader_trait":
                        effect_traits.add(node.value if isinstance(node.value, str) else scalar(node.value, "trait"))
                    elif isinstance(node.value, list):
                        for child in node.value:
                            if child.key == "country_leader" and isinstance(child.value, list):
                                effect_traits.update(bare_traits(child.value))
                    if target == char_id and trait_id in effect_traits:
                        matches.append(node)
                if isinstance(node.value, list):
                    next_char = (node.key if node.key in characters else char_scope
                                 if (node.key or "").lower() in SAFE_SCOPE_WRAPPERS else None)
                    verify_effect(node.value, next_char)
        verify_effect(evidence_trees[file])
        if len(matches) != 1:
            raise ValueError(f"Reviewed cross-role evidence changed; re-audit {char_id}/{trait_id}: {file}:{line}")
        evidence = {"character_id": char_id, "trait_id": trait_id, "role": "country_leader",
                    "effect": effect, "file": file, "line": line, "sha256": files[file]["sha256"]}
        verified_cross_role[(char_id, trait_id)] = evidence
        other_traits[char_id].add(trait_id)

    # Explicit add_advisor_role and add_trait effects describe additional possible
    # role/trait combinations; runtime checks determine whether they are present.
    # Dynamic character targets and uncertain implicit scopes are not guessed.
    trait_additions = []
    for folder in ("common/scripted_effects", "common/national_focus", "common/decisions",
                   "common/on_actions", "events", "history/countries"):
        for path in sorted((game / folder).rglob("*.txt")):
            text = path.read_text(encoding="utf-8-sig")
            if "add_advisor_role" not in text and "add_trait" not in text:
                continue
            rel, tree = read(path)

            def visit(entries, char_scope=None):
                for node in entries:
                    if not isinstance(node.value, list):
                        continue
                    if node.key in {"add_advisor_role", "add_trait"}:
                        char = scalar(node.value, "character", char_scope)
                        if char not in characters:
                            reject(char or "<dynamic_character>", rel, node.line,
                                   "dynamic_or_unresolved_effect_character", effect=node.key)
                            continue
                        if node.key == "add_advisor_role":
                            for role in node.value:
                                if role.key == "advisor" and isinstance(role.value, list):
                                    roles.append({"character": char, "entry": role, "file": rel,
                                                  "traits": bare_traits(role.value), "origin": "add_advisor_role"})
                        else:
                            slot, trait = scalar(node.value, "slot"), scalar(node.value, "trait")
                            if slot in SLOTS and trait and TOKEN.fullmatch(trait):
                                trait_additions.append((char, slot, trait, rel, node.line))
                        continue
                    next_char = node.key if node.key in characters else char_scope if node.key in SAFE_SCOPE_WRAPPERS else None
                    visit(node.value, next_char)
            visit(tree)

    # Read the country trait database, not unit_leader. File-local constants are
    # resolved only when a single direct numeric definition exists in that file.
    traits = defaultdict(list)
    for path in sorted((game / "common/country_leader").glob("*.txt")):
        rel, tree = read(path)
        constants = defaultdict(list)
        for entry in tree:
            if entry.key and entry.key.startswith("@"):
                constants[entry.key].append(entry)
        constants = {key: entries[0] for key, entries in constants.items()
                     if len(entries) == 1 and number(entries[0].value) is not None}
        for outer in tree:
            if outer.key == "leader_traits" and isinstance(outer.value, list):
                for trait in outer.value:
                    if isinstance(trait.value, list):
                        traits[trait.key].append((trait, rel, constants))

    # Merge repeated descriptions of exactly the same role, but reject token or
    # condition ambiguity. A token shared by different characters is unsafe.
    role_groups = defaultdict(list)
    token_owners = defaultdict(set)
    for role in roles:
        entry = role["entry"]
        slot = scalar(entry.value, "slot")
        token = scalar(entry.value, "idea_token")
        if slot not in SLOTS or not token or not TOKEN.fullmatch(token):
            reject(role["character"], role["file"], entry.line, "unsupported_role_or_token")
            continue
        role.update(slot=slot, token=token)
        role_groups[(role["character"], slot, token)].append(role)
        token_owners[token].add((role["character"], slot))
    by_char_slot = defaultdict(set)
    for (char, slot, token), group in role_groups.items():
        for role in group:
            by_char_slot[(char, slot)].update(role["traits"])
    for char, slot, trait, _, _ in trait_additions:
        by_char_slot[(char, slot)].add(trait)
    # Vanilla military advisor promotion replaces numbered traits; the current
    # trait determines the exact value. There is no guessed skill multiplier.
    for key, available in by_char_slot.items():
        for trait in list(available):
            if key[1] in {"army_chief", "navy_chief", "air_chief", "high_command"} and re.search(r"_[123]$", trait):
                available.update(candidate for rank in (1, 2, 3)
                                 if (candidate := trait[:-1] + str(rank)) in traits)

    by_modifier = {key: [] for key in sorted(selected)}
    accepted_roles, accepted_characters, accepted_traits = set(), set(), set()
    for (char_id, slot, token), group in sorted(role_groups.items()):
        role = group[0]
        role_id = f"{char_id}:{slot}:{token}"
        if len(characters[char_id]) != 1 or char_id in uncertain_ids or len(token_owners[token]) != 1:
            reject(role_id, role["file"], role["entry"].line, "ambiguous_character_or_idea_token")
            continue
        # do_effect can leave a hired advisor inactive; omit until an adapter
        # can preserve its exact evaluation scope rather than assuming activity.
        bad_fields = sorted({field.key for candidate in group for field in candidate["entry"].value
                             if field.key not in ROLE_METADATA})
        if bad_fields:
            reject(role_id, role["file"], role["entry"].line, "conditional_or_unknown_role_fields", fields=bad_fields)
            continue
        # A token changed by scripts within a slot cannot be safely associated
        # with a trait solely from has_trait; require one token per character slot.
        if len({tok for cid, sl, tok in role_groups if cid == char_id and sl == slot}) != 1:
            reject(role_id, role["file"], role["entry"].line, "multiple_tokens_for_character_slot")
            continue
        char, char_file = characters[char_id][0]
        char_name = scalar(char.value, "name", char_id)
        char_loc = localized(char_name)
        literal_char_name = False
        # Older vanilla character files legitimately store a quoted human name
        # directly instead of a localisation key. Preserve that actual name;
        # do not expose an unresolved token as if it were a display label.
        if (not char_loc and isinstance(char_name, str) and char_name.strip()
                and not TOKEN.fullmatch(char_name) and not any(c in char_name for c in "$[]{}\\\r\n")):
            char_loc = (char_name, char_name)
            literal_char_name = True
        if not char_loc:
            reject(role_id, char_file, char.line, "missing_or_ambiguous_character_name")
            continue
        try:
            char_display = tuple(expand_name(text, language) for text, language in
                                 zip(char_loc, ("simp_chinese", "english")))
        except ValueError as exc:
            reject(role_id, char_file, char.line, "unresolved_character_name_alias", detail=str(exc))
            continue
        other = set(other_traits[char_id])
        for (cid, other_slot), candidates in by_char_slot.items():
            if cid == char_id and other_slot != slot:
                other.update(candidates)
        for trait_id in sorted(by_char_slot[(char_id, slot)]):
            source_id = f"{role_id}:{trait_id}"
            if trait_id in other:
                evidence = verified_cross_role.get((char_id, trait_id))
                reject(source_id, role["file"], role["entry"].line, "trait_ambiguous_between_character_roles",
                       **({"non_advisor_trait_evidence": evidence} if evidence else {}))
                continue
            if len(traits.get(trait_id, [])) != 1 or trait_id in uncertain_ids:
                reject(source_id, role["file"], role["entry"].line, "missing_or_duplicate_trait")
                continue
            trait, trait_file, constants = traits[trait_id][0]
            trait_name = scalar(trait.value, "name", trait_id)
            trait_loc = localized(trait_name)
            if not trait_loc:
                reject(source_id, trait_file, trait.line, "missing_or_ambiguous_trait_name")
                continue
            try:
                trait_display = tuple(expand_name(text, language) for text, language in
                                      zip(trait_loc, ("simp_chinese", "english")))
            except ValueError as exc:
                reject(source_id, trait_file, trait.line, "unresolved_trait_name_alias", detail=str(exc))
                continue
            uncertain = []
            for field in trait.value:
                lower = (field.key or "").lower()
                if lower in TRAIT_METADATA or lower in IGNORED_TRAIT_BLOCKS:
                    continue
                if lower not in modifier_keys:
                    uncertain.append(lower)
            if uncertain:
                reject(source_id, trait_file, trait.line, "unknown_trait_fields", fields=sorted(set(uncertain)))
                continue
            duplicate_fields = Counter((field.key or "").lower() for field in trait.value)
            hire = HIRE_TRIGGERS.get(slot, "is_hired_as_advisor")
            role_check = (f"{char_id} = {{ has_advisor_role = {slot} "
                          f"{hire} = yes has_trait = {trait_id} }}")
            # Advisor tokens may be created only when a scripted role is added.
            # An eager has_idea on such a nonexistent token logs engine errors.
            # Documented conditional triggers guard evaluation independently of
            # AND short-circuit behavior. Explicit conditions outside each inner
            # if keep the overall predicate false when that if is skipped.
            activation = (f"AND = {{ has_character = {char_id} "
                          f"if = {{ limit = {{ has_character = {char_id} }} "
                          f"{role_check} if = {{ limit = {{ {role_check} }} "
                          f"has_idea = {token} }} }} }}")
            found = False
            for field in trait.value:
                key = canonical.get((field.key or "").lower())
                if key is None:
                    continue
                value_raw = field.value
                constant = constants.get(value_raw) if isinstance(value_raw, str) else None
                literal = constant.value if constant else value_raw
                value = number(literal)
                if duplicate_fields[(field.key or "").lower()] != 1 or value is None:
                    reject(source_id, trait_file, field.line, "duplicate_or_nonliteral_modifier", modifier=key)
                    continue
                if value == 0:
                    continue
                found = True
                row = {
                    "id": f"advisor:{source_id}:{key}", "source_id": source_id,
                    "source_type": "advisor_trait", "source_category": slot,
                    "character_id": char_id, "idea_token": token, "trait_id": trait_id,
                    "name_loc_key": trait_name if literal_char_name else char_name,
                    "character_name_loc_key": None if literal_char_name else char_name,
                    "character_literal_name": char_name if literal_char_name else None,
                    "trait_name_loc_key": trait_name,
                    "name_zh": char_loc[0], "name_en": char_loc[1],
                    "display_name_zh": trait_display[0],
                    "display_name_en": trait_display[1],
                    "value": int(value) if value == value.to_integral_value() else float(value),
                    "value_literal": literal,
                    "activation": {"has_idea": token, "character": char_id, "hired_slot": slot,
                                   "has_trait": trait_id},
                    "activation_script": activation,
                    "source": {"file": trait_file, "line": field.line, "trait_line": trait.line,
                               "sha256": files[trait_file]["sha256"],
                               "role_file": role["file"], "role_line": role["entry"].line,
                               "role_sha256": files[role["file"]]["sha256"],
                               "character_file": char_file, "character_line": char.line},
                    "runtime_validated": False,
                }
                if constant:
                    row["source"]["constant"] = {"name": value_raw, "line": constant.line,
                                                   "resolved_literal": literal}
                by_modifier[key].append(row)
            if found:
                accepted_roles.add(role_id)
                accepted_characters.add(char_id)
                accepted_traits.add(trait_id)
            else:
                reject(source_id, trait_file, trait.line, "no_selected_nonzero_direct_modifier")
    for rows in by_modifier.values():
        rows.sort(key=lambda row: row["source_id"].casefold())
    return {
        "schema_version": 1, "game_root": str(game),
        "scope": "vanilla_hired_advisor_role_current_direct_national_traits_only",
        "input_index": {"path": str(index_path), "sha256": digest(index_path)},
        "input_registry": {"path": str(registry_path), "sha256": digest(registry_path)},
        "assumptions": [
            "The loaded vanilla character, role and trait definitions must match the scanned files.",
            "Conditional triggers first prove character, role and current trait; only then is the role idea token queried.",
            "has_idea proves the role token is active; hired-slot and current has_trait checks must also pass.",
            "A character's traits shared between distinct roles are excluded to prevent cross-role attribution.",
            "Fifteen reviewed dynamic leader-role overlaps are also excluded, with AST-checked evidence; unknown dynamic scopes are not claimed to be exhaustively covered.",
            "Declared roles, explicit scripted role/trait additions, and existing numbered promotion variants are candidates only.",
            "do_effect and unknown role fields are excluded; equipment, targeted and hidden trait blocks are not attributed.",
            "Military advisor levels use their current numbered trait; no experience or skill scaling is invented.",
            "This incomplete source list never replaces the engine's ROOT.modifier total and never emits residuals.",
        ],
        "display_policy": {"zero_sources": False, "unresolved_residual": False, "other_sources_row": False},
        "statistics": {"selected_modifier_count": len(selected),
                       "covered_modifier_count": sum(bool(rows) for rows in by_modifier.values()),
                       "binding_count": sum(len(rows) for rows in by_modifier.values()),
                       "source_character_count": len(accepted_characters),
                       "source_role_count": len(accepted_roles), "source_trait_count": len(accepted_traits),
                       "verified_dynamic_cross_role_exclusion_count": len(verified_cross_role),
                       "parsed_role_definition_count": len(roles), "scripted_trait_addition_count": len(trait_additions),
                       "scanned_file_count": len(files), "parse_failure_count": len(failures),
                       "excluded_by_reason": dict(sorted(Counter(row["reason"] for row in excluded).items()))},
        "engine_probes": [{"character_id": "GER_franz_halder", "idea_token": "franz_halder",
                           "slot": "army_chief", "trait_id": "army_chief_offensive_2",
                           "modifier": "army_attack_factor", "value": 0.1,
                           "activate_effect": "activate_advisor = franz_halder",
                           "deactivate_effect": "deactivate_advisor = franz_halder",
                           "remove_trait_effect": "remove_trait = { character = GER_franz_halder slot = army_chief trait = army_chief_offensive_2 }",
                           "restore_trait_effect": "add_trait = { character = GER_franz_halder slot = army_chief trait = army_chief_offensive_2 }"},
                          {"character_id": "GER_martin_bormann", "idea_token": "martin_bormann",
                           "slot": "political_advisor", "trait_id": "GER_secretary_to_the_fuhrer",
                           "modifier": "political_power_factor", "value": 0.1},
                          {"character_id": "GER_ferdinand_schorner", "idea_token": "ferdinand_schorner",
                           "slot": "high_command", "trait_id": "army_infantry_2",
                           "modifier": "army_infantry_attack_factor", "value": 0.1},
                          {"character_id": "GER_walther_wever", "idea_token": "walther_wever",
                           "slot": "theorist", "trait_id": "air_warfare_theorist",
                           "modifier": "air_doctrine_cost_factor", "value": -0.1}],
        "source_files": files, "by_modifier": by_modifier,
        "verified_dynamic_cross_role_exclusions": list(verified_cross_role.values()),
        "uncovered_modifier_keys": [key for key, rows in by_modifier.items() if not rows],
        "parse_failures": failures, "excluded": excluded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME)
    parser.add_argument("--index", type=Path, default=ROOT / "tools/data/metric-index.json")
    parser.add_argument("--output", type=Path, default=ROOT / "tools/data/advisor-source-bindings.json")
    args = parser.parse_args()
    result = build(args.game_root, args.index)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["statistics"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
