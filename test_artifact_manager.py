import unittest
import os
import shutil
import artifact_manager

class TestArtifactManager(unittest.TestCase):
    def setUp(self):
        # Ensure clean state before each test
        if os.path.exists(artifact_manager.OUTPUT_DIR):
            shutil.rmtree(artifact_manager.OUTPUT_DIR)
            
    def tearDown(self):
        # Clean up after tests
        if os.path.exists(artifact_manager.OUTPUT_DIR):
            shutil.rmtree(artifact_manager.OUTPUT_DIR)

    def dummy_init(self):
        return {"weather": "test", "pet": {"mood": "happy"}}

    def test_missing_output_initialization(self):
        self.assertFalse(os.path.exists(artifact_manager.OUTPUT_DIR))
        
        state = artifact_manager.load_state(self.dummy_init)
        
        # It shouldn't create the directory just by loading if it falls back
        # Wait, the load_state explicitly calls _ensure_output_dir()
        self.assertTrue(os.path.exists(artifact_manager.OUTPUT_DIR))
        self.assertEqual(state["weather"], "test")

    def test_state_persistence(self):
        state = {"weather": "storm"}
        artifact_manager.save_state(state)
        
        self.assertTrue(os.path.exists(artifact_manager.STATE_FILE))
        
        loaded = artifact_manager.load_state(self.dummy_init)
        self.assertEqual(loaded["weather"], "storm")

    def test_svg_persistence(self):
        svg_content = "<svg>test</svg>"
        artifact_manager.save_world_svg(svg_content)
        
        self.assertTrue(os.path.exists(artifact_manager.OUTPUT_SVG_FILE))
        with open(artifact_manager.OUTPUT_SVG_FILE, "r") as f:
            content = f.read()
        self.assertEqual(content, svg_content)

if __name__ == '__main__':
    unittest.main()
