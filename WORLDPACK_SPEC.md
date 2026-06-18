# World Pack Specification

The README World Engine is transitioning from a hardcoded single-pet application into a generic execution environment. A **World Pack** defines all the visual assets, configuration, and structural constraints independently of the Python execution engine.

The engine must **never** contain hardcoded strings referencing specific species (e.g., `if character == "cat"`), specific items (e.g., `gift_type == "wool"`), or specific biomes (`if biome == "forest"`).

## 1. Directory Structure

A compliant World Pack MUST contain the following root elements:

```text
/manifest.yml
/sprites/
  /{character_name}/
    happy.svg
    sleepy.svg
    hungry.svg
    scared.svg
/biomes/
  /{biome_name}/
    tree.svg
    mushroom.svg
    ... (arbitrary scene props)
/weather/
  cloud.svg
  rain.svg
  snow.svg
  storm.svg
/ui/
  panel.svg
```

## 2. The `manifest.yml` Contract

The manifest defines the interaction rules and metadata for the entire world. The engine consumes this document dynamically.

```yaml
version: "1.0"
world:
  name: "Traveller's Realm"
  default_biome: "forest"

characters:
  cat:
    display_name: "Orange Tabby"
    gifts:
      # Item ID -> Effects mapping
      fish:
        hunger: -20
        friendship: 10
        mood: "happy"
      wool:
        energy: -5
        friendship: 5
        mood: "happy"
      bone:
        friendship: 1
  dog:
    display_name: "Golden Retriever"
    gifts:
      bone:
        friendship: 10
        mood: "happy"
      ball:
        energy: -10
        friendship: 8

biomes:
  forest:
    sky_color: "#87CEEB"
    ground_color: "#4a7c3f"
    props:
      # Prop name, coordinates, and CSS animation class
      - name: "tree"
        x: 80
        y: 168
        anim: "anim-sway"
      - name: "tree"
        x: 350
        y: 168
        anim: "anim-sway"
```

## 3. Dynamic Rendering Expectations

When `generate_world.py` runs, it must perform the following algorithm instead of relying on hardcoded coordinates:

1. **Read `manifest.yml`** to determine the current `biome` and background colors.
2. **Iterate `props`** array inside the biome definition to loop through `<use>` tags dynamically.
3. **Parse interactions:** When an event like `/gift fish` arrives, the `event_processor` must look up `characters -> [current_character] -> gifts -> fish` in the YAML to calculate state mutations. No hardcoded logic allowed in Python.

## 4. SVG Constraints
All SVGs within the World Pack must strictly adhere to the fragment protocol (bare `<g>` tags with explicitly named IDs tracking their path, e.g., `cat_happy` or `forest_tree`). No nested `<svg>` boilerplate is allowed.
