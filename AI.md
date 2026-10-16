# AI.md - guide for AI agents working on Haoma (هوم)

Read this before changing anything. It describes the site, the editor, the file formats and the rules that keep both working. Humans can use it too.

## 1. What this project is
Haoma is a bilingual (English + Farsi/RTL) mythology podcast and wiki: wiki-style pages per culture, a podcast section, a media library. It is a **static Hugo site** deployed to **GitHub Pages**. A local **editor** (`tools/`) generates the files for you.

Hard constraints (do not break them):
- **Files only.** No database, no server at runtime, no build step other than `hugo`.
- **Relative URLs only.** The site may live under `/repo-name/`. Use `relURL` / `relLangURL` in templates; never hardcode `/css/...` or a domain. In Markdown, links like `/cultures/norse/` and images like `/img/x.jpg` are fixed up by render hooks.
- **No external requests** (no CDNs, no web fonts, no analytics). Fonts are self-hosted in `static/fonts`.
- **Both languages.** Every user-visible string goes through `i18n/*.toml`; every content page should exist in `content/en` and `content/fa` with the same relative path.
- **RTL safe.** Use logical CSS properties (`inline-start/end`, `margin-inline`), never assume left/right. Never add `letter-spacing` or `text-transform` to Farsi text.
- **Open and honest.** Only public-domain or open-licensed media. Never invent sources, quotes or dates.

## 2. Repository map
```
hugo.toml                 languages (en default, fa RTL), markup settings
content/en|fa/            pages (same relative paths in both languages)
  cultures/<key>/         one folder per culture: _index.md + characters|stories|history/
  episodes/<nnn-slug>/index.md
  library/ about/ guide/
data/themes.json          per-culture theme (colours, animation, strip pattern, banner)
data/nav.json             top navigation per language
data/site.json            {"repo": "https://github.com/you/repo", "branch": "master"}
i18n/en.toml fa.toml      interface strings
layouts/                  templates, partials, shortcodes, markdown render hooks
static/css/style.css      all styling; theme colours come from data/themes.json
static/js/boot.js site.js culture pick, slider, play-on-scroll, notes, tabs
static/img/               banners (<culture>.svg), maps/ for map artwork, media/ for page images and GIFs
static/img/brand/         logo set, favicon, podcast cover, share image (generated, see 8a)
tools/brand/              logo generator (build.py) and its font
static/video/ audio/ library/   MP4/WebM, episode audio, downloadable PDFs and Markdown
MAP-DESIGN.md             map house style, creature rules, workflow, hover and print contract
tools/genmaps.py          map artwork generator (Natural Earth in tools/geo/; art in tools/mapart.py)
tools/mapart.py           engraved monsters/ships/terrain symbols used by genmaps.py
tools/fetch_geo.py        download Natural Earth 1:50m land/rivers/lakes for genmaps
tools/regions.py          prints `region` lines for a map (lon/lat rings -> % points)
tools/editor.py           local editor server (Python standard library only)
tools/admin.html          the editor UI (single file, vanilla JS)
.devcontainer/            Codespace: Hugo (extended) + Python, forwards 8765/1313, starts the editor
tools/uicheck.py          headless-Chrome (CDP) driver (+ `nocache`, see 10)
tools/uicheck_map.py      the editor's map studio, driven without clicking
tools/uicheck_layout.py   the page grid: one shell, one reading column, no overflow
tools/uicheck_pick.py     the culture picker: colours, keyboard, RTL anchoring
tools/uicheck_pdf.py      the PDF export: one control per page, and the print sheet
tools/linkcheck.py        every internal link and anchor in a built site
tools/parity.py           EN/FA structural parity check (see 10, Verify)
.github/                  Pages workflow, issue and PR templates
```
Never edit `public/`, `resources/`, `tools/.preview/`, `tools/.drafts/`, `tools/.history/` (generated, git-ignored).

## 3. Content model
### 3.1 Culture pages
Path: `content/<lang>/cultures/<culture>/<section>/<slug>.md`. Sections used by the home page tabs: `characters`, `stories`, `history` (others are allowed and appear in the sidebar).

`_index.md` of a culture MUST contain both `culture: <key>` and `cascade: {culture: <key>}`; each section `_index.md` MUST contain `cascade: {sec: <section>}`. Without them the theme and the home page tabs break.

```yaml
---
title: "Mehr (Mithra)"
tagline: "Lord of oaths, covenants and light"   # card subtitle
grade: "primary text"      # primary text | later compilation | archaeology | modern scholarship | draft
sources:
  - "Avesta, Mihr Yasht (Yasht 10) - primary"
reviewed: 2026-10-12       # ISO date, update when you verify the page
wide: true                 # optional: wide article, needed for grids/infobox
---
```
Culture `_index.md` also takes `quote`, `quoteSource` (hero line, paraphrase unless public domain) and `tagline`.

### 3.2 Episodes
`content/<lang>/episodes/<nnn-slug>/index.md` with `date`, `culture`, `audio` (path under `static/`, e.g. `audio/002.mp3`, or a full https URL), `grade`, `sources`, `reviewed`. Body: show notes, `## Script`, `## Media credits` (every asset with its licence).

### 3.3 Translations
Pages are linked as translations when the relative path is identical in `content/en` and `content/fa`. A stub should have the title `TODO translate: ...` and be flagged by the editor's Review view. Machine-translated text must be marked `grade: draft` until a native reader checks it.

### 3.4 Evidence and honesty rules for agents
- Every factual claim needs a source in `sources`. If you cannot source it, say so in the page and set `grade: draft`.
- Quote at most a short phrase of any copyrighted text; paraphrase otherwise.
- Do not state dates or etymologies you are unsure about; use ranges and say "scholars disagree".
- After verifying a page, set `reviewed` to today.

## 4. Writing components (shortcodes)
Delimiters matter: `{{< >}}` = raw HTML output, `{{% %}}` = content is parsed as Markdown (use for containers).

| Tool | Syntax |
|---|---|
| Hover note | `{{< note text="Explanation" >}}highlighted words{{< /note >}}` (escape quotes as `\"`) |
| Figure | `{{< fig src="img/media/a.jpg" caption="..." note="hover text" align="full|center|start|end" w="40%" >}}` (`start`/`end` float so text wraps) |
| Slider | `{{< slider autoplay="5" ratio="16/9" >}}` then one item per line `path \| caption`, close with `{{< /slider >}}`. Items may be images, GIFs, MP4, WebM |
| Play on scroll | `{{< scrollplay src="img/media/clip.gif" caption="..." align="full" >}}` GIFs start when 60% visible and restart on re-entry; MP4/WebM play muted and pause off-screen |
| Grid | `{{% grid cols="2fr 1fr" rows="auto" gap="2rem" align="start" %}}` containing `{{% col %}}...{{% /col %}}`; `col` takes `span="2"` and `rowspan="2"` |
| Infobox | `{{% infobox side="end" w="33%" title="Quick facts" %}}...{{% /infobox %}}` floats; text wraps around it |
| Media | `{{< media src="audio/x.mp3" >}}` (audio, video, PDF embed, or link) |
| Map | `{{< map id="map-x" src="img/maps/persia.svg" width="100%" height="480px" theme="dark\|sepia" route="auto" pulse="false" caption="..." >}}` with one **pin** `pin x="58%" y="54%" label="Uruk" note="hover text" color="gold\|fire\|blood\|teal\|silver" href="/optional/page/" /` and/or one **region** `region points="9.4,17.3 20.8,11.4 30.5,17.3" label="Media" note="hover text" color="gold" href="/cultures/iranian/" /` per line, close with `{{< /map >}}` (all attributes optional except a pin's `x`/`y` and a region's `points`). Pins are the dots; regions are the shaded, labelled borders drawn over the artwork — `points` is three or more `x,y` pairs, in order, in % of the map box, so the ring closes itself. `href` makes a pin or region a link to a page (the full text lives there); without it the hover text is all you get. Internal paths get the current-language prefix (`/cultures/x/` → `/fa/cultures/x/` on Farsi); `http(s)://`, `mailto:` and `#anchor` pass through untouched. `route` draws a dashed travel line ("auto" joins pins in order, or explicit `route="58,54 54,47"`). `pulse="false"` stills the pin rings — use it where the points are places rather than events (the world overview). Omit `src` for the procedural parchment map. Ready-made artwork: `static/img/maps/` (`world`, `middle-east`, `persia`, `india`, `aegean`, `scandinavia`, each also `-fa.svg`). **Generate `region` points with `python3 tools/regions.py <map> <en\|fa>`** — never hand-invent them. In the editor, the 🗺 Map button opens the Map Studio (see 9.3). |
| Couplets | `{{< verse lang="fa" source="Ferdowsi, Shahnameh" >}}` then one couplet per line, hemistichs split by `\|`, close with `{{< /verse >}}`. `lang="fa"` sets RTL and the Nastaliq face |

Rules: paths in shortcodes have no leading slash and are relative to `static/`. Wide layouts need `wide: true` in front matter. On screens under 760px grids stack and floats become full width; do not rely on side-by-side layout for meaning. Always give images useful alt text or captions. Live demo: `content/en/guide/_index.md`.

Preset grids the editor offers: 2/3+1/3, 1/3+2/3, 1/2+1/2, 3 and 4 columns, 2x2, header row + 2 or 3 columns, 3 images in a row.

## 5. Themes (`data/themes.json`)
```json
"norse": {"accent":"#7fa8c9","bg":"#12161c","surface":"#1a2029","border":"#273241",
          "text":"#c9ccd3","muted":"#8a8f9a","anim":"fall","pattern":"none",
          "glyphs":"ᚠ ᚢ ᚦ ...","banner":"norse.svg"}
```
- `anim`: `fall` (snow), `drift`, `rise` (embers), `none`.
- `pattern`: `none | meander | rosette | zigzag | waves` (top strip, tinted with `accent`).
- `glyphs`: text strip, e.g. runes. `banner`: file name inside `static/img/` (empty = no banner).
- `base` is the general, no-culture theme. Keep contrast WCAG AA (text on bg >= 4.5:1). Keep the dark, dimmed mood: backgrounds under ~#1a1a1a lightness, text never pure white.
- Theme is applied through `data-culture` on `<html>`; culture pages are fixed to their culture, other pages follow the visitor's culture pick.

New culture checklist: folder + `_index.md` files in both languages (3.1), theme entry, banner, tagline/quote, at least one page per section, translations, Review view clean.

## 6. Banner and art (SVG) rules
- `viewBox="0 0 1200 300"`, `preserveAspectRatio="xMidYMid slice"`; one file, under ~20 KB.
- Animation only with CSS `@keyframes` inside the SVG `<style>` (works when loaded via `<img>`). No scripts, no external `href`, no web fonts, no raster embeds.
- Include `@media (prefers-reduced-motion: reduce){*{animation:none}}` inside the SVG style.
- Palette from the theme (dark gradient sky, 2-3 silhouette layers, one accent glow). Subject must evoke the culture without copying copyrighted art or depicting real people.
- Names: `<culture>.svg` for hand-made art, `<culture>-gen.svg` for editor-generated art. **Never overwrite an existing banner**; add a new file and point `themes.json` at it.
- Culture landing pages and every other page share one hero band: `--hero-h: clamp(500px, calc(25vw + 120px), 700px)` in `static/css/style.css`, applied to `.hero-art` and to `.cine`. It is always at least the banner's own width/4 (so a 4:1 banner fits whole) and never the viewport height, so the first screen still shows what follows. The banner **contains** the band (`.hero-art .sfg{object-fit:contain}`) — nothing is cropped; `.sbg` is a blurred, scaled copy of the same file behind it filling the letterbox. Keep a banner's subject near the horizontal centre so the contained box stays balanced. Do not reintroduce per-page hero heights or a JS fit routine.
- Slow, subtle motion (6-30 s loops). Nothing flashing.
- **Map artwork**: read [MAP-DESIGN.md](MAP-DESIGN.md) first (the approved look, the creature rules and what was already rejected). It lives in `static/img/maps/` (`<name>.svg` English, `<name>-fa.svg` Farsi) and is generated by `python3 tools/genmaps.py` (optional `python3 tools/fetch_geo.py` for 1:50m Natural Earth detail in `tools/geo/`). Terrain symbols, ships and monsters are engraved SVG in `tools/mapart.py`; place them via the `MAPS` table (`creatures`, ranges, forests, etc.) and re-run genmaps — it only rewrites those SVGs. Same palette and no-scripts rules as banners.  **Pin and region positions are percentages of the map box**, and `python3 tools/genmaps.py` / `tools/regions.py` print them for any lon/lat you feed them: `tools/regions.py` holds one lon/lat ring per country or civilisation drawn on a map, re-derives it against that map's own projection, and prints the `region` line for both languages. Change a ring in `regions.py` and regenerate — the same table feeds English and Farsi, so the borders can never drift apart; never hand-write `points=`.

## 7. Navigation and UI strings
`data/nav.json`: `{"en":[{"name":"Cultures","url":"cultures/"}],"fa":[...]}`; `url` is relative to the language root. UI strings live in `i18n/<lang>.toml` as `[key]\n  other = "..."`; add every new key to both files.

**The culture picker in the top bar is a listbox, not a `<select>`.** A native select cannot tint an option with that culture's colour while you hover it, which is the whole point of this control (`layouts/_default/baseof.html`, `.cpick*` in style.css, wired in `site.js`). Each `<li role="option">` carries `data-pick` (the culture key), `data-href`, `data-name`, and inline `--c` — that culture's main colour from `data/themes.json` — plus `--pat`, its motif (`--m-meander|rosette|zigzag|waves`; `--m-star` for the general box). The wrapper `#culture-pick` carries the colour of the culture *in force*, which is what tints the trigger and the panel frame, and `paintPick()` copies the chosen option's `--c`/`--pat` onto it and sets `aria-selected`. The first entry is the **general box**: neutral `#9aa3b5`, star-marked, divided off from the cultures. Keep the accessibility contract when touching it — `aria-haspopup`/`aria-expanded` on the button, `role="listbox"` on the panel, arrows move focus, Enter picks, Escape closes and returns focus, a click outside closes — and keep the panel anchored to the trigger's *inline-end* edge so it opens toward the page centre in both directions.

## 8. Media
- Images/GIFs: `static/img/media/`. Video: `static/video/` (MP4 H.264 or WebM, muted loops; prefer MP4/WebM over GIF above ~1 MB). Audio: `static/audio/`. PDFs/Markdown: `static/library/` (listed automatically in the Library).
- Lower-case file names, `a-z0-9.-` only. Keep the repo under ~1 GB; host long audio on archive.org and put the full URL in `audio:`.
- Record the licence and author of every asset in the page's "Media credits".

## 8a. Brand and typography (Haoma)
**Name.** Haoma (هوم) is the Avestan word for the sacred plant pressed in the Yasna ritual and for the divinity praised in the Hom Yasht (Yasna 9-11); the Vedic cousin is Soma. Use "Haoma" in English prose and "هوم" in Farsi. Do not translate or respell it.

**Logo set** (`static/img/brand/`, all SVG unless noted):
- Mark `haoma-mark.svg`: the Nastaliq هوم monogram in gold, inside a double-ruled square frame. It is the icon of the brand.
- English wordmark in `haoma-logo.svg`: HAOMA in the display serif (Cinzel-style capitals) with a cuneiform wedge rule beneath.
- Persian wordmark in `haoma-logo-fa.svg`: هوم in Nastaliq with the same cuneiform wedge rule beneath. The mark sits on the right in RTL.
- `favicon.svg` plus the raster icons `favicon-32.png`, `favicon-192.png`, `favicon-512.png` and `apple-touch-icon.png` (the mark on a dark rounded square), `haoma-mark-512.png` (mark at 512 px), raster wordmarks `haoma-logo-en.png` and `haoma-logo-fa.png`, `haoma-cover.svg` + `haoma-cover-3000.jpg` (podcast cover, 3000x3000, under 512 KB), `haoma-og.svg` + `haoma-og.png` (1200x630 share image). The cover and share image still carry the earlier plant-and-ring emblem.
- The site header and hero use the inline partial `layouts/partials/logo.html` (`{{ partial "logo.html" (dict "v" "word" "id" "h") }}`; `v` is `word` (wordmark text only — what the header and hero use), `full` (mark + wordmark lockup) or `mark` (mark alone); give every use on a page a different `id`). The mark appears as the site icon only (favicon/apple-touch), never beside the wordmark. Never retype the wordmark in a font.
- `tools/brand/build.py` still generates the previous logo generation (the wedge wordmark and the plant-and-ring emblem). It has not been updated to the set above, so do not run it until it is, or it will revert the brand. The cover and share image are exported from their SVGs with `@resvg/resvg-js` or Inkscape: cover 3000x3000 to JPEG (quality ~90, keep under 512 KB), share image 1200x630 PNG.

**Brand colours.** Haoma gold `#f6cf7a` to `#d9972c` (gradient), stem gold `#e8b455`, flame highlight `#fff4cf`, night `#14161a`, ember `#c0503a` (token `--rubric`). Ember on night is only 3.8:1, so use it for large or decorative marks, never for body text. Culture themes keep their own accents; the logo always stays gold.

**Logo rules.** Clear space of at least the height of the mark's frame on all sides. Minimum size: full lockup 28 px high, mark 16 px (use the favicon version below that). Place on dark backgrounds or a dark plate. Do not recolour, stretch, outline or add shadows.

**Type roles.**
| Role | Latin | Persian |
|---|---|---|
| Wordmark | custom wedge letters (SVG) | Nastaliq outlines (SVG) |
| Display / titles | Cinzel (inscriptional capitals) | Lalezar |
| Reading / section heads | Lora | Markazi Text (Google Font, self-hosted in `static/fonts/`) |
| Interface | system-ui | Vazirmatn |
| Couplets / poetry | Lora italic | Noto Nastaliq Urdu (`static/fonts/nastaliq.woff2`), couplets only, never body text |

**Persian text rules.** No `letter-spacing` or `text-transform` on Farsi (breaks joining); line-height about 2.1 (2.7 for Nastaliq couplets); use the half-space (ZWNJ, U+200C) in compounds; use Persian digits and punctuation (۰-۹ « » ، ؛ ؟) in Farsi text; keep first hemistich on the right.

**Ornament system** (all CSS, tinted by the active theme accent): a headpiece under every page title (`--m-orn` mask on `article h1::after`), eight-pointed star list markers (`--m-star`), the couplet cartouche (`.verse`), an optional drop cap (front matter `dropcap: true`, English only), and the pearl ring and star-cornered frame in cover art. Add new ornaments as small SVG masks, not images, so they follow the theme. Live demo: `content/en/guide/typography.md`.

## 8b. Page grid and spacing
Three tokens in `:root` define the whole layout; change them there and never inline a width:

| token | value | what it fixes |
|---|---|---|
| `--shell` | `1320px` | every page container. `.layout` and `.wrap` share it, so the home sections and the article pages use the same box |
| `--aside` | `210px` | both rails — the culture nav and the on-page table of contents |
| `--col` | `772px` | the reading column: shell − 2 gutters − 2 rails − 2 gaps |

`.layout` is a **three-column grid**, `var(--aside) minmax(0,var(--col)) var(--aside)`, and `aside.side` / `article` / `aside.toc` are placed *explicitly* (`grid-column:1|2|3`, `grid-row:1`). A page with no table of contents simply leaves the third slot empty, so the reading column starts at the same place on every page in both languages and at every width: 250px in from the content edge (210 rail + 40 gap). `article.wide` spans `2/-1` and ends flush with the shell. Do not reach for `margin:0 auto` or a `ch` width here — the column is the measure, and an RTL page mirrors it exactly (which is why `uicheck_layout.py` judges the rail offset rather than the raw x).

Prose never exceeds `--col`, including inside a wide article (`article.wide > p,ul,ol,blockquote`); maps, grids, sliders and figures may use the full article width. Vertical rhythm comes off the `--s1..--s5` scale only: 16px between paragraphs, 24px around a content block, 40px above a section heading and above `sources`.

Two cascade traps to keep in mind. **Responsive overrides live at the bottom of style.css** — the `article h1` scale rule sits in the reading section, so a `@media` block written above it is silently overridden and headings stayed full size on phones. And **`html[dir=rtl]` rules outrank plain class selectors**, so an RTL margin can beat a mobile reset; when you reset a floated box for small screens, list the RTL selector too.

A third block closes the file: `@page{margin:0}` and `@media print` are the PDF export (README §8). They are the only paper-only rules, so they cannot affect screen rendering, but keep their two invariants. `@page{margin:0}` is deliberate — a browser clips the canvas background to the page box, so any real page margin prints as a white frame around a dark article; the inset comes from `body{padding}` instead. And `print-color-adjust:exact` with the page's own `--bg`/`--text` is the whole point of the export, so a new UI element must either be hidden for print (the chrome list) or checked that it still prints in the theme (the tab panels and scroll rails are flattened because a control must not hide content from paper). Two more rules for paper. **Phone breakpoints are `@media screen and (max-width:…)`**: an A4 sheet is narrow enough to match a plain `max-width:760px`, which once collapsed every grid and hid the map's pin names in the PDF. And **a browser snapshots the page the moment print starts**: it does not wait for an image that only begins loading then. That is why the PDF button awaits `haomaPrintPrep()` in `site.js` (it turns lazy images eager, decodes them, and gives each GIF a decoded first-frame still, `.gif-still`, which is what prints) before calling `window.print()`. Anything new that loads late must join that preparation.

## 9. The editor (`python tools/editor.py`)
Needs Python 3.8+, git, hugo. Binds to 127.0.0.1; every API call needs the per-run token (`X-Token` header or `t` query parameter); only `content data i18n layouts static assets hugo.toml` are writable.

**In a GitHub codespace** the editor is reached through a forwarded https hostname, not localhost, so `forward_url()` builds every URL it hands out from `CODESPACE_NAME` + `GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN`. That covers the editor's own printed URL and `GET preview` (the UI takes its iframe base from `url`), and `preview_start()` passes `--baseURL <forwarded>/ --appendPort=false` so the preview's own links point back at the forwarded host instead of the reader's machine. A codespace has no browser, so it skips `webbrowser.open`, and a bind failure (the editor already running — `postAttachCommand` re-runs on every attach) prints a line and exits instead of a traceback.

**Keep Hugo out of a devcontainer feature.** A feature is pulled from `ghcr.io` while the image builds, and a failed pull makes Codespaces fall back **silently** to a recovery container (`/workspaces/.codespaces/shared/merged_devcontainer.json` then carries `CODESPACES_RECOVERY_CONTAINER:true` and an Alpine image) with no Hugo, no forwarded ports and no `postAttachCommand` — the codespace still reports `Available`, so nothing tells you. `.devcontainer/setup-hugo.sh` runs from `postCreateCommand` instead, pinned to the workflow's version, and a failure lands in the creation log where you can see it.

`gh cs ssh` needs an ssh server *inside* the container and the devcontainer image above carries none, so the CLI cannot get a shell — it reports `failed to start SSH server`. VS Code and the browser editor do not need it. Add `ghcr.io/devcontainers/features/sshd` only if you specifically want CLI access, and accept the `ghcr.io` pull risk described above. (The recovery container is the confusing part: it is Alpine and *does* ship sshd, so `gh cs ssh` works there and only there — the one place nothing else works.)

### 9.1 Safety model - keep these invariants
1. **Nothing reaches the project until Save.** Edits are *temporary drafts* stored in `tools/.drafts/` (survive page switches and reloads). `POST /api/apply` moves drafts into real files.
2. **Preview runs on a copy** (`tools/.preview/` = saved files + drafts). `hugo server --source tools/.preview`. The UI navigates the preview to the page being edited (`pageUrl()` in admin.html); do not re-add `--navigateToChanged`, it jumps to whichever file changed last.
3. **Every save is reversible.** Before a real write the previous content is backed up in `tools/.history/` under a change id; `POST /api/rollback` restores it. All writes must pass a change id (`x`) and label (`l`).
4. Structured editors (themes, navigation, settings) edit a draft of their JSON file; they never share mutable state.
5. Generated assets never overwrite existing files.

### 9.2 API (JSON unless noted)
`GET tree` · `GET file?path=` (text) · `PUT file?path=&x=&l=` · `DELETE file?path=&x=&l=` · `POST upload?path=&x=&l=` (raw body, under `static/`) · `PUT draft?path=` (raw body) · `POST draftdel?path=` · `POST discard?path=` · `GET drafts` · `POST apply` `{paths,x,l}` · `POST resync` · `GET raw?path=&ws=1` · `GET history` · `POST rollback[?id=]` · `GET audit` · `POST preview?a=start|stop`, `GET preview` · `GET check` (hugo build of saved files) · `GET git` · `GET diff` · `POST commit` `{message,branch,push,newBranch}` · `POST pull` · `POST revert`.

### 9.3 Extending the editor
`tools/admin.html` is one file: state (`drafts`, `orig`, `files`), views in the `VIEWS` table, insert builders `bSlider bGrid bInfobox bFig bPlay bNote bMap bVerse` (use `modal()` and `wirePicker()`). `modal(title, html, onOk, opts)` takes optional `opts` — `{wide:true, ok:'Label'}` for a full-width dialog with its own primary-button label; plain three-argument calls are unchanged. To add a view: write `pName()`, register it in `VIEWS`, make any edit go through `setDraft()` / `setJ()` and any save through `commit()`. Use unique element ids (modal fields are prefixed `m_`, the map studio's `mp_`). Add a builder when you add a shortcode.

**The map studio (`bMap`) is more than an inserter.** It is called as `bMap({ins, ta, wide})`: it scans `ta.value` for `{{< map >}}…{{< /map >}}` blocks, and if the caret sits inside one (or the page holds maps) a chooser at the top lets you edit that block in place — parsing it with `parseMap()` and rewriting exactly the block range on OK, so nothing else in the file moves. On the canvas the artwork is drawn at its own aspect ratio, so a click's % matches what the site will render: **click to drop a pin, drag to fine-tune**; **Regions** mode selects a shaded area (or a row in the list) and drags its corners, while *Start a new border* + clicks draws a new polygon (Esc cancels, Close border needs 3+ corners). The right column covers the whole shortcode surface — artwork gallery from `static/img/maps/` with an EN/FA toggle that follows the page's language, `width`, `height`, `theme`, `pulse`, `route` (off / join pins / custom points), `caption`, `id` — and it emits lines in the same attribute order the content already uses, so re-saving a map you did not change produces no diff. `tools/uicheck_map.py` drives all of this in headless Chrome.

## 10. Workflows for agents
Add a page: create the file in both languages with the front matter above, sources and grade, then `hugo --quiet` must pass. Add a shortcode: template in `layouts/shortcodes/`, CSS in `style.css` (RTL-safe, mobile rule under 760px), JS only if needed in `site.js` (guard for missing `IntersectionObserver`, respect reduced motion), documentation row in section 4 and the guide page, and an editor builder.

Verify before finishing:
- `hugo --quiet --destination /tmp/out` builds with no errors, also with `--baseURL https://x.github.io/repo/` (check asset links start with `/repo/`).
- EN and FA pages both render; RTL layout checked.
- No new external requests; no absolute URLs; images have alt/captions.
- `python3 -c "import ast;ast.parse(open('tools/editor.py').read())"` and a JS syntax check of the script in `tools/admin.html` (`node --check` cannot read .html, so extract the single `<script>` first — the command is in README §11).
- Editor changes: `python3 -c "import ast;ast.parse(open('tools/editor.py').read())"`, a `node --check` of the script extracted from `tools/admin.html`, and — for anything you can only reach by clicking — `python3 tools/uicheck_map.py` (headless Chrome over CDP against a running `tools/editor.py`): edits stay drafts, the builder round-trips its own output, Save writes, rollback restores, drafts survive reload.
- Any new page or section: `python3 tools/parity.py` must print **0 difference(s)**. It walks `content/en` against `content/fa` and compares the file set, front-matter keys, heading depths, link targets (the `/fa/` prefix ignored), the shortcode sequence and its static parameters, pin/region line counts, the number of `sources` cited and the media paths a slider points at — and only reports a body-size gap when one side is a stub. It also checks the two other places EN/FA drift: `i18n/*.toml` must define the same keys, and no template may bake English into a text node (`HARDCODED` — this is what catches a `>Home<` or `>scale<` that would render untranslated on every Farsi page). Word counts drift ~10% between languages and are not a bug; a structural difference is. `-v` also lists every file that matches. Add a check here whenever you fix a new class of EN/FA divergence.
- **Strings belong in `i18n/en.toml` + `i18n/fa.toml`, never inline in a template.** Every reader-visible word in `layouts/` goes through `{{ i18n "key" }}` — breadcrumbs, the footer licence, map labels, tool buttons. When you add a key, add it to *both* language files (parity.py fails otherwise). `{{ i18n "key" | default "English fallback" }}` is the established pattern in shortcodes.

- `python3 tools/linkcheck.py` must print **0 broken** — and again with `--baseURL=/repo/` against a `hugo --baseURL https://x.github.io/repo/` build, because that is the only way to catch a root-absolute link. It resolves every internal `href`/`src` in the output tree and checks fragments too. **The rule behind it: a path starting with `/` is passed through untouched by Hugo's `relURL`/`relLangURL`, so the baseURL path is never applied** and the link breaks whenever the site is served from a subdirectory. Trim it first — `relLangURL (strings.TrimPrefix "/" $p)` — which is why `layouts/shortcodes/map.html` (pin and region hrefs) and `layouts/_default/_markup/render-link.html` (every Markdown link) do so. Follow that pattern for any path that comes out of front matter or a body.
- `python3 tools/uicheck_layout.py [width height]` must exit 0 (try 1440×980 and 390×844). It asserts one shell for `.layout` and `.wrap`, one reading column at the same rail offset in EN and FA, prose inside that column, every `:root` token defined and `box-sizing:border-box` in force, and no horizontal overflow. The token check exists because **a stray `}` anywhere in style.css silently swallows the following rule** — one put `*{box-sizing:border-box}` inside a bogus selector and made every container 48px too wide before anything looked obviously wrong.
- `python3 tools/uicheck_pick.py` must exit 0: the trigger names and tints itself from the culture in force, the general box leads the list, every option lights in its own colour on hover (dot, sigil motif, wash, label), the keyboard drives the listbox, picking navigates and switches the theme, and in Farsi the panel hangs off the trigger's inline-end edge and stays inside the viewport.
- `python3 tools/uicheck_pdf.py` must exit 0 across its eight routes. It presses the export control with `window.print` stubbed (exactly one call, polled, because the button first awaits `haomaPrintPrep()`), checks that every printed image is loaded with height, that every slide prints with its image and each GIF prints its first-frame still, and then inspects the sheet under `Emulation.setEmulatedMedia(media="print")`: the body must still carry the page's own `--bg` and `--text`, `print-color-adjust` must be `exact`, the `@page` margin must be 0, the chrome must be unrendered, and the tab panels and scroll rails must be back. It judges "hidden" by `getClientRects()`, not by an element's own `display`, because a child of a `display:none` header still reports the display it would have had.
- The CDP profile directory persists between runs, so `connect()` in `uicheck.py` is always followed by `nocache(p)`. Without it a scenario can silently test the previous build's CSS or JS — which looks exactly like a bug in your change.

Commit style: one logical change per commit, message in the imperative; open a pull request (`fix/<topic>`) rather than pushing to the main branch when proposing corrections.
