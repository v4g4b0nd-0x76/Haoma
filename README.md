# Haoma (هوم)

A bilingual (English + Farsi/RTL) mythology **podcast and wiki** — static [Hugo](https://gohugo.io/) site deployed to **GitHub Pages**. Covers cultures (Norse, Iranian, Indian, Greek, Mesopotamian, …), podcast episodes, and a media library, all built from primary sources.

The name _Haoma_ is the Avestan word for the sacred plant pressed in the Yasna ritual and for the divinity praised in the Hom Yasht (Yasna 9–11). Its Vedic cousin is Soma.

---

## Table of contents

1. [What this site does](#1-what-this-site-does)
2. [Quick start](#2-quick-start)
3. [Project structure](#3-project-structure)
4. [Content model](#4-content-model)
5. [The local editor](#5-the-local-editor)
6. [Writing components (shortcodes)](#6-writing-components-shortcodes)
7. [Themes and visuals](#7-themes-and-visuals)
8. [Deploying to GitHub Pages](#8-deploying-to-github-pages)
9. [Tools live demo (editor on GitHub Pages)](#9-tools-live-demo-editor-on-github-pages)
10. [Verification checklist](#10-verification-checklist)
11. [Contributing](#11-contributing)
12. [Licences](#12-licences)

---

## 1. What this site does

| Feature | Detail |
|---|---|
| **Bilingual** | Every page exists in `content/en/` and `content/fa/`. Farsi is RTL; CSS uses logical properties throughout. |
| **Cultures** | Each culture (Norse, Iranian, Indian, Greek, Mesopotamian) gets its own folder with `characters`, `stories`, and `history` sub-sections. |
| **Podcast** | Episodes are numbered Markdown files with an `audio:` field pointing to an MP3 (local or archive.org). |
| **Library** | PDFs and Markdown files in `static/library/` are listed automatically. |
| **Static only** | No database, no server at runtime. Only Hugo builds it; no other build step. |
| **Local editor** | `python tools/editor.py` — a local web app that edits content with draft/preview/rollback, no IDE needed. |
| **Rich layouts** | Sliders, grids, infoboxes, hover notes, figures, maps, play-on-scroll GIFs, Farsi verse couplets — all via shortcodes. |

---

## 2. Quick start

### Prerequisites

- [Hugo extended](https://gohugo.io/installation/) ≥ 0.139 (`hugo version` should say `extended`)
- Python 3.8+ (for the editor and tooling scripts)
- git

### Run locally

```bash
git clone https://github.com/v4g4b0nd-0x76/Haoma
cd Haoma
hugo server
# Open http://localhost:1313/
```

### Run the local editor

```bash
python tools/editor.py
# Open http://localhost:3000/ (or whatever port it prints)
```

The editor gives you: live preview of the page you are editing, draft saves (nothing touches real files until **Save**), undo/rollback history, theme editor, navigation editor, review dashboard, and a **Publish & PR** button.

---

## 3. Project structure

```
hugo.toml                 Site config: languages (en default, fa RTL), markup
content/en|fa/            All pages — same relative paths in both languages
  cultures/<culture>/     One folder per culture
    _index.md             Culture landing page (must have culture: and cascade:)
    characters/           Character profiles
    stories/              Myth summaries and retellings
    history/              Historical context
  episodes/<nnn-slug>/    Podcast episodes (index.md, numbered)
  library/_index.md       Auto-lists static/library/
  about/_index.md
  guide/_index.md         Live demo of every writing component (read this!)
data/
  themes.json             Per-culture colours, animation, strip pattern, banner
  nav.json                Top navigation links per language
  site.json               {"repo": "...", "branch": "master"}
i18n/
  en.toml  fa.toml        Every UI string — never hardcode text in templates
layouts/                  Hugo templates, partials, shortcodes, render hooks
static/
  css/style.css           All styling (theme colours from data/themes.json)
  js/boot.js  site.js     Culture picker, slider, play-on-scroll, notes, tabs
  img/                    Banners (<culture>.svg), maps/, media/
  img/brand/              Logo SVGs, favicon, podcast cover, share image
  fonts/                  Self-hosted web fonts (no CDN)
  audio/  video/          Episode audio and video clips
  library/                Downloadable PDFs and Markdown
tools/
  editor.py               Local editor server (Python stdlib only)
  admin.html              Editor UI (single-file vanilla JS + HTML)
  genmaps.py              Map artwork generator (Natural Earth data)
  regions.py              Prints region points (lon/lat → %)
  parity.py               EN/FA structural parity check
  linkcheck.py            Internal link and anchor checker
  uicheck.py              Headless-Chrome CDP driver
  uicheck_layout.py       Page-grid assertions
  uicheck_map.py          Map studio assertions
  uicheck_pick.py         Culture-picker assertions
  brand/build.py          Logo regenerator
.github/workflows/hugo.yml  Pages build and deploy on push to master/main
```

> **Never edit** `public/`, `resources/`, `tools/.preview/`, `tools/.drafts/`, `tools/.history/` — they are generated and git-ignored.

---

## 4. Content model

### 4.1 Culture landing page

`content/<lang>/cultures/<culture>/_index.md` **must** contain both:

```yaml
---
title: "Norse Mythology"
culture: norse          # ← required
cascade:
  culture: norse        # ← required (inherits into all sub-pages)
quote: "..."
quoteSource: "..."
tagline: "..."
---
```

Each section folder (`characters/`, `stories/`, `history/`) also needs its own `_index.md` with `cascade: {sec: characters}` (etc.).

### 4.2 Individual content page

```yaml
---
title: "Mehr (Mithra)"
tagline: "Lord of oaths, covenants and light"
grade: "primary text"   # primary text | later compilation | archaeology | modern scholarship | draft
sources:
  - "Avesta, Mihr Yasht (Yasht 10) - primary"
reviewed: 2026-10-12    # ISO date — update when you verify the page
wide: true              # optional: wide article (needed for grids/infoboxes)
---
```

`grade` is shown on every page so readers know how solid the sourcing is.

### 4.3 Episode

`content/<lang>/episodes/<nnn-slug>/index.md`:

```yaml
---
title: "001 · The First Giant"
date: 2026-10-12
audio: audio/001.mp3    # or a full https:// URL (archive.org recommended for large files)
culture: norse
grade: draft
sources: ["Prose Edda, Gylfaginning", "Poetic Edda, Voluspa"]
reviewed: 2026-10-12
---
Show notes here.

## Script
Full script here.

## Media credits
Every asset with its licence.
```

### 4.4 Translations

Pages are linked as translations when the relative path is **identical** in `content/en/` and `content/fa/`. A stub should be titled `TODO translate: …` and graded `draft`. Machine-translated text stays `draft` until a native reader reviews it.

---

## 5. The local editor

Start with:

```bash
python tools/editor.py
```

### What the editor does

| Feature | How it works |
|---|---|
| **Draft saves** | Edits go to `tools/.drafts/` first. Nothing touches real files until you click **Save**. |
| **Live preview** | Hugo serves `tools/.preview/` (saved files + current drafts). The UI auto-navigates to the page you are editing. |
| **Rollback** | Every save backs up the previous version in `tools/.history/`. One click restores it. |
| **Theme editor** | Visual editor for `data/themes.json` — colours, animation, strip pattern, banner. |
| **Navigation editor** | Edit `data/nav.json` for both languages. |
| **Review dashboard** | Lists pages with missing translations, unreviewed content, and draft grades. |
| **Publish & PR** | Commits on a `fix/<topic>` branch and opens a GitHub pull request. |
| **Map studio** | Click-to-drop pins, drag regions/borders on the actual map artwork. |
| **Insert builders** | Toolbar buttons generate slider, grid, infobox, figure, note, map, verse shortcodes. |

### Security

The editor binds to `127.0.0.1` only. Every API call requires the per-run token (`X-Token` header or `?t=` query param). Only the paths `content data i18n layouts static assets hugo.toml` are writable.

---

## 6. Writing components (shortcodes)

Open `content/en/guide/_index.md` (or visit `/en/guide/` in the running site) for a **live demo** of every component.

| Component | Syntax |
|---|---|
| **Hover note** | `{{</* note text="Explanation" */>}}highlighted words{{</* /note */>}}` |
| **Figure** | `{{</* fig src="img/media/a.jpg" caption="..." align="full\|center\|start\|end" w="40%" */>}}` |
| **Slider** | `{{</* slider autoplay="5" ratio="16/9" */>}}` then `path \| caption` per line, `{{</* /slider */>}}` |
| **Play-on-scroll** | `{{</* scrollplay src="img/media/clip.gif" caption="..." */>}}` |
| **Grid** | `{{% grid cols="2fr 1fr" gap="2rem" %}}` … `{{% col %}}…{{% /col %}}` … `{{% /grid %}}` |
| **Infobox** | `{{% infobox side="end" w="33%" title="Quick facts" %}}…{{% /infobox %}}` |
| **Media embed** | `{{</* media src="audio/x.mp3" */>}}` (audio, video, PDF, or link) |
| **Map** | `{{</* map id="m" src="img/maps/persia.svg" height="440px" route="auto" */>}}` + `pin` / `region` lines |
| **Verse couplets** | `{{</* verse lang="fa" source="Ferdowsi, Shahnameh" */>}}` hemistich `\|` hemistich `{{</* /verse */>}}` |

Paths in shortcodes have **no leading slash** and are relative to `static/`. Wide layouts need `wide: true` in front matter.

### Map pins and regions

```
{{< map id="map-x" src="img/maps/persia.svg" height="440px" route="auto" caption="..." >}}
pin x="36.9%" y="25.3%" label="Damavand" note="hover text" color="fire" href="/cultures/iranian/" /
region points="9.4,17.3 20.8,11.4 30.5,17.3" label="Media" note="hover text" color="gold" /
{{< /map >}}
```

Generate `region` points (never write them by hand):

```bash
python3 tools/regions.py <map> <en|fa>
```

---

## 7. Themes and visuals

Each culture has a theme entry in `data/themes.json`:

```json
"norse": {
  "accent": "#7fa8c9",
  "bg": "#12161c",
  "surface": "#1a2029",
  "border": "#273241",
  "text": "#c9ccd3",
  "muted": "#8a8f9a",
  "anim": "fall",
  "pattern": "none",
  "glyphs": "ᚠ ᚢ ᚦ ...",
  "banner": "norse.svg"
}
```

- `anim`: `fall` (snow), `drift`, `rise` (embers), `none`
- `pattern`: `none | meander | rosette | zigzag | waves` (decorative top strip)
- Banner SVGs live in `static/img/`. Rules: `viewBox="0 0 1200 300"`, CSS-only animation, under ~20 KB, dark palette, no external resources.
- Regenerate the brand (logo, favicon, cover) with `python tools/brand/build.py` (requires `fonttools brotli uharfbuzz`).
- Regenerate map artwork with `python3 tools/genmaps.py`.

### Typography

| Role | Latin | Persian |
|---|---|---|
| Display / titles | Cinzel | Lalezar |
| Reading text | Lora | Vazirmatn |
| Interface | system-ui | Vazirmatn |
| Verse / poetry | Lora italic | Noto Nastaliq Urdu |

---

## 8. Deploying to GitHub Pages

### Automatic (recommended)

1. Push to `master` or `main`.
2. Go to **Settings → Pages → Source** and set it to **GitHub Actions**.
3. `.github/workflows/hugo.yml` handles the rest — Hugo extended 0.139 is installed and the site is published.

### Manual test build

```bash
# Test with the production baseURL (catches subdirectory link bugs)
hugo --gc --minify --baseURL "https://<user>.github.io/<repo>/"
```

---

## 9. Tools live demo (editor on GitHub Pages)

The editor (`tools/admin.html`) is a self-contained single-file HTML/JS app. It can be served as a **static page** on GitHub Pages at a separate path (e.g. `/tools/`) for demonstration and UI review purposes — without the Python backend it runs in a read-only preview mode, letting anyone browse the admin UI.

The workflow file `.github/workflows/hugo.yml` copies `tools/admin.html` into the Hugo output under `public/tools/index.html` at build time, so it is automatically deployed alongside the main site at:

```
https://<user>.github.io/<repo>/tools/
```

> **Note:** In this static-hosted mode the editor has no backend (no `editor.py`), so saves, commits, and preview do not work. It is a UI demo and style reference only.

To enable this, the build step in `.github/workflows/hugo.yml` includes:

```yaml
- name: Copy editor UI to /tools/
  run: |
    mkdir -p public/tools
    cp tools/admin.html public/tools/index.html
```

---

## 10. Verification checklist

Run these before opening a pull request:

```bash
# 1. Hugo builds cleanly
hugo --quiet --destination /tmp/out
# Also test with a subdirectory baseURL:
hugo --quiet --destination /tmp/out --baseURL https://x.github.io/repo/

# 2. EN/FA structural parity (must print "0 difference(s)")
python3 tools/parity.py

# 3. No broken internal links (must print "0 broken")
python3 tools/linkcheck.py
# And with subdirectory baseURL:
python3 tools/linkcheck.py --baseURL=/repo/

# 4. Python syntax check
python3 -c "import ast; ast.parse(open('tools/editor.py').read())"

# 5. JS syntax check
node --check tools/admin.html   # (extracts and checks the <script> block)

# 6. Page grid (try 1440×980 and 390×844)
python3 tools/uicheck_layout.py 1440 980
python3 tools/uicheck_layout.py 390 844

# 7. Map studio round-trip (needs headless Chrome)
python3 tools/uicheck_map.py

# 8. Culture picker (needs headless Chrome)
python3 tools/uicheck_pick.py
```

---

## 11. Contributing

Three easy ways:

1. **On any page** — click **Edit this page on GitHub** and propose a change as a pull request.
2. **Issue** — click **Report a correction** to open a prefilled issue.
3. **Full editor** — clone the repo, run `python tools/editor.py`, use **Publish & PR** to create a branch and open a pull request.

**Rules:**
- Every factual claim needs a `sources:` entry. If you cannot source it, set `grade: draft`.
- Use only public-domain or open-licensed media; record the licence in the page's **Media credits** section.
- Do not invent dates, etymologies, or quotes. Use ranges and note scholarly disagreement.
- Commit style: one logical change per commit, imperative message; use a `fix/<topic>` branch, not `master`/`main`.

See `CONTRIBUTING.md` for the full guide and `AI.md` for agent-specific instructions.

---

## 12. Licences

| Asset | Licence |
|---|---|
| Site text and content | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Code (templates, scripts, editor) | [MIT](https://opensource.org/licenses/MIT) |
| Third-party media | Listed per-page in **Media credits** (public domain or open-licensed only) |
