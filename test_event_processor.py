import unittest
import os
import json
from state import initialize_state, save_state
from event_processor import process_comment

class TestEventProcessor(unittest.TestCase):
    def setUp(self):
        # Reset state to default before each test
        state = initialize_state()
        save_state(state)
        
    def test_successful_pet_comment(self):
        result = process_comment("/pet", "testuser")
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "pet")
        self.assertEqual(result["user"], "testuser")
        
        # Verify state mutated
        with open("state.json", "r") as f:
            state = json.load(f)
        self.assertEqual(state["recent_action"], "pet")
        self.assertEqual(state["recent_user"], "testuser")
        
        # Verify SVG generated
        self.assertTrue(os.path.exists("world.svg"))

    def test_invalid_command_comment(self):
        result = process_comment("hello world", "testuser")
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Not a command.")

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
        with open("state.json", "r") as f:
            state = json.load(f)
        self.assertEqual(state["weather"], "storm")
        
if __name__ == '__main__':
    unittest.main()
