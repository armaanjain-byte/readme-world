import os
import json
import yaml

CONFIG_FILE = "world.config.yml"
STATE_FILE = "state.json"
OUTPUT_FILE = "world.svg"

def load_config():
    """Load the user configuration."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    return {}

def load_state():
    """Load the current world state."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {"weather": "clear"}

def get_weather_colors(weather):
    """Determine sky and ground colors based on weather."""
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

def generate_defs():
    """Generate SVG definitions for reusable pixel art sprites."""
    # Pixel art cat
    cat_sprite = '''
    <g id="cat" transform="scale(2)">
        <rect x="0" y="8" width="12" height="6" fill="#f4a460"/>
        <rect x="2" y="14" width="2" height="2" fill="#f4a460"/>
        <rect x="8" y="14" width="2" height="2" fill="#f4a460"/>
        <rect x="10" y="4" width="6" height="6" fill="#f4a460"/>
        <rect x="10" y="2" width="2" height="2" fill="#f4a460"/>
        <rect x="14" y="2" width="2" height="2" fill="#f4a460"/>
    </g>
    '''
    # Pixel art dog
    dog_sprite = '''
    <g id="dog" transform="scale(2)">
        <rect x="2" y="8" width="14" height="6" fill="#c8a882"/>
        <rect x="4" y="14" width="2" height="4" fill="#c8a882"/>
        <rect x="12" y="14" width="2" height="4" fill="#c8a882"/>
        <rect x="0" y="4" width="6" height="6" fill="#c8a882"/>
        <rect x="0" y="2" width="2" height="4" fill="#8b6347"/>
    </g>
    '''
    # Simple pixel tree
    tree_sprite = '''
    <g id="tree" transform="scale(3)">
        <rect x="6" y="16" width="4" height="8" fill="#8B4513"/>
        <rect x="2" y="8" width="12" height="8" fill="#228B22"/>
        <rect x="4" y="4" width="8" height="4" fill="#228B22"/>
        <rect x="6" y="0" width="4" height="4" fill="#228B22"/>
    </g>
    '''
    # Pixel cloud
    cloud_sprite = '''
    <g id="cloud" transform="scale(2)">
        <rect x="4" y="4" width="16" height="8" fill="#ffffff" opacity="0.8"/>
        <rect x="8" y="0" width="8" height="4" fill="#ffffff" opacity="0.8"/>
        <rect x="0" y="6" width="24" height="6" fill="#ffffff" opacity="0.8"/>
    </g>
    '''
    
    return f"<defs>\n{cat_sprite}\n{dog_sprite}\n{tree_sprite}\n{cloud_sprite}\n</defs>"

def generate_background(colors):
    """Generate the sky and ground layers."""
    sky = f'<rect id="sky" x="0" y="0" width="800" height="300" fill="{colors["sky"]}" />'
    ground = f'<rect id="ground" x="0" y="240" width="800" height="60" fill="{colors["ground"]}" />'
    return f"{sky}\n{ground}"

def generate_scenery():
    """Place trees to create a forest background."""
    trees = '''
    <use href="#tree" x="80" y="168" />
    <use href="#tree" x="350" y="168" />
    <use href="#tree" x="650" y="168" />
    '''
    return trees

def generate_weather_overlay(weather):
    """Generate visual weather effects like rain streaks or snow."""
    elements = []
    
    # Add clouds for non-clear weather
    if weather in ["cloudy", "rain", "storm", "snow"]:
        elements.append('<use href="#cloud" x="100" y="20" />')
        elements.append('<use href="#cloud" x="400" y="40" />')
        elements.append('<use href="#cloud" x="600" y="10" />')
    
    # Add rain streaks
    if weather in ["rain", "storm"]:
        for i in range(0, 800, 40):
            elements.append(f'<rect x="{i}" y="50" width="2" height="15" fill="#89b4d4" opacity="0.6"/>')
            elements.append(f'<rect x="{i+20}" y="100" width="2" height="15" fill="#89b4d4" opacity="0.6"/>')
            elements.append(f'<rect x="{i+10}" y="150" width="2" height="15" fill="#89b4d4" opacity="0.6"/>')
    
    # Add snow flakes
    if weather == "snow":
        for i in range(0, 800, 50):
            elements.append(f'<rect x="{i}" y="80" width="4" height="4" fill="#ffffff" opacity="0.8"/>')
            elements.append(f'<rect x="{i+25}" y="130" width="4" height="4" fill="#ffffff" opacity="0.8"/>')
            elements.append(f'<rect x="{i+10}" y="180" width="4" height="4" fill="#ffffff" opacity="0.8"/>')
            
    # Add storm effects
    if weather == "storm":
        elements.append('<rect x="0" y="0" width="800" height="300" fill="#000000" opacity="0.3" />')
        elements.append('<path d="M 400 20 L 380 120 L 410 120 L 390 220" stroke="#FFD700" stroke-width="3" fill="none" opacity="0.8"/>')

    return "\n".join(elements)

def generate_characters():
    """Place the cat and dog in the world."""
    cat = '<use href="#cat" x="200" y="210" />'
    dog = '<use href="#dog" x="550" y="204" />'
    return f"{cat}\n{dog}"

def generate_svg():
    """Main function to compose and write the SVG."""
    config = load_config()
    state = load_state()
    weather = state.get("weather", "clear")
    colors = get_weather_colors(weather)

    svg_open = '<svg width="100%" viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges" image-rendering="pixelated">'
    svg_close = '</svg>'

    # Assemble layers
    defs = generate_defs()
    bg = generate_background(colors)
    scenery = generate_scenery()
    weather_overlay = generate_weather_overlay(weather)
    chars = generate_characters()

    content = "\n".join([
        svg_open,
        defs,
        bg,
        scenery,
        weather_overlay,
        chars,
        svg_close
    ])

    with open(OUTPUT_FILE, "w") as f:
        f.write(content)
    print(f"Generated {OUTPUT_FILE} with weather: {weather}")

if __name__ == "__main__":
    generate_svg()
