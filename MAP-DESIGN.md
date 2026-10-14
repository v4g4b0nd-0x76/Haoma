# MAP-DESIGN.md - house style and rules for the myth maps

Read this before you touch a map. It records the look the maps were approved in,
how that look is produced, and the mistakes that were already made and rejected,
so nobody has to rediscover them. [AI.md](AI.md) holds the general site rules; this
file is only about maps.

**The one pipeline.** Map artwork is produced by `tools/genmaps.py` with the art
helpers in `tools/mapart.py` and nothing else. Earlier experiments (cartoon
creature sheets, a separate creature module, hand-drawn beast reviews) were
deleted on purpose. Do not bring them back, and do not paint or import raster
artwork onto a map.

## 1. The look we are after

An old engraved atlas seen at night. The references are the Middle-earth
endpaper maps and antique sea charts: a dense, hand-engraved surface with
mountains, forests, sea ripples, curved lettering, a few monsters and ships, a
ladder border and a cartouche, all in our own dark palette.

- **Engraved, not illustrated.** Everything on the artwork is drawn like a
  copper-plate engraving: a dark inked fill, a thin gold or pale outline, hatching
  on the shaded side. There are no gradients on the objects, no soft airbrushing,
  no outlines that look like a felt pen.
- **Dark and serious.** It is a manuscript of myths, not a children's book. No
  smiles, no googly eyes, no rounded "cute" bodies, no bright saturated colours.
- **Relief has weight.** Every mountain has a lit face and a shaded face, plus
  hatching and a snow line, so ranges read as solid volumes rather than flat
  triangles. A range is two staggered rows of peaks, larger in front and smaller
  behind, mixing four peak shapes, so it reads as a chain rather than a row of
  stamps.
- **Detail rewards zoom.** The art is dense enough that zooming in on the site
  (up to 4×) shows more texture, not blurrier shapes. It is pure vector, so keep it
  that way.
- **Map first.** Creatures and ships decorate the map; they never dominate it. A
  monster is about the size of a small range of hills, never wider than a region
  or larger than the land it sits on.

## 2. Palette and type

All colours are constants at the top of `tools/genmaps.py` (map surface) and
`tools/mapart.py` (art). Change them there, never inline.

| Role | Value |
|---|---|
| Sea, top to bottom gradient | `#10283a` to `#07131d`, with `#6fb0d0` shore ripples |
| Land | `#34452a` olive with grain, shaded rim `#0a1208` |
| Coastline | gold `#d4b86e` over a dark ink line |
| Rivers | `#6fb4d6` over a `#06141c` casing, tapered toward the source |
| Land / sea lettering | `#e6d7ae` / `#8fb8d2` italic, both with a dark halo |
| Art (monsters, ships) | ink `#05080b`, fills `#16230f` / `#22331a`, gold outline `#dcc07a`, sails `#d9cba0` |
| Terrain glyphs | peak `#4f5f3d`, shade `#16200e`, edge `#d3c186`, hatch `#0c1208`; forest `#1d2e18` / `#8fb064`; sand `#9a8650`; marsh `#74a893` |

Gold is used only for **lines** on the art: coastline, outlines, the border and
the cartouche. A creature filled with gold was rejected as "awful", so do not fill
creatures with gold.

Lettering: English in Cinzel (Georgia fallback) with wide letter spacing; Farsi in
Vazirmatn with **no** letter spacing and no case transforms. Labels follow a
gentle curve, carry a halo (`paint-order:stroke`) so they read over terrain, and
are placed by a collision pass that keeps them clear of pins, monsters, ships,
the cartouche, the compass and the scale bar.

## 3. Anatomy of a map

Drawn in this order by `build()` in `tools/genmaps.py`:

1. Sea gradient, a faint wave pattern, graticule and compass rhumb lines.
2. Land from Natural Earth (1:50m regional, 1:110m for the world) with a slight
   displacement filter, so the coast looks hand-traced. Shore ripples are drawn
   as four widening translucent strokes.
3. Inside the land: grain, a shaded rim, then terrain glyphs sorted by y
   so nearer symbols overlap farther ones: dunes and stipple (`deserts`),
   reeds (`marsh`), round hills (`hills`), pines and broadleaf trees
   (`forests`), and mountain chains along each `ranges` polyline.
4. Lakes and tapered rivers, then the coastline (ink under gold).
5. Ships and monsters, each with an optional name under it.
6. Curved region and sea labels.
7. Ladder border, ribbon cartouche with the map title, compass rose and scale
   bar.

The SVG has no scripts and no external references, and stays a few hundred KB at
most. The world map sits on 1:110m data for exactly that reason.

## 4. The `MAPS` table

One entry per map in `tools/genmaps.py`. Positions are always lon/lat; the
generator projects them.

| Key | Meaning |
|---|---|
| `box`, `w`, `cos` | lon/lat window, pixel width, whether to correct for latitude. **Changing `box` moves every pin and region on the site**, so don't. |
| `labels` | `(TEXT, lon, lat, size, "r"\|"s", angle)`: `r` for land or region lettering, `s` for sea; the Farsi text comes from the `FA` table |
| `ranges` | polylines of lon/lat points; mountains are laid along them |
| `forests`, `deserts`, `hills`, `marsh` | `(lon, lat, half-width°, half-height°, _)` ellipses that get scattered with glyphs |
| `rivers` | lon/lat polylines from the mouth toward the source |
| `creatures` | `(kind, lon, lat, scale, flip, LABEL)`; `LABEL` also picks the variant through `VARIANT` |
| `ships` | `(kind, lon, lat, scale, flip)`: `longship`, `dhow`, `trireme` |
| `cs`, `gscale`, `graticule` | creature/ship scale, glyph scale, graticule step in degrees |

Kinds available in `mapart.CREATURES`: `serpent`, `dragon`, `wyrm`, `mushussu`,
`dahaka`, `bird`, `simurgh`, `garuda`, `anzu`, `wolf`, `minotaur`, `humbaba`,
`div`, `naga`, `scylla`, `makara`. A creature spans about 40–50 local units, and
scales between 1.1 and 1.8 are the approved range. Anything bigger starts to
swallow the land.

## 5. Creatures: who lives where

Each culture's map carries only its own tradition's beings, placed where the
texts put them:

| Map | Creatures (label) |
|---|---|
| persia | SIMORGH over the Alborz, DAHAKA in the Zagros west, DAEVA in the east |
| middle-east | HUMBABA in the cedar forest (Lebanon/Amanus), MUSHUSSU on the upper Tigris, ANZU in the Zagros |
| india | GARUDA under the Himalaya, NAGA in Bengal, MAKARA in the southern sea |
| aegean | SCYLLA at the strait, PYTHON in the Ionian Sea west of Delphi, MINOTAUR on Crete, CHIMERA in Lycia |
| scandinavia | JORMUNGANDR in the North Sea, FENRIR in the mountains, NIDHOGG in the north |
| world | unnamed sea serpent, dragon and great bird as atlas ornament |

Rules for the creatures, all learned from rejected rounds:

- **Silhouettes must read at a glance.** The name sits under each one, but you
  should recognise a bird, a serpent or a horned demon before reading it.
- **Proportions are naturalistic.** Real anatomy, believable limbs and necks,
  no oversized heads, nothing chibi.
- **Aži Dahāka vs Zahhak.** The Avestan *Aži Dahāka* is a three-headed dragon,
  which is what `dahaka` draws. The Shahnameh's **Zahhak** is a *man*: a tyrant
  king with two serpents growing from his shoulders, grim and cruel, never
  smiling. If Zahhak is ever drawn, he must be that human figure, and the label
  must say which tradition is meant. Do not put a dragon over a Zahhak label.
- A creature stays off pins and labels; the collision pass protects them only if
  the creature is placed sensibly in the first place.
- Never invent a creature for a culture. If a being is not in that culture's
  sources, it does not go on its map.

## 6. Places that must be right

Pin coordinates live in the shortcodes (as % of the map box) and in `PINS` in
`genmaps.py` (lon/lat, used only to keep labels clear of them). Real places
go at their real lon/lat. Damavand is a pin in the Alborz chain on the persia
map, and the Himalaya runs as a range across the top of the india map. If you
ever give a landmark peak its own glyph, keep it distinct but no taller than
about two ordinary peaks: Damavand drawn as a giant cone was rejected as too
big.

## 7. Workflow

```sh
python3 tools/fetch_geo.py          # once: Natural Earth 1:50m into tools/geo/
python3 tools/genmaps.py            # all maps, EN and FA
python3 tools/genmaps.py persia     # one map
python3 tools/regions.py persia en  # region lines for the shortcode (and fa)
```

- genmaps rewrites only `static/img/maps/<name>.svg` and `<name>-fa.svg`, and prints
  the pin percentages at the end of a run. Those must not change unless you meant
  to move a pin.
- Region borders come from the lon/lat rings in `tools/regions.py`; paste its
  output into the `{{< map >}}` block in **both** languages. Never write
  `points=` by hand.
- **Look at every map you changed before committing.** Render it to PNG (for
  example `cairosvg` in a throwaway virtualenv, or headless Chrome) and inspect the
  whole map and a zoomed crop of the dense areas. A change that has not been
  looked at is not finished.

## 8. The interactive layer (site, not artwork)

Pins, regions, zoom and the hover cards are HTML/CSS/JS on top of the SVG
(`layouts/shortcodes/map.html`, the map section of `static/css/style.css`,
the map IIFE in `static/js/site.js`). Their contract:

- The artwork and every pin and region share one transformed layer
  (`.myth-map__inner`), so % positions stay on the art at every zoom. Zoom runs
  from 0.4 to 4; `data-zband` (far / mid / near) on `.myth-map` controls how much
  of the pin text is shown.
- **Hover cards keep their on-screen size at every zoom.** `--izr` (1/zoom) cancels
  the layer's scale, and any nudge offset is divided by the zoom before it is
  applied. A card that grows with the map is a bug.
- **Cards are never cut off or buried.** A pin's card shifts sideways to stay inside
  the frame and opens *below* the pin (`.myth-pin--below`) when the top edge would
  cut it. Region text is shown in one shared card (`.myth-map__tip`) above every
  region and pin: each region is its own stacking layer, so a card drawn inside one
  would sit under every border painted after it. The shared card takes no pointer
  events, so the pins under it stay hoverable.
- Region outlines are thin (under 1px, dashed, low opacity); the artwork
  carries the region names, and the outline is only there for hover and focus.

## 9. Print / PDF

The PDF export is the browser's own print dialog (see AI.md 8b and README §8). For
maps it must deliver:

- **The whole map, unzoomed.** On print, the transform is forced to identity, whatever
  zoom or pan the reader left the map in.
- **Every note readable without hover.** The on-map cards are hidden. The pin
  names stay on the map on a dark chip, and every pin and region note is
  printed as a list under the map (`.myth-map__print-notes`). The map is
  never split across pages; the list may flow onto the next one.
- **No phone layout on paper.** Phone breakpoints are written as
  `@media screen and (max-width:…)`, because paper is narrow enough to trigger
  them; a plain `max-width` query once hid the pin names in every PDF.
- Run `python3 tools/uicheck_pdf.py` after any map, media or print change.
