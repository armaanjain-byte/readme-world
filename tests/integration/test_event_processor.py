import unittest
import os
import json
import state
from event_processor import process_comment

class TestEventProcessor(unittest.TestCase):
    def setUp(self):
        # Reset state to default before each test
        self.state = state.initialize_state()
        state.save_state(self.state)
        
    def test_successful_pet_comment(self):
        result = process_comment("/pet", "testuser")
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "pet")
        self.assertEqual(result["user"], "testuser")
        
        # Verify state mutated
        with open(state.STATE_FILE, "r") as f:
            saved_state = json.load(f)
        self.assertEqual(saved_state["recent_action"], "pet")
        self.assertEqual(saved_state["recent_user"], "testuser")
        
        # Verify SVG generated
        self.assertTrue(os.path.exists("generated/world.svg"))

    def test_invalid_command_comment(self):
        result = process_comment("hello world", "testuser")
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "invalid_prefix")

    def test_unknown_slash_command(self):
        result = process_comment("/fly", "testuser")
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Command not found.")
        
    def test_unauthorized_weather_comment(self):
        result = process_comment("/weather storm", "testuser", is_owner=False)
        self.assertFalse(result["success"])
        self.assertIn("Only the owner", result["message"])

    def test_authorized_weather_comment(self):
        result = process_comment("/weather storm", "owner_name", is_owner=True)
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "weather")
        
        # Verify state mutated
        with open(state.STATE_FILE, "r") as f:
            saved_state = json.load(f)
        self.assertEqual(saved_state["weather"], "storm")
        
if __name__ == '__main__':
    unittest.main()
