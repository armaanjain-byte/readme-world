import time

class Event:
    """Base model for an interaction event."""
    def __init__(self, username: str, command_text: str, is_owner: bool = False):
        self.username = username
        self.command_text = command_text.strip()
        self.is_owner = is_owner
        self.timestamp = time.time()

class CommentEvent(Event):
    """Represents an event triggered by an issue comment."""
    pass

class ManualEvent(Event):
    """Represents an event triggered manually (e.g. from CLI)."""
    pass
