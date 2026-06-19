import os
import re

SPRITES_DIR = "sprites"
BIOMES_DIR = "biomes"
WEATHER_DIR = "weather"

def load_svg_fragment(filepath, target_id=None):
    """Reads a .svg file and returns the inner <g>...</g> fragment.

    Handles:
    - Bare <g> files (returned as-is)
    - Full SVG files with nested <g> (extracts outermost <g> from body)
    - Inkscape SVGs with <defs>, <metadata>, <sodipodi:namedview> etc.

    If target_id is provided, the id attribute on the outermost <g> is
    replaced (or injected) to match, so <use href="#target_id"> works.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    fragment = _extract_g_fragment(content)

    if target_id and fragment:
        fragment = _set_g_id(fragment, target_id)

    return fragment

def _extract_g_fragment(content):
    """Extract the outermost meaningful <g> block from SVG content."""
    stripped = content.strip()

    # Case 1: File is already a bare <g>...</g>
    if stripped.startswith("<g"):
        return stripped

    # Case 2: Full SVG — find outermost <g> inside <svg>, ignoring
    # <defs>, <metadata>, <sodipodi:namedview> etc.
    # We need a greedy approach that captures nested <g> elements.
    # Strategy: find all top-level <g> blocks inside <svg> and take
    # the one most likely to be the content layer (not metadata).

    # First, strip the <svg> wrapper to get inner content
    svg_match = re.search(r'<svg[^>]*>(.*)</svg\s*>', stripped, re.DOTALL)
    if not svg_match:
        return stripped

    inner = svg_match.group(1)

    # Remove <defs>...</defs>, <metadata>...</metadata>,
    # <sodipodi:namedview.../> blocks to isolate content <g> elements
    inner = re.sub(r'<defs\b.*?</defs>', '', inner, flags=re.DOTALL)
    inner = re.sub(r'<metadata\b.*?</metadata\s*>', '', inner, flags=re.DOTALL)
    inner = re.sub(r'<sodipodi:namedview\b[^>]*/>', '', inner, flags=re.DOTALL)
    inner = re.sub(r'<sodipodi:namedview\b.*?/>', '', inner, flags=re.DOTALL)

    # Now find the outermost <g>...</g> using a balancing approach
    g_match = _find_outermost_g(inner)
    if g_match:
        return g_match.strip()

    # Fallback: return whatever is left, wrapped in a <g> if not already
    result = inner.strip() if inner.strip() else content.strip()
    if result and not result.startswith("<g"):
        result = f"<g>\n{result}\n</g>"
    return result

def _find_outermost_g(text):
    """Find the outermost <g>...</g> block, correctly handling nesting."""
    start = text.find('<g')
    if start == -1:
        return None

    depth = 0
    i = start
    while i < len(text):
        # Check for <g opening tag
        if text[i:i+2] == '<g' and (i+2 >= len(text) or text[i+2] in ' \t\n\r>'):
            depth += 1
            # Skip to end of this opening tag
            close = text.find('>', i)
            if close == -1:
                break
            # Check for self-closing
            if text[close-1] == '/':
                depth -= 1
            i = close + 1
        elif text[i:i+4] == '</g>' or text[i:i+4] == '</g ':
            depth -= 1
            if depth == 0:
                end = text.find('>', i) + 1
                return text[start:end]
            i += 4
        else:
            i += 1

    return None

def _set_g_id(fragment, target_id):
    """Replace or inject the id attribute on the outermost <g> tag."""
    # Find the first <g tag
    g_open_end = fragment.find('>')
    if g_open_end == -1:
        return fragment

    g_open = fragment[:g_open_end + 1]
    rest = fragment[g_open_end + 1:]

    # Replace existing id or inject one
    if re.search(r'\bid\s*=\s*["\']', g_open):
        g_open = re.sub(r'\bid\s*=\s*["\'][^"\']*["\']', f'id="{target_id}"', g_open, count=1)
    else:
        g_open = g_open.replace('<g', f'<g id="{target_id}"', 1)

    return g_open + rest

def load_character(character, mood):
    """Returns SVG fragment for a character+mood. Falls back to 'happy' if mood file missing."""
    path = os.path.join(SPRITES_DIR, character, f"{mood}.svg")
    if not os.path.exists(path):
        path = os.path.join(SPRITES_DIR, character, "happy.svg")
    target_id = f"{character}_{mood}"
    return load_svg_fragment(path, target_id=target_id)

def load_biome_asset(biome, name):
    path = os.path.join(BIOMES_DIR, biome, f"{name}.svg")
    if not os.path.exists(path): return ""
    target_id = f"{biome}_{name}"
    return load_svg_fragment(path, target_id=target_id)

def load_weather_asset(name):
    path = os.path.join(WEATHER_DIR, f"{name}.svg")
    if not os.path.exists(path): return ""
    target_id = f"weather_{name}"
    return load_svg_fragment(path, target_id=target_id)

def build_defs(*fragments):
    """Wraps all fragments into a single SVG <defs> block."""
    inner = "\n".join(f for f in fragments if f)
    return f"<defs>\n{inner}\n</defs>"

