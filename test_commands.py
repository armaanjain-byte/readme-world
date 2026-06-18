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

    def test_gift_reactions(self):
        self.state["pet"]["hunger"] = 100
        
        # Give Fish
        self.state["cooldowns"] = {}
        success, msg = parse_and_execute("/gift fish", "alice", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["last_gift"], "fish")
        self.assertEqual(self.state["gifted_by"], "alice")
        self.assertEqual(self.state["pet"]["hunger"], 80)
        self.assertEqual(self.state["pet"]["friendship"], 10)
        self.assertEqual(self.state["friendship_log"]["alice"], 10)

        # Give Wool
        self.state["pet"]["energy"] = 100
        self.state["cooldowns"] = {}
        success, msg = parse_and_execute("/gift wool", "bob", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["pet"]["energy"], 95)
        self.assertEqual(self.state["pet"]["friendship"], 15) # 10 + 5
        self.assertEqual(self.state["friendship_log"]["bob"], 5)

        # Give Bone (minimal effect for cat)
        self.state["cooldowns"] = {}
        success, msg = parse_and_execute("/gift bone", "alice", False, self.state, self.registry)
        self.assertTrue(success)
        self.assertEqual(self.state["pet"]["friendship"], 16) # 15 + 1
        self.assertEqual(self.state["friendship_log"]["alice"], 11) # 10 + 1


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

    def test_recent_events_tracking(self):
        # Fire 11 commands to test trimming to 10
        for i in range(11):
            parse_and_execute(f"/gift fish", f"user_{i}", False, self.state, self.registry)
            
        events = self.state["recent_events"]
        self.assertEqual(len(events), 10)
        
        # Most recent should be user_10
        self.assertEqual(events[0]["type"], "gift")
        self.assertEqual(events[0]["user"], "user_10")
        self.assertEqual(events[0]["item"], "fish")
        self.assertIn("timestamp", events[0])

if __name__ == '__main__':
    unittest.main()
