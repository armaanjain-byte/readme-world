import sys
import os
from event_processor import process_comment

def main():
    # Expecting: python github_action_runner.py "comment body" "username" "repo_owner" "issue_number"
    if len(sys.argv) < 5:
        print("Usage: python github_action_runner.py <comment_body> <username> <repo_owner> <issue_number>")
        sys.exit(1)
        
    comment_body = sys.argv[1]
    username = sys.argv[2]
    repo_owner = sys.argv[3]
    try:
        issue_number = int(sys.argv[4])
    except ValueError:
        print("Issue number must be an integer.")
        sys.exit(1)
        
    is_owner = (username.lower() == repo_owner.lower())
    
    result = process_comment(comment_body, username, is_owner, issue_number)
    
    # Print structured result for workflow logging
    print(f"Result: {result}")
    
    # Export a GitHub Actions output variable indicating if we should commit
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            # We only commit if success is True
            should_commit = "true" if result.get("success") else "false"
            f.write(f"should_commit={should_commit}\n")
            
    # Always exit 0 so the workflow step itself doesn't "fail" and show red,
    # unless it's a catastrophic Python error. The output flag controls the commit.
    sys.exit(0)

if __name__ == "__main__":
    main()
