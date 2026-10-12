# AI.md - guide for AI agents working on this project

Read this before changing anything. It describes the site, the editor, the file formats and the rules that keep both working. Humans can use it too.

## 1. What this project is
A bilingual (English + Farsi/RTL) mythology notebook: wiki-style pages per culture, a podcast section, a media library. It is a **static Hugo site** deployed to **GitHub Pages**. A local **editor** (`tools/`) generates the files for you.

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
static/img/               banners (<culture>.svg), media/ for page images and GIFs
static/video/ audio/ library/   MP4/WebM, episode audio, downloadable PDFs and Markdown
tools/editor.py           local editor server (Python standard library only)
tools/admin.html          the editor UI (single file, vanilla JS)
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
- Slow, subtle motion (6-30 s loops). Nothing flashing.

## 7. Navigation and UI strings
`data/nav.json`: `{"en":[{"name":"Cultures","url":"cultures/"}],"fa":[...]}`; `url` is relative to the language root. UI strings live in `i18n/<lang>.toml` as `[key]\n  other = "..."`; add every new key to both files.

## 8. Media
- Images/GIFs: `static/img/media/`. Video: `static/video/` (MP4 H.264 or WebM, muted loops; prefer MP4/WebM over GIF above ~1 MB). Audio: `static/audio/`. PDFs/Markdown: `static/library/` (listed automatically in the Library).
- Lower-case file names, `a-z0-9.-` only. Keep the repo under ~1 GB; host long audio on archive.org and put the full URL in `audio:`.
- Record the licence and author of every asset in the page's "Media credits".

## 9. The editor (`python tools/editor.py`)
Needs Python 3.8+, git, hugo. Binds to 127.0.0.1; every API call needs the per-run token (`X-Token` header or `t` query parameter); only `content data i18n layouts static assets hugo.toml` are writable.

### 9.1 Safety model - keep these invariants
1. **Nothing reaches the project until Save.** Edits are *temporary drafts* stored in `tools/.drafts/` (survive page switches and reloads). `POST /api/apply` moves drafts into real files.
2. **Preview runs on a copy** (`tools/.preview/` = saved files + drafts). `hugo server --source tools/.preview`. The UI navigates the preview to the page being edited (`pageUrl()` in admin.html); do not re-add `--navigateToChanged`, it jumps to whichever file changed last.
3. **Every save is reversible.** Before a real write the previous content is backed up in `tools/.history/` under a change id; `POST /api/rollback` restores it. All writes must pass a change id (`x`) and label (`l`).
4. Structured editors (themes, navigation, settings) edit a draft of their JSON file; they never share mutable state.
5. Generated assets never overwrite existing files.

### 9.2 API (JSON unless noted)
`GET tree` · `GET file?path=` (text) · `PUT file?path=&x=&l=` · `DELETE file?path=&x=&l=` · `POST upload?path=&x=&l=` (raw body, under `static/`) · `PUT draft?path=` (raw body) · `POST draftdel?path=` · `POST discard?path=` · `GET drafts` · `POST apply` `{paths,x,l}` · `POST resync` · `GET raw?path=&ws=1` · `GET history` · `POST rollback[?id=]` · `GET audit` · `POST preview?a=start|stop`, `GET preview` · `GET check` (hugo build of saved files) · `GET git` · `GET diff` · `POST commit` `{message,branch,push,newBranch}` · `POST pull` · `POST revert`.

### 9.3 Extending the editor
`tools/admin.html` is one file: state (`drafts`, `orig`, `files`), views in the `VIEWS` table, insert builders `bSlider bGrid bInfobox bFig bPlay bNote` (use `modal()` and `wirePicker()`). To add a view: write `pName()`, register it in `VIEWS`, make any edit go through `setDraft()` / `setJ()` and any save through `commit()`. Use unique element ids (modal fields are prefixed `m_`). Add a builder when you add a shortcode.

## 10. Workflows for agents
Add a page: create the file in both languages with the front matter above, sources and grade, then `hugo --quiet` must pass. Add a shortcode: template in `layouts/shortcodes/`, CSS in `style.css` (RTL-safe, mobile rule under 760px), JS only if needed in `site.js` (guard for missing `IntersectionObserver`, respect reduced motion), documentation row in section 4 and the guide page, and an editor builder.

Verify before finishing:
- `hugo --quiet --destination /tmp/out` builds with no errors, also with `--baseURL https://x.github.io/repo/` (check asset links start with `/repo/`).
- EN and FA pages both render; RTL layout checked.
- No new external requests; no absolute URLs; images have alt/captions.
- `python3 -c "import ast;ast.parse(open('tools/editor.py').read())"` and a JS syntax check of the script in `tools/admin.html` (`node --check`).
- Editor changes: test with a headless DOM (jsdom) against a running `tools/editor.py` on a copy of the repo: edits stay drafts, Save writes, rollback restores, drafts survive reload.

Commit style: one logical change per commit, message in the imperative; open a pull request (`fix/<topic>`) rather than pushing to the main branch when proposing corrections.
