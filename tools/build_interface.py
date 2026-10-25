"""Generate the single-list, compact National Buff Viewer interface.

Each dynamic list entry is one entire horizontal row.  Mixing the 3-column
and 4-column cards inside one list gives the engine one unambiguous content
height, instead of positioning a second grid with GUI temporary variables.
"""

from pathlib import Path
import json
from sidebar_placement import placement


ROOT = Path(__file__).resolve().parents[1]


def cell(band: str, index: int, x: int, width: int) -> str:
    # Name and value have separate, non-overlapping single-line text regions.
    # The complete name and value remain available in the card tooltip.
    value_width = 78 if band == "high" else 68
    value_x = width - value_width - 8
    name_width = value_x - 12
    prefix = f"nbv_{band}"
    return f'''        containerWindowType = {{
            name = "{prefix}_cell_{index}"
            position = {{ x = {x} y = 0 }}
            size = {{ width = {width} height = 30 }}
            clipping = yes
            buttonType = {{
                name = "{prefix}_hitbox_{index}"
                position = {{ x = 0 y = 0 }}
                size = {{ x = {width} y = 30 }}
                quadTextureSprite = "GFX_tiled_window_small_small"
                pdx_tooltip = "{prefix}_tooltip_{index}"
            }}
            instantTextboxType = {{
                name = "{prefix}_name_{index}"
                position = {{ x = 8 y = 5 }}
                font = "hoi_16mbs"
                text = "{prefix}_name_{index}_text"
                maxWidth = {name_width}
                maxHeight = 20
                fixedsize = yes
                format = left
                alwaystransparent = yes
            }}
            instantTextboxType = {{
                name = "{prefix}_value_{index}"
                position = {{ x = {value_x} y = 5 }}
                font = "hoi_16mbs"
                text = "{prefix}_value_{index}_text"
                maxWidth = {value_width}
                maxHeight = 20
                fixedsize = yes
                format = right
                alwaystransparent = yes
            }}
        }}
'''


def build() -> str:
    result = '''# National Buff Viewer. Base-game window artwork and fonts.
# Names use private text icons ported from Modifier Icons CN; see nbv_modifier_icons.gfx.
# A single vertical list owns every heading and row, so content bounds and
# scroll range come from one grid. Row height 34; card height 30.
# Scroll-container pattern: BUFF UI 3795966002/interface/BDUI_gui_tools.gui.
# right_vertical_slider_intel is an existing base-game extendedScrollbarType.
# A scroll container needs its own input-capable background and clipping.
# Root-level transparent header art follows KR Mitteleuropa / vanilla achievements.
guiTypes = {
    containerWindowType = {
        name = "nbv_entry_window"
        position = { x = @@ENTRY_X@@ y = @@ENTRY_Y@@ }
        size = { width = 77 height = 77 }
        clipping = no
        buttonType = {
            name = "nbv_open_button"
            position = { x = 3 y = 3 }
            size = { x = 71 y = 71 }
            quadTextureSprite = "GFX_tiled_window_small_selectable"
            pdx_tooltip = "nbv_entry_tooltip"
            clicksound = click_ok
            oversound = ui_menu_over
        }
        iconType = {
            name = "nbv_entry_icon"
            # Native ledger frame is 55x41; centre it inside the 71x71 button.
            position = { x = 11 y = 18 }
            spriteType = "GFX_ledger_button"
            frame = 1
            alwaystransparent = yes
        }
    }

    containerWindowType = {
        name = "nbv_window"
        position = { x = -500 y = -325 }
        size = { width = 1000 height = 650 }
        orientation = center
        moveable = yes
        click_to_front = yes
        clipping = yes
        show_sound = menu_open_window
        hide_sound = menu_close_window
        iconType = {
            name = "nbv_calculator"
            position = { x = 0 y = 0 }
            spriteType = "GFX_tiled_window_transparent_transparent"
            alwaystransparent = yes
        }
        background = {
            name = "nbv_window_background"
            quadTextureSprite = "GFX_tiled_window"
        }
        iconType = {
            name = "nbv_header_background"
            position = { x = 8 y = 6 }
            spriteType = "GFX_nbv_header_background"
            alwaystransparent = yes
        }
        instantTextboxType = {
            name = "nbv_title"
            position = { x = 24 y = 14 }
            font = "hoi_24header"
            text = "nbv_window_title"
            maxWidth = 890
            maxHeight = 30
            format = left
            alwaystransparent = yes
        }
        buttonType = {
            name = "nbv_close_button"
            position = { x = -51 y = 13 }
            orientation = upper_right
            quadTextureSprite = "GFX_closebutton"
            shortcut = "ESCAPE"
            clicksound = click_close
            pdx_tooltip = "CLOSE"
        }
'''
    for page in range(1, 7):
        result += f'''        buttonType = {{
            name = "nbv_tab_{page}"
            position = {{ x = {24 + (page - 1) * 158} y = 60 }}
            quadTextureSprite = "GFX_nbv_tab_normal"
            buttonText = "nbv_page_{page}"
            buttonFont = "hoi_18mbs"
            clicksound = click_default
        }}
'''
    result += '''        buttonType = {
            name = "nbv_filter_button"
            position = { x = 706 y = 104 }
            quadTextureSprite = "GFX_button_123x34"
            buttonText = "nbv_filter_button_text"
            buttonFont = "hoi_16mbs"
            clicksound = click_default
        }
        buttonType = {
            name = "nbv_refresh_button"
            position = { x = 839 y = 104 }
            quadTextureSprite = "GFX_button_123x34"
            buttonText = "nbv_refresh"
            buttonFont = "hoi_16mbs"
            clicksound = click_default
        }
        containerWindowType = {
            name = "nbv_scroll_area"
            position = { x = 24 y = 148 }
            size = { width = 970 height = 486 }
            clipping = yes
            verticalScrollbar = "right_vertical_slider_intel"
            autohide_scrollbars = no
            scroll_wheel_factor = 34
            smooth_scrolling = yes
            background = {
                name = "nbv_scroll_background"
                quadTextureSprite = "GFX_tiled_window_transparent"
            }
            gridBoxType = {
                name = "nbv_rows_grid"
                position = { x = 0 y = 0 }
                size = { width = 944 height = 34 }
                slotsize = { width = 944 height = 34 }
                max_slots_horizontal = 1
                format = "UPPER_LEFT"
            }
            instantTextboxType = {
                name = "nbv_empty_state"
                position = { x = 24 y = 50 }
                font = "hoi_18mbs"
                text = "nbv_empty_state"
                maxWidth = 890
                maxHeight = 24
                format = center
                alwaystransparent = yes
            }
        }
    }
'''
    for band in ("high", "low"):
        result += f'''
    containerWindowType = {{
        name = "nbv_{band}_heading_row"
        position = {{ x = 0 y = 0 }}
        size = {{ width = 944 height = 34 }}
        instantTextboxType = {{
            name = "nbv_{band}_heading"
            position = {{ x = 6 y = 5 }}
            font = "hoi_18mbs"
            text = "nbv_{band}_title"
            maxWidth = 930
            maxHeight = 24
            format = left
            alwaystransparent = yes
        }}
    }}
'''
    for band, count, pitch, width in (("high", 3, 314, 306), ("low", 4, 235, 227)):
        result += f'''
    containerWindowType = {{
        name = "nbv_{band}_row"
        position = {{ x = 0 y = 0 }}
        size = {{ width = 944 height = 34 }}
'''
        for index in range(1, count + 1):
            result += cell(band, index, (index - 1) * pitch, width)
        result += "    }\n"
    result += "}\n"
    entry = placement()['position']
    return result.replace('@@ENTRY_X@@', str(entry['x'])).replace('@@ENTRY_Y@@', str(entry['y']))


if __name__ == "__main__":
    target = ROOT / "interface" / "nbv.gui"
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(build())
    (ROOT / 'tools/data/sidebar-placement.json').write_text(
        json.dumps(placement(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Wrote {target}")
