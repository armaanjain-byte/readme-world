import sys
import argparse
from state import load_state, save_state
from command_parser import CommandRegistry, parse_and_execute
from interaction_handlers import PetCommand, GiftCommand, WeatherCommand

def setup_registry():
    registry = CommandRegistry()
    registry.register("pet", PetCommand)
    registry.register("gift", GiftCommand)
    registry.register("weather", WeatherCommand)
    return registry

def main():
    parser = argparse.ArgumentParser(description="Process readme-world interaction commands.")
    parser.add_argument("command_string", type=str, help='The command string, e.g. "/gift wool octocat"')
    parser.add_argument("--owner", action="store_true", help="Set this flag if the executor is the repository owner.")
    
    args = parser.parse_args()

    raw_cmd = args.command_string.strip()
    parts = raw_cmd.split()
    username = "guest"
    
    # Heuristic to extract username from the trailing arg for public commands
    # /pet [username]
    # /gift [item] [username]
    if parts[0].startswith("/pet") and len(parts) == 2:
        username = parts[1]
        raw_cmd = parts[0]
    elif parts[0].startswith("/gift") and len(parts) >= 3:
        username = parts[2]
        raw_cmd = f"{parts[0]} {parts[1]}"
    # Weather is owner-only, usually won't have a trailing username
    
    registry = setup_registry()
    state = load_state()
    
    success, msg = parse_and_execute(raw_cmd, username, args.owner, state, registry)
    
    if success:
        save_state(state)
        print(f"Success: {msg}")
    else:
        print(f"Error: {msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()
