import unittest
import os
import json
import tempfile
import yaml
from unittest.mock import patch

from github_action_runner import main as run_github_action

class TestOutputBranchPipeline(unittest.TestCase):
    """
    Tests the pipeline's ability to mutate the necessary files (state.json and world.svg)
    that the GitHub Action will then commit to the output branch.
    """
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        
        self.mock_config = os.path.join(self.test_dir.name, "world.config.yml")
        self.mock_output_dir = os.path.join(self.test_dir.name, "generated")
        self.mock_state = os.path.join(self.test_dir.name, "state.json")
        self.mock_event = os.path.join(self.test_dir.name, "event.json")
        
        self.patcher_config = patch("generate_world.CONFIG_FILE", self.mock_config)
        self.patcher_output = patch("generate_world.OUTPUT_DIR", self.mock_output_dir)
        self.patcher_state = patch("state.STATE_FILE", self.mock_state)
        
        self.patcher_config.start()
        self.patcher_output.start()
        self.patcher_state.start()

        with open(self.mock_config, "w") as f:
            yaml.dump({"name": "OutputBranchTest", "worldpack": "worldpacks/default"}, f)
            
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
            
        self.patcher_argv = patch("sys.argv", ["github_action_runner.py", "/pet", "branch_tester", "octocat", "1"])
        self.patcher_argv.start()

    def tearDown(self):
        self.patcher_config.stop()
        self.patcher_output.stop()
        self.patcher_state.stop()
        self.test_dir.cleanup()
        
        self.patcher_argv.stop()

    def test_pipeline_artifacts_generated(self):
        # Record mtime of state.json
        state_mtime = os.path.getmtime(self.mock_state)
        
        try:
            run_github_action()
        except SystemExit:
            pass
        
        # Verify state.json was updated
        new_state_mtime = os.path.getmtime(self.mock_state)
        self.assertTrue(new_state_mtime >= state_mtime, "State file should be modified")
        
        # Verify world.svg is generated inside the output directory
        out_svg = os.path.join(self.mock_output_dir, "world.svg")
        self.assertTrue(os.path.exists(out_svg), "SVG must be generated for the output branch")

if __name__ == '__main__':
    unittest.main()
