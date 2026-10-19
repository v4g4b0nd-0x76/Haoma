# Agents

Start with **[AI.md](AI.md)** — full project reference (content model, editor, themes, verification).

Short pointers (do not duplicate AI.md):

| Topic | Where |
|---|---|
| Culture flourishes / eggs / reduced motion | AI.md §5 |
| Library off-git + remote `url` | AI.md §8, [docs/repo-hygiene.md](docs/repo-hygiene.md) |
| Cache-bust `?v=` tokens | AI.md § Working agreements; `layouts/_default/baseof.html` |
| Editor ports / Codespaces | AI.md §9 (`8765` editor, Hugo via `/__hugo__/`) |
| Release tags | `editor-v*` (binaries), `cult-flourish-*` (CSS/JS asset tags) |
| Art / maps / translation | [art-gen-ai.md](art-gen-ai.md), [MAP-DESIGN.md](MAP-DESIGN.md), [translate-ai.md](translate-ai.md) |
| History purge (never auto-run) | [docs/repo-hygiene.md](docs/repo-hygiene.md) |

Shell: prefer `rtk` prefix for git/test/build commands when available (see parent `CLAUDE.md` / RTK).

**Working agreements** are in AI.md — measure before large media commits; never commit `tools/.preview`, `tools/.history`, `tools/.drafts`, or `static/.preview-maps`; prefer original SVG motifs; no Pinterest scraping; no secrets in the tree.
