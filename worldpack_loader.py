"""
worldpack_loader.py — Loads and queries a WorldPack manifest.

A WorldPack is a directory containing a manifest.yml and associated
SVG asset files. The manifest defines all rendering parameters,
gift effects, weather colors, and biome props so that the engine
operates entirely on generic concepts without any species- or
content-specific hardcoding.
"""

import os
import yaml

def load_manifest(worldpack_path):
    """Load and return the parsed manifest.yml from a worldpack directory."""
    manifest_path = os.path.join(worldpack_path, "manifest.yml")
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_sprite_path(manifest, mood):
    """Return the sprite file path for a given mood, falling back to 'happy'."""
    sprites = manifest.get("sprites", {})
    path = sprites.get(mood)
    if not path:
        path = sprites.get("happy", "")
    return path

def get_valid_gifts(manifest):
    """Return the list of valid gift names defined in the manifest."""
    return list(manifest.get("gifts", {}).keys())

def get_gift_effects(manifest, gift_type):
    """Return the effects dict for a gift type, or None if not found."""
    return manifest.get("gifts", {}).get(gift_type)

def get_weather_colors(manifest, weather):
    """Return {'sky': ..., 'ground': ...} for a weather type."""
    weather_def = manifest.get("weather", {}).get(weather, {})
    default_clear = manifest.get("weather", {}).get("clear", {})
    return {
        "sky": weather_def.get("sky", default_clear.get("sky", "#87CEEB")),
        "ground": weather_def.get("ground", default_clear.get("ground", "#4a7c3f"))
    }

def get_weather_overlay(manifest, weather):
    """Return the overlay asset path for a weather type, or None."""
    weather_def = manifest.get("weather", {}).get(weather, {})
    return weather_def.get("overlay")

def has_lightning(manifest, weather):
    """Return whether a weather type should show the lightning flash."""
    weather_def = manifest.get("weather", {}).get(weather, {})
    return weather_def.get("lightning", False)

def get_cloud_config(manifest):
    """Return {'asset': path, 'positions': [...]} for clouds."""
    return manifest.get("clouds", {})

def get_biome_props(manifest):
    """Return list of prop dicts from the biome definition."""
    return manifest.get("biome", {}).get("props", [])

def get_actor_position(manifest):
    """Return (x, y) tuple for the actor's base rendering position."""
    actor = manifest.get("actor", {})
    return actor.get("x", 400), actor.get("y", 210)

def get_available_weather(manifest):
    """Return list of weather type names defined in the manifest."""
    return list(manifest.get("weather", {}).keys())

def get_progression_props(manifest, current_friendship):
    """Return list of prop dicts from progression tiers <= current_friendship."""
    progression = manifest.get("progression", [])
    props = []
    for tier in progression:
        if current_friendship >= tier.get("threshold", 0):
            props.extend(tier.get("props", []))
    return props

def get_gift_asset(manifest, gift_type):
    """Return asset path and optional offset for a gift."""
    gift_def = manifest.get("gifts", {}).get(gift_type, {})
    asset = gift_def.get("asset")
    x = gift_def.get("x", 450)
    y = gift_def.get("y", 240)
    if not asset:
        return None
    return {"asset": asset, "x": x, "y": y}
