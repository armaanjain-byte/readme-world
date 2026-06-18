import os
import re

SPRITES_DIR = "sprites"
BIOMES_DIR = "biomes"
WEATHER_DIR = "weather"

def load_svg_fragment(filepath):
    """Reads a .svg file and returns the inner <g>...</g> fragment only."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # If file is a bare <g>, return as-is
    if content.strip().startswith("<g"):
        return content.strip()
    # Strip SVG wrapper if present
    match = re.search(r'(<g\b.*?</g>)', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()

def load_character(character, mood):
    """Returns SVG fragment for a character+mood. Falls back to 'happy' if mood file missing."""
    path = os.path.join(SPRITES_DIR, character, f"{mood}.svg")
    if not os.path.exists(path):
        path = os.path.join(SPRITES_DIR, character, "happy.svg")
    return load_svg_fragment(path)

def load_biome_asset(biome, name):
    path = os.path.join(BIOMES_DIR, biome, f"{name}.svg")
    if not os.path.exists(path): return ""
    return load_svg_fragment(path)

def load_weather_asset(name):
    path = os.path.join(WEATHER_DIR, f"{name}.svg")
    if not os.path.exists(path): return ""
    return load_svg_fragment(path)

def build_defs(*fragments):
    """Wraps all fragments into a single SVG <defs> block."""
    inner = "\n".join(f for f in fragments if f)
    return f"<defs>\n{inner}\n</defs>"
