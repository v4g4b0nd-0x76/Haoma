# Repo hygiene

Keep the git history lean. Large binaries belong outside the tree; the site only needs paths or URLs.

## Library policy

- **In git:** `static/library/manifest.json` and `static/library/.gitkeep` only.
- **Out of git:** PDFs, EPUBs, ZIPs, and other large media under `static/library/` (see `.gitignore`).
- **Hosting:** put binaries on GitHub Releases, Cloudflare R2, S3, archive.org, or similar. Point at them with a remote `url` / `href` in the manifest (see below), or drop a local copy for Hugo `readDir` listing during preview — local binaries stay untracked.
- **Local Markdown** under `static/library/` (`.md` / `.txt`) may still be committed if small and open-licensed.

### Manifest schema (`static/library/manifest.json`)

```json
{
  "categories": [
    {
      "id": "persian-mythology",
      "title": { "en": "Persian Mythology", "fa": "اساطیر ایرانی" },
      "pages": ["cultures/iranian/"]
    }
  ],
  "files": {
    "local-handbook.pdf": {
      "title": { "en": "Local handbook", "fa": "…" },
      "categories": ["persian-mythology"],
      "pages": ["cultures/iranian/"]
    },
    "curtis-persian-myths": {
      "title": { "en": "Persian Myths", "fa": "اساطیر ایران" },
      "url": "https://example.com/releases/persian-myths.pdf",
      "kind": "pdf",
      "categories": ["persian-mythology"],
      "pages": ["cultures/iranian/", "cultures/iranian/traditions/zoroastrian/"]
    }
  }
}
```

| Field | Meaning |
|---|---|
| key | Stable id: local filename **or** slug for a remote-only entry |
| `title` | string or `{en,fa}` |
| `url` / `href` | Absolute `https://…` (or `http://…`) download link. Prefer `url`. |
| `kind` | Optional: `pdf` \| `epub` \| `image` \| `md` \| `text` \| `file` (inferred from key/URL when omitted) |
| `categories` | Category ids |
| `pages` | Site-root paths (no language prefix) for related-library chips |

The Library page lists every local file under `static/library/` **plus** any manifest entry that has a remote `url`/`href` and no matching local file. Related links on culture pages use `url`/`href` when set.

Editor: **Library → Add remote URL…** creates a manifest-only entry (no upload). Uploads still work for local preview; remember binaries are gitignored — Publish must not rely on them being in the repo.

## History purge runbook (one-time, maintainer only)

A large PDF was once committed under `static/library/` and later removed from the tip of the tree; it may still live in git history and inflate clones. **Do not run this unless you are ready to force-push and coordinate with every fork/clone.**

This repo policy is: **document the procedure; do not run `git filter-repo` / force-push from agent sessions** unless a human maintainer explicitly asks.

### When to run

- Maintainer chooses to shrink `.git` after confirming no one needs the old blob.
- Tip of `master` already has no binary under `static/library/` (only manifest / `.gitkeep`).

### Steps (example)

1. Install [git-filter-repo](https://github.com/newren/git-filter-repo) (preferred over `filter-branch`).
2. Clone a fresh mirror and work there:
   ```bash
   git clone --mirror git@github.com:OWNER/Haoma.git haoma-mirror.git
   cd haoma-mirror.git
   ```
3. Drop the known path (adjust if more blobs show up):
   ```bash
   git filter-repo --path static/library/persian-myths-vesta-sarkhosh-curtis-z-library.sk-1lib.sk-z-lib.sk-.pdf --invert-paths
   ```
   Or remove every historical PDF under that folder:
   ```bash
   git filter-repo --path-glob 'static/library/*.pdf' --invert-paths
   ```
4. Verify size: `du -sh .` and `git rev-list --objects --all | grep '\.pdf$'` should be empty for library PDFs.
5. Force-push the mirror (this rewrites history):
   ```bash
   git push --force --all
   git push --force --tags
   ```
6. Tell collaborators to re-clone or hard-reset to the new history. Old PR branches based on pre-rewrite commits need rebasing or recreating.
7. Re-attach any Release assets that pointed at the purged blob; library downloads should use Release / R2 URLs in the manifest instead.

### Safer alternative

Leave history alone if clone size is acceptable. Keep binaries out going forward via `.gitignore` and remote `url` entries.

## Agent / contributor reminders

See [AI.md](../AI.md) § Working agreements and [AGENTS.md](../AGENTS.md).
