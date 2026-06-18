# Contributing to README World

Welcome to the README World project!

This document outlines how the asset system works and how to contribute new characters, biomes, or weather effects.

## Asset System Overview

We use a pure file-based SVG fragment system. This means no Python configuration is needed to "register" assets. The file path and the `<g>` ID are the only things that matter.

### Directory Structure

```
sprites/
  {character_name}/
    happy.svg
    sleepy.svg
    hungry.svg
    scared.svg
biomes/
  {biome_name}/
    tree.svg
    mushroom.svg  (optional)
    doghouse.svg  (optional)
weather/
  cloud.svg
  rain.svg
  snow.svg
  storm.svg
```

### The Sprite Format Rule

Every SVG asset must be a **bare `<g>` fragment**. 
- No outer `<svg>` wrappers.
- No `<?xml ... ?>` declarations.

**Example `sprites/cat/happy.svg`:**
```xml
<g id="cat_happy" transform="scale(2)">
  <rect x="0" y="8" width="12" height="6" fill="#f4a460"/>
  ...
</g>
```

**CRITICAL RULE:** The `id` attribute on the `<g>` tag must exactly match the pattern `{character}_{mood}` for sprites, `{biome}_{asset}` for biomes, or `weather_{type}` for weather.

### Pixel Grid Spec

All art must be drawn on a **16x16 logical pixel grid**.
To display correctly at 32x32 pixels in the world, wrap your art in a `<g transform="scale(2)">` block as shown above.

### Available Moods

Every character must have four standard moods:
1. `happy` - Default state
2. `sleepy` - Triggered when energy is low
3. `hungry` - Triggered when hunger is high
4. `scared` - Triggered by bad weather (rain, storm, snow)

If a mood file is missing, the system will fall back to `happy.svg`.

### Color Palette

To keep characters visually consistent, please try to adhere to these base palettes:
- **Cat (Orange Tabby):** `#f4a460` (Body), `#ffffff` (Belly/Paws), `#000000` (Eyes)
- **Dog (Golden Retriever):** `#daa520` (Body), `#8b4513` (Nose/Ears), `#000000` (Eyes)

### How to Add a New Character

1. Create a new directory under `sprites/`: `sprites/{name}/`
2. Create `happy.svg`, `sleepy.svg`, `hungry.svg`, and `scared.svg` in that folder.
3. Ensure the `<g>` ID matches your character name: `<g id="{name}_happy" ...>`
4. Test by opening `world.config.yml` and changing `character: cat` to `character: {name}`.

### How to Add a New Biome

1. Create a new directory under `biomes/`: `biomes/{name}/`
2. Create `tree.svg` (and optionally `mushroom.svg`, `doghouse.svg`, etc).
3. Ensure the ID is `<g id="{name}_tree" ...>`.
4. Test by changing `biome: forest` to `biome: {name}` in `world.config.yml`.
