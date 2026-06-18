import os
import re

def migrate_asset(src, dst, new_id=None):
    if not os.path.exists(src): return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, 'r') as f:
        content = f.read()
    
    match = re.search(r'(<g\b.*?</g>)', content, re.DOTALL)
    if match:
        fragment = match.group(1).strip()
        if new_id:
            fragment = re.sub(r'id="[^"]+"', f'id="{new_id}"', fragment, count=1)
            
        with open(dst, 'w') as f:
            f.write(fragment)
    else:
        # If no <g> is found, maybe it's just the root
        with open(dst, 'w') as f:
            f.write(content.strip())

migrate_asset('assets/biomes/forest/tree.svg', 'biomes/forest/tree.svg', 'forest_tree')
for mood in ['happy', 'hungry', 'scared', 'sleepy']:
    migrate_asset(f'assets/characters/cat/{mood}.svg', f'sprites/cat/{mood}.svg', f'cat_{mood}')
    migrate_asset(f'assets/characters/dog/{mood}.svg', f'sprites/dog/{mood}.svg', f'dog_{mood}')

migrate_asset('assets/weather/cloud.svg', 'weather/cloud.svg', 'weather_cloud')
migrate_asset('assets/weather/rain_overlay.svg', 'weather/rain.svg', 'weather_rain')
migrate_asset('assets/weather/snow_overlay.svg', 'weather/snow.svg', 'weather_snow')
migrate_asset('assets/weather/storm_overlay.svg', 'weather/storm.svg', 'weather_storm')
