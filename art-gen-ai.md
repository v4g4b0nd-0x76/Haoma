# art-gen-ai.md — Haoma visual style for AI image agents

**Read this before generating any art for Haoma.**  
This file is for cheaper / weaker image models and agents. Follow sizes, palettes, and bans exactly. Prefer matching existing files over inventing a new look.

Related docs (do not contradict them):

| Doc | Use when |
|---|---|
| [AI.md](AI.md) §6, §8, §8a | Site rules, SVG banner rules, brand |
| [MAP-DESIGN.md](MAP-DESIGN.md) | Myth maps only (engraved atlas) — different pipeline |
| [data/themes.json](data/themes.json) | Per-culture accent / bg / anim / pattern |
| Existing art | `static/img/*.svg`, `static/img/media/`, `static/img/atlas/`, `static/img/brand/` |

---

## 1. North star (one sentence)

**A night manuscript of myths:** dark, serious, engraved / silhouette storytelling with one culture accent glow — never cartoon, never bright fantasy poster, never photoreal celebrity faces.

Think: antique endpaper + copper-plate silhouette + slow ember light.  
Not: anime, Disney, Marvel, stock-photo gods, neon cyberpunk, purple-on-white SaaS gradients.

---

## 2. Hard bans (reject / regenerate if any appear)

1. **Cute / children’s book** — smiles, googly eyes, soft rounded “toy” bodies.
2. **Photoreal people** — no real faces, no AI “beautiful influencer” gods.
3. **Copyrighted likenesses** — no film/game/comic characters; evoke texts, not franchises.
4. **Bright saturated fills** — no neon, no flat candy colours, no white backgrounds.
5. **Gold-filled creatures** — gold is for **lines, outlines, rays, ornaments**; fills stay dark ink / olive / dusk.
6. **Busy chrome on cards** — no watermarks, logos, UI mockups, or huge text blocks inside card art (titles live in HTML).
7. **Flashy motion** — no strobe, spin-spam, or sub-2s loops on hero/card art.
8. **Overwriting** — never replace an existing `static/img/*.svg` banner; add a new file and point `themes.json` / front matter at it.
9. **External deps in SVG** — no `<script>`, no external fonts/hrefs, no embedded rasters inside banner SVGs.
10. **Letter-spacing on Farsi** — if type appears in art for FA, do not track/space letters; prefer English-free art or pure ornament.

---

## 3. Global palette language

### 3.1 Always true

| Role | Guidance |
|---|---|
| Night / sky | Near-black to deep dusk (`#0a0c12` … `#1a1520`). Gradients OK. |
| Ground / silhouette | Flat or 2–3 layered dark shapes (`#0d0910`, `#17263a`, `#1b1120`…). |
| Accent | **One** culture accent (from table below) for glow, rays, small ornaments. |
| Gold line | Brand / map gold ≈ `#d4b86e` … `#e0a03a` / `#f6cf7a` — thin strokes only. |
| Mist / evil / distance | Soft translucent ovals, low opacity; never huge fog covering subject. |
| Stars | Tiny sparse dots, not milky-way wallpaper. |

Backgrounds stay under ~#1a lightness. Text (if any) never pure `#ffffff` on large areas — prefer `#cfd2d9` / warm `#d1c9c0`.

### 3.2 Culture accents (match `themes.json`)

Use these accents for glows, small ornaments, and particle colour. Do not invent new culture colours.

| Culture | Accent | Mood notes | Motif cues |
|---|---|---|---|
| **base** (general) | `#9aa3b5` | Neutral steel | Star / pearl, no culture seal |
| **iranian** | `#e0a03a` | Ember gold, dusk violet→amber sky | Rosette, Derafsh geometry, Mehr disc, cypress, Simorgh line-work |
| **norse** | `#7fa8c9` | Cold sea steel | Longship silhouette, aurora wash, sparse stars, fjord ridges |
| **greek** | `#c98a5a` | Warm bronze | Meander strip, temple silhouette, olive / sea |
| **mesopotamian** | `#6f8fd6` | Lapis dusk | Zigzag / reed, cedar trunks, night blue-green |
| **indian** | `#d9708f` | Lotus dusk rose | Waves / mandala hint, soft pink accent only as glow |

Page particle anim (site chrome, not the image file): `fall` · `drift` · `rise` · `none` — see themes. Card fallback uses the same particle idea + culture lattice/seal from `static/img/atlas/*-motifs.svg`.

### 3.3 Brand gold (logo / cover only)

- Gradient gold `#f6cf7a` → `#d9972c`
- Flame highlight `#fff4cf`
- Night plate `#14161a`
- Ember rubric `#c0503a` (decorative only, not body text)

Logo art stays gold-on-night. Culture page art uses **culture accent**, not logo gradient, unless the piece is brand chrome.

---

## 4. Style recipes (how to draw)

### 4.1 Silhouette epic (banners, hero, most posters)

1. Full-bleed dark sky gradient (2–3 stops).
2. Optional faint stars / slow aurora (norse) / Mehr rays (iranian).
3. **2–3 mountain or architecture silhouette layers** (far → near, darker nearer).
4. One **centred or centre-weighted** subject: figure, ship, disc, flag, bird — readable at small size.
5. One accent glow behind or under the subject (radial, soft).
6. Tiny secondary story details at edges (eyes in rock, mist, sparks) — low contrast.
7. Keep the **horizontal centre** interesting: hero CSS uses `object-fit: contain` with a blurred duplicate behind — empty centre looks broken.

**Reference files:** `static/img/norse.svg`, `static/img/iranian-epic-derafsh.svg`, `static/img/greek.svg`, `static/img/mesopotamian.svg`, `static/img/indian.svg`, `static/img/base.svg`.

### 4.2 Engraved night atlas (maps only)

Follow [MAP-DESIGN.md](MAP-DESIGN.md). Do **not** freehand map creatures in Midjourney style — use `tools/genmaps.py` / `tools/mapart.py`.

### 4.3 Literary seal / motif (card fallbacks, atlas nodes)

Geometric, flat, high-contrast **mask-friendly** white-on-transparent line art (rosette, meander, zigzag, waves). See `static/img/atlas/*-motifs.svg`. Sparse, regal, not sticker-cute.

### 4.4 Scene plates (in-article figures / slider frames)

Slightly taller than banners. Same palette. Example: `static/img/media/cedar-forest.svg` — layered trees, mist bands, tiny human silhouettes for scale, hidden face in canopy. Story first, face second.

### 4.5 Character key art (for `card_bg` or posters)

- **Three-quarter or profile silhouette** preferred over full frontal portrait.
- Head + shoulders or full figure with **large negative night** around them.
- Attributes from the **text** (Mehr: covenant / light / horse; Zarathustra: fire / three sparks; Rostam: mace / Rakhsh) — one or two symbols max.
- No speech bubbles, no modern weapons, no anachronistic armour chrome.
- Face: simplified planes or full silhouette — not skin-pore realism.

---

## 5. Exact sizes & formats (persist these)

Use the slot you were asked for. Wrong aspect = reject.

| Slot | Pixel / viewBox | Aspect | Format | Max size | Notes |
|---|---|---|---|---|---|
| **Culture / page hero banner** | `1200 × 300` | **4:1** | SVG preferred | ≲ 20 KB SVG | `viewBox="0 0 1200 300"`; CSS anim only; subject near centre |
| **Home cinema slide** | same as banner | 4:1 | SVG | ≲ 20 KB | Same files as culture banners |
| **In-article scene / slider still** | `960 × 540` | **16:9** | SVG or PNG/WebP | SVG few hundred KB; raster ≲ 400 KB | Example cedar plates |
| **Article / category card media** | **800 × 450** (preferred) or 960×540 | **16:9** | PNG/WebP **or GIF** | Static ≲ 350 KB; GIF ≲ 1.5 MB | Front matter `card_bg` + `card_bg_kind` |
| **Card GIF loop** | **800 × 450** | 16:9 | GIF | ≲ 1.5 MB | 6–12 fps; 2–4 colours + dither sparingly; loop seamless; prefer MP4 if >1 MB (then not for `card_bg` — use static keyframe or compress GIF) |
| **Character portrait (poster)** | **1080 × 1350** | **4:5** | PNG/WebP | ≲ 600 KB | Vertical; for social / library; not the list-card crop |
| **Character square** | **1024 × 1024** | 1:1 | PNG/WebP | ≲ 500 KB | Optional alternate |
| **Podcast cover** | **3000 × 3000`** | 1:1 | JPG from SVG | < 512 KB | Brand pipeline — see AI.md §8a |
| **OG / share image** | **1200 × 630`** | ~1.91:1 | PNG | ≲ 500 KB | Brand / episode share |
| **Atlas motif seal** | **320 × 320`** | 1:1 | SVG | tiny | White strokes, transparent bg, maskable |

### 5.1 How the site crops (so you compose correctly)

| Placement | CSS behaviour | Compose for |
|---|---|---|
| Hero `.hero-art .sfg` | `object-fit: **contain**` | Full 4:1 scene visible; centre-weighted |
| Hero `.sbg` | blurred cover of same art | Extra margin OK |
| Card media `.art img` | `object-fit: **cover**`, band ~**150–200 px** tall | Keep subject in **safe centre 70%**; edges may clip |
| Article without `card_bg` | narrow seal column ~92 px | No custom art needed |
| Category card art | ~148 px tall band | Wide landscape read |

**Safe zone for card art:** keep faces / main symbol inside the middle 70% width and middle 80% height of the 16:9 frame.

### 5.2 File names & paths

- Lower-case `a-z0-9.-` only.
- Banners: `static/img/<culture>.svg` or `<culture>-gen.svg` / descriptive `-epic-….svg`.
- Card / media: `static/img/media/<slug>-card.png` or `<slug>-card.gif`.
- Never commit secrets; credit licence on the page (CC BY-SA for original project art unless stated).

Front matter for cards:

```yaml
card_bg: "media/mehr-card.gif"
card_bg_kind: gif          # static | gif
```

---

## 6. Animation rules

### 6.1 SVG banners (preferred for hero)

- Animation **only** via CSS `@keyframes` inside the SVG `<style>` (works in `<img>`).
- Always include:
  ```css
  @media (prefers-reduced-motion: reduce){*{animation:none!important}}
  ```
- Loop length **6–30 s** (slow). Opacity / translate / gentle skew OK. No flicker.
- Examples of approved motions: aurora drift, ship bob, flag wave, rising embers, slow ray spin (very slow, e.g. 140 s), mist drift, twin star twinkle.

### 6.2 Card GIFs

- Seamless loop, calm motion (embers, shimmer, slow parallax silhouette — not action fight cycles).
- Limited palette keyed to culture accent + night.
- Site loads GIFs with `data-gif` (plays when in view; print uses first-frame still).

### 6.3 Do not animate

- Map SVGs from genmaps (static engraved).
- Brand wordmarks.
- Atlas motif seals (CSS mask only).

---

## 7. Prompt templates (copy, fill braces)

### 7.1 Hero banner (SVG brief or raster→trace)

```
Haoma myth banner, 1200x300 extreme landscape, dark night manuscript style,
{culture} accent glow {accent_hex}, 2-3 silhouette layers of {terrain},
centred {subject from primary texts}, sparse stars, soft radial glow,
engraved silhouette not cartoon, no text, no watermark, no photoreal face,
big empty dusk sky, serious tone, slow epic atmosphere
```

### 7.2 Character card media (16:9)

```
Haoma list-card art 800x450 16:9, dark {culture} night palette accent {accent_hex},
{character name} as silhouette or simplified mythic figure, attribute: {1-2 symbols},
centre-weighted safe zone, large negative space, no title text, no UI,
engraved dusk mood, not anime, not photoreal, not cute
```

### 7.3 Character poster (4:5)

```
Haoma character poster 1080x1350, vertical, night manuscript, {culture} accent {accent_hex},
{character} from {source text}, symbolic not photoreal, silhouette+glow,
ornament hint ({motif}), no logo, no modern clothing, museum-epic seriousness
```

### 7.4 Animated GIF card

```
Haoma card loop 800x450, 8fps seamless, dark {culture} tones + {accent_hex} particles,
slow {embers|shimmer|aurora|flag wave}, silhouette {subject} almost still,
no flash, limited colours, myth manuscript mood
```

### 7.5 Negative prompt (always append)

```
cartoon, chibi, anime, disney, marvel, photoreal face, stock photo, neon,
white background, watermark, logo, UI, text, letters, cute smile, glossy 3d,
purple gradient SaaS, oversaturated, busy collage
```

---

## 8. Per-culture subject bank (safe defaults)

Use primary-text cues; do not invent pop-culture mashups.

| Culture | Safe banner / card subjects |
|---|---|
| Iranian | Mehr disc & rays; Simorgh line; Damavand; Derafsh Kaviani geometry; cypress; fire with three sparks; serpent Ahriman as **line**, not gore |
| Norse | Longship on dark sea; aurora; ridge line; sparse runes as **tiny** ornaments only |
| Greek | Temple / column silhouette; meander border hint; olive / dark sea; bronze accent |
| Mesopotamian | Cedar trunks & mist; reed zigzag; night river; lapis accent (not gold-filled beasts) |
| Indian | Lotus dusk geometry; soft wave motif; temple silhouette; rose accent glow |
| Base | Abstract night + steel accent; star / pearl; no culture-specific deity |

---

## 9. Agent checklist (tick before delivering)

1. [ ] Correct **slot size / aspect** from §5  
2. [ ] Culture accent matches `themes.json`  
3. [ ] Dark night mood; no white canvas  
4. [ ] Subject centre-weighted for contain/cover  
5. [ ] No banned style from §2  
6. [ ] SVG banners: CSS-only anim + reduced-motion rule + ≲20 KB  
7. [ ] Card GIF/static: `card_bg` + `card_bg_kind` documented  
8. [ ] New filename; did **not** overwrite existing banner  
9. [ ] Licence / credits line ready for the page  
10. [ ] Maps? Stop — use [MAP-DESIGN.md](MAP-DESIGN.md) instead  

---

## 10. Weak-model survival tips

- **Fewer objects.** One subject + ground + sky beats five heroes.
- **Silhouette first.** If the face fails, drop to profile/silhouette + attribute.
- **Match a reference file.** Open `static/img/norse.svg` or `iranian-epic-derafsh.svg` and copy layering (sky → glow → far ridge → near ridge → subject).
- **Desaturate.** If output looks like a game splash, multiply a dark night overlay and keep only accent highlights.
- **Crop for cards.** Export 16:9; do not squeeze a 4:5 poster into the card slot.
- **When unsure:** generate a **static** 800×450 card plate; skip GIF until the still reads clearly at 200 px height.

---

## 11. Where this art lands in the product

| Asset | Wired by |
|---|---|
| Culture banner SVG | `data/themes.json` → `banner` |
| Card image/GIF | page front matter `card_bg` / `card_bg_kind` (editor form) |
| Scene plates | shortcodes `fig`, `slider`, `scrollplay` under `static/img/media/` |
| Atlas seals | `static/img/atlas/<culture>-motifs.svg` (CSS masks) |
| Maps | `tools/genmaps.py` only |

End of brief. If a request conflicts with this file, **follow this file** unless a human explicitly overrides it.
