from security import sanitize_username
from rate_limiter import check_rate_limits

class CommandContext:
    def __init__(self, raw_string, username, is_owner):
        self.raw_string = raw_string
        self.username = sanitize_username(username)
        self.is_owner = is_owner
        self.args = raw_string.strip().split()

class Command:
    def validate(self, context: CommandContext) -> tuple[bool, str]:
        """Validate command arguments and authorization."""
        raise NotImplementedError
        
    def execute(self, state, context: CommandContext) -> str:
        """Execute the command and mutate state."""
        raise NotImplementedError

class CommandRegistry:
    def __init__(self):
        self._commands = {}
        
    def register(self, prefix, command_cls):
        self._commands[prefix] = command_cls()
        
    def get_command(self, context: CommandContext) -> Command:
        if not context.args:
            return None
            
        cmd_str = context.args[0].lower()
        if cmd_str.startswith("/"):
            cmd_str = cmd_str[1:]
            
        return self._commands.get(cmd_str)

def parse_and_execute(raw_string, username, is_owner, state, registry):
    """Parses a command string, validates it, checks rate limits, and executes it."""
    context = CommandContext(raw_string, username, is_owner)
    cmd = registry.get_command(context)
    
    if not cmd:
        return False, "Command not found."
        
    is_valid, err_msg = cmd.validate(context)
    if not is_valid:
        return False, err_msg
        
    # Get command type for rate limiting
    cmd_type = context.args[0].lower().replace("/", "")
    
    # Check rate limits
    allowed, limit_reason = check_rate_limits(state, context.username, cmd_type, context.is_owner)
    if not allowed:
        # Return the specific limit_reason ("cooldown" or "rate_limit")
        return False, limit_reason
        
    result_msg = cmd.execute(state, context)
    return True, result_msg
