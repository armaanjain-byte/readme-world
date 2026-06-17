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
    def __init__(self, username: str, command_text: str, is_owner: bool = False, issue_number: int = None):
        super().__init__(username, command_text, is_owner)
        self.issue_number = issue_number

class ManualEvent(Event):
    """Represents an event triggered manually (e.g. from CLI)."""
    pass
