#!/usr/bin/env python3
"""Rebuild NBV backend files from the user display layout and stable registry.

Run: python tools/build_backend.py
Check without changing files: python tools/build_backend.py --check

Only the three backend files listed in OUTPUTS are written. The UI layout,
localization, metric catalog and game installation are never modified.
"""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["政治", "工业", "陆军", "海军", "空军", "情报"]

GUI_TEMPLATE = r"""# National Buff Viewer. Stable IDs: metric-index.json; GUI order: display-layout.json.
# KR 1521695605: Mitteleuropa entry attachment, separate window and country flags.
# BUFF UI 3795966002: numbered metric lists and direct ROOT.modifier localization.
# TNO 3449417512: calculator_visible -> temp array -> dynamic_lists pattern.
# TNO reference: common/scripted_guis/TNO_Politics.txt:1025,1044;
# interface/TNO_SG_Politics_Misc.gui:73 (calculator icon before the list).
# This UI and its timing still require validation in the target engine version.
# State is per country. No gameplay modifiers are set, summed or cached.
# Default GUI updates: intentionally no dirty binding, AI effects or on_actions.
scripted_gui = {
    nbv_entry = {
        context_type = player_context
        parent_window_name = raid_filter
        window_name = "nbv_entry_window"
        visible = { always = yes }
        effects = {
            nbv_open_button_click = { nbv_toggle = yes }
        }
    }
    nbv_main = {
        context_type = player_context
        window_name = "nbv_window"
        visible = {
            has_country_flag = nbv_window_open
        }
        dynamic_lists = {
            nbv_rows_grid = {
                array = nbv_display_rows
                value = nbv_row_id
                index = nbv_row_index
                change_scope = no
                entry_container = "[NBVRowContainer]"
            }
        }
        properties = {
            nbv_tab_1 = { image = "[nbv_tab_1_sprite]" }
            nbv_tab_2 = { image = "[nbv_tab_2_sprite]" }
            nbv_tab_3 = { image = "[nbv_tab_3_sprite]" }
            nbv_tab_4 = { image = "[nbv_tab_4_sprite]" }
            nbv_tab_5 = { image = "[nbv_tab_5_sprite]" }
            nbv_tab_6 = { image = "[nbv_tab_6_sprite]" }
        }
        triggers = {
            nbv_calculator_visible = { nbv_prepare_view = yes }
@@CELL_VISIBILITY@@
            nbv_empty_state_visible = {
                check_variable = { nbv_high_count = 0 }
                check_variable = { nbv_low_count = 0 }
            }
        }
        effects = {
            nbv_close_button_click = { nbv_close = yes }
            nbv_filter_button_click = { nbv_toggle_zero_filter = yes }
            nbv_refresh_button_click = { nbv_refresh = yes }
            nbv_tab_1_click = { nbv_select_page_1 = yes }
            nbv_tab_2_click = { nbv_select_page_2 = yes }
            nbv_tab_3_click = { nbv_select_page_3 = yes }
            nbv_tab_4_click = { nbv_select_page_4 = yes }
            nbv_tab_5_click = { nbv_select_page_5 = yes }
            nbv_tab_6_click = { nbv_select_page_6 = yes }
        }
    }
}
"""

EFFECTS_TEMPLATE = r"""# National Buff Viewer. Stable IDs: metric-index.json; GUI order: display-layout.json.
# KR 1521695605: Mitteleuropa entry attachment, separate window and country flags.
# BUFF UI 3795966002: numbered metric lists and direct ROOT.modifier localization.
# TNO 3449417512: calculator_visible -> temp array -> dynamic_lists pattern.
# TNO reference: common/scripted_guis/TNO_Politics.txt:1025,1044;
# interface/TNO_SG_Politics_Misc.gui:73 (calculator icon before the list).
# This UI and its timing still require validation in the target engine version.
# State is per country. No gameplay modifiers are set, summed or cached.
# Page memory survives all close paths. It is country state, not a client setting.
# player_context rebinds flags/page/ROOT on tag change; an unopened country closes.
# There is no documented on_tag-change callback in the installed game.

nbv_refresh = {
    if = {
        limit = { nbv_valid_page = no }
        set_variable = { nbv_page = 1 }
        set_country_flag = nbv_show_zero
    }
    nbv_rebuild_cached_lists = yes
}

nbv_open = {
    nbv_refresh = yes
    set_country_flag = nbv_window_open
}

nbv_close = {
    # The selected nbv_page already is the remembered page. Do not reset it.
    clr_country_flag = nbv_window_open
}

nbv_toggle = {
    if = {
        limit = { has_country_flag = nbv_window_open }
        nbv_close = yes
    }
    else = { nbv_open = yes }
}

nbv_toggle_zero_filter = {
    if = {
        limit = { has_country_flag = nbv_show_zero }
        clr_country_flag = nbv_show_zero
    }
    else = { set_country_flag = nbv_show_zero }
    nbv_refresh = yes
}

nbv_select_page_1 = {
    set_variable = { nbv_page = 1 }
    nbv_refresh = yes
}

nbv_select_page_2 = {
    set_variable = { nbv_page = 2 }
    nbv_refresh = yes
}

nbv_select_page_3 = {
    set_variable = { nbv_page = 3 }
    nbv_refresh = yes
}

nbv_select_page_4 = {
    set_variable = { nbv_page = 4 }
    nbv_refresh = yes
}

nbv_select_page_5 = {
    set_variable = { nbv_page = 5 }
    nbv_refresh = yes
}

nbv_select_page_6 = {
    set_variable = { nbv_page = 6 }
    nbv_refresh = yes
}

# Fallback membership only; never cache modifier values. Intended for diagnosing
# temp-array lifetime in the engine. Normal GUI uses the temporary arrays.
nbv_rebuild_cached_lists = {
    clear_array = nbv_high_entries_cache
    clear_array = nbv_low_entries_cache
@@GENERATED_ROWS@@}
"""

TRIGGERS_TEMPLATE = r"""# National Buff Viewer. Stable IDs: metric-index.json; GUI order: display-layout.json.
# KR 1521695605: Mitteleuropa entry attachment, separate window and country flags.
# BUFF UI 3795966002: numbered metric lists and direct ROOT.modifier localization.
# TNO 3449417512: calculator_visible -> temp array -> dynamic_lists pattern.
# TNO reference: common/scripted_guis/TNO_Politics.txt:1025,1044;
# interface/TNO_SG_Politics_Misc.gui:73 (calculator icon before the list).
# This UI and its timing still require validation in the target engine version.
# State is per country. No gameplay modifiers are set, summed or cached.
# Prepare arrays in the first transparent calculator icon, before list controls.
# This follows the installed TNO pattern; no dirty binding or timed polling.
# Pending read validations stay visible at zero. nbv_debug_filter_unverified
# is a developer-only country flag, never enabled by a normal button.

nbv_valid_page = {
    OR = {
        check_variable = { nbv_page = 1 }
        check_variable = { nbv_page = 2 }
        check_variable = { nbv_page = 3 }
        check_variable = { nbv_page = 4 }
        check_variable = { nbv_page = 5 }
        check_variable = { nbv_page = 6 }
    }
}

nbv_prepare_view = {
    clear_temp_array = nbv_high_entries
    clear_temp_array = nbv_low_entries
@@GENERATED_ROWS@@    set_temp_variable = { nbv_high_count = nbv_high_entries^num }
    set_temp_variable = { nbv_low_count = nbv_low_entries^num }
    nbv_prepare_layout = yes
    always = yes
}

# One flat list owns every row and section heading. No dynamic Y properties:
# those were evaluated before calculator temporaries and left two grids overlapping.
nbv_prepare_layout = {
    clear_temp_array = nbv_display_rows
@@DISPLAY_ROWS@@
    always = yes
}

@@CELL_RESOLVERS@@
"""


def build_rows(records, temporary):
    command = "add_to_temp_array" if temporary else "add_to_array"
    suffix = "" if temporary else "_cache"
    lines = []
    for page, category in enumerate(PAGES, 1):
        lines.append(f"    if = {{\n        limit = {{ check_variable = {{ nbv_page = {page} }} }}\n")
        for row in records:
            if row["category"] != category:
                continue
            ident, key, band = row["id"], row["key"], row["display_priority_band"]
            validated = bool(row.get("runtime_read_validated", False))
            # Pending zero readings remain visible. Debug filtering must be explicitly
            # enabled by a developer; ordinary UI controls never set this flag.
            pending = "" if validated else "NOT = { has_country_flag = nbv_debug_filter_unverified } "
            guard = f"OR = {{ has_country_flag = nbv_show_zero {pending}NOT = {{ check_variable = {{ ROOT.modifier@{key} = 0 }} }} }}"
            lines.append(f"        # {ident}: {key}; {row['priority']}; runtime_read_validated={str(validated).lower()}\n")
            lines.append(f"        if = {{\n            limit = {{ {guard} }}\n            {command} = {{ nbv_{band}_entries{suffix} = {ident} }}\n        }}\n")
        lines.append("    }\n")
    return "".join(lines)


def load_records():
    from display_layout import load_display_records
    records = load_display_records()
    assert len({row["id"] for row in records}) == len(records), "Duplicate modifier IDs"
    assert len({row["key"] for row in records}) == len(records), "Duplicate modifier keys"
    assert all(re.fullmatch(r"[a-z0-9_]+", row["key"]) for row in records), "Unsafe or unexpected modifier key"
    assert all(row["category"] in PAGES for row in records), "Unknown category"
    assert all(row["display_priority_band"] in ("high", "low") for row in records), "Unknown priority band"
    return records


def outputs(records):
    display_rows, resolvers, visibility = [], [], []
    for band, columns, marker in (("high", 3, 10000), ("low", 4, 20000)):
        maximum = max(sum(r['category'] == category and r['display_priority_band'] == band for r in records) for category in PAGES)
        display_rows.append(f"    if = {{ limit = {{ check_variable = {{ nbv_{band}_count > 0 }} }} add_to_temp_array = {{ nbv_display_rows = {marker} }} }}")
        for start in range(0, maximum, columns):
            ident = start + 1 if band == 'high' else -(start + 1)
            display_rows.append(f"    if = {{ limit = {{ check_variable = {{ nbv_{band}_count > {start} }} }} add_to_temp_array = {{ nbv_display_rows = {ident} }} }}")
        for slot in range(1, columns + 1):
            condition = 'check_variable = { nbv_row_id > 0 } check_variable = { nbv_row_id < 10000 }' if band == 'high' else 'check_variable = { nbv_row_id < 0 }'
            negate = '\n        multiply_temp_variable = { nbv_lookup_index = -1 }' if band == 'low' else ''
            resolvers.append(f'''nbv_resolve_{band}_{slot} = {{
    set_temp_variable = {{ nbv_entry_id = 0 }}
    if = {{
        limit = {{ {condition} }}
        set_temp_variable = {{ nbv_lookup_index = nbv_row_id }}{negate}
        add_to_temp_variable = {{ nbv_lookup_index = {slot - 2} }}
        if = {{
            limit = {{ check_variable = {{ nbv_lookup_index < nbv_{band}_count }} }}
            set_temp_variable = {{ nbv_entry_id = nbv_{band}_entries^nbv_lookup_index }}
        }}
    }}
    check_variable = {{ nbv_entry_id > 0 }}
}}
''')
            visibility.append(f"            nbv_{band}_cell_{slot}_visible = {{ nbv_resolve_{band}_{slot} = yes }}")
    return {
        "common/scripted_guis/nbv_scripted_gui.txt": GUI_TEMPLATE.replace('@@CELL_VISIBILITY@@', '\n'.join(visibility)),
        "common/scripted_effects/nbv_effects.txt": EFFECTS_TEMPLATE.replace("@@GENERATED_ROWS@@", build_rows(records, False)),
        "common/scripted_triggers/nbv_triggers.txt": TRIGGERS_TEMPLATE.replace("@@GENERATED_ROWS@@", build_rows(records, True)).replace('@@DISPLAY_ROWS@@', '\n'.join(display_rows)).replace('@@CELL_RESOLVERS@@', '\n'.join(resolvers)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify generated files without writing them")
    args = parser.parse_args()
    stale = []
    records = load_records()
    for rel, text in outputs(records).items():
        path = ROOT / rel
        if args.check:
            if not path.exists() or path.read_bytes() != text.encode("utf-8"):
                stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
            print(f"Wrote {rel}: {len(text.splitlines())} lines")
    if stale:
        raise SystemExit("Stale or missing backend output: " + ", ".join(stale))
    if args.check:
        high_count = sum(r['display_priority_band'] == 'high' for r in records)
        print(f"Backend outputs match display-layout.json and generator templates ({len(records)} displayed; {high_count} common / {len(records) - high_count} other).")


if __name__ == "__main__":
    main()
