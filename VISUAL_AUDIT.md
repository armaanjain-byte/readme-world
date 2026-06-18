# Visual Audit

## Current Problems
1. **Static Orange Blob:** The default actor (`sprites/cat/*.svg`) is literally a collection of `<rect>` tags. It feels like a placeholder rather than a living pet.
2. **Invisible Weather:** Weather relies on basic sky/ground hex colors. The SVGs for rain, snow, and storm overlays (`weather/rain.svg`, etc.) are either rudimentary or entirely absent, leaving the weather feeling disconnected from the world.
3. **Ghost Gifts:** When users gift an item (e.g., `/gift fish`), the pet stats change and the UI text updates, but the fish never appears on the screen. There is no physical evidence of the interaction.
4. **Static World / Zero Progression:** The biome props (trees, clouds) are statically placed. A user with 0 friendship sees the exact same world as a user with 500 friendship. There is no sense of evolving attachment.
5. **UI Overload:** The black semi-transparent UI box dominates the top of the SVG, overshadowing the actual "world" rendering.

## Recommended Fixes
| Priority | Improvement | Impact | Complexity | ROI |
|----------|-------------|--------|------------|-----|
| 1 | **Physical Gifts:** Add a rendering layer for `state.last_gift` using a new `asset` property in the manifest's `gifts` definitions. Render the gift next to the actor. | High | Low | High |
| 2 | **World Progression:** Introduce a `progression` array in `manifest.yml`. Render specific `props` based on integer thresholds of the pet's `friendship` stat. | High | Medium | High |
| 3 | **Real Weather Overlays:** Overhaul `weather/*.svg` assets with proper semi-transparent raindrop/snowflake patterns, and attach the existing CSS animation classes (`anim-rain`, `anim-snowfall`) to them. | High | Medium | High |
| 4 | **Actor Redesign (SVG):** Replace the `<rect>` cat with a curved, path-based SVG cat that actually resembles a stylized creature. | Medium | High | Medium |

## Reference Requirements
- **Rain Overlay:** A repeating pattern of semi-transparent angled lines (`<line stroke="rgba(255,255,255,0.4)">`).
- **Snow Overlay:** A scatter of white `<circle>` elements with varying opacities.
- **Progression Assets:** Small SVGs for a flower, a pond, and a house to layer dynamically behind/around the actor.
- **Gift Assets:** Small SVGs for fish, toy, and treat.

## Will a first-time GitHub visitor immediately notice this?
- **Weather / Actor / Gifts:** Yes. The screen will be moving and visually distinct based on the exact moment they visit.
- **Progression:** Yes. If they return later, the world will have grown.
