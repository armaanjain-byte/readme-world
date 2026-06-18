# WorldPack Specification

A WorldPack is a directory containing a `manifest.yml` and associated SVG assets. It defines everything needed to render a world and calculate interactions.

## Directory Structure
```
worldpacks/
  my_world/
    manifest.yml
    assets/
      idle.svg
      ...
```
*Note: Asset paths inside the manifest are relative to the repository root, so you can share assets across packs.*

## SVG Asset Requirements
Currently, the engine expects **SVG Fragments**.
These are bare `<g>` tags without the outer `<svg>` wrapper or `<?xml>` declaration.

*Future-proofing note: The architecture is designed so that future PNG support or full SVG support can be handled entirely within `worldpack_loader.py` without touching the renderer.*

## Manifest Schema

```yaml
name: "World Name"
version: "1.0"

# Actor placement
actor:
  x: 400
  y: 210

# Actor sprites (must provide at least happy, sleepy, hungry, scared)
sprites:
  happy: path/to/happy.svg
  sleepy: path/to/sleepy.svg
  hungry: path/to/hungry.svg
  scared: path/to/scared.svg

# Interactions
gifts:
  item_name:
    hunger: -20         # Optional delta
    energy: 5           # Optional delta
    friendship: 10      # Optional delta
    mood: happy         # Optional override

# Environment
weather:
  clear:
    sky: "#hexcode"
    ground: "#hexcode"
  rain:
    sky: "#hexcode"
    ground: "#hexcode"
    overlay: path/to/rain_overlay.svg
    lightning: false    # If true, enables flash animation

clouds:
  asset: path/to/cloud.svg
  positions:
    - { x: 100, y: 20 }

biome:
  props:
    - asset: path/to/prop.svg
      positions:
        - { x: 80, y: 168, anim: "anim-sway" }
```
