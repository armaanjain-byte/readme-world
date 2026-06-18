import unittest
import os
import json
import tempfile
import yaml
from unittest.mock import patch

import generate_world
import state

class TestRenderer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Mock paths
        self.mock_config = os.path.join(self.test_dir.name, "world.config.yml")
        self.mock_output_dir = os.path.join(self.test_dir.name, "generated")
        self.mock_state = os.path.join(self.test_dir.name, "state.json")
        
        self.patcher_config = patch("generate_world.CONFIG_FILE", self.mock_config)
        self.patcher_output = patch("generate_world.OUTPUT_DIR", self.mock_output_dir)
        self.patcher_state = patch("state.STATE_FILE", self.mock_state)
        
        self.patcher_config.start()
        self.patcher_output.start()
        self.patcher_state.start()

        # Create basic config
        with open(self.mock_config, "w") as f:
            yaml.dump({"name": "TestUser", "worldpack": "worldpacks/default"}, f)
            
        # Create minimal state
        self.default_state = {
            "weather": "clear",
            "pet": {"mood": "happy", "friendship": 10, "energy": 100, "hunger": 0},
            "recent_action": None,
            "recent_user": None,
            "recent_events": [],
            "friendship_log": {"alice": 5}
        }
        os.makedirs(self.mock_output_dir, exist_ok=True)
        with open(self.mock_state, "w") as f:
            json.dump(self.default_state, f)

    def tearDown(self):
        self.patcher_config.stop()
        self.patcher_output.stop()
        self.patcher_state.stop()
        self.test_dir.cleanup()

    def test_css_generation(self):
        css = generate_world.generate_css()
        self.assertIn("<style>", css)
        self.assertIn("anim-bounce", css)
        self.assertIn("</style>", css)

    def test_render_ui_happy_path(self):
        ui_svg = generate_world.render_ui("TestUser", "clear", self.default_state)
        self.assertIn("Mood: Happy", ui_svg)
        self.assertIn("alice (5)", ui_svg) # Leaderboard

    def test_generate_svg_end_to_end(self):
        # We assume worldpacks/default exists in the repo since we run from root
        generate_world.generate_svg()
        
        out_file = os.path.join(self.mock_output_dir, "world.svg")
        self.assertTrue(os.path.exists(out_file))
        
        with open(out_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("<svg", content)
        self.assertIn("</svg>", content)
        self.assertIn('<rect id="sky"', content) # Background

    def test_generate_svg_sad_mood_conversion(self):
        self.default_state["pet"]["mood"] = "sad"
        with open(self.mock_state, "w") as f:
            json.dump(self.default_state, f)
            
        generate_world.generate_svg()
        
        out_file = os.path.join(self.mock_output_dir, "world.svg")
        with open(out_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # "sad" should map to "scared" behind the scenes for the sprite, 
        # but the UI might show 'Scared' because of the conversion in generate_world
        self.assertIn("Sad", content)

    @patch("generate_world.load_manifest")
    def test_generate_svg_missing_worldpack(self, mock_load):
        # If manifest throws error (simulating bad path or corrupt file)
        mock_load.side_effect = FileNotFoundError("Manifest not found")
        
        with self.assertRaises(FileNotFoundError):
            generate_world.generate_svg()

if __name__ == '__main__':
    unittest.main()
