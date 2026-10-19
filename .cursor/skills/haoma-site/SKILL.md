---
name: haoma-site
description: >
  Haoma (هوم) Hugo bilingual mythology site conventions — culture pages, flourishes,
  EN/FA i18n+RTL, library-off-git, editor on :8765, RTK shell, parity checks, and
  GitHub Pages release tags. Use when editing this repo's content, layouts, CSS/JS,
  themes, editor (tools/), library manifest, or when the user mentions Haoma, cultures,
  flourishes, eggs, atlas, or FA/RTL.
---

# Haoma site

Read **[AI.md](../../../AI.md)** first for full detail. This skill is the short actionable checklist.

## Hard constraints (never break)

- Static Hugo only — no runtime DB/server beyond the local editor.
- Relative URLs (`relURL` / `relLangURL`); no hardcoded domains or absolute `/css/…`.
- No external CDNs/fonts/analytics; fonts in `static/fonts`.
- Every reader-visible string → `i18n/en.toml` **and** `i18n/fa.toml`.
- Every content path exists in both `content/en/` and `content/fa/`.
- RTL-safe CSS: logical properties (`margin-inline`, `inset-inline-*`); never `letter-spacing` / `text-transform` on Farsi.
- Honest sources only — no invented quotes, dates, or closed media.

## Culture UI / flourishes

- Culture-bound pages use `data-fixed` themes from `data/themes.json`.
- Expect **2–3 light motions** (motif drift, ornament shimmer, soft parallax) + chip/card accents.
- Easter eggs only when `data-fixed` is set; honour `prefers-reduced-motion`.
- Motifs: original SVG / atlas masks (`static/img/atlas/*-motifs.svg`). No Pinterest scrape; no fake runes; no clipart Faravahar/peacock as filler.
- Footer glyphs: real script marks via `--egg-glyph` only.

## Section toggles & content

- Culture hubs: Atlas from leaves + undirected `related:` edges; optional `atlas_path:`.
- Shortcodes: disagree / recon / art-strip / tree / etc. — demo on `/guide/`.
- New UI copy → both i18n files; templates use `{{ i18n "key" }}` (never hardcoded English in layouts).

## Library (off-git)

- Git tracks only `static/library/manifest.json` + `.gitkeep`.
- Large binaries → GitHub Releases / R2 / S3 / archive.org; manifest entries may use remote `url`/`href`.
- Never commit `tools/.preview`, `tools/.history`, `tools/.drafts`, `static/.preview-maps`, `public/`, `resources/`.
- History purge (`git filter-repo`) — document in `docs/repo-hygiene.md`; **never auto-run**.

## Editor

- Local: `python tools/editor.py` → `127.0.0.1:8765` (+ token).
- Codespaces: Hugo via `/__hugo__/`; do **not** put 8765 in `forwardPorts` (use `portsAttributes` + `openBrowser`).
- Writable paths only: `content data i18n layouts static assets hugo.toml`.
- Release binaries: tags `editor-v*`. Flourish/asset cache-bust: bump `?v=` in `layouts/_default/baseof.html`; tags like `cult-flourish-*`.

## Shell & verify

- Prefer `rtk` prefix for git/test/build when available.
- Before finishing substantive work:
  - `python3 tools/parity.py` → **0 difference(s)**
  - Relevant checks from AI.md §10 (`uicheck_pdf.py`, Hugo build, etc.)

## Companion skills (read when relevant)

| Skill | When |
|---|---|
| `frontend-design` | New UI / visual polish (still obey Haoma brand + flourishes) |
| `rtl` | Logical CSS / FA RTL audits |
| `accessibility-auditing` | Browser a11y pass on a rendered page |
| `github-release` | Cutting tags/releases (adapt SemVer flow to `editor-v*` / `cult-flourish-*`) |

Paths: user `~/.cursor/skills/<name>/`; this skill `.cursor/skills/haoma-site/`.
