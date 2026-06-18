import os
import tempfile
import json
import unittest
from unittest.mock import patch, MagicMock

# Import the main orchestration components
import state
from command_parser import CommandRegistry
from interaction_handlers import PetCommand, GiftCommand, WeatherCommand

class TestStateIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_file = os.path.join(self.temp_dir.name, "state.json")
        self.registry = CommandRegistry()
        self.registry.register("pet", PetCommand)
        self.registry.register("gift", GiftCommand)
        self.registry.register("weather", WeatherCommand)

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("state.STATE_FILE", new_callable=lambda: None)
    def test_scenario_1_sequential_interactions(self, mock_state_file):
        """Scenario 1: multiple interactions processed sequentially"""
        # We need to manually set the state.STATE_FILE for this test
        state.STATE_FILE = self.state_file
        
        # Initial state
        initial_state = state.load_state()
        self.assertEqual(initial_state["pet"]["energy"], 100)
        state.save_state(initial_state)

        # Interaction 1: /pet
        from command_parser import parse_and_execute
        st1 = state.load_state()
        parse_and_execute("/pet", "alice", False, st1, self.registry)
        state.save_state(st1)

        # Interaction 2: /gift fish
        st2 = state.load_state()
        parse_and_execute("/gift fish", "bob", False, st2, self.registry)
        state.save_state(st2)

        # Interaction 3: /pet
        st3 = state.load_state()
        parse_and_execute("/pet", "charlie", False, st3, self.registry)
        state.save_state(st3)

        # Verify
        final_state = state.load_state()
        self.assertTrue(len(final_state["recent_events"]) > 0)
        self.assertEqual(final_state["recent_events"][0]["user"], "charlie")

    @patch("state.STATE_FILE", new_callable=lambda: None)
    def test_scenario_2_update_between_interactions(self, mock_state_file):
        """Scenario 2: update workflow runs between interactions"""
        state.STATE_FILE = self.state_file
        
        # Initial state
        st0 = state.load_state()
        st0["pet"]["energy"] = 100
        state.save_state(st0)

        # Interaction 1
        from command_parser import parse_and_execute
        st1 = state.load_state()
        parse_and_execute("/pet", "alice", False, st1, self.registry)
        state.save_state(st1)

        # Update workflow (simulated by calling load_state and checking transitions)
        # We simulate time passing and then update
        st_update = state.load_state()
        # simulate some decay if needed, but here we just prove state loads cleanly
        state.save_state(st_update)

        # Interaction 2
        st2 = state.load_state()
        parse_and_execute("/gift fish", "bob", False, st2, self.registry)
        state.save_state(st2)

        final_state = state.load_state()
        self.assertEqual(final_state["last_gift"], "fish")
        self.assertEqual(final_state["recent_events"][0]["user"], "bob")

    @patch("state.STATE_FILE", new_callable=lambda: None)
    def test_scenario_3_corrupted_state_recovery(self, mock_state_file):
        """Scenario 3: corrupted state recovery"""
        state.STATE_FILE = self.state_file
        
        # Write corrupted JSON
        with open(self.state_file, "w") as f:
            f.write("{ invalid json")

        # load_state should gracefully recover to default
        recovered_state = state.load_state()
        self.assertIn("pet", recovered_state)
        self.assertEqual(recovered_state["pet"]["energy"], 100)

    @patch("state.STATE_FILE", new_callable=lambda: None)
    def test_scenario_4_missing_output_branch_recovery(self, mock_state_file):
        """Scenario 4: missing output branch recovery"""
        state.STATE_FILE = self.state_file
        
        # Ensure file does not exist
        if os.path.exists(self.state_file):
            os.remove(self.state_file)

        # Engine should create a fresh state if output branch had no state.json
        new_state = state.load_state()
        self.assertIn("pet", new_state)
        
        # Save should work
        state.save_state(new_state)
        self.assertTrue(os.path.exists(self.state_file))

if __name__ == "__main__":
    unittest.main()
