import unittest
import subprocess
import os
import json
from state import initialize_state, save_state

class TestGitHubActionRunner(unittest.TestCase):
    def setUp(self):
        # Reset state to default
        state = initialize_state()
        save_state(state)
        
        # Ensure dummy GITHUB_OUTPUT file exists for capturing output
        self.output_file = "dummy_github_output.txt"
        with open(self.output_file, "w") as f:
            f.write("")
        os.environ["GITHUB_OUTPUT"] = self.output_file

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if "GITHUB_OUTPUT" in os.environ:
            del os.environ["GITHUB_OUTPUT"]

    def run_runner(self, body, username, repo_owner, issue_number):
        result = subprocess.run(
            ["python", "github_action_runner.py", body, username, repo_owner, str(issue_number)],
            capture_output=True,
            text=True
        )
        return result

    def test_successful_comment(self):
        # Issue 1 is allowed
        res = self.run_runner("/pet", "alice", "repo_owner", 1)
        self.assertEqual(res.returncode, 0)
        
        # Verify output flag indicates commit=true
        with open(self.output_file, "r") as f:
            content = f.read()
        self.assertIn("should_commit=true", content)

    def test_rejected_comment_wrong_issue(self):
        # Issue 99 is rejected
        res = self.run_runner("/pet", "alice", "repo_owner", 99)
        self.assertEqual(res.returncode, 0) # Still exits 0 so workflow doesn't artificially fail
        
        with open(self.output_file, "r") as f:
            content = f.read()
        self.assertIn("should_commit=false", content)

    def test_rejected_comment_invalid_format(self):
        res = self.run_runner("this is not a command", "alice", "repo_owner", 1)
        self.assertEqual(res.returncode, 0)
        
        with open(self.output_file, "r") as f:
            content = f.read()
        self.assertIn("should_commit=false", content)

if __name__ == '__main__':
    unittest.main()
