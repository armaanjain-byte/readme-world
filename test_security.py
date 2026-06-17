import unittest
import os
import time
from security import sanitize_username, escape_svg_text
from rate_limiter import check_rate_limits
from state import initialize_state, save_state, load_state
from command_parser import parse_and_execute
from event_processor import process_comment

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.state = initialize_state()
        save_state(self.state)

    def test_username_sanitization(self):
        # Strip whitespaces
        self.assertEqual(sanitize_username("  alice  "), "alice")
        
        # Remove control characters
        self.assertEqual(sanitize_username("bob\x00\x1f\n\rsmith"), "bobsmith")
        
        # Truncate
        long_name = "a" * 50
        self.assertEqual(len(sanitize_username(long_name)), 39)
        
        # Empty fallback
        self.assertEqual(sanitize_username("   "), "anonymous")

    def test_svg_escaping(self):
        malicious = '<script>alert(1)</script> & "hack" \''
        safe = escape_svg_text(malicious)
        self.assertNotIn("<script>", safe)
        self.assertIn("&lt;script&gt;", safe)
        self.assertIn("&quot;", safe)
        self.assertIn("&#x27;", safe)

    def test_state_recovery(self):
        # Write corrupted data
        with open("state.json", "w") as f:
            f.write("THIS IS NOT JSON")
            
        # load_state should safely recover using initialize_state
        state = load_state()
        self.assertIn("weather", state)
        self.assertIn("pet", state)
        self.assertIn("cooldowns", state)

    def test_cooldowns(self):
        # Pet should be allowed
        allowed, reason = check_rate_limits(self.state, "user1", "pet", False)
        self.assertTrue(allowed)
        
        # Pet immediately again should be blocked by cooldown
        allowed, reason = check_rate_limits(self.state, "user1", "pet", False)
        self.assertFalse(allowed)
        self.assertEqual(reason, "cooldown")
        
        # Owner should bypass cooldown
        allowed, reason = check_rate_limits(self.state, "owner", "pet", True)
        self.assertTrue(allowed)
        allowed, reason = check_rate_limits(self.state, "owner", "pet", True)
        self.assertTrue(allowed)

    def test_daily_rate_limit(self):
        # Use up daily limit (10)
        for i in range(10):
            # Hack cooldown to allow immediate use
            self.state["cooldowns"] = {}
            allowed, reason = check_rate_limits(self.state, "user_spammer", "pet", False)
            self.assertTrue(allowed)
            
        # 11th should be blocked
        self.state["cooldowns"] = {}
        allowed, reason = check_rate_limits(self.state, "user_spammer", "pet", False)
        self.assertFalse(allowed)
        self.assertEqual(reason, "rate_limit")
        
    def test_event_processor_structured_results(self):
        # First valid pet
        result = process_comment("/pet", "alice")
        self.assertTrue(result["success"])
        
        # Second should be blocked by cooldown and return structured reason
        result = process_comment("/pet", "alice")
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "cooldown")

if __name__ == '__main__':
    unittest.main()
