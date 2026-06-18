# File Dependency Map

This map outlines the static import dependencies and execution paths within the engine.

## Import Chain

### Core Execution Path
- **`github_action_runner.py`** -> Imports `event_processor.process_comment`
- **`event_processor.py`** -> Imports:
  - `github_event_models.Event`, `CommentEvent`
  - `command_parser.CommandRegistry`, `parse_and_execute`
  - `interaction_handlers.PetCommand`, `GiftCommand`, `WeatherCommand`
  - `state.load_state`, `save_state`
  - `generate_world.generate_svg`
  - `interaction_policy.RepositoryPolicy`
- **`command_parser.py`** -> Imports `security.sanitize_username`, `rate_limiter.check_rate_limits`
- **`generate_world.py`** -> Imports:
  - `state.load_state`
  - `sprite_loader.load_character`, `load_biome_asset`, `load_weather_asset`, `build_defs`
  - `security.escape_svg_text`

### Auxiliary Execution
- **`commands.py`** -> Standalone CLI wrapper utilizing `command_parser` and `interaction_handlers`.

---

## State Model (`generated/state.json`)

The state schema holds the engine's memory.

**Top-Level Fields:**
- `weather` (string): Current environmental weather.
- `pet` (dict):
  - `species` (string)
  - `mood` (string)
  - `energy` (int)
  - `hunger` (int)
  - `friendship` (int)
- `recent_action` (string | null): The last interaction type.
- `recent_user` (string | null): The last user to interact.
- `thank_you_cycles` (int): Tick duration for the "Thank You" banner.
- `last_gift` (string | null)
- `gifted_by` (string | null)
- `friendship_log` (dict): Key-value map of `username: score`.
- `recent_events` (list): Ring buffer of the last 10 interactions.
- `cooldowns` (dict): Rate-limiting enforcement data.
- `daily_usage` (dict): Date-keyed tracking array.

---

## Artifact Generation

- **`world.config.yml`**: Static configuration (e.g. `character: cat`).
- **`generated/world.svg`**: Output visual, explicitly synthesized by `generate_world.py`.
- **`generated/state.json`**: Runtime memory.

---

## Branch Interaction Map

- **`.github/workflows/process_comment.yml`**: Bound to `main`. Listens to `issue_comment`. Checks out the `output` branch. Commits `generated/*` back to `output`.
- **`.github/workflows/update.yml`**: Bound to a cron schedule. Modifies `state.json` via random drift and pushes to `output`.
