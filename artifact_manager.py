import os
import json

OUTPUT_DIR = "generated"
STATE_FILE = os.path.join(OUTPUT_DIR, "state.json")
OUTPUT_SVG_FILE = os.path.join(OUTPUT_DIR, "world.svg")
DEFAULT_STATE_FILE = "default_state.json"

def _ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_state(initialize_func):
    """
    Attempts to read state from the generated artifacts representation (generated/state.json).
    If it doesn't exist, is malformed, or corrupted, it falls back to the initialize_func
    (which reads from default_state.json).
    """
    _ensure_output_dir()
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return initialize_func()

def save_state(state):
    """Saves the active state to generated/state.json"""
    _ensure_output_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def save_world_svg(content):
    """Saves the generated SVG to generated/world.svg"""
    _ensure_output_dir()
    with open(OUTPUT_SVG_FILE, "w", encoding="utf-8") as f:
        f.write(content)
