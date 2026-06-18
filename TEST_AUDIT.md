# Test Audit Report

## Current Test Inventory
- `test_commands.py`: Tests command parsing and interaction logic.
- `test_event_processor.py`: Tests the central orchestrator (`process_comment`).
- `test_github_action_runner.py`: Tests the GitHub action entrypoint and output writing.
- `test_interaction_policy.py`: Tests cooldowns, max daily limits, and valid actions.
- `test_security.py`: Tests input sanitization and username length constraints.
- `test_state.py`: Tests state loading, defaults, mutations, and saving.

## Findings

### 1. Obsolete Tests
- Tests expecting hardcoded species logic are now obsolete. We refactored `test_commands.py` to remove `test_dog_gift_reactions` in a previous step, but other references to "cat" vs "dog" concepts may linger in naming.
- `test_state.py` might still be testing concepts that should really be manifest-driven.

### 2. Missing Coverage
The test suite currently lacks coverage for several core components:
- **`generate_world.py` (Renderer)**: There are **zero** tests for SVG generation, CSS generation, component assembly, or fallback logic.
- **`worldpack_loader.py`**: No tests verify that the manifest parser correctly falls back to defaults or handles missing YAML files.
- **`sprite_loader.py`**: No tests verify SVG fragment loading or `build_defs()`.
- **E2E Workflows**: No tests execute the *complete* pipeline from `github_action_runner` → state mutation → `generate_world.py` execution.

### 3. Duplicate / Low-Value Tests
- `test_event_processor.py` mostly repeats the exact same assertions as `test_commands.py` but through a single layer of indirection.
- Several state update tests manually poke `state["cooldowns"]` rather than relying on realistic event flows.

### 4. Poor Organization
All tests are currently dumped in the root directory. There is no separation between unit tests, integration tests, or end-to-end tests. There is no `conftest.py` providing shared fixtures (meaning `setUp` logic is duplicated across every test class).

## Conclusion
The test suite is highly fractured and heavily skewed toward unit testing state dictionaries. The most critical system—the renderer—is entirely untested. We need to restructure into `tests/unit/`, `tests/integration/`, and `tests/e2e/`, implement shared `pytest` fixtures, and dramatically increase coverage of the rendering and WorldPack loading systems.
