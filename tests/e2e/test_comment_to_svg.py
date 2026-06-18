import unittest
import os
import json
import tempfile
import yaml
from unittest.mock import patch

from github_action_runner import main as run_github_action
import state

class TestCommentToSvgE2E(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Mock paths
        self.mock_config = os.path.join(self.test_dir.name, "world.config.yml")
        self.mock_output_dir = os.path.join(self.test_dir.name, "generated")
        self.mock_state = os.path.join(self.test_dir.name, "state.json")
        self.mock_default_state = os.path.join(self.test_dir.name, "default_state.json")
        self.mock_event = os.path.join(self.test_dir.name, "event.json")
        
        self.patcher_config = patch("generate_world.CONFIG_FILE", self.mock_config)
        self.patcher_output = patch("generate_world.OUTPUT_DIR", self.mock_output_dir)
        self.patcher_state = patch("state.STATE_FILE", self.mock_state)
        self.patcher_default_state = patch("state.DEFAULT_STATE_FILE", self.mock_default_state)
        
        self.patcher_config.start()
        self.patcher_output.start()
        self.patcher_state.start()
        self.patcher_default_state.start()

        # Create basic config
        with open(self.mock_config, "w") as f:
            yaml.dump({"name": "TestUser", "worldpack": "worldpacks/default"}, f)
            
        # Create minimal state
        self.default_state = {
            "weather": "clear",
            "pet": {"mood": "happy", "friendship": 0, "energy": 100, "hunger": 50},
            "recent_action": None,
            "recent_user": None,
            "recent_events": [],
            "friendship_log": {},
            "cooldowns": {}
        }
        os.makedirs(self.mock_output_dir, exist_ok=True)
        with open(self.mock_state, "w") as f:
            json.dump(self.default_state, f)

    def tearDown(self):
        self.patcher_config.stop()
        self.patcher_output.stop()
        self.patcher_state.stop()
        self.patcher_default_state.stop()
        self.test_dir.cleanup()
        
        # Clean up env vars
        for key in ["GITHUB_EVENT_PATH", "GITHUB_REPOSITORY_OWNER"]:
            if key in os.environ:
                del os.environ[key]

    def _setup_event(self, body, user="alice", owner="octocat"):
        self.patcher_argv = patch("sys.argv", ["github_action_runner.py", body, user, owner, "1"])
        self.patcher_argv.start()
        
    def tearDown_event(self):
        if hasattr(self, 'patcher_argv'):
            self.patcher_argv.stop()

    def test_scenario_1_pet_comment(self):
        # Scenario 1: /pet alice
        self._setup_event("/pet", user="alice")
        
        # Run action
        try:
            run_github_action()
        except SystemExit:
            pass
        
        # Expected: state updates, friendship increases, SVG regenerated
        with open(self.mock_state, "r") as f:
            updated_state = json.load(f)
            
        self.assertEqual(updated_state["recent_action"], "pet")
        self.assertEqual(updated_state["pet"]["friendship"], 10)
        self.assertIn("alice", updated_state["friendship_log"])
        
        out_svg = os.path.join(self.mock_output_dir, "world.svg")
        self.assertTrue(os.path.exists(out_svg))
        with open(out_svg, "r") as f:
            svg_content = f.read()
            self.assertIn("alice", svg_content) # Leaderboard
        self.tearDown_event()

    def test_scenario_2_gift_fish_comment(self):
        # Scenario 2: /gift fish alice
        self._setup_event("/gift fish", user="alice")
        
        try:
            run_github_action()
        except SystemExit:
            pass
        
        with open(self.mock_state, "r") as f:
            updated_state = json.load(f)
            
        self.assertEqual(updated_state["last_gift"], "fish")
        self.assertEqual(updated_state["gifted_by"], "alice")
        # Friendship increases from 0 -> 10 for default fish
        self.assertEqual(updated_state["pet"]["friendship"], 10)
        
        out_svg = os.path.join(self.mock_output_dir, "world.svg")
        self.assertTrue(os.path.exists(out_svg))

    def test_scenario_3_unauthorized_weather(self):
        # Scenario 3: Unauthorized weather override
        self._setup_event("/weather storm", user="alice", owner="octocat") # owner is octocat
        
        try:
            run_github_action()
        except SystemExit:
            pass
        
        with open(self.mock_state, "r") as f:
            updated_state = json.load(f)
            
        # Expected: state unchanged
        self.assertEqual(updated_state["weather"], "clear")
        self.assertEqual(updated_state["recent_action"], None) # Should not process
        self.tearDown_event()

    def test_scenario_4_corrupted_state_recovery(self):
        # Scenario 4: Corrupted state.json
        # Also need a fallback default_state
        with open(self.mock_default_state, "w") as f:
            json.dump({
                "weather": "clear",
                "pet": {"mood": "happy", "friendship": 0, "energy": 100, "hunger": 50},
                "recent_action": None,
                "recent_user": None,
                "recent_events": [],
                "friendship_log": {},
                "cooldowns": {}
            }, f)
            
        with open(self.mock_state, "w") as f:
            f.write("{ invalid json")
            
        self._setup_event("/pet", user="bob")
        
        # It should catch JSON decode error, fallback to default, and apply the pet command
        try:
            run_github_action()
        except SystemExit:
            pass
        
        with open(self.mock_state, "r") as f:
            recovered_state = json.load(f)
            
        self.assertEqual(recovered_state["recent_user"], "bob")
        self.assertEqual(recovered_state["pet"]["friendship"], 10)
        self.tearDown_event()

if __name__ == '__main__':
    unittest.main()
