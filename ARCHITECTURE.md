# README World Engine Architecture

This document describes the core architecture of the README World Engine, which powers the repository's interactive state and SVG generation.

## 1. Event Processing Pipeline

The system is triggered via a GitHub Action (`process_comment.yml`), which executes `github_action_runner.py` to route the comment into the event processor.

1. **GitHub Comment Received:** The user comments on an issue with a command (e.g. `/pet`).
2. **Action Runner (`github_action_runner.py`):** Acts as the entrypoint. It bridges the GitHub environment variables to the Python logic.
3. **Event Processor (`event_processor.py`):** The orchestrator.
   - Validates the event against the `RepositoryPolicy` (e.g. anti-spam, blocklists).
   - Loads the current world state (`state.py`).
   - Delegates command execution.
   - Saves the mutated state.
   - Triggers the visual rendering.
4. **Command Parser (`command_parser.py`):** Parses raw strings into specific commands (`/pet`, `/gift`, `/weather`), applying rate-limiting logic.

## 2. Rendering System

The rendering pipeline translates the JSON state into a visual SVG output. It is powered by `generate_world.py`.

1. **State Evaluation:** The renderer assesses the state variables (pet hunger, energy, friendship, recent events, and weather).
2. **Sprite Resolution:** `sprite_loader.py` dynamically fetches raw `<g>` SVG fragments from the file system (`sprites/`, `biomes/`, `weather/`) based on the required ID (e.g. `cat_happy`).
3. **DOM Construction:** The `<g>` fragments are compiled into a central `<defs>` block.
4. **Scene Rendering:** The background, weather layers, pet, and UI panel are composited via SVG `<use>` tags referencing the defs block.
5. **Output Generation:** The assembled SVG is saved directly to `generated/world.svg`.

## 3. State Management

State is persisted locally via `state.json` (inside the `generated/` directory), which acts as the source of truth between workflow runs.

- **`state.py`**: Manages state instantiation, normalization (fallback values), and standard mutations (e.g., probability-based weather drift, energy/hunger decay).
- State includes global interaction cooldowns and friendship logs to persist relationships.

## 4. Policy & Security

- **`interaction_policy.py`**: A pre-execution firewall determining if an event is globally permitted.
- **`security.py`**: Sanitizes usernames and string inputs before they reach the SVG DOM, mitigating injection vectors.

## Summary

The architecture is explicitly designed around a stateless execution environment (GitHub Actions runners) using a JSON file as persistent memory, and a flat SVG fragment layer for highly extensible, Python-agnostic visual asset loading.
