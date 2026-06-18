from command_parser import Command, CommandContext
import state as state_module

class PetCommand(Command):
    """Handles the /pet command."""
    def validate(self, context: CommandContext) -> tuple[bool, str]:
        return True, ""
        
    def execute(self, state, context: CommandContext) -> str:
        state_module.apply_pet_interaction(state, context.username)
        return "You petted the animal!"

class GiftCommand(Command):
    """Handles the /gift command."""
    
    def validate(self, context: CommandContext) -> tuple[bool, str]:
        manifest = state_module._get_manifest()
        from worldpack_loader import get_valid_gifts
        valid_gifts = get_valid_gifts(manifest)
        
        if len(context.args) < 2:
            return False, f"Missing gift item. Usage: /gift [{'|'.join(valid_gifts)}]"
        
        gift = context.args[1].lower()
        if gift not in valid_gifts:
            return False, f"Invalid gift. Must be one of {', '.join(valid_gifts)}."
            
        return True, ""
        
    def execute(self, state, context: CommandContext) -> str:
        gift = context.args[1].lower()
        state_module.apply_gift_interaction(state, gift, context.username)
        return f"You gifted a {gift}!"

class WeatherCommand(Command):
    """Handles the /weather command (Owner only)."""
    
    def validate(self, context: CommandContext) -> tuple[bool, str]:
        if not context.is_owner:
            return False, "Only the owner can change the weather."
            
        manifest = state_module._get_manifest()
        from worldpack_loader import get_available_weather
        valid_weather = get_available_weather(manifest)
            
        if len(context.args) < 2:
            return False, f"Missing weather state. Usage: /weather [{'|'.join(valid_weather)}]"
            
        weather = context.args[1].lower()
        if weather not in valid_weather:
            return False, f"Invalid weather. Must be one of {', '.join(valid_weather)}."
            
        return True, ""
        
    def execute(self, state, context: CommandContext) -> str:
        weather = context.args[1].lower()
        state_module.apply_weather_override(state, weather, context.username)
        return f"Weather magically changed to {weather}."
