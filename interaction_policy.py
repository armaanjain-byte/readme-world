import re
from github_event_models import Event, CommentEvent

class RepositoryPolicy:
    INTERACTION_ISSUE = 1
    MAX_COMMAND_LENGTH = 100
    ALLOWED_CHARS_PATTERN = re.compile(r'^[a-zA-Z0-9 /]+$')

    @classmethod
    def validate(cls, event: Event) -> dict:
        """
        Validates an event against the repository interaction policy.
        Returns a dict: {"allowed": bool, "reason": str}
        """
        # 1. Accepted Source
        if isinstance(event, CommentEvent):
            if event.issue_number != cls.INTERACTION_ISSUE:
                return {"allowed": False, "reason": "wrong_issue"}
                
        # 2. Command Prefix Validation
        if not event.command_text or not event.command_text.startswith("/"):
            return {"allowed": False, "reason": "invalid_prefix"}
            
        # 3. Maximum Command Length
        if len(event.command_text) > cls.MAX_COMMAND_LENGTH:
            return {"allowed": False, "reason": "too_long"}
            
        # 4. Allowed Command Characters
        if not cls.ALLOWED_CHARS_PATTERN.match(event.command_text):
            return {"allowed": False, "reason": "invalid_characters"}
            
        return {"allowed": True, "reason": ""}
