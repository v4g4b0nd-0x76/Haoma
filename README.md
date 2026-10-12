# Mythology Notebook
Local editor: `python tools/editor.py` (needs Python 3.8+, git, hugo). Opens http://localhost:8765
- Content: + Page / + Culture generate the files and folders for you (English and Farsi).
- Themes: colours, animation, strip pattern, banner (upload or generate). Data lives in data/themes.json.
- Navigation: data/nav.json. Files: edit any template, CSS, SVG or i18n file.
- Preview: starts `hugo server` and shows it beside the editor. Publish: check build, commit, push.
Deploy: Settings > Pages > Source = "GitHub Actions"; the workflow builds on push.
Large audio: host on archive.org and set `audio:` to the full URL (keep the repo under ~1 GB).
