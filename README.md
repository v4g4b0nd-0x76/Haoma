# Mythology Notebook
Static Hugo site (English + Farsi) for GitHub Pages. Local editor: `python tools/editor.py` (Python 3.8+, git, hugo).

- **Editor:** temporary drafts (survive reloads, never touch files until Save), live preview of the page you are editing, undo/rollback history, themes, navigation, review dashboard, publish and pull requests.
- **Writing tools:** sliders (images, GIFs, video), hover notes, figures, play-on-scroll GIFs, grids (2/3 + 1/3 and more), Wikipedia-style infobox. See `content/en/guide/_index.md`.
- **Agents and contributors:** read `AI.md` and `CONTRIBUTING.md`.

Deploy (free): push to GitHub, Settings > Pages > Source = "GitHub Actions"; `.github/workflows/hugo.yml` builds on every push.
Large audio: host on archive.org and set `audio:` to the full URL (keep the repo under about 1 GB).
