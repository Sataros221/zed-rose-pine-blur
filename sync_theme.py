#!/usr/bin/env python3
"""
Rose Pine Blur - theme synchronizer.

Fetches the 3 official Rose Pine Zed themes from upstream, generates the
custom "Dusk" variant (a very dark variant using the Rose Pine accent
palette), and applies the blur-specific overrides defined in
theme_overrides.py for each blur level (light, medium, heavy).

The final theme file is written to themes/rose-pine-blur.json.
"""

import hashlib
import json
import os
import re
import sys
import time

import requests

from theme_overrides import (
    BLUR_LEVELS,
    THEME_OVERRIDES,
)

try:
    import jsonschema
except ImportError:
    print("jsonschema package not found. Installing...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema"])
    import jsonschema


# ANSI color codes
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


# URLs - the 3 official Rose Pine Zed themes
THEME_URLS = {
    "rose_pine": "https://raw.githubusercontent.com/rose-pine/zed/main/themes/rose-pine.json",
    "moon": "https://raw.githubusercontent.com/rose-pine/zed/main/themes/rose-pine-moon.json",
    "dawn": "https://raw.githubusercontent.com/rose-pine/zed/main/themes/rose-pine-dawn.json",
}
SCHEMA_URL = "https://zed.dev/schema/themes/v0.2.0.json"
SCHEMA_CACHE_FILE = ".theme_schema_cache.json"


def print_header():
    print(f"\n{Colors.PURPLE}╭{'─' * 48}╮{Colors.RESET}")
    print(
        f"{Colors.PURPLE}│{Colors.RESET} {Colors.BOLD}🎨 Rose Pine Blur Theme Sync{Colors.RESET}{'  ' * 9}{Colors.PURPLE}│{Colors.RESET}"
    )
    print(f"{Colors.PURPLE}╰{'─' * 48}╯{Colors.RESET}\n")


def print_step(step: str, status: str = "info"):
    icons = {
        "info": f"{Colors.BLUE}ℹ{Colors.RESET}",
        "success": f"{Colors.GREEN}✓{Colors.RESET}",
        "error": f"{Colors.RED}✗{Colors.RESET}",
        "warning": f"{Colors.YELLOW}⚠{Colors.RESET}",
        "processing": f"{Colors.CYAN}◆{Colors.RESET}",
    }
    print(f"{icons.get(status, icons['info'])} {step}")


def progress_bar(current: int, total: int, prefix: str = "", width: int = 30):
    percent = current / total
    filled = int(width * percent)
    bar = f"{'█' * filled}{'░' * (width - filled)}"

    sys.stdout.write(f"\r{prefix} {Colors.CYAN}[{bar}]{Colors.RESET} {percent:.0%}")
    sys.stdout.flush()

    if current == total:
        print()  # New line when complete


def get_file_hash(filepath: str) -> str:
    """Calculate SHA256 hash of a file."""
    if not os.path.exists(filepath):
        return ""

    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_content_hash(content: str) -> str:
    """Calculate SHA256 hash of string content."""
    return hashlib.sha256(content.encode()).hexdigest()


def fetch_schema() -> dict:
    """
    Fetch and cache the Zed theme schema.
    Cache expires after 7 days to ensure we stay up-to-date.
    Falls back to cached version if network request fails.
    """
    if os.path.exists(SCHEMA_CACHE_FILE):
        cache_age = time.time() - os.path.getmtime(SCHEMA_CACHE_FILE)
        if cache_age < 7 * 24 * 60 * 60:
            print_step("Using cached theme schema", "info")
            with open(SCHEMA_CACHE_FILE, "r") as f:
                return json.load(f)

    print_step("Fetching theme schema...", "processing")
    try:
        response = requests.get(SCHEMA_URL)
        response.raise_for_status()
        schema = response.json()

        with open(SCHEMA_CACHE_FILE, "w") as f:
            json.dump(schema, f, indent=2)

        print_step("Theme schema fetched and cached", "success")
        return schema
    except Exception as e:
        print_step(f"Failed to fetch schema: {str(e)}", "warning")
        if os.path.exists(SCHEMA_CACHE_FILE):
            print_step("Falling back to cached schema", "info")
            with open(SCHEMA_CACHE_FILE, "r") as f:
                return json.load(f)
        return None  # pyright: ignore[reportReturnType]


def validate_theme(theme: dict, schema: dict) -> bool:
    """Validate theme against the Zed schema."""
    if not schema:
        print_step("Skipping validation - no schema available", "warning")
        return True

    try:
        jsonschema.validate(instance=theme, schema=schema)
        print_step("Theme validation passed", "success")
        return True
    except jsonschema.ValidationError as e:
        print_step(f"Theme validation failed: {e.message}", "error")
        print(f"{Colors.DIM}  Path: {'.'.join(str(p) for p in e.path)}{Colors.RESET}")
        return False
    except Exception as e:
        print_step(f"Validation error: {str(e)}", "error")
        return False


def fix_json(json_str):
    """
    Fix common JSON syntax errors in theme files.
    Removes trailing commas before closing brackets/braces.
    """
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)
    return json_str


def fetch_theme(url: str, label: str) -> dict:
    """Fetch a single Rose Pine theme JSON from upstream."""
    print_step(f"Fetching {label}...", "processing")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        block_size = 8192
        downloaded = 0
        content = []

        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        spinner_idx = 0

        for data in response.iter_content(block_size):
            content.append(data)
            downloaded += len(data)
            sys.stdout.write(
                f"\r  {Colors.CYAN}{spinner[spinner_idx]}{Colors.RESET} Downloading {label}... ({downloaded / 1024:.1f} KB)"
            )
            sys.stdout.flush()
            spinner_idx = (spinner_idx + 1) % len(spinner)

        print()
        full_content = b"".join(content).decode("utf-8")
        print_step(f"{label} downloaded ({downloaded / 1024:.1f} KB)", "success")

        fixed = fix_json(full_content)
        return json.loads(fixed)
    except Exception as e:
        print_step(f"Failed to fetch {label}: {e}", "error")
        raise


def fetch_all_themes() -> dict:
    """
    Fetch all 3 official Rose Pine Zed themes and merge them into a single
    container structure compatible with the rest of the pipeline:
      {"themes": [ {theme...}, {theme...}, {theme...} ]}
    """
    merged = {"themes": []}
    for key, url in THEME_URLS.items():
        data = fetch_theme(url, key)
        # Each upstream file contains exactly one theme entry
        if "themes" in data and len(data["themes"]) > 0:
            merged["themes"].append(data["themes"][0])
        elif "name" in data and "style" in data:
            # Some versions store the theme at the top level
            merged["themes"].append(data)
    print_step(f"All {len(merged['themes'])} upstream themes fetched", "success")
    return merged


def make_dusk_theme(rose_pine_theme: dict) -> dict:
    """
    Create the custom "Dusk" variant by taking the default Rose Pine
    theme and overriding its background colors with near-black equivalents
    while keeping the Rose Pine accent palette.

    This mirrors how the original Catppuccin "Dusk" variant was built
    from Macchiato (black backgrounds + Macchiato accents), but applied to
    the Rose Pine palette.
    """
    dusk = json.loads(json.dumps(rose_pine_theme))  # deep copy
    dusk["name"] = "Rose Pine Dusk"
    dusk["appearance"] = "dark"

    s = dusk["style"]

    # Deep dark backgrounds (Dusk signature)
    s["background"] = "#0d0c14"
    s["status_bar.background"] = "#0d0c14"
    s["title_bar.background"] = "#0d0c14"
    s["title_bar.inactive_background"] = "#08070d"
    s["toolbar.background"] = "#0d0c14"
    s["tab_bar.background"] = "#08070d"
    s["tab.active_background"] = "#0d0c14"
    s["tab.inactive_background"] = "#08070d"
    s["panel.background"] = "#0d0c14"
    s["panel.overlay_background"] = "#0a0912"
    s["surface.background"] = "#14131e"
    s["elevated_surface.background"] = "#08070d"
    s["editor.background"] = "#0d0c14"
    s["editor.gutter.background"] = "#0d0c14"
    s["editor.active_line.background"] = "#14131e"
    s["editor.highlighted_line.background"] = "#14131e"
    s["editor.subheader.background"] = "#08070d"
    s["terminal.background"] = "#0d0c14"
    s["terminal.ansi.background"] = "#0d0c14"
    s["hidden.background"] = "#0d0c14"
    s["ignored.background"] = "#0d0c14"
    s["predictive.background"] = "#14131e"
    s["hint.background"] = "#14131e"
    s["renamed.background"] = "#14131e"
    s["conflict.background"] = "#14131e"
    s["info.background"] = "#0f1c22"
    s["warning.background"] = "#241c0f"
    s["error.background"] = "#2a0f15"
    s["success.background"] = "#0f2118"

    # Borders - keep Rose Pine's surface color for subtle borders
    s["border"] = "#26233a"
    s["border.variant"] = "#1a1925"
    s["pane_group.border"] = "#26233a"
    s["pane.focused_border"] = "#c4a7e744"

    return dusk


def apply_blur(theme):
    """
    Apply blur modifications to the Rose Pine theme.

    Steps:
      1. Take the 3 upstream themes (Dawn, Rose Pine, Moon).
      2. Generate the custom Dusk variant from Rose Pine.
      3. For each of the 4 base variants, generate 3 blur level variants
         (light, medium, heavy) by applying the overrides from
         THEME_OVERRIDES on top of the upstream style.
    """
    print_step("Applying blur modifications...", "processing")

    # Map variant name -> upstream theme entry
    base_themes = {}
    for entry in theme["themes"]:
        n = entry["name"].lower()
        if "dawn" in n:
            base_themes["dawn"] = entry
        elif "moon" in n:
            base_themes["moon"] = entry
        elif "rose pine" in n or "rosé pine" in n:
            base_themes["rose_pine"] = entry

    if "rose_pine" not in base_themes:
        raise RuntimeError(
            "Default Rose Pine theme not found upstream; cannot build variants."
        )

    # Build the custom Dusk variant from the default Rose Pine theme
    print_step("Creating custom Dusk variant...", "processing")
    base_themes["dusk"] = make_dusk_theme(base_themes["rose_pine"])
    print_step("Dusk variant created", "success")

    new_themes = []

    print(f"\n{Colors.BOLD}Generating all blur level variants:{Colors.RESET}")
    for level_name, level_config in BLUR_LEVELS.items():
        print(
            f"\n  {Colors.PURPLE}◆{Colors.RESET} Creating {Colors.BOLD}{level_name.capitalize()}{Colors.RESET} blur variants..."
        )

        for variant_key, base_theme in base_themes.items():
            new_theme = json.loads(json.dumps(base_theme))  # deep copy

            # Naming: medium = "Rose Pine (Blur)", others = "Rose Pine (Blur) [Light|Heavy]"
            display_name = base_theme["name"].replace(
                "Rosé Pine", "Rose Pine"
            )  # normalize
            if level_name == "medium":
                new_theme["name"] = f"{display_name} (Blur)"
            else:
                new_theme["name"] = f"{display_name} (Blur) [{level_name.capitalize()}]"

            override_key = f"{variant_key}_{level_name}"
            if override_key in THEME_OVERRIDES:
                for k, v in THEME_OVERRIDES[override_key].items():
                    new_theme["style"][k] = v
                new_themes.append(new_theme)
                print(
                    f"    {Colors.GREEN}✓{Colors.RESET} {display_name} ({level_name})"
                )
            else:
                print(
                    f"    {Colors.YELLOW}⚠{Colors.RESET} No overrides for {override_key}, skipping"
                )

    theme["themes"] = new_themes
    print(
        f"\n{Colors.GREEN}✓{Colors.RESET} All blur modifications applied successfully!"
    )
    return theme


def main():
    print_header()

    start_time = time.time()

    output_path = "themes/rose-pine-blur.json"

    # Create themes directory
    os.makedirs("themes", exist_ok=True)
    print_step("Initialized themes directory", "success")

    # Get hash of existing file
    existing_hash = get_file_hash(output_path)

    try:
        print()
        schema = fetch_schema()

        print()
        theme = fetch_all_themes()
        print()
        theme = apply_blur(theme)

        print(f"\n{Colors.BOLD}Finalizing theme:{Colors.RESET}")
        print_step("Updating theme metadata...", "processing")

        theme["name"] = "Rose Pine Blur"
        theme["author"] = "Sataros221 (Javier Valdés González) <sataros221@gmail.com>"
        theme["$schema"] = SCHEMA_URL
        variant_count = len(theme["themes"])

        print_step(f"Updated {variant_count} variant names", "success")

        # Validate theme before saving
        print(f"\n{Colors.BOLD}Validating theme:{Colors.RESET}")
        if not validate_theme(theme, schema):
            print_step("Theme validation failed - aborting", "error")
            sys.exit(1)

        # Generate new content
        new_content = json.dumps(theme, indent=2, ensure_ascii=False)
        new_hash = get_content_hash(new_content)

        # Check if content has changed
        if existing_hash == new_hash:
            print_step("No changes detected - theme is already up to date!", "info")

            elapsed = time.time() - start_time
            print(f"\n{Colors.BLUE}{'═' * 50}{Colors.RESET}")
            print(f"{Colors.BLUE}ℹ Theme is already up to date{Colors.RESET}")
            print(f"{Colors.DIM}   • No changes required{Colors.RESET}")
            print(f"{Colors.DIM}   • Time: {elapsed:.2f}s{Colors.RESET}")
            print(f"{Colors.DIM}   • Output: {output_path}{Colors.RESET}")
            print(f"{Colors.BLUE}{'═' * 50}{Colors.RESET}\n")
            return

        print_step("Changes detected - updating theme file...", "processing")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        file_size = os.path.getsize(output_path) / 1024  # KB
        print_step(
            f"Theme saved to {Colors.BOLD}{output_path}{Colors.RESET} ({file_size:.1f} KB)",
            "success",
        )

        elapsed = time.time() - start_time
        print(f"\n{Colors.GREEN}{'═' * 50}{Colors.RESET}")
        print(f"{Colors.GREEN}✨ Theme synchronization complete!{Colors.RESET}")
        print(f"{Colors.DIM}   • Variants: {variant_count}{Colors.RESET}")
        print(f"{Colors.DIM}   • Time: {elapsed:.2f}s{Colors.RESET}")
        print(f"{Colors.DIM}   • Output: {output_path}{Colors.RESET}")
        print(f"{Colors.GREEN}{'═' * 50}{Colors.RESET}\n")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠{Colors.RESET}  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Failed to update theme:{Colors.RESET} {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
