# readme-world
Stagnant project the svg loads from output branch.
A living world in your GitHub profile README. The pet changes based on visitor interactions.

![World](https://raw.githubusercontent.com/armaanjain-byte/readme-world/output/world.svg)

---

## Interact with the pet

Comment on **[Issue #1](https://github.com/armaanjain-byte/readme-world/issues/1)** with one of these commands:

| Command | Effect |
|---|---|
| `/pet` | Pet the animal (+friendship) |
| `/gift fish` | Give a fish |
| `/gift wool` | Give some wool |
| `/gift bone` | Give a bone |
| `/gift ball` | Give a ball |

After you comment, a GitHub Actions workflow runs automatically and updates the image above. Changes typically appear within a minute.

---

## How it works

- Interactions are accepted only from Issue #1
- The pet's mood, energy, and friendship respond to gifts
- The world SVG is regenerated and committed to the `output` branch
- The README always pulls the latest image from that branch

---

## Credits

- Cat sprites from the **Gray Cat Asset Pack**.
