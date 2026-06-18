# WorldPack Asset Guide

Welcome! WorldPacks are completely driven by SVG assets. You do not need to know any Python to build a living world — you only need to provide SVG images and map them in `manifest.yml`.

## 1. Engine Rules for SVGs

The engine uses a strict **"SVG Fragment"** rendering pipeline.

**The Golden Rule:** Every asset file must contain ONLY a bare `<g>` tag wrapper. It must NOT contain an outer `<svg>` tag, XML declaration (`<?xml>`), or `<!DOCTYPE>`.

### ✅ Correct Format
```xml
<g id="my_asset" transform="scale(2)">
    <circle cx="10" cy="10" r="5" fill="#ff0000" />
    <rect x="0" y="0" width="10" height="10" fill="#0000ff" />
</g>
```

### ❌ Incorrect Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <g id="my_asset">...</g>
</svg>
```

## 2. Converting PNGs to SVG Fragments

The engine **does not support PNG or JPG images at runtime**. It is explicitly SVG-first to ensure crisp scaling, CSS animation support, and security.

If you have existing PNG pixel art, you must vectorize it:
1. Use a free online converter like [Pixelied](https://pixelied.com/convert/png-to-svg) or [Vectorizer.ai](https://vectorizer.ai).
2. Open the resulting SVG in a text editor.
3. Delete the outer `<svg>` and `<?xml>` tags.
4. Wrap all the inner paths with a `<g id="your_asset_name">` tag.
5. Save it to your WorldPack directory.

## 3. Creating Original SVGs

You can use standard vector tools:
- **Figma** (Export as SVG, then manually strip the `<svg>` tag in a text editor)
- **Inkscape**
- **Adobe Illustrator**

Ensure that coordinates are generally near `(0,0)` to make it easy to position them via the `manifest.yml` offsets.

## 4. Required Sprites

A complete WorldPack usually requires at least four actor sprites to map to moods:
- `happy.svg`
- `hungry.svg`
- `sleepy.svg`
- `scared.svg`

If any are missing, the engine will safely fallback to `happy.svg`.

## 5. Free Asset Resources

If you aren't an artist, you can find free, open-source SVG assets to build your world:
- [Kenney.nl](https://www.kenney.nl) (Amazing free 2D assets, many in SVG format)
- [SVGRepo](https://www.svgrepo.com) (Millions of free vector icons)
- [OpenClipart](https://openclipart.org)
