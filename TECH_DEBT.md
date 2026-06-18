# Technical Debt Report

This document identifies fragility, technical debt, and synchronization risks within the repository's architecture. Issues are ranked by priority.

## Critical Priority

### 1. Workflow Parallelism Race Condition
**Root Cause:** If multiple users comment on GitHub Issues within seconds of each other, GitHub Actions spawns concurrent workflow runners.
**Impact:** Both runners fetch `origin/output` state simultaneously. The runner that finishes last will blindly overwrite the first runner's JSON file. The first user's interaction (and pet friendship gain) is permanently lost.
**Fix Recommendation:** Implement an optimistic concurrency model or lockfile mechanism during the state commit phase (e.g., pulling latest branch tip and attempting a fast-forward, retrying the Python state mutation if the SHA shifted).

### 2. Orphan Output Branch Fragility
**Root Cause:** The `process_comment.yml` workflow aggressively uses `git checkout --orphan output` if it thinks the branch doesn't exist, and forces pushes using `git push origin HEAD:output`.
**Impact:** If GitHub API lags and returns an incorrect `ls-remote` response, or if a user accidentally merges `output` into `main`, the push command will fail with a `non-fast-forward` error. The workflow permanently breaks until manual CLI intervention occurs.
**Fix Recommendation:** Standardize on checking out the actual `origin/output` branch gracefully without forcing orphan creation. Remove the `rm -rf .` clearing logic and use a dedicated `generated/` tracked branch with standard fast-forward merges.

## High Priority

### 3. Hardcoded Logic in `generate_world.py` and `state.py`
**Root Cause:** The renderer explicitly checks `if character == "cat"` to set Y coordinates, and `state.py` hardcodes species-specific logic (`if species == "cat"` checking for "fish" gifts).
**Impact:** Completely breaks the "World Pack" engine extraction goal. Users cannot add a "penguin" without writing Python code to manage the Y-coordinate offset and food preferences.
**Fix Recommendation:** Adopt the `WORLDPACK_SPEC.md` `manifest.yml`. Move all coordinates, gift mappings, and species data out of `.py` files into the declarative configuration format.

### 4. Camo Flushing Reliability
**Root Cause:** The repository relies on `curl -sLk "https://github.com/..." | grep -Eo "camo.githubusercontent..."` to purge the README image cache.
**Impact:** Extremely fragile. If GitHub alters their DOM structure or lazy-loading HTML attributes, the `grep` fails. The image silently caches for hours. Users think the project is broken.
**Fix Recommendation:** Adopt a dynamic query parameter on the image URL inside the README itself (e.g., `![World](world.svg?cache_bust=12345)` dynamically injected via GitHub Actions), bypassing the need to hack GitHub's Camo API entirely.

## Medium Priority

### 5. SVG Fragment Boilerplate Sanitization
**Root Cause:** `sprite_loader.py` uses crude Regex `re.search(r'(<g\b.*?</g>)', content, re.DOTALL)` to extract fragments if users upload raw SVGs.
**Impact:** Fails silently on complex nested SVGs or malformed vector exports from Illustrator/Figma.
**Fix Recommendation:** Introduce a lightweight XML parser (`xml.etree.ElementTree`) during the validation step to safely pluck out the intended `<g>` by ID instead of using Regex.

## Low Priority

### 6. Command CLI Clutter
**Root Cause:** `commands.py` acts as a local CLI wrapper for the engine but duplicates the payload execution logic found in `github_action_runner.py`.
**Impact:** Minor maintenance overhead. If `parse_and_execute` signature changes, both runners must be updated.
**Fix Recommendation:** Refactor `github_action_runner.py` to consume a unified `cli()` interface that handles both local terminal tests and GitHub Action injections elegantly.
