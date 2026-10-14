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
8. [Exporting a page as PDF](#8-exporting-a-page-as-pdf)
9. [Deploying to GitHub Pages](#9-deploying-to-github-pages)
10. [The published editor panel](#10-the-published-editor-panel)
11. [Verification checklist](#11-verification-checklist)
12. [Editing and contributing](#12-editing-and-contributing)
13. [Licences](#13-licences)

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
| **Web editor** | Open the repo in a **Codespace** to run that same editor in the browser, no local install. See §5. |
| **Rich layouts** | Sliders, grids, infoboxes, hover notes, figures, maps, play-on-scroll GIFs, Farsi verse couplets — all via shortcodes. |
| **PDF export** | Every page offers an export that prints to PDF from the browser, keeping the page's own background and theme. See §8. |

### The sections of the site

Every route below exists in both languages (`/fa/…` mirrors `/…`); Farsi is RTL throughout.

| Section | Path | What it is |
|---|---|---|
| **Home** | `/` | The cinematic landing page: culture banners, the latest episodes, and one tab per culture listing its characters, stories and history. |
| **Cultures** | `/cultures/` | Index of every culture. |
| **Culture** | `/cultures/<culture>/` | A culture's landing page: its quote and tagline, then cards for its sections. |
| **Characters** | `/cultures/<culture>/characters/` | Profiles of gods, heroes and beings. |
| **Stories** | `/cultures/<culture>/stories/` | Myth summaries and retellings. |
| **History** | `/cultures/<culture>/history/` | Historical context and scholarship. |
| **Episodes** | `/episodes/` | The podcast: numbered episodes with audio, show notes, script and media credits. |
| **Library** | `/library/` | Everything in `static/library/` — downloadable PDFs and Markdown. |
| **Guide** | `/guide/` | A live demo of every writing component. Read it before editing content. |
| **About** | `/about/` | What the project is and how it is sourced. |
| **Editor panel** | `/tools/` | The editor's interface published as a static file. Not linked from the site; see §10. |

> **Read next.** This README is the human guide. `AI.md` is the complete technical reference — every shortcode attribute, the editor's API and safety model, the page grid, the brand rules and the exact verification commands. When the two overlap, `AI.md` is the detailed one.

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
# Open http://localhost:8765/ (the port is printed, and usually opened for you)
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
  uicheck_pdf.py          PDF-export and print-sheet assertions
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

### Edit in the browser (GitHub Codespaces)

GitHub Pages serves static files only, so it cannot run `editor.py` — the panel published at `/tools/` has no backend (§10). To get the **real editor** without a local clone, open the repository in a Codespace: **Code → Codespaces → Create codespace on `<branch>`**. The `.devcontainer/devcontainer.json` in this repo installs Hugo (extended) and Python, forwards ports 8765 and 1313, and starts `python tools/editor.py` for you when the editor attaches.

Open the forwarded URL for port 8765 (the editor also prints it — `https://<codespace>-8765.app.github.dev/`) and you get the same editor: drafts, rollback, the map studio, the live Hugo preview, and **Publish & PR** — the codespace carries git credentials, so the branch push works. If the preview pane stays blank, open port 1313's URL directly from the **Ports** tab (forwarded ports are private to your account by default).

Codespaces gives personal accounts a monthly free allowance (compute core-hours + storage) and simply stops when it is used up, with no payment method on file. It also sleeps after a period of inactivity; drafts live on disk in `tools/.drafts/`, so they survive.

---

## 6. Writing components (shortcodes)

Open `content/en/guide/_index.md` (or visit `/guide/` in the running site) for a **live demo** of every component.

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
- **Never overwrite an existing banner.** Add a new file and point `themes.json` at it.
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

## 8. Exporting a page as PDF

Every page that carries content offers an **Export PDF** control, in both languages: the toolbar button on articles, section lists and the library, and an outline button in the home page's intro (the home page has no toolbar).

It calls the browser's own `window.print()`, so **you** pick *Save as PDF*. There is no renderer, no service, no extra copy of the page and no request anywhere — the export stays as static as the rest of the site, works offline, and cannot drift from what the page shows.

What makes the PDF look like the page is the `@media print` block at the end of `static/css/style.css`:

| What | How |
|---|---|
| **Same background and theme** | `print-color-adjust: exact` plus the page's own `--bg`/`--text`, so the culture's colours survive instead of printing a dark site onto white paper. |
| **Full bleed** | `@page { margin: 0 }`; the inset comes from the body padding instead. A browser clips the background to the page box, so a real page margin would be a white frame around a dark article. |
| **Chrome dropped** | Header, nav, rails, toolbar, controls, footer and the animated background are hidden. Breadcrumbs stay, so a loose sheet says where it came from. |
| **Nothing hidden by a control** | Tab strips are flattened — every panel prints, not just the selected one — and scroll rails unclip. A tab or a rail cannot silently drop content. |
| **Paper-sized art** | The banner prints at its 4:1 ratio, and the home hero gets a fixed cover height instead of its on-paper `clamp()` floor. |
| **Useful links** | Prose links print their target in parentheses. |

Sources, figures, tables, maps, verse and infoboxes are kept whole, and headings are not left stranded at the foot of a page.

`tools/uicheck_pdf.py` verifies all of it without producing a file: the control must appear once per page and call `window.print()` exactly once, and under `Emulation.setEmulatedMedia(media="print")` the body must still carry the page's own `--bg`, the chrome must be gone, and the hidden panels must be back.

---

## 9. Deploying to GitHub Pages

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

## 10. The published editor panel

The editor UI (`tools/admin.html`) is one self-contained HTML file with no build step, so it can be published as a plain page alongside the site. The Pages workflow copies it into the Hugo output, so it is automatically deployed at:

```
https://<user>.github.io/<repo>/tools/
```

Nothing on the public site links to it. Its `<head>` carries `<meta name="robots" content="noindex,nofollow">` and it is kept out of the sitemap, so it is reachable only by typing the URL.

Since there is no `editor.py` behind it, `/api/` does not exist. The panel therefore boots into **static mode**: it disables the write controls, hides the empty file panel, and shows one notice saying what this copy is and how to run a real editor (`python tools/editor.py`). It cannot read or change the project — the token it ships with is the literal `__TOKEN__` placeholder, so even a running backend would refuse it.

GitHub Pages cannot run the Python backend at all — it is a static file host. For a working editor without a local clone, use a Codespace (§5).

The build step in `.github/workflows/hugo.yml` does the copy:

```yaml
- name: Copy editor UI to /tools/
  run: |
    mkdir -p public/tools
    cp tools/admin.html public/tools/index.html
```

> To edit the panel itself, change `tools/admin.html` and run `python tools/editor.py` — the server substitutes a fresh token and the panel boots normally. A local `hugo` build never contains `/tools/`; only the workflow adds it.

---

## 11. Verification checklist

Run these before opening a pull request:

```bash
```bash
# 1. Hugo builds cleanly
hugo --quiet --destination /tmp/out
# Also test with a subdirectory baseURL (same output tree, different links):
hugo --quiet --destination /tmp/out-repo --baseURL "https://x.github.io/repo/"

# 2. EN/FA structural parity (must print "0 difference(s)")
python3 tools/parity.py

# 3. No broken internal links (must print "0 broken")
python3 tools/linkcheck.py
# And against the subdirectory build, with --baseURL= (the "=" form is required):
python3 tools/linkcheck.py /tmp/out-repo --baseURL=/repo/

# 4. Python syntax check
python3 -c "import ast; ast.parse(open('tools/editor.py').read())"

# 5. JS syntax check (the editor UI is HTML, so extract its one <script> first:
#    `node --check` cannot read .html)
python3 -c "import re;print(re.findall(r'<script>(.*?)</script>',open('tools/admin.html',encoding='utf-8').read(),re.S)[0])" > /tmp/admin.js && node --check /tmp/admin.js
node --check static/js/site.js && node --check static/js/boot.js

# 6. Page grid (try 1440×980 and 390×844)
python3 tools/uicheck_layout.py 1440 980
python3 tools/uicheck_layout.py 390 844

# 7. Map studio round-trip (needs headless Chrome)
python3 tools/uicheck_map.py

# 8. Culture picker (needs headless Chrome)
python3 tools/uicheck_pick.py

# 9. PDF export and print sheet (needs headless Chrome)
python3 tools/uicheck_pdf.py
```

The `uicheck_*` scripts drive a real browser, so start a server and point them at it first:

```bash
hugo --quiet --destination /tmp/out
python3 -m http.server 8123 --directory /tmp/out &
UICHECK_URL=http://127.0.0.1:8123/ python3 tools/uicheck_pdf.py
```

---

## 12. Editing and contributing

### Where to edit what

| To change | Edit |
|---|---|
| A page's text | `content/<lang>/…` — the same relative path in `en` and `fa` |
| A culture's colours, animation, strip pattern or banner | `data/themes.json` |
| The top navigation | `data/nav.json` |
| Any interface string (buttons, breadcrumbs, footer) | `i18n/en.toml` **and** `i18n/fa.toml` — never inline text in a template |
| Styling | `static/css/style.css` |
| Interaction (slider, notes, culture picker, tabs) | `static/js/site.js` / `boot.js` |
| Layout, or a new component | `layouts/` |
| Banners, maps, images, audio | `static/img/…`, `static/audio/…` — banners and maps are generated, see §7 |

### Add a page

1. Create the file in **both** languages with the same relative path, e.g. `content/en/cultures/norse/stories/yggdrasil.md` and `content/fa/cultures/norse/stories/yggdrasil.md`.
2. Give it front matter: `title`, `tagline`, `grade`, `sources` (at least one), and `reviewed` set to today. Add `wide: true` if it uses a grid or a floated infobox. See §4.
3. Write the body with the shortcodes in §6; the live demo is `/guide/`.
4. Run the checks in §11. `python3 tools/parity.py` must print `0 difference(s)`.
5. Commit one logical change with an imperative message, on a `fix/<topic>` branch.

The **local editor** (§5) does steps 1–3 for you — it has a builder for every component, a live preview, and a **Publish & PR** button.

### Four easy ways to contribute

1. **On any page** — click **Edit this page on GitHub** and propose a change as a pull request.
2. **Issue** — click **Report a correction** to open a prefilled issue.
3. **Full editor, locally** — clone the repo, run `python tools/editor.py`, use **Publish & PR** to create a branch and open a pull request.
4. **Full editor, in the browser** — open the repo in a Codespace (§5) to run the same editor with no local install.

**Rules:**
- Every factual claim needs a `sources:` entry. If you cannot source it, set `grade: draft`.
- Use only public-domain or open-licensed media; record the licence in the page's **Media credits** section.
- Do not invent dates, etymologies, or quotes. Use ranges and note scholarly disagreement.
- Commit style: one logical change per commit, imperative message; use a `fix/<topic>` branch, not `master`/`main`.

See `CONTRIBUTING.md` for the full guide and `AI.md` for agent-specific instructions.

---

## 13. Licences

| Asset | Licence |
|---|---|
| Site text and content | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| Code (templates, scripts, editor) | [MIT](https://opensource.org/licenses/MIT) |
| Third-party media | Listed per-page in **Media credits** (public domain or open-licensed only) |
