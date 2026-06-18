import unittest
from interaction_policy import RepositoryPolicy
from github_event_models import CommentEvent, ManualEvent
from event_processor import process_comment

class TestInteractionPolicy(unittest.TestCase):

    def test_correct_issue_number(self):
        event = CommentEvent("alice", "/pet", issue_number=1)
        result = RepositoryPolicy.validate(event)
        self.assertTrue(result["allowed"])

    def test_wrong_issue_number(self):
        event = CommentEvent("alice", "/pet", issue_number=2)
        result = RepositoryPolicy.validate(event)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "wrong_issue")

    def test_manual_event_bypasses_issue_check(self):
        # A ManualEvent isn't a CommentEvent, so it shouldn't be blocked by issue number
        event = ManualEvent("bob", "/pet")
        result = RepositoryPolicy.validate(event)
        self.assertTrue(result["allowed"])

    def test_valid_command_prefix(self):
        event = CommentEvent("alice", "/gift fish", issue_number=1)
        result = RepositoryPolicy.validate(event)
        self.assertTrue(result["allowed"])

    def test_invalid_command_prefix(self):
        event = CommentEvent("alice", "I like this project!", issue_number=1)
        result = RepositoryPolicy.validate(event)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "invalid_prefix")

    def test_overly_long_command(self):
        long_cmd = "/" + "a" * 100
        event = CommentEvent("alice", long_cmd, issue_number=1)
        result = RepositoryPolicy.validate(event)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "too_long")

    def test_invalid_characters(self):
        # Using a character like < which is not in a-zA-Z0-9 /
        event = CommentEvent("alice", "/gift <script>", issue_number=1)
        result = RepositoryPolicy.validate(event)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "invalid_characters")
        
    def test_processor_integration(self):
        # Test wrong issue via the pipeline helper
        result = process_comment("/pet", "alice", False, issue_number=99)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "wrong_issue")

if __name__ == '__main__':
    unittest.main()
