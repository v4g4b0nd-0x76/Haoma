# Beast review — #1 Dahaka

**Status:** awaiting approval. Not baked into `genmaps` / map SVGs.

## What was drawn

Aži Dahāka (Iranian three-headed dragon-serpent) as a **standalone dark volumetric SVG**: coiled serpentine mass with scale texture, lit/shade faces and soft ground shadow, three distinct heads (center dominant), bone horns/teeth, crimson-ink eyes and gullet, ash/bronze body. Serious mythic tone — not a cute map doodle and not the old gold-wireframe/volumetric-gold style.

## Proposed map placement (after approval)

| Field | Value |
|-------|--------|
| Map | `persia` |
| Lon / lat | **53.30°E, 35.50°N** |
| Rationale | South flank of Damavand (Zahhak chained in the mountain). Offset from the Damavand summit pin at 53.06°E, 35.95°N so the beast mark and pin do not stack. |
| Pin % (persia box 42–72°E / 24–40°N) | ≈ **x=37.7% y=28.1%** |

Do **not** add to `MAPS["persia"]["creatures"]` or `map_creatures.CREATURE_ART` until approved.

## Palette

| Role | Hex (approx) |
|------|----------------|
| Dark ink ground | `#0a0908` / `#12100e` |
| Ash body | `#3a322a` → `#1c1814` |
| Bone | `#c8bcae` / `#9a8c7c` |
| Muted bronze | `#8a6e52` / `#5c4a38` |
| Crimson ink | `#4a1010` / `#8a1c1c` (eyes/maw only) |

**Explicitly avoided:** `#c9a45c` (map UI gold) as primary fill or outline.

## Files

- `static/.preview-maps/beast-review/dahaka.svg`
- `static/.preview-maps/beast-review/dahaka.png` (Chrome headless @1200×960)

## Checkpoint

Revert maps+old creatures: `git checkout checkpoint/maps-pre-beast-redesign` (or reset to that tag).

## Next

Approve / revise Dahaka only. Do not design Simorgh, Fenrir, etc. until this one lands.
