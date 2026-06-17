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
        self.assertEqual(self.state["pet"]["friendship"], 10) # 0 + 10
        self.assertEqual(self.state["pet"]["mood"], "happy")
        self.assertEqual(self.state["friendship_log"]["octocat"], 2) # Base score for pet

    def test_cat_gift_reactions(self):
        self.state["pet"]["species"] = "cat"
        self.state["pet"]["hunger"] = 100
        
        # Give Fish
        success, msg = parse_and_execute("/gift fish", "alice", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["last_gift"], "fish")
        self.assertEqual(self.state["gifted_by"], "alice")
        self.assertEqual(self.state["pet"]["hunger"], 80)
        self.assertEqual(self.state["pet"]["friendship"], 10)
        self.assertEqual(self.state["friendship_log"]["alice"], 10)

        # Give Wool
        self.state["pet"]["energy"] = 100
        success, msg = parse_and_execute("/gift wool", "bob", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["pet"]["energy"], 95)
        self.assertEqual(self.state["pet"]["friendship"], 15) # 10 + 5
        self.assertEqual(self.state["friendship_log"]["bob"], 5)

        # Give Bone (minimal effect for cat)
        success, msg = parse_and_execute("/gift bone", "alice", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["pet"]["friendship"], 16) # 15 + 1
        self.assertEqual(self.state["friendship_log"]["alice"], 11) # 10 + 1

    def test_dog_gift_reactions(self):
        self.state["pet"]["species"] = "dog"
        
        # Give Bone
        success, msg = parse_and_execute("/gift bone", "charlie", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["last_gift"], "bone")
        self.assertEqual(self.state["gifted_by"], "charlie")
        self.assertEqual(self.state["pet"]["friendship"], 10)
        self.assertEqual(self.state["pet"]["mood"], "happy")
        self.assertEqual(self.state["friendship_log"]["charlie"], 10)

        # Give Ball
        self.state["pet"]["energy"] = 100
        success, msg = parse_and_execute("/gift ball", "charlie", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["pet"]["energy"], 90)
        self.assertEqual(self.state["pet"]["friendship"], 18) # 10 + 8
        self.assertEqual(self.state["friendship_log"]["charlie"], 18) # 10 + 8

        # Give Wool (minimal effect for dog)
        success, msg = parse_and_execute("/gift wool", "diana", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["pet"]["friendship"], 19) # 18 + 1
        self.assertEqual(self.state["friendship_log"]["diana"], 1)

    def test_guest_friendship_ignored(self):
        success, msg = parse_and_execute("/pet", "guest", False, self.state, self.registry)
        self.assertTrue(success)
        # Guest shouldn't appear in friendship_log
        self.assertNotIn("guest", self.state.get("friendship_log", {}))

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
