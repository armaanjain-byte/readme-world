# Production Readiness Report

This document audits the stability of the README World workflows, specifically focusing on data corruption risks in a high-traffic GitHub repository.

## Identified Risks

### 1. Concurrent Comment Execution (Race Condition)
**Severity:** CRITICAL
**Description:** When multiple users comment simultaneously, GitHub Actions spawns concurrent workflow runners. Both runners fetch the `output` branch and download the exact same `state.json`. Runner A mutates the state and pushes. Runner B mutates its stale state and pushes, permanently overwriting Runner A's changes.
**Recommended Fix:** 
Implement an optimistic concurrency loop in `process_comment.yml`:
1. Check out `output` branch.
2. Read `state.json`.
3. Run python engine to mutate state.
4. Try `git commit` and `git push`.
5. If `git push` fails (due to non-fast-forward), `git pull --rebase` is NOT enough because the JSON state must be semantically re-merged. The workflow must `git reset --hard origin/output` and jump back to Step 2 to replay the comment event against the newly fetched state.
**Estimated Effort:** Medium (Requires a bash retry-loop in the YAML file).

### 2. Output Branch Corruption (`checkout --orphan`)
**Severity:** HIGH
**Description:** The current workflow attempts to do a graceful checkout of the output branch, but falls back to `git checkout --orphan output` if `git ls-remote` fails. If this fallback triggers erroneously (e.g., due to a temporary GitHub API outage), the workflow force-pushes a completely new git history, effectively destroying the repository's interaction history and causing localized clone failures for anyone tracking the branch.
**Recommended Fix:** Stop using orphan branches dynamically. Track `generated/` in the main branch, OR require the user to manually create the `output` branch once. Fail the action cleanly if `origin/output` is unreachable.
**Estimated Effort:** Low.

### 3. Camo Cache Stale Responses
**Severity:** MEDIUM
**Description:** GitHub aggressively caches `world.svg` through its Camo proxy. The current `curl` purge logic is brittle because it relies on regex matching `camo.githubusercontent.com` URLs from the raw HTML of the README. If GitHub modifies its DOM, the cache won't clear.
**Recommended Fix:** Avoid purging entirely. Inject a dynamic query parameter into the README image link (e.g., `![World](world.svg?v=${{ github.run_id }})`) using a secondary step in the workflow that commits directly to `main` when the image updates.
**Estimated Effort:** High (Requires giving the workflow write permissions to `main`, which introduces its own security risks).

## Summary
The WorldPack abstraction handles the Python engine elegantly, but the GitHub Actions orchestration layer is currently unfit for viral repositories due to the critical state-overwrite race condition. This must be resolved before advertising the project to large communities.
