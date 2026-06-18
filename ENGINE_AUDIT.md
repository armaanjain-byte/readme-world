# Engine Audit: Hardcoding

This document identifies remaining hardcoded terms (species, items, moods) across the repository.

| Term | File | Line | Reason | Classification |
|------|------|------|--------|----------------|
| `species`, `cat`, `dog` | `tests/unit/test_state.py` | 24, 55 | Legacy test cases checking state parsing and initialization. Tests use mock state payloads with `species`. | SAFE |
| `fish`, `bone`, `wool`, `ball` | `tests/unit/test_commands.py` | 28, 41, 49, 95 | Legacy unit tests for the `/gift` command testing specific default pack interactions. | SAFE |
| `fish` | `tests/unit/test_policy.py` | 26 | Mocking a `/gift` command argument. | SAFE |
| `fish` | `tests/e2e/test_comment_to_svg.py` | 96, 107 | E2E integration tests verifying the GitHub Action processes a comment properly. | SAFE |
| `happy` | `worldpack_loader.py` | 23, 27 | Fallback mechanism ensuring a sprite always loads if a requested mood is absent from a manifest. | SAFE |
| `happy`, `sleepy`, `hungry`, `scared` | `validate_worldpack.py` | 38 | Validation script explicitly requires all WorldPacks to define these four moods. | MIGRATION NEEDED |
| `happy`, `sleepy`, `hungry` | `state.py` | 52, 94, 96, 100, 140, 204 | Pet stat boundaries directly dictate transitions between these specific string values. The "engine" is hardcoded to output these four moods based on stats. | MIGRATION NEEDED |
| `happy` | `sprite_loader.py` | 22, 25 | File loading fallback mechanism looking for `happy.svg`. | SAFE |
| `happy`, `sleepy`, `hungry`, `scared` | `generate_world.py` | 16-19, 234, 311, 314, 315 | CSS classes (`MOOD_ANIMATIONS`) are hardcoded to these four specific mood states. Sad is automatically converted to `scared`. | MIGRATION NEEDED |
| `wool`, `octocat` | `commands.py` | 16 | Appears strictly in the CLI `argparse` help documentation string. | SAFE |

## Summary
The remaining hardcoded Python occurrences of "cat", "dog", "fish", "bone", etc. exist solely within **Test Files** and **CLI Docstrings**, which is acceptable since testing scenarios need concrete mock instances. 

However, the "engine" is still heavily hardcoded to support **exactly four pet moods** (`happy`, `sleepy`, `hungry`, `scared`). The state manager, manifest validator, and CSS generation strictly expect these four mood states to represent the actor. Removing these would require an architecture change so that WorldPacks can define custom dynamic states and transition triggers, but under current limitations, they act as the base behavioral framework for all creatures.
