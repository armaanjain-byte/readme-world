# Branch Architecture Validation

The repository relies on a two-branch architecture (`main` and `output`) to separate source code from generated assets. This prevents the repository history from ballooning with thousands of SVG generation commits.

## Branch Roles

### `main` Branch
- **Purpose**: Hosts the immutable engine code, Python scripts, configuration (`world.config.yml`), and base vector assets (`sprites/`, `biomes/`, `weather/`).
- **Trigger**: Listens for GitHub `issue_comment` events. 

### `output` Branch
- **Purpose**: Hosts exactly two files:
  - `world.svg` (The final rendered frame displayed on the README)
  - `state.json` (The serialized runtime memory of the pets and world)
- **Constraint**: Must *never* contain Python source code or raw asset directories.

## Execution & Event Flow

When a user comments on an issue, the following workflow (`.github/workflows/process_comment.yml`) executes:

1. **Checkout `main`**: The action checks out the repository source.
2. **State Restoration**: 
   - A shell script queries `origin/output` specifically for `state.json`.
   - It extracts `state.json` and places it into the local `generated/` directory so the engine can pick up where it left off.
3. **Engine Execution**: 
   - `github_action_runner.py` is invoked.
   - It runs the command parser, mutates state, and invokes `generate_world.py`.
   - Artifacts (`state.json`, `world.svg`) are written to the local `generated/` folder.
   - The runner sets the `should_commit` output variable.
4. **Commit Phase**:
   - The modified artifacts are backed up to `/tmp/`.
   - The GitHub Action runner forcibly checks out the `output` branch.
   - `git rm -rf .` clears the source files from the working directory.
   - The artifacts are restored from `/tmp/` to the root directory.
   - The artifacts are committed and pushed to `origin/output`.
5. **Cache Invalidation**:
   - A fallback script actively polls GitHub's Camo CDN proxies to flush the cached image so the README immediately displays the new SVG.

## Possible Failure Points (Risks)

1. **State Overwrites (Race Conditions):** 
   - If two users comment simultaneously, GitHub Actions spawns two parallel runners. Both fetch the same `state.json`. The runner that finishes last will blindly overwrite the first runner's state, erasing the first user's interaction.
2. **Orphan Branch Conflict:** 
   - If a user deletes the `output` branch from GitHub but `git ls-remote` caches incorrectly, the push step (`git push origin HEAD:output`) will fail due to non-fast-forward tracking.
3. **Camo Flushing Fragility:**
   - The `curl` command searching for `camo.githubusercontent.com` URLs relies on GitHub's exact README rendering HTML. If GitHub changes how they construct proxy tags in the DOM, the cache won't purge, and users will see stale SVG files.
