#!/usr/bin/env python3
"""
Theme override definitions for Rose Pine Blur variants.

Each variant has specific color and transparency overrides to create
the blur effect while maintaining Rose Pine's color scheme.

Official Rose Pine variants (3):
  - Dawn       (light)
  - Rose Pine  (default dark)
  - Moon       (darker dark)

Custom variant:
  - Dusk       (very dark, uses Rose Pine accent colors on near-black backgrounds)
"""

# ---------------------------------------------------------------------------
# Rose Pine palette (official)
# Used as reference for the overrides below. The actual syntax/UI colors
# come from the upstream Rose Pine theme JSON files fetched by sync_theme.py.
# ---------------------------------------------------------------------------
#
# Rose Pine (default dark):
#   base         #191724    surface      #1f1d2e    overlay      #26233a
#   muted        #6e6a86    subtle       #908caa    text         #e0def4
#   love         #eb6f92    gold         #f6c177    rose         #ebbcba
#   pine         #31748f    foam         #9ccfd8    iris         #c4a7e7
#   highlight_low  #21202e  highlight_med #403d52   highlight_high #524f67
#
# Rose Pine Moon:
#   base         #232136    surface      #2a273f    overlay      #393552
#   muted        #6e6a86    subtle       #908caa    text         #e0def4
#   love         #eb6f92    gold         #f6c177    rose         #ea9a97
#   pine         #3e8fb0    foam         #9ccfd8    iris         #c4a7e7
#   highlight_low  #2a283e  highlight_med #44415a   highlight_high #56526e
#
# Rose Pine Dawn:
#   base         #faf4ed    surface      #fffaf3    overlay      #f2e9e0
#   muted        #9893a5    subtle       #797593    text         #575279
#   love         #b4637a    gold         #ea9d34    rose         #d7827e
#   pine         #286983    foam         #56949f    iris         #907aa9
#   highlight_low  #f4ede8  highlight_med #dfdad9   highlight_high #cdc6ce
#
# Dusk (custom): deep purple-black backgrounds with the default
# Rose Pine accent colors.
#   base         #0d0c14    surface      #14131e    overlay      #1a1925
#   elevated     #08070d    panel        #0a0912
#   accents: love #eb6f92, gold #f6c177, rose #ebbcba, pine #31748f,
#            foam #9ccfd8, iris #c4a7e7
# ---------------------------------------------------------------------------

# Blur intensity levels - higher values = less transparency/more opaque
BLUR_LEVELS = {
    "light": {
        "main": "99",
        "surface": "8c",
        "elements": "80",
        "active": "90",
    },  # ~60% opacity
    "medium": {
        "main": "d7",
        "surface": "d0",
        "elements": "a0",
        "active": "b0",
    },  # ~85% opacity
    "heavy": {
        "main": "e0",
        "surface": "db",
        "elements": "c0",
        "active": "d0",
    },  # ~88% opacity
}


def generate_theme_overrides_for_level(base_overrides, level_config):
    """Generate theme overrides for a specific blur level."""
    overrides = base_overrides.copy()

    # Update transparency values based on blur level
    for key, value in overrides.items():
        if isinstance(value, str) and len(value) == 9 and value.startswith("#"):
            # Extract base color and replace alpha channel
            base_color = value[:7]
            if "background" in key and (
                "status_bar" in key or "title_bar" in key or key == "background"
            ):
                overrides[key] = base_color + level_config["main"]
            elif "surface" in key:
                overrides[key] = base_color + level_config["surface"]
            elif any(elem in key for elem in ["drop_target", "tab.active"]):
                overrides[key] = base_color + level_config["active"]
            elif (
                any(elem in key for elem in ["thumb", "hover", "selected"])
                and "ghost_element" not in key
            ):
                overrides[key] = base_color + level_config["elements"]
            # Note: ghost_element colors are kept as-is for solid buttons

    return overrides


# ---------------------------------------------------------------------------
# Base theme overrides (per variant, applied on top of the upstream
# Rose Pine theme). These define the blur effect.
# ---------------------------------------------------------------------------
BASE_THEME_OVERRIDES = {
    # -----------------------------------------------------------------
    # Dawn (light variant)
    # -----------------------------------------------------------------
    "dawn": {
        "background.appearance": "blurred",
        "background": "#faf4edd7",
        "status_bar.background": "#faf4edd7",
        "title_bar.background": "#faf4edd7",
        "elevated_surface.background": "#fffaf3",
        "surface.background": "#faf4edd0",
        "border": "#9893a515",
        "hint.background": "#f2e9e0c0",
        "editor.background": "#00000000",
        "editor.line_number": "#79759320",
        "editor.active_line_number": "#907aa990",
        "editor.gutter.background": "#00000000",
        "tab_bar.background": "#00000000",
        "terminal.background": "#00000000",
        "toolbar.background": "#00000000",
        "tab.active_background": "#fffaf360",
        "tab.inactive_background": "#00000000",
        "panel.background": "#00000000",
        "panel.focused_border": "00000000",
        "panel.overlay_background": "#fffaf3",
        "pane_group.border": "#9893a515",
        "pane.focused_border": "#9893a510",
        "element.active": "#00000000",
        "border.variant": "#00000000",
        "scrollbar.track.border": "#00000000",
        "editor.active_line.background": "#00000000",
        "scrollbar.track.background": "#00000000",
        "scrollbar.thumb.background": "#79759330",
        "ghost_element.background": "#fffaf360",
        "ghost_element.hover": "#fffaf390",
        "ghost_element.active": "#907aa930",
        "ghost_element.selected": "#907aa950",
        "drop_target.background": "#907aa920",
        "editor.highlighted_line.background": "#907aa912",
        "error.background": "#f2e9e0",
        "warning.background": "#f2e9e0",
        "info.background": "#f2e9e0",
        "success.background": "#f2e9e0",
    },
    # -----------------------------------------------------------------
    # Rose Pine (default dark)
    # -----------------------------------------------------------------
    "rose_pine": {
        "background.appearance": "blurred",
        "background": "#191724d7",
        "status_bar.background": "#191724d7",
        "title_bar.background": "#191724d7",
        "elevated_surface.background": "#1f1d2e",
        "surface.background": "#191724d0",
        "border": "#26233a15",
        "hint.background": "#26233ac0",
        "editor.background": "#00000000",
        "editor.line_number": "#ffffff20",
        "editor.active_line_number": "#ebbcba90",
        "editor.gutter.background": "#00000000",
        "tab_bar.background": "#00000000",
        "terminal.background": "#00000000",
        "toolbar.background": "#00000000",
        "tab.active_background": "#1f1d2e60",
        "tab.inactive_background": "#00000000",
        "panel.background": "#00000000",
        "panel.focused_border": "00000000",
        "panel.overlay_background": "#191724",
        "pane_group.border": "#26233a15",
        "pane.focused_border": "#26233a10",
        "element.active": "#00000000",
        "border.variant": "#00000000",
        "scrollbar.track.border": "#00000000",
        "editor.active_line.background": "#00000000",
        "scrollbar.track.background": "#00000000",
        "scrollbar.thumb.background": "#6e6a8630",
        "ghost_element.background": "#1f1d2e60",
        "ghost_element.hover": "#1f1d2e90",
        "ghost_element.active": "#c4a7e730",
        "ghost_element.selected": "#c4a7e750",
        "drop_target.background": "#c4a7e720",
        "editor.highlighted_line.background": "#ebbcba12",
        "error.background": "#2a1c25",
        "warning.background": "#2a251c",
        "info.background": "#1a262c",
        "success.background": "#1c2a23",
    },
    # -----------------------------------------------------------------
    # Rose Pine Moon (darker dark)
    # -----------------------------------------------------------------
    "moon": {
        "background.appearance": "blurred",
        "background": "#232136d7",
        "status_bar.background": "#232136d7",
        "title_bar.background": "#232136d7",
        "elevated_surface.background": "#2a273f",
        "surface.background": "#232136d0",
        "border": "#39355215",
        "hint.background": "#393552c0",
        "editor.background": "#00000000",
        "editor.line_number": "#ffffff20",
        "editor.active_line_number": "#ea9a9790",
        "editor.gutter.background": "#00000000",
        "tab_bar.background": "#00000000",
        "terminal.background": "#00000000",
        "toolbar.background": "#00000000",
        "tab.active_background": "#2a273f60",
        "tab.inactive_background": "#00000000",
        "panel.background": "#00000000",
        "panel.focused_border": "00000000",
        "panel.overlay_background": "#232136",
        "pane_group.border": "#39355215",
        "pane.focused_border": "#39355210",
        "element.active": "#00000000",
        "border.variant": "#00000000",
        "scrollbar.track.border": "#00000000",
        "editor.active_line.background": "#00000000",
        "scrollbar.track.background": "#00000000",
        "scrollbar.thumb.background": "#6e6a8630",
        "ghost_element.background": "#2a273f60",
        "ghost_element.hover": "#2a273f90",
        "ghost_element.active": "#c4a7e730",
        "ghost_element.selected": "#c4a7e750",
        "drop_target.background": "#c4a7e720",
        "editor.highlighted_line.background": "#ea9a9712",
        "error.background": "#312228",
        "warning.background": "#2d281f",
        "info.background": "#1e2a32",
        "success.background": "#1f2c25",
    },
    # -----------------------------------------------------------------
    # Dusk (custom: very dark backgrounds with Rose Pine accents)
    # Based on Rose Pine (default dark) accent colors but with deeper,
    # near-black backgrounds for an "dusk" feel.
    # -----------------------------------------------------------------
    "dusk": {
        "background.appearance": "blurred",
        "background": "#0d0c14d7",
        "status_bar.background": "#0d0c14d7",
        "title_bar.background": "#0d0c14d7",
        "elevated_surface.background": "#08070d",
        "surface.background": "#0d0c14d0",
        "border": "#26233a15",
        "hint.background": "#1a1925c0",
        "editor.background": "#00000000",
        "editor.line_number": "#ffffff20",
        "editor.active_line_number": "#ebbcba90",
        "editor.gutter.background": "#00000000",
        "tab_bar.background": "#00000000",
        "terminal.background": "#00000000",
        "toolbar.background": "#00000000",
        "tab.active_background": "#08070d60",
        "tab.inactive_background": "#00000000",
        "panel.background": "#00000000",
        "panel.focused_border": "00000000",
        "panel.overlay_background": "#0a0912",
        "pane_group.border": "#26233a15",
        "pane.focused_border": "#26233a10",
        "element.active": "#00000000",
        "border.variant": "#00000000",
        "scrollbar.track.border": "#00000000",
        "editor.active_line.background": "#00000000",
        "scrollbar.track.background": "#00000000",
        "scrollbar.thumb.background": "#6e6a8630",
        "ghost_element.background": "#08070d60",
        "ghost_element.hover": "#08070d90",
        "ghost_element.active": "#c4a7e730",
        "ghost_element.selected": "#c4a7e750",
        "drop_target.background": "#c4a7e720",
        "editor.highlighted_line.background": "#ebbcba12",
        "error.background": "#2a0f15",
        "warning.background": "#241c0f",
        "info.background": "#0f1c22",
        "success.background": "#0f2118",
    },
}

# Generate all theme overrides for all blur levels
THEME_OVERRIDES = {}
for level_name, level_config in BLUR_LEVELS.items():
    for variant_name, base_overrides in BASE_THEME_OVERRIDES.items():
        key = f"{variant_name}_{level_name}"
        THEME_OVERRIDES[key] = generate_theme_overrides_for_level(
            base_overrides, level_config
        )


# ---------------------------------------------------------------------------
# Map upstream theme variant names to our override keys.
# Upstream Rose Pine provides 3 variants: "Rosé Pine", "Rosé Pine Moon",
# "Rosé Pine Dawn". The Dusk variant is generated locally by
# sync_theme.py (based on "Rosé Pine").
# ---------------------------------------------------------------------------
VARIANT_MAP = {
    "dawn": "dawn_medium",
    "rose pine": "rose_pine_medium",
    "moon": "moon_medium",
}
