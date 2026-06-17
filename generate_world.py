import os
import json
import yaml
import re

CONFIG_FILE = "world.config.yml"
STATE_FILE = "state.json"
OUTPUT_FILE = "world.svg"
ASSETS_DIR = "assets"

class AssetLoader:
    """Loads SVG files and strips outer tags to prepare them for <defs> insertion."""
    
    @staticmethod
    def load_asset(filepath):
        if not os.path.exists(filepath):
            return ""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract content inside <svg> if it exists
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
        """Loads an asset from a file and registers it if found."""
        content = self.loader.load_asset(filepath)
        if content:
            self.assets[name] = content
            return True
        return False
        
    def get_defs_block(self):
        """Constructs the <defs> block containing all loaded assets."""
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

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"weather": "clear", "pet": {"species": "cat", "mood": "happy"}}

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

def render_background(weather, registry):
    colors = get_weather_colors(weather)
    sky = f'<rect id="sky" x="0" y="0" width="800" height="300" fill="{colors["sky"]}" />'
    ground = f'<rect id="ground" x="0" y="240" width="800" height="60" fill="{colors["ground"]}" />'
    
    trees = ""
    if "forest_tree" in registry.assets:
        trees = '''
        <use href="#forest_tree" x="80" y="168" />
        <use href="#forest_tree" x="350" y="168" />
        <use href="#forest_tree" x="650" y="168" />
        '''
    
    return f"{sky}\n{ground}\n{trees}"

def render_weather(weather, registry):
    elements = []
    
    if weather in ["cloudy", "rain", "storm", "snow"]:
        if "weather_cloud" in registry.assets:
            elements.append('<use href="#weather_cloud" x="100" y="20" />')
            elements.append('<use href="#weather_cloud" x="400" y="40" />')
            elements.append('<use href="#weather_cloud" x="600" y="10" />')
    
    if weather == "rain":
        if "weather_rain_overlay" in registry.assets:
            elements.append('<use href="#weather_rain_overlay" x="0" y="0" />')
            
    if weather == "storm":
        if "weather_storm_overlay" in registry.assets:
            elements.append('<use href="#weather_storm_overlay" x="0" y="0" />')
    
    if weather == "snow":
        if "weather_snow_overlay" in registry.assets:
            elements.append('<use href="#weather_snow_overlay" x="0" y="0" />')

    return "\n".join(elements)

def render_pet(character, mood, registry):
    if mood not in ["happy", "sleepy", "hungry", "scared"]:
        if mood == "sad":
            mood = "scared"
        else:
            mood = "happy"
            
    asset_id = f"{character}_{mood}"
    
    y_pos = 210 if character == "cat" else 204
    if mood == "sleepy":
        y_pos += 4
    elif mood == "hungry" and character == "dog":
        y_pos += 4
        
    if asset_id in registry.assets:
        return f'<use href="#{asset_id}" x="400" y="{y_pos}" />'
    
    return ""

def render_ui(name, mood, weather, registry):
    ui_elements = ['<g id="ui" transform="translate(10, 10)">']
    
    if "ui_panel" in registry.assets:
        ui_elements.append('<use href="#ui_panel" x="0" y="0" />')
    else:
        ui_elements.append('<rect x="0" y="0" width="220" height="80" fill="#000000" opacity="0.5" rx="5" />')
        
    ui_elements.append(f'<text x="10" y="25" font-family="sans-serif" font-size="16" fill="#ffffff">Owner: {name}</text>')
    ui_elements.append(f'<text x="10" y="50" font-family="sans-serif" font-size="16" fill="#ffffff">Weather: {weather}</text>')
    ui_elements.append(f'<text x="10" y="75" font-family="sans-serif" font-size="16" fill="#ffffff">Mood: {mood}</text>')
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

    # Initialize Asset System
    registry = AssetRegistry()
    
    # Load necessary assets
    registry.load(f"{character}_{mood}", os.path.join(ASSETS_DIR, "characters", character, f"{mood}.svg"))
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
        registry.get_defs_block(),
        render_background(weather, registry),
        render_weather(weather, registry),
        render_pet(character, mood, registry),
        render_ui(name, mood, weather, registry),
        svg_close
    ])

    with open(OUTPUT_FILE, "w") as f:
        f.write(content)
    print(f"Generated {OUTPUT_FILE} with weather: {weather}, character: {character}, mood: {mood}, biome: {biome}")

if __name__ == "__main__":
    generate_svg()
