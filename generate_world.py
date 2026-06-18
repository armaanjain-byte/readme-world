"""
generate_world.py — SVG world renderer.

Reads state and a WorldPack manifest, then assembles the final world.svg.
Contains zero content-specific logic — all coordinates, colors, assets,
and prop placements come from the manifest.
"""

import os
import yaml

CONFIG_FILE = "world.config.yml"
OUTPUT_DIR = "generated"

MOOD_ANIMATIONS = {
    "happy": "anim-bounce",
    "sleepy": "anim-breathe",
    "hungry": "anim-pace",
    "scared": "anim-shake"
}

WEATHER_ANIMATIONS = {
    "cloud": "anim-float",
    "rain": "anim-rain",
    "snow": "anim-snowfall",
    "lightning": "anim-lightning"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    return {}

from state import load_state
from sprite_loader import load_svg_fragment, build_defs
from worldpack_loader import (
    load_manifest, get_sprite_path, get_weather_colors,
    get_weather_overlay, has_lightning, get_cloud_config,
    get_biome_props, get_actor_position
)
from security import escape_svg_text


def generate_css():
    """Generates the centralized CSS animation layer for the SVG."""
    return '''
<style>
    /* Base animation properties */
    .anim-bounce, .anim-breathe, .anim-pace, .anim-shake, .anim-float, .anim-rain, .anim-snowfall, .anim-lightning, .anim-sway, .anim-blink {
        transform-box: fill-box;
        transform-origin: center;
    }

    /* Weather Animations */
    .anim-float {
        animation: float 20s linear infinite;
    }
    @keyframes float {
        0% { transform: translateX(0px); }
        50% { transform: translateX(30px); }
        100% { transform: translateX(0px); }
    }

    .anim-rain {
        animation: rain 1s linear infinite;
    }
    @keyframes rain {
        0% { transform: translateY(-50px); }
        100% { transform: translateY(50px); }
    }

    .anim-snowfall {
        animation: snowfall 5s linear infinite;
    }
    @keyframes snowfall {
        0% { transform: translate(0px, -50px); }
        50% { transform: translate(20px, 0px); }
        100% { transform: translate(-10px, 50px); }
    }

    .anim-lightning {
        animation: lightning 10s infinite;
    }
    @keyframes lightning {
        0%, 90%, 100% { opacity: 0; }
        92% { opacity: 1; }
        94% { opacity: 0; }
        96% { opacity: 0.8; }
        98% { opacity: 0; }
    }
    
    .anim-sway {
        animation: sway 4s ease-in-out infinite alternate;
    }
    @keyframes sway {
        0% { transform: rotate(-2deg); }
        100% { transform: rotate(2deg); }
    }

    .anim-blink {
        animation: blink 3s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.2; }
    }

    /* Pet Behavior Animations */
    .anim-bounce {
        animation: bounce 1s ease-in-out infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .anim-breathe {
        animation: breathe 3s ease-in-out infinite;
    }
    @keyframes breathe {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    .anim-pace {
        animation: pace 6s linear infinite;
    }
    @keyframes pace {
        0% { transform: translateX(0) scaleX(1); }
        25% { transform: translateX(40px) scaleX(1); }
        26% { transform: translateX(40px) scaleX(-1); } /* flip */
        75% { transform: translateX(-40px) scaleX(-1); }
        76% { transform: translateX(-40px) scaleX(1); } /* flip back */
        100% { transform: translateX(0) scaleX(1); }
    }

    .anim-shake {
        animation: shake 0.2s linear infinite;
    }
    @keyframes shake {
        0% { transform: translateX(-2px); }
        50% { transform: translateX(2px); }
        100% { transform: translateX(-2px); }
    }
</style>
'''


def render_animated_asset(asset_id, x, y, anim_class=None):
    """Renders a loaded asset, optionally applying a CSS animation class."""
    if anim_class:
        return f'<g transform="translate({x}, {y})"><g class="{anim_class}"><use href="#{asset_id}" /></g></g>'
    else:
        return f'<use href="#{asset_id}" x="{x}" y="{y}" />'


def render_background(manifest, weather):
    """Render sky, ground, and biome props — all driven by manifest."""
    colors = get_weather_colors(manifest, weather)
    sky = f'<rect id="sky" x="0" y="0" width="800" height="300" fill="{colors["sky"]}" />'
    ground = f'<rect id="ground" x="0" y="240" width="800" height="60" fill="{colors["ground"]}" />'

    props = []
    for prop_def in get_biome_props(manifest):
        # Extract the asset ID from the <g id="..."> in the loaded fragment
        asset_path = prop_def.get("asset", "")
        # Derive a stable ID from the path: "biomes/forest/tree.svg" -> "forest_tree"
        base = os.path.splitext(os.path.basename(asset_path))[0]
        parent = os.path.basename(os.path.dirname(asset_path))
        asset_id = f"{parent}_{base}" if parent else base

        for pos in prop_def.get("positions", []):
            anim = pos.get("anim")
            props.append(render_animated_asset(asset_id, pos["x"], pos["y"], anim))

    return f"{sky}\n{ground}\n" + "\n".join(props)


def render_weather(manifest, weather):
    """Render weather overlays — all driven by manifest."""
    elements = []

    # Clouds for non-clear weather
    cloud_config = get_cloud_config(manifest)
    if weather != "clear" and cloud_config:
        cloud_asset = cloud_config.get("asset", "")
        base = os.path.splitext(os.path.basename(cloud_asset))[0]
        cloud_id = f"weather_{base}"
        anim = WEATHER_ANIMATIONS.get("cloud")
        for pos in cloud_config.get("positions", []):
            elements.append(render_animated_asset(cloud_id, pos["x"], pos["y"], anim))

    # Weather overlay
    overlay_path = get_weather_overlay(manifest, weather)
    if overlay_path:
        base = os.path.splitext(os.path.basename(overlay_path))[0]
        overlay_id = f"weather_{base}"
        # Use rain animation for overlays
        anim = WEATHER_ANIMATIONS.get("rain")
        elements.append(render_animated_asset(overlay_id, 0, 0, anim))

    # Lightning flash
    if has_lightning(manifest, weather):
        anim_lightning = WEATHER_ANIMATIONS.get("lightning")
        elements.append(f'<rect x="0" y="0" width="800" height="300" fill="#ffffff" class="{anim_lightning}" pointer-events="none" />')

    return "\n".join(elements)


def render_actor(manifest, mood):
    """Render the actor sprite — position from manifest, no species knowledge."""
    # Build the asset ID from the sprite path in the manifest
    sprite_path = get_sprite_path(manifest, mood)
    base = os.path.splitext(os.path.basename(sprite_path))[0]
    parent = os.path.basename(os.path.dirname(sprite_path))
    asset_id = f"{parent}_{base}" if parent else base

    anim_class = MOOD_ANIMATIONS.get(mood)
    actor_x, actor_y = get_actor_position(manifest)

    return render_animated_asset(asset_id, actor_x, actor_y, anim_class)


def render_ui(name, weather, state):
    """Render the UI overlay — generic, no species knowledge."""
    ui_elements = ['<g id="ui" transform="translate(10, 10)">']
    ui_elements.append('<rect x="0" y="0" width="780" height="90" fill="#000000" opacity="0.6" rx="5" />')

    safe_name = escape_svg_text(name)
    safe_weather = escape_svg_text(weather)

    pet = state.get("pet", {})
    safe_mood = escape_svg_text(pet.get("mood", "happy").capitalize())
    friendship = pet.get("friendship", 0)
    energy = pet.get("energy", 100)
    hunger = pet.get("hunger", 0)

    # --- Column 1: Status ---
    col1_x = 10
    ui_elements.append(f'<text x="{col1_x}" y="20" font-family="sans-serif" font-size="14" fill="#ffffff" font-weight="bold">Status</text>')
    ui_elements.append(f'<text x="{col1_x}" y="40" font-family="sans-serif" font-size="12" fill="#ffffff">Mood: {safe_mood}</text>')
    ui_elements.append(f'<text x="{col1_x}" y="55" font-family="sans-serif" font-size="12" fill="#ffffff">Friendship: {friendship}</text>')
    ui_elements.append(f'<text x="{col1_x}" y="70" font-family="sans-serif" font-size="12" fill="#ffffff">Energy: {energy}</text>')
    ui_elements.append(f'<text x="{col1_x}" y="85" font-family="sans-serif" font-size="12" fill="#ffffff">Hunger: {hunger}</text>')

    # --- Column 2: Leaderboard ---
    col2_x = 200
    friendship_log = state.get("friendship_log", {})
    sorted_friends = sorted(friendship_log.items(), key=lambda item: item[1], reverse=True)[:3]

    ui_elements.append(f'<text x="{col2_x}" y="20" font-family="sans-serif" font-size="14" fill="#ffffff" font-weight="bold">Top Friends</text>')
    if not sorted_friends:
        ui_elements.append(f'<text x="{col2_x}" y="40" font-family="sans-serif" font-size="12" fill="#aaaaaa">No friends yet</text>')
    else:
        for i, (f_user, f_score) in enumerate(sorted_friends):
            safe_f_user = escape_svg_text(f_user)
            ui_elements.append(f'<text x="{col2_x}" y="{40 + (i*15)}" font-family="sans-serif" font-size="12" fill="#ffffff">{i+1}. {safe_f_user} ({f_score})</text>')

    # --- Column 3: Gifts & Events ---
    col3_x = 450
    last_gift = state.get("last_gift")
    gifted_by = state.get("gifted_by")

    ui_elements.append(f'<text x="{col3_x}" y="20" font-family="sans-serif" font-size="14" fill="#ffffff" font-weight="bold">Recent Activity</text>')

    y_offset = 40
    if last_gift and gifted_by:
        safe_gift = escape_svg_text(str(last_gift).capitalize())
        safe_giver = escape_svg_text(str(gifted_by))
        ui_elements.append(f'<text x="{col3_x}" y="{y_offset}" font-family="sans-serif" font-size="12" fill="#ffffff">Gift: {safe_gift} (From: {safe_giver})</text>')
        y_offset += 15

    recent_events = state.get("recent_events", [])
    sign_text = "No recent visitors"
    if recent_events and len(recent_events) > 0:
        event = recent_events[0]
        e_type = event.get("type")
        e_user = escape_svg_text(event.get("user", ""))
        e_item = escape_svg_text(event.get("item", ""))

        if e_type == "gift":
            sign_text = f"Thanks {e_user} for the {e_item}!"
        elif e_type == "pet":
            sign_text = f"{e_user} petted the actor"
        elif e_type == "weather":
            sign_text = f"{e_user} changed weather to {e_item}"

    ui_elements.append(f'<text x="{col3_x}" y="{y_offset}" font-family="sans-serif" font-size="12" fill="#ffd700">{sign_text}</text>')

    # --- DEBUG FOOTER ---
    recent_action = state.get("recent_action", "None")
    ui_elements.append(f'<text x="10" y="280" font-family="monospace" font-size="10" fill="#ff0000">DEBUG - Friendship: {friendship} | Last Gift: {last_gift} | Gifted By: {gifted_by} | Recent Action: {recent_action}</text>')

    ui_elements.append('</g>')
    return "\n".join(ui_elements)


def generate_svg():
    """Main entry point — loads config, manifest, state, and renders world.svg."""
    config = load_config()

    name = config.get("name", "Traveller")
    worldpack_path = config.get("worldpack", "worldpacks/default")

    manifest = load_manifest(worldpack_path)

    state = load_state()
    weather = state.get("weather", "clear")
    pet_state = state.get("pet", {})
    mood = pet_state.get("mood", "happy")

    # Normalize mood to available moods
    if mood not in ["happy", "sleepy", "hungry", "scared"]:
        mood = "scared" if mood == "sad" else "happy"

    # Load all SVG fragments referenced by the manifest
    fragments = []

    # Actor sprite
    sprite_path = get_sprite_path(manifest, mood)
    if os.path.exists(sprite_path):
        fragments.append(load_svg_fragment(sprite_path))

    # Biome props
    for prop_def in get_biome_props(manifest):
        asset_path = prop_def.get("asset", "")
        if os.path.exists(asset_path):
            fragments.append(load_svg_fragment(asset_path))

    # Cloud asset
    cloud_config = get_cloud_config(manifest)
    cloud_asset = cloud_config.get("asset", "")
    if cloud_asset and os.path.exists(cloud_asset):
        fragments.append(load_svg_fragment(cloud_asset))

    # Weather overlay
    overlay_path = get_weather_overlay(manifest, weather)
    if overlay_path and os.path.exists(overlay_path):
        fragments.append(load_svg_fragment(overlay_path))

    defs = build_defs(*fragments)

    svg_open = '<svg width="100%" viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges" image-rendering="pixelated">'
    svg_close = '</svg>'

    content = "\n".join([
        svg_open,
        generate_css(),
        defs,
        render_background(manifest, weather),
        render_weather(manifest, weather),
        render_actor(manifest, mood),
        render_ui(name, weather, state),
        svg_close
    ])

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(os.path.join(OUTPUT_DIR, "world.svg"), "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated world.svg with weather: {weather}, mood: {mood}")


if __name__ == "__main__":
    generate_svg()
