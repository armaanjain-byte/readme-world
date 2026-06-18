import os, json  
from generate_world import AssetLoader, AssetRegistry, load_config  
from state import initialize_state  
config = load_config()  
character = config.get('character', 'cat')  
registry = AssetRegistry()  
moods = ['happy', 'sleepy', 'hungry', 'scared']  
for mood in moods:  
    mood_to_sprite = {'happy': 'idle.png', 'sleepy': 'idle.png', 'hungry': 'walk.png', 'scared': 'run.png'}  
    sprite_file = mood_to_sprite.get(mood, f'{mood}.svg')  
    sprite_path = os.path.join('assets', 'characters', character, sprite_file)  
    loaded = registry.load(f'{character}_{mood}', sprite_path)  
    print(f'{mood}: Loaded {sprite_path} (success={loaded})')  
print('Registered IDs:', list(registry.assets.keys()))  
