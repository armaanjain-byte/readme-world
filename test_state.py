import unittest
import os
import json
import artifact_manager
from state import (
    load_state,
    save_state,
    initialize_state,
    update_random_world_state,
    DEFAULT_STATE_FILE
)

STATE_FILE = artifact_manager.STATE_FILE

class TestStateManagement(unittest.TestCase):
    def setUp(self):
        # Clean up files before each test to ensure a clean state
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        if os.path.exists(DEFAULT_STATE_FILE):
            os.rename(DEFAULT_STATE_FILE, DEFAULT_STATE_FILE + ".bak")

        # Create a mock default_state for testing if needed
        self.mock_default = {
            "weather": "clear",
            "pet": {
                "species": "cat",
                "mood": "happy",
                "energy": 100,
                "hunger": 0,
                "friendship": 0
            },
            "recent_action": None,
            "recent_user": None,
            "thank_you_cycles": 0
        }
        with open(DEFAULT_STATE_FILE, "w") as f:
            json.dump(self.mock_default, f)

    def tearDown(self):
        # Clean up files after each test
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        if os.path.exists(DEFAULT_STATE_FILE):
            os.remove(DEFAULT_STATE_FILE)
        if os.path.exists(DEFAULT_STATE_FILE + ".bak"):
            os.rename(DEFAULT_STATE_FILE + ".bak", DEFAULT_STATE_FILE)

    def test_initialize_state_no_default(self):
        os.remove(DEFAULT_STATE_FILE) # remove the one created in setUp
        state = initialize_state()
        self.assertEqual(state["weather"], "clear")
        self.assertEqual(state["pet"]["species"], "cat")
        self.assertEqual(state["pet"]["energy"], 100)

    def test_initialize_state_with_default(self):
        default_state = {
            "weather": "rain",
            "pet": {"species": "dog", "mood": "happy", "energy": 50, "hunger": 10, "friendship": 5},
            "recent_action": None,
            "recent_user": None,
            "thank_you_cycles": 0
        }
        with open(DEFAULT_STATE_FILE, "w") as f:
            json.dump(default_state, f)
            
        state = initialize_state()
        self.assertEqual(state["weather"], "rain")
        self.assertEqual(state["pet"]["species"], "dog")

    def test_load_and_save_state(self):
        state = initialize_state()
        state["weather"] = "snow"
        save_state(state)
        
        self.assertTrue(os.path.exists(STATE_FILE))
        
        loaded_state = load_state()
        self.assertEqual(loaded_state["weather"], "snow")

    def test_load_corrupt_state(self):
        with open(STATE_FILE, "w") as f:
            f.write("invalid json {")
            
        # Should fallback to initialized state
        state = load_state()
        self.assertEqual(state["weather"], "clear")

    def test_update_random_world_state(self):
        state = initialize_state()
        
        # Test basic updates
        new_state = update_random_world_state(state)
        self.assertIn(new_state["weather"], ["clear", "rain", "cloudy", "storm", "snow"])
        self.assertEqual(new_state["pet"]["hunger"], 5)
        self.assertEqual(new_state["pet"]["energy"], 95)
        
    def test_mood_changes_hungry(self):
        state = initialize_state()
        state["pet"]["hunger"] = 80
        new_state = update_random_world_state(state)
        # 80 + 5 = 85 -> >80 is hungry
        self.assertEqual(new_state["pet"]["mood"], "hungry")

    def test_mood_changes_sleepy(self):
        state = initialize_state()
        state["pet"]["energy"] = 20
        new_state = update_random_world_state(state)
        # 20 - 5 = 15 -> <20 is sleepy
        self.assertEqual(new_state["pet"]["mood"], "sleepy")

    def test_mood_changes_sad_weather(self):
        state = initialize_state()
        state["weather"] = "storm"
        # override random weather to ensure it stays bad for the test
        # or we just monkeypatch the random, but since we are passing state, let's just make
        # sure we can reach sad state. Actually update_random_world_state will randomly assign weather.
        # Let's mock random
        import random
        original_random = random.random
        random.random = lambda: 0.999 # snow (0.99 - 1.0)
        try:
            new_state = update_random_world_state(state)
            self.assertEqual(new_state["weather"], "snow")
            self.assertEqual(new_state["pet"]["mood"], "sad")
        finally:
            random.random = original_random

    def test_boundaries(self):
        state = initialize_state()
        state["pet"]["hunger"] = 98
        state["pet"]["energy"] = 2
        new_state = update_random_world_state(state)
        
        self.assertEqual(new_state["pet"]["hunger"], 100)
        self.assertEqual(new_state["pet"]["energy"], 0)

    def test_thank_you_cycles(self):
        state = initialize_state()
        state["thank_you_cycles"] = 2
        state["recent_action"] = "feed"
        state["recent_user"] = "user123"
        
        state = update_random_world_state(state)
        self.assertEqual(state["thank_you_cycles"], 1)
        self.assertEqual(state["recent_action"], "feed")
        
        state = update_random_world_state(state)
        self.assertEqual(state["thank_you_cycles"], 0)
        self.assertIsNone(state["recent_action"])
        self.assertIsNone(state["recent_user"])

if __name__ == "__main__":
    unittest.main()
