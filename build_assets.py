import os

assets = {
    "assets/characters/cat/happy.svg": '''<g id="cat_happy" transform="scale(2)">
    <rect x="0" y="8" width="12" height="6" fill="#f4a460"/>
    <rect x="2" y="14" width="2" height="2" fill="#f4a460"/>
    <rect x="8" y="14" width="2" height="2" fill="#f4a460"/>
    <rect x="10" y="4" width="6" height="6" fill="#f4a460"/>
    <rect x="10" y="2" width="2" height="2" fill="#f4a460"/>
    <rect x="14" y="2" width="2" height="2" fill="#f4a460"/>
    <rect x="0" y="4" width="2" height="4" fill="#f4a460"/> <!-- tail up -->
</g>''',
    
    "assets/characters/cat/sleepy.svg": '''<g id="cat_sleepy" transform="scale(2)">
    <rect x="0" y="10" width="14" height="6" fill="#f4a460"/> <!-- curled -->
    <rect x="12" y="10" width="4" height="4" fill="#f4a460"/> <!-- head tucked -->
    <rect x="0" y="8" width="4" height="2" fill="#f4a460"/> <!-- tail wrapped -->
</g>''',

    "assets/characters/cat/hungry.svg": '''<g id="cat_hungry" transform="scale(2)">
    <rect x="0" y="8" width="12" height="6" fill="#f4a460"/>
    <rect x="2" y="14" width="2" height="2" fill="#f4a460"/>
    <rect x="8" y="14" width="2" height="2" fill="#f4a460"/>
    <rect x="10" y="6" width="6" height="6" fill="#f4a460"/> <!-- head lowered -->
    <rect x="10" y="4" width="2" height="2" fill="#f4a460"/>
    <rect x="14" y="4" width="2" height="2" fill="#f4a460"/>
    <rect x="-2" y="12" width="4" height="2" fill="#f4a460"/> <!-- tail down -->
</g>''',

    "assets/characters/cat/scared.svg": '''<g id="cat_scared" transform="scale(2)">
    <rect x="0" y="6" width="12" height="8" fill="#f4a460"/> <!-- arched back -->
    <rect x="2" y="14" width="2" height="2" fill="#f4a460"/>
    <rect x="8" y="14" width="2" height="2" fill="#f4a460"/>
    <rect x="10" y="4" width="6" height="6" fill="#f4a460"/>
    <rect x="10" y="2" width="2" height="2" fill="#f4a460"/>
    <rect x="14" y="2" width="2" height="2" fill="#f4a460"/>
    <rect x="-2" y="2" width="2" height="6" fill="#f4a460"/> <!-- bushy tail straight up -->
</g>''',

    "assets/characters/dog/happy.svg": '''<g id="dog_happy" transform="scale(2)">
    <rect x="2" y="8" width="14" height="6" fill="#c8a882"/>
    <rect x="4" y="14" width="2" height="4" fill="#c8a882"/>
    <rect x="12" y="14" width="2" height="4" fill="#c8a882"/>
    <rect x="0" y="4" width="6" height="6" fill="#c8a882"/>
    <rect x="0" y="2" width="2" height="4" fill="#8b6347"/>
    <rect x="16" y="4" width="2" height="4" fill="#c8a882"/> <!-- tail wagging high -->
</g>''',

    "assets/characters/dog/sleepy.svg": '''<g id="dog_sleepy" transform="scale(2)">
    <rect x="2" y="12" width="16" height="6" fill="#c8a882"/> <!-- sleeping flat -->
    <rect x="0" y="10" width="8" height="6" fill="#c8a882"/>
    <rect x="0" y="8" width="2" height="4" fill="#8b6347"/>
</g>''',

    "assets/characters/dog/hungry.svg": '''<g id="dog_hungry" transform="scale(2)">
    <rect x="4" y="8" width="10" height="8" fill="#c8a882"/> <!-- sitting -->
    <rect x="4" y="16" width="4" height="2" fill="#c8a882"/>
    <rect x="10" y="16" width="4" height="2" fill="#c8a882"/>
    <rect x="2" y="6" width="6" height="6" fill="#c8a882"/> <!-- head down -->
    <rect x="2" y="4" width="2" height="4" fill="#8b6347"/>
</g>''',

    "assets/characters/dog/scared.svg": '''<g id="dog_scared" transform="scale(2)">
    <rect x="2" y="10" width="14" height="6" fill="#c8a882"/> <!-- cowering lower -->
    <rect x="4" y="16" width="2" height="2" fill="#c8a882"/>
    <rect x="12" y="16" width="2" height="2" fill="#c8a882"/>
    <rect x="0" y="6" width="6" height="6" fill="#c8a882"/>
    <rect x="0" y="4" width="2" height="4" fill="#8b6347"/> <!-- ears down flat -->
    <rect x="16" y="12" width="2" height="4" fill="#c8a882"/> <!-- tail tucked -->
</g>''',

    "assets/biomes/forest/tree.svg": '''<g id="forest_tree" transform="scale(3)">
    <rect x="6" y="16" width="4" height="8" fill="#8B4513"/>
    <rect x="2" y="8" width="12" height="8" fill="#228B22"/>
    <rect x="4" y="4" width="8" height="4" fill="#228B22"/>
    <rect x="6" y="0" width="4" height="4" fill="#228B22"/>
</g>''',

    "assets/weather/cloud.svg": '''<g id="weather_cloud" transform="scale(2)">
    <rect x="4" y="4" width="16" height="8" fill="#ffffff" opacity="0.8"/>
    <rect x="8" y="0" width="8" height="4" fill="#ffffff" opacity="0.8"/>
    <rect x="0" y="6" width="24" height="6" fill="#ffffff" opacity="0.8"/>
</g>''',

    "assets/ui/panel.svg": '''<g id="ui_panel">
    <rect x="0" y="0" width="220" height="80" fill="#000000" opacity="0.5" rx="5" />
</g>'''
}

# Add full-screen overlays dynamically so we don't have huge strings
rain_streaks = []
for i in range(0, 800, 40):
    rain_streaks.append(f'<rect x="{i}" y="50" width="2" height="15" fill="#89b4d4" opacity="0.6"/>')
    rain_streaks.append(f'<rect x="{i+20}" y="100" width="2" height="15" fill="#89b4d4" opacity="0.6"/>')
    rain_streaks.append(f'<rect x="{i+10}" y="150" width="2" height="15" fill="#89b4d4" opacity="0.6"/>')
assets["assets/weather/rain_overlay.svg"] = f'<g id="weather_rain_overlay">\n{"\\n".join(rain_streaks)}\n</g>'

storm_streaks = []
for i in range(0, 800, 30):
    storm_streaks.append(f'<rect x="{i}" y="50" width="2" height="25" fill="#89b4d4" opacity="0.8"/>')
    storm_streaks.append(f'<rect x="{i+15}" y="100" width="2" height="25" fill="#89b4d4" opacity="0.8"/>')
storm_streaks.append('<rect x="0" y="0" width="800" height="300" fill="#000000" opacity="0.4" />')
storm_streaks.append('<path d="M 400 20 L 380 120 L 410 120 L 390 220" stroke="#FFD700" stroke-width="4" fill="none" opacity="0.9"/>')
assets["assets/weather/storm_overlay.svg"] = f'<g id="weather_storm_overlay">\n{"\\n".join(storm_streaks)}\n</g>'

snow_flakes = []
for i in range(0, 800, 50):
    snow_flakes.append(f'<rect x="{i}" y="80" width="4" height="4" fill="#ffffff" opacity="0.9"/>')
    snow_flakes.append(f'<rect x="{i+25}" y="130" width="4" height="4" fill="#ffffff" opacity="0.9"/>')
    snow_flakes.append(f'<rect x="{i+10}" y="180" width="4" height="4" fill="#ffffff" opacity="0.9"/>')
    snow_flakes.append(f'<rect x="{i-10}" y="220" width="4" height="4" fill="#ffffff" opacity="0.9"/>')
assets["assets/weather/snow_overlay.svg"] = f'<g id="weather_snow_overlay">\n{"\\n".join(snow_flakes)}\n</g>'

def main():
    for filepath, content in assets.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        # Wrap everything in a standard SVG tag just in case, or leave as pure <g>?
        # The prompt says: "Assets are loaded from SVG files. Assets are injected into SVG defs automatically."
        # Usually SVG tools expect valid SVGs.
        # Let's wrap them in an <svg> tag so they are valid previewable SVGs, 
        # and our python loader will strip the <svg> wrapper or just insert the file content if it's already a <g>.
        # I'll just write pure <g> to keep it simple, or <svg> with the inner <g>. 
        # Actually pure <g> inside the .svg file is easiest for our custom loader.
        # But to be standard compliant, let's wrap it in <svg>.
        svg_wrapper = f'<?xml version="1.0" encoding="utf-8"?>\n<svg xmlns="http://www.w3.org/2000/svg">\n{content}\n</svg>'
        
        with open(filepath, "w") as f:
            f.write(svg_wrapper)
            
    print("Created all assets.")

if __name__ == "__main__":
    main()
