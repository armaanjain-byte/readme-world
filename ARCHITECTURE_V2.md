# README World Engine Architecture V2

The repository has been decoupled into two distinct layers: the **Execution Engine** (Python logic) and the **Content Layer** (WorldPacks).

## The Execution Engine
The engine is completely unaware of species, biomes, or specific assets. It understands generic concepts:
- **Actor**: An entity with moods, hunger, energy, and friendship.
- **Interactions**: Arbitrary commands (gifts, weather changes) mapped to generic stat modifications.
- **Rendering**: A compositor that layers SVGs based on coordinate data provided externally.

## The Content Layer (WorldPacks)
A WorldPack is a standalone directory (e.g., `worldpacks/default/`) containing a `manifest.yml` and static SVG assets.

The `manifest.yml` defines the entire reality of the repository:
1. **Visuals**: Which SVG fragments correspond to which actor mood.
2. **Layout**: Exact `x/y` coordinates for the actor and environmental props.
3. **Logic Mapping**: How specific interactions mutate the actor's stats (e.g., `/gift fish` might grant +10 friendship and -20 hunger).
4. **Environment**: Sky and ground hex colors, and weather overlay configurations.

## Event Pipeline
1. GitHub Action captures an Issue comment and routes it to `github_action_runner.py`.
2. `event_processor` parses the command.
3. The command handler (e.g., `GiftCommand`) reads the active WorldPack manifest to see if the item exists and what its effects are.
4. `state.py` applies those effects generically.
5. `generate_world.py` reads the manifest to composit the `<defs>` and layout layers, rendering `world.svg`.
6. Output is committed to the `output` branch.
