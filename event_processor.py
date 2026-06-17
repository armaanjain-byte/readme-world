from github_event_models import Event, CommentEvent
from command_parser import CommandRegistry, parse_and_execute
from interaction_handlers import PetCommand, GiftCommand, WeatherCommand
from state import load_state, save_state
from generate_world import generate_svg

# We initialize a global registry for the event processor to use
def setup_registry():
    registry = CommandRegistry()
    registry.register("pet", PetCommand)
    registry.register("gift", GiftCommand)
    registry.register("weather", WeatherCommand)
    return registry

_REGISTRY = setup_registry()

def process_event(event: Event) -> dict:
    """Processes an event, executes the command, saves state, and regenerates SVG."""
    if not event.command_text or not event.command_text.startswith("/"):
        return {
            "success": False,
            "message": "Not a command.",
            "command": None,
            "user": event.username
        }
        
    state = load_state()
    
    # We parse the command. Note: parse_and_execute takes (raw_string, username, is_owner, state, registry)
    success, msg = parse_and_execute(
        raw_string=event.command_text,
        username=event.username,
        is_owner=event.is_owner,
        state=state,
        registry=_REGISTRY
    )
    
    cmd_name = event.command_text.split()[0].replace("/", "") if event.command_text else None
    
    if not success and msg in ["cooldown", "rate_limit"]:
        return {
            "success": False,
            "reason": msg,
            "command": cmd_name,
            "user": event.username
        }
    
    result = {
        "success": success,
        "message": msg,
        "command": cmd_name,
        "user": event.username
    }
    
    if success:
        # Commit state updates
        save_state(state)
        # Regenerate the visualization immediately
        try:
            generate_svg()
        except Exception as e:
            result["success"] = False
            result["message"] = f"Command succeeded but SVG generation failed: {e}"
            
    return result

def process_comment(comment_body: str, username: str, is_owner: bool = False) -> dict:
    """Helper method to construct a CommentEvent and process it."""
    event = CommentEvent(username, comment_body, is_owner)
    return process_event(event)
