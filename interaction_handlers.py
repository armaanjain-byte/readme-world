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
    VALID_GIFTS = ["wool", "fish", "bone", "ball"]
    
    def validate(self, context: CommandContext) -> tuple[bool, str]:
        if len(context.args) < 2:
            return False, "Missing gift item. Usage: /gift [wool|fish|bone|ball]"
        
        gift = context.args[1].lower()
        if gift not in self.VALID_GIFTS:
            return False, f"Invalid gift. Must be one of {', '.join(self.VALID_GIFTS)}."
            
        return True, ""
        
    def execute(self, state, context: CommandContext) -> str:
        gift = context.args[1].lower()
        state_module.apply_gift_interaction(state, gift, context.username)
        return f"You gifted a {gift}!"

class WeatherCommand(Command):
    """Handles the /weather command (Owner only)."""
    VALID_WEATHER = ["clear", "rain", "storm", "snow"]
    
    def validate(self, context: CommandContext) -> tuple[bool, str]:
        if not context.is_owner:
            return False, "Only the owner can change the weather."
            
        if len(context.args) < 2:
            return False, "Missing weather state. Usage: /weather [clear|rain|storm|snow]"
            
        weather = context.args[1].lower()
        if weather not in self.VALID_WEATHER:
            return False, f"Invalid weather. Must be one of {', '.join(self.VALID_WEATHER)}."
            
        return True, ""
        
    def execute(self, state, context: CommandContext) -> str:
        weather = context.args[1].lower()
        state_module.apply_weather_override(state, weather)
        return f"Weather magically changed to {weather}."
