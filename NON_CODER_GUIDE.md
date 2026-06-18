# The Non-Coder's Guide to Customizing README World

Welcome! You don't need to know any Python or programming to personalize your README World repository.

This guide will walk you through swapping out characters, changing the environment, and pushing your changes to GitHub so they appear on your profile.

## Step 1: Downloading a World Pack (or Customizing Assets)

If you have downloaded a **World Pack** zip file from a creator:
1. Unzip the file.
2. Inside, you will see folders like `sprites/`, `biomes/`, and `weather/`.
3. Simply drag and drop these folders directly into the root directory of your forked repository on your computer, overwriting the existing folders.

### Editing Assets Manually
If you want to draw your own characters:
1. Open the `sprites/cat/` folder.
2. You will see 4 SVG files: `happy.svg`, `hungry.svg`, `scared.svg`, and `sleepy.svg`.
3. Open them in a vector editor (like Inkscape or Figma). 
4. **Important**: When you save, do NOT export standard web SVGs. You must save them as a "bare group."
   - Delete the outer `<svg viewBox="...">` wrapper in a text editor like Notepad.
   - Ensure the content starts and ends with `<g id="cat_happy" transform="scale(2)"> ... </g>`.

## Step 2: Update Configuration

1. Open the file named `world.config.yml` in a text editor (Notepad, TextEdit).
2. It looks like this:
   ```yaml
   name: "My Awesome Pet"
   character: "cat"
   biome: "forest"
   ```
3. Change the name or character to match your new folders. For example, if you created a `sprites/penguin/` folder, change `character: "cat"` to `character: "penguin"`.
4. Save the file.

## Step 3: Push to GitHub

Once your files are updated locally, you just need to upload them to GitHub. You do **not** need to touch the `output` branch or the `state.json` file.

Open your terminal or GitHub Desktop and commit your changes to the `main` branch:

```bash
git add sprites/ world.config.yml
git commit -m "Personalize my README World"
git push origin main
```

## Step 4: Verify

That's it! Go to your GitHub repository URL.
Leave a comment on any Issue (like `/pet`), and the GitHub Actions engine will automatically wake up, process your new files, and generate the updated image on your README.
