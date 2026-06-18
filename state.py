import json
import os
import random
from datetime import datetime, timezone

DEFAULT_STATE_FILE = "default_state.json"

WEATHER_PROBS = {
    "clear": 0.70,
    "rain": 0.15,
    "cloudy": 0.10,
    "storm": 0.04,
    "snow": 0.01
}

def _ensure_output_dir():
    if not os.path.exists("generated"):
        os.makedirs("generated")

def load_state():
    """Load state from output, fallback to initialization if missing/corrupt."""
    _ensure_output_dir()
    if os.path.exists("generated/state.json"):
        try:
            with open("generated/state.json", "r") as f:
                return json.load(f)
        except Exception:
            pass
    return initialize_state()

def save_state(state):
    """Save the current state to output."""
    _ensure_output_dir()
    with open("generated/state.json", "w") as f:
        json.dump(state, f, indent=2)

def initialize_state():
    """Initialize state from default_state.json, or fallback to hardcoded defaults."""
    if os.path.exists(DEFAULT_STATE_FILE):
        try:
            with open(DEFAULT_STATE_FILE, "r") as f:
                state = json.load(f)
        except Exception:
            state = None
            
    if not os.path.exists(DEFAULT_STATE_FILE) or state is None:
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        state = {
            "weather": "clear",
            "pet": {
                "mood": "happy",
                "energy": 100,
                "hunger": 0,
                "friendship": 0
            },
            "recent_action": None,
            "recent_user": None,
            "thank_you_cycles": 0,
            "last_gift": None,
            "gifted_by": None,
            "friendship_log": {},
            "recent_events": [],
            "cooldowns": {},
            "daily_usage": {
                "date": today_str,
                "users": {}
            }
        }
    return state

def update_random_world_state(state):
    """Update world state based on random drift and rules."""
    # 1. Update weather based on probabilities
    r = random.random()
    cumulative = 0.0
    for w, prob in WEATHER_PROBS.items():
        cumulative += prob
        if r <= cumulative:
            state["weather"] = w
            break

    # 2. Update pet attributes
    pet = state["pet"]
    
    # Hunger increases slowly (+5 per update), capped at 100
    pet["hunger"] = min(100, pet["hunger"] + 5)
    
    # Energy decreases slowly (-5 per update), floored at 0
    pet["energy"] = max(0, pet["energy"] - 5)
    
    # 3. Update mood based on hunger, energy, and weather
    if pet["hunger"] > 80:
        pet["mood"] = "hungry"
    elif pet["energy"] < 20:
        pet["mood"] = "sleepy"
    elif state["weather"] in ["storm", "rain", "snow"]:
        pet["mood"] = "sad"
    else:
        pet["mood"] = "happy"
        
    # 4. Update thank_you_cycles
    if state.get("thank_you_cycles", 0) > 0:
        state["thank_you_cycles"] -= 1
        if state["thank_you_cycles"] == 0:
            state["recent_action"] = None
            state["recent_user"] = None

    return state


# --- Dedicated Interaction Mutation Functions ---

import time

def _append_event(state, event_type, user, item=None):
    events = state.setdefault("recent_events", [])
    event = {
        "type": event_type,
        "user": user,
        "timestamp": time.time()
    }
    if item:
        event["item"] = item
        
    events.insert(0, event)
    # Keep only the 10 most recent
    state["recent_events"] = events[:10]

def _increase_user_friendship(state, user, amount):
    if user == "guest" or not user:
        return
    f_log = state.setdefault("friendship_log", {})
    f_log[user] = f_log.get(user, 0) + amount

def apply_pet_interaction(state, user):
    """Increase friendship and set recent action for a pet command."""
    pet = state.setdefault("pet", {})
    pet["friendship"] = min(100, pet.get("friendship", 0) + 10)
    pet["mood"] = "happy"
    
    state["recent_action"] = "pet"
    state["recent_user"] = user
    state["thank_you_cycles"] = 2
    
    _increase_user_friendship(state, user, 2)
    _append_event(state, "pet", user)

def _get_manifest():
    import yaml
    from worldpack_loader import load_manifest
    worldpack_path = "worldpacks/default"
    if os.path.exists("world.config.yml"):
        try:
            with open("world.config.yml", "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                worldpack_path = cfg.get("worldpack", worldpack_path)
        except Exception:
            pass
    try:
        return load_manifest(worldpack_path)
    except Exception:
        return {}

def apply_gift_interaction(state, gift_type, user):
    """Apply a gift interaction to state using manifest logic."""
    state["recent_action"] = f"gift_{gift_type}"
    state["recent_user"] = user
    state["thank_you_cycles"] = 2
    state["last_gift"] = gift_type
    state["gifted_by"] = user
    
    pet = state.setdefault("pet", {})
    manifest = _get_manifest()
    from worldpack_loader import get_gift_effects
    effects = get_gift_effects(manifest, gift_type) or {}
    
    # Apply stats generically from manifest
    friendship_gain = effects.get("friendship", 0)
    
    hunger_delta = effects.get("hunger", 0)
    if hunger_delta:
        pet["hunger"] = max(0, min(100, pet.get("hunger", 0) + hunger_delta))
        
    energy_delta = effects.get("energy", 0)
    if energy_delta:
        pet["energy"] = max(0, min(100, pet.get("energy", 100) + energy_delta))
        
    mood_override = effects.get("mood")
    if mood_override:
        pet["mood"] = mood_override

    pet["friendship"] = min(100, pet.get("friendship", 0) + friendship_gain)
    _increase_user_friendship(state, user, friendship_gain)
    _append_event(state, "gift", user, item=gift_type)

def apply_weather_override(state, weather, user="owner"):
    """Force weather override."""
    if weather in ["clear", "rain", "storm", "snow"]:
        state["weather"] = weather
        
        pet = state.setdefault("pet", {})
        if weather in ["storm", "rain", "snow"]:
            if pet.get("mood") not in ["hungry", "sleepy"]:
                pet["mood"] = "sad"
        else:
            if pet.get("mood") == "sad":
                pet["mood"] = "happy"
                
        _append_event(state, "weather", user, item=weather)
