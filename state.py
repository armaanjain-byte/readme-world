import json
import os
import random

STATE_FILE = "state.json"
DEFAULT_STATE_FILE = "default_state.json"

WEATHER_PROBS = {
    "clear": 0.70,
    "rain": 0.15,
    "cloudy": 0.10,
    "storm": 0.04,
    "snow": 0.01
}

def load_state():
    """Load state from state.json, fallback to initialization if missing/corrupt."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return initialize_state()

def save_state(state):
    """Save the current state to state.json."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def initialize_state():
    """Initialize state from default_state.json, or fallback to hardcoded defaults."""
    if os.path.exists(DEFAULT_STATE_FILE):
        with open(DEFAULT_STATE_FILE, "r") as f:
            state = json.load(f)
    else:
        state = {
            "weather": "clear",
            "pet": {
                "species": "cat",
                "mood": "happy",
                "energy": 100,
                "hunger": 0,
                "friendship": 0
            },
            "recent_action": None,
            "recent_user": None,
            "thank_you_cycles": 0
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
