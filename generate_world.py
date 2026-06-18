import os
import json
import yaml
import re

CONFIG_FILE = "world.config.yml"
ASSETS_DIR = "assets"

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

class AssetLoader:
    """Loads SVG and PNG files and prepares them for <defs> insertion."""
    
    @staticmethod
    def load_asset(name, filepath):
        if not os.path.exists(filepath):
            return ""
            
        if filepath.lower().endswith(".png"):
            import base64
            with open(filepath, "rb") as f:
                data = f.read()
            b64_data = base64.b64encode(data).decode('utf-8')
            width = int.from_bytes(data[16:20], byteorder='big')
            height = int.from_bytes(data[20:24], byteorder='big')
            
            # Assume each frame is a square (e.g. 32x32 for height=32)
            frame_width = height
            frames = width // frame_width
            
            values = ";".join([str(-i * frame_width) for i in range(frames)])
            
            # Wrap PNG in an animated SVG group
            return f'''<g id="{name}" transform="scale(2)">
    <svg width="{frame_width}" height="{frame_width}" viewBox="0 0 {frame_width} {frame_width}">
        <image href="data:image/png;base64,{b64_data}" width="{width}" height="{height}">
            <animate attributeName="x" values="{values}" dur="0.8s" calcMode="discrete" repeatCount="indefinite"/>
        </image>
    </svg>
</g>'''

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r'<svg[^>]*>(.*?)</svg>', content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return content.strip()

class AssetRegistry:
    """Manages loaded assets and generates the SVG <defs> block."""
    
    def __init__(self):
        self.assets = {}
        self.loader = AssetLoader()
        
    def load(self, name, filepath):
        content = self.loader.load_asset(name, filepath)
        if content:
            self.assets[name] = content
            return True
        return False
        
    def get_defs_block(self):
        defs = ["<defs>"]
        for content in self.assets.values():
            defs.append(content)
        defs.append("</defs>")
        return "\n".join(defs)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    return {}

from state import load_state

def get_weather_colors(weather):
    if weather == "clear":
        return {"sky": "#87CEEB", "ground": "#4a7c3f"}
    elif weather == "cloudy":
        return {"sky": "#B0C4DE", "ground": "#4a7c3f"}
    elif weather == "rain":
        return {"sky": "#708090", "ground": "#3a5c2f"}
    elif weather == "storm":
        return {"sky": "#2F4F4F", "ground": "#2a4a2a"}
    elif weather == "snow":
        return {"sky": "#E0FFFF", "ground": "#e0e0e0"}
    return {"sky": "#87CEEB", "ground": "#4a7c3f"}

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

def render_animated_asset(registry, asset_id, x, y, anim_class=None):
    """Renders a loaded asset, optionally applying a CSS animation class."""
    if asset_id not in registry.assets:
        return ""
        
    if anim_class:
        # Wrap the <use> in translation and animation groups
        return f'<g transform="translate({x}, {y})"><g class="{anim_class}"><use href="#{asset_id}" /></g></g>'
    else:
        return f'<use href="#{asset_id}" x="{x}" y="{y}" />'


def render_background(weather, registry):
    colors = get_weather_colors(weather)
    sky = f'<rect id="sky" x="0" y="0" width="800" height="300" fill="{colors["sky"]}" />'
    ground = f'<rect id="ground" x="0" y="240" width="800" height="60" fill="{colors["ground"]}" />'
    
    trees = []
    if "forest_tree" in registry.assets:
        # Give trees a subtle sway
        trees.append(render_animated_asset(registry, "forest_tree", 80, 168, "anim-sway"))
        trees.append(render_animated_asset(registry, "forest_tree", 350, 168, "anim-sway"))
        trees.append(render_animated_asset(registry, "forest_tree", 650, 168, "anim-sway"))
    
    return f"{sky}\n{ground}\n" + "\n".join(trees)

def render_weather(weather, registry):
    elements = []
    
    if weather in ["cloudy", "rain", "storm", "snow"]:
        anim = WEATHER_ANIMATIONS.get("cloud")
        elements.append(render_animated_asset(registry, "weather_cloud", 100, 20, anim))
        elements.append(render_animated_asset(registry, "weather_cloud", 400, 40, anim))
        elements.append(render_animated_asset(registry, "weather_cloud", 600, 10, anim))
    
    if weather == "rain":
        anim = WEATHER_ANIMATIONS.get("rain")
        elements.append(render_animated_asset(registry, "weather_rain_overlay", 0, 0, anim))
            
    if weather == "storm":
        anim_rain = WEATHER_ANIMATIONS.get("rain")
        anim_lightning = WEATHER_ANIMATIONS.get("lightning")
        elements.append(render_animated_asset(registry, "weather_storm_overlay", 0, 0, anim_rain))
        # Add lightning flash spanning the screen
        elements.append(f'<rect x="0" y="0" width="800" height="300" fill="#ffffff" class="{anim_lightning}" pointer-events="none" />')
    
    if weather == "snow":
        anim = WEATHER_ANIMATIONS.get("snow")
        elements.append(render_animated_asset(registry, "weather_snow_overlay", 0, 0, anim))

    return "\n".join(elements)

def render_pet(character, mood, registry):
    if mood not in ["happy", "sleepy", "hungry", "scared"]:
        if mood == "sad":
            mood = "scared"
        else:
            mood = "happy"
            
    asset_id = f"{character}_{mood}"
    anim_class = MOOD_ANIMATIONS.get(mood)
    
    y_pos = 210 if character == "cat" else 204
    if mood == "sleepy":
        y_pos += 4
    elif mood == "hungry" and character == "dog":
        y_pos += 4
        
    return render_animated_asset(registry, asset_id, 400, y_pos, anim_class)

from security import escape_svg_text

def render_ui(name, weather, character, state, registry):
    ui_elements = ['<g id="ui" transform="translate(10, 10)">']
    
    # We will use a larger UI panel or multiple rects for layout.
    # We'll use a single wide translucent black rect.
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
        safe_char = escape_svg_text(character)
        
        if e_type == "gift":
            sign_text = f"Thanks {e_user} for the {e_item}!"
        elif e_type == "pet":
            sign_text = f"{e_user} petted the {safe_char}"
        elif e_type == "weather":
            sign_text = f"{e_user} changed weather to {e_item}"
            
    ui_elements.append(f'<text x="{col3_x}" y="{y_offset}" font-family="sans-serif" font-size="12" fill="#ffd700">{sign_text}</text>')

    # --- DEBUG FOOTER ---
    recent_action = state.get("recent_action", "None")
    ui_elements.append(f'<text x="10" y="280" font-family="monospace" font-size="10" fill="#ff0000">DEBUG - Friendship: {friendship} | Last Gift: {last_gift} | Gifted By: {gifted_by} | Recent Action: {recent_action}</text>')

    ui_elements.append('</g>')
    return "\n".join(ui_elements)

def generate_svg():
    config = load_config()
    state = load_state()
    
    name = config.get("name", "Traveller")
    character = config.get("character", "cat")
    biome = config.get("biome", "forest")
    
    weather = state.get("weather", "clear")
    pet_state = state.get("pet", {})
    mood = pet_state.get("mood", "happy")
    
    # Normalize mood to match available assets, mirroring render_pet logic
    if mood not in ["happy", "sleepy", "hungry", "scared"]:
        mood = "scared" if mood == "sad" else "happy"
        
    recent_events = state.get("recent_events", [])

    registry = AssetRegistry()
    
    # Map moods to sprite files based on Gray Cat Asset Pack requirements
    mood_to_sprite = {
        "happy": "idle.png",
        "sleepy": "idle.png",
        "hungry": "walk.png",
        "scared": "run.png"
    }
    
    # Fallback to existing SVG if PNG doesn't exist (for other characters/moods)
    sprite_file = mood_to_sprite.get(mood, f"{mood}.svg")
    sprite_path = os.path.join(ASSETS_DIR, "characters", character, sprite_file)
    
    # If the mapped PNG doesn't exist, try falling back to the default SVG
    if not os.path.exists(sprite_path) and sprite_file.endswith(".png"):
        sprite_path = os.path.join(ASSETS_DIR, "characters", character, f"{mood}.svg")
        
    registry.load(f"{character}_{mood}", sprite_path)
    
    registry.load("forest_tree", os.path.join(ASSETS_DIR, "biomes", biome, "tree.svg"))
    
    registry.load("weather_cloud", os.path.join(ASSETS_DIR, "weather", "cloud.svg"))
    if weather == "rain":
        registry.load("weather_rain_overlay", os.path.join(ASSETS_DIR, "weather", "rain_overlay.svg"))
    elif weather == "storm":
        registry.load("weather_storm_overlay", os.path.join(ASSETS_DIR, "weather", "storm_overlay.svg"))
    elif weather == "snow":
        registry.load("weather_snow_overlay", os.path.join(ASSETS_DIR, "weather", "snow_overlay.svg"))
        
    registry.load("ui_panel", os.path.join(ASSETS_DIR, "ui", "panel.svg"))

    svg_open = '<svg width="100%" viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges" image-rendering="pixelated">'
    svg_close = '</svg>'

    content = "\n".join([
        svg_open,
        generate_css(),
        registry.get_defs_block(),
        render_background(weather, registry),
        render_weather(weather, registry),
        render_pet(character, mood, registry),
        render_ui(name, weather, character, state, registry),
        svg_close
    ])

    import artifact_manager
    artifact_manager.save_world_svg(content)
    print(f"Generated world.svg with weather: {weather}, character: {character}, mood: {mood}, biome: {biome}")

if __name__ == "__main__":
    generate_svg()
