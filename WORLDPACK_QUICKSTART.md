# WorldPack Quickstart Guide

Want to build your own custom pet simulation without writing a single line of Python? You're in the right place!

## Step 1: Create your pack
1. Go to the `worldpacks/` directory.
2. Duplicate the `default` folder and rename it (e.g., `worldpacks/my_penguin`).
3. Open `manifest.yml` inside your new folder.

## Step 2: Add your art
The repository already uses "SVG fragments" (SVGs without the `<svg>` tag wrapper).
1. Place your art inside a folder like `sprites/penguin/`.
2. Update the `sprites:` section of your `manifest.yml` to point to your new files:
   ```yaml
   sprites:
     happy: sprites/penguin/happy.svg
     sleepy: sprites/penguin/sleepy.svg
     # etc...
   ```
3. Adjust the `actor:` `x` and `y` coordinates in the manifest so your penguin sits perfectly on the ground.

## Step 3: Define Interactions
Want visitors to feed your penguin fish?
1. Edit the `gifts:` section in your manifest:
   ```yaml
   gifts:
     squid:
       hunger: -50
       friendship: 20
       mood: happy
   ```
2. Now, anyone commenting `/gift squid` on your Issue #1 will trigger those exact stat changes automatically!

## Step 4: Activate it
1. Open `world.config.yml` in the root of the repository.
2. Change the `worldpack:` setting to point to your new folder:
   ```yaml
   worldpack: worldpacks/my_penguin
   ```
3. Commit and push your changes. The GitHub Action will immediately start using your world!
