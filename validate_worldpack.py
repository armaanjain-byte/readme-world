"""
validate_worldpack.py — Validates a WorldPack directory against the generic specification.
"""

import sys
import os
import yaml

def check_file_exists(path, context):
    if not os.path.exists(path):
        print(f"Error: Missing file '{path}' (referenced in {context})")
        return False
    return True

def validate_worldpack(worldpack_path):
    print(f"Validating WorldPack: {worldpack_path}...")
    manifest_path = os.path.join(worldpack_path, "manifest.yml")
    
    if not os.path.exists(manifest_path):
        print(f"Error: Missing manifest at '{manifest_path}'")
        return False
        
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
    except Exception as e:
        print(f"Error: Failed to parse YAML: {e}")
        return False
        
    if not isinstance(manifest, dict):
        print("Error: Manifest must be a YAML dictionary")
        return False
        
    all_good = True
    
    # 1. Check Sprites
    sprites = manifest.get("sprites", {})
    required_moods = ["happy", "sleepy", "hungry", "scared"]
    for mood in required_moods:
        path = sprites.get(mood)
        if not path:
            print(f"Error: Missing required sprite mood '{mood}' in manifest")
            all_good = False
        else:
            if not check_file_exists(path, f"sprites -> {mood}"):
                all_good = False
                
    # 2. Check Weather
    weather_dict = manifest.get("weather", {})
    if "clear" not in weather_dict:
        print("Error: Missing required weather type 'clear'")
        all_good = False
        
    for w_type, w_data in weather_dict.items():
        overlay = w_data.get("overlay")
        if overlay:
            if not check_file_exists(overlay, f"weather -> {w_type} -> overlay"):
                all_good = False
                
    # 3. Check Clouds
    clouds = manifest.get("clouds")
    if clouds and "asset" in clouds:
        if not check_file_exists(clouds["asset"], "clouds -> asset"):
            all_good = False
            
    # 4. Check Biomes
    biome = manifest.get("biome", {})
    props = biome.get("props", [])
    for idx, prop in enumerate(props):
        asset = prop.get("asset")
        if not asset:
            print(f"Error: Biome prop #{idx} missing 'asset' path")
            all_good = False
        else:
            if not check_file_exists(asset, f"biome -> props[{idx}]"):
                all_good = False

    if all_good:
        print("Success! The WorldPack is fully compliant.")
    else:
        print("\nFailure. Please fix the errors above.")
        
    return all_good

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_worldpack.py <path_to_worldpack_dir>")
        sys.exit(1)
        
    success = validate_worldpack(sys.argv[1])
    sys.exit(0 if success else 1)
