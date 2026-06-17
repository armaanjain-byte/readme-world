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
            "thank_you_cycles": 0,
            "last_gift": None,
            "gifted_by": None,
            "friendship_log": {}
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
    
    _increase_user_friendship(state, user, 2) # Arbitrary base score for petting

def apply_gift_interaction(state, gift_type, user):
    """Apply a gift interaction to state using species-aware logic."""
    state["recent_action"] = f"gift_{gift_type}"
    state["recent_user"] = user
    state["thank_you_cycles"] = 2
    state["last_gift"] = gift_type
    state["gifted_by"] = user
    
    pet = state.setdefault("pet", {})
    species = pet.get("species", "cat")
    friendship_gain = 0
    
    if species == "cat":
        if gift_type == "fish":
            pet["hunger"] = max(0, pet.get("hunger", 0) - 20)
            friendship_gain = 10
            pet["mood"] = "happy"
        elif gift_type == "wool":
            pet["energy"] = max(0, pet.get("energy", 100) - 5)
            friendship_gain = 5
            pet["mood"] = "happy"
        elif gift_type == "ball":
            pet["energy"] = max(0, pet.get("energy", 100) - 10)
            friendship_gain = 3
        elif gift_type == "bone":
            friendship_gain = 1 # minimal effect
            
    elif species == "dog":
        if gift_type == "bone":
            friendship_gain = 10
            pet["mood"] = "happy"
        elif gift_type == "ball":
            pet["energy"] = max(0, pet.get("energy", 100) - 10)
            friendship_gain = 8
        elif gift_type == "fish":
            friendship_gain = 3
        elif gift_type == "wool":
            friendship_gain = 1 # minimal effect

    pet["friendship"] = min(100, pet.get("friendship", 0) + friendship_gain)
    _increase_user_friendship(state, user, friendship_gain)

def apply_weather_override(state, weather):
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
