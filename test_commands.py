import unittest
import os
import json
from state import initialize_state
from command_parser import CommandContext, CommandRegistry, parse_and_execute
from interaction_handlers import PetCommand, GiftCommand, WeatherCommand

class TestInteractionEngine(unittest.TestCase):
    def setUp(self):
        self.registry = CommandRegistry()
        self.registry.register("pet", PetCommand)
        self.registry.register("gift", GiftCommand)
        self.registry.register("weather", WeatherCommand)
        self.state = initialize_state()
        
    def test_valid_pet_command(self):
        success, msg = parse_and_execute("/pet", "octocat", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["recent_action"], "pet")
        self.assertEqual(self.state["recent_user"], "octocat")
        self.assertEqual(self.state["pet"]["friendship"], 10)
        self.assertEqual(self.state["pet"]["mood"], "happy")

    def test_valid_gift_command(self):
        self.state["pet"]["hunger"] = 100
        success, msg = parse_and_execute("/gift fish", "alice", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["recent_action"], "gift_fish")
        self.assertEqual(self.state["recent_user"], "alice")
        self.assertEqual(self.state["pet"]["hunger"], 70)  # 100 - 30
        self.assertEqual(self.state["pet"]["mood"], "happy")

    def test_invalid_gift_command(self):
        success, msg = parse_and_execute("/gift computer", "alice", False, self.state, self.registry)
        self.assertFalse(success)
        self.assertIn("Invalid gift", msg)

    def test_missing_gift_arg(self):
        success, msg = parse_and_execute("/gift", "alice", False, self.state, self.registry)
        self.assertFalse(success)
        self.assertIn("Missing gift item", msg)

    def test_valid_weather_command(self):
        success, msg = parse_and_execute("/weather storm", "owner_name", True, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["weather"], "storm")
        self.assertEqual(self.state["pet"]["mood"], "sad")

    def test_invalid_weather_arg(self):
        success, msg = parse_and_execute("/weather apocalypse", "owner_name", True, self.state, self.registry)
        self.assertFalse(success)
        self.assertIn("Invalid weather", msg)

    def test_unauthorized_weather_command(self):
        success, msg = parse_and_execute("/weather clear", "guest", False, self.state, self.registry)
        self.assertFalse(success)
        self.assertIn("Only the owner", msg)

    def test_unknown_command(self):
        success, msg = parse_and_execute("/dance", "bob", False, self.state, self.registry)
        self.assertFalse(success)
        self.assertEqual("Command not found.", msg)

if __name__ == '__main__':
    unittest.main()
