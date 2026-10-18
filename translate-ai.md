# translate-ai.md — Haoma translation brief for AI agents

**Read this before translating any Haoma page.**  
Use with the editor **Prompt generator → Translation** tab: pick a source page, target language (English or Farsi), model, and optional notes. The tool pastes the **full source file** into a ready-to-run agent prompt.

Related docs (do not contradict them):

| Doc | Use when |
|---|---|
| [AI.md](AI.md) §3.1–3.4 | Front matter, evidence grades, honesty rules |
| [art-gen-ai.md](art-gen-ai.md) | Image work only — not translation |
| On-site editor | `/editor/` · Prompt generator → Translation |

---

## 1. Goal

Produce a **faithful, publishable translation** of one existing Markdown page into the other site language, keeping Haoma’s structure, shortcodes, and honesty rules intact.

Supported languages today: **English (`en`)** ↔ **Farsi / Persian (`fa`)**.

---

## 2. Output contract

1. Return **one complete Markdown file**: YAML front matter + body (same shape as the source).
2. Suggested path: same relative path under the other language root  
   `content/en/...` ↔ `content/fa/...`
3. Do **not** invent a new slug or move the page.
4. If unsure about a fact, keep the source’s caution; do not “improve” history.

---

## 3. Front matter rules

| Field | Rule |
|---|---|
| Keys | Keep English keys (`title`, `tagline`, `grade`, `related`, …) |
| `title`, `tagline`, `quote`, `quoteSource`, `pronounce` | Translate into the target language |
| `culture`, `sec`, `subculture`, `card_bg`, `card_bg_kind`, `wide`, `dropcap` | **Do not translate** — keep values identical |
| `themes`, `related`, `atlas_path`, `audio`, `youtube`, `spotify` | Keep paths / IDs unchanged (site-root paths, never `/fa/` or `/en/` prefixes) |
| `sources` | Keep bibliographic strings; you may add a short target-language gloss in parentheses only if it helps readers — never delete a source |
| `grade` | After machine translation set `grade: draft` until a native reader verifies (see AI.md §3.3). Canonical keys: `primary text`, `later compilation`, `archaeology`, `modern scholarship`, `draft`, `guide` |
| `reviewed` | Leave blank or keep source date; do not claim a new review unless a human verified |

---

## 4. Body rules

1. Translate **all** prose (paragraphs, headings, list items, captions).
2. **Preserve shortcodes exactly** — names, attributes, delimiters (`{{< >}}` / `{{% %}}`). Translate only human-visible attribute values (`caption`, `note`, `text`, `title` on shortcodes) and content between tags when that content is prose.
3. Do **not** translate: file paths, `culture` keys, map `id`s, CSS-like tokens, or code fences meant as identifiers.
4. Keep Markdown structure (heading levels, lists, tables, links). Internal links that use site-root paths stay as-is.
5. **Verse / Farsi**: for `{{< verse lang="fa" >}}` keep couplet structure (`\|` hemistich splits). When translating *into* Farsi, use natural Persian; when translating *out of* Farsi, prefer clear literary English, not word-for-word calques.
6. Quotes: at most a short phrase of copyrighted text; paraphrase otherwise (AI.md §3.4).
7. Tone: serious myth-atlas voice — clear, not chatty, not academic jargon for its own sake.

### 4.1 English → Farsi

- Natural contemporary Persian for encyclopedia prose; avoid stilted calques.
- Use Persian digits only if the surrounding site page already does; otherwise keep numerals consistent with nearby FA pages.
- Do not letter-space Farsi.
- Prefer established Persian names for well-known figures (e.g. زرتشت, مهر) when FA content already uses them.

### 4.2 Farsi → English

- Clear literary English; keep proper names consistent with the English tree (`Mehr`, `Zarathustra`, …).
- Preserve scholarly hedging (“scholars disagree”, date ranges).

---

## 5. Agent checklist (before accept)

- [ ] Full file returned (front matter + body)
- [ ] Path pairing correct (`en` ↔ `fa`, same relative path)
- [ ] Shortcodes still parse; paths unchanged
- [ ] `grade: draft` if this was machine-assisted
- [ ] No new unsourced claims
- [ ] Title/tagline localized; structural keys untouched

---

## 6. How to use the editor tool

1. Open **Prompt generator** → **Translation**.
2. Select the **source document** (existing `content/…` page).
3. Choose **target language** (the other of English / Farsi).
4. Pick the **model / agent** flavour (wording of the brief).
5. Optional: **extra explanation** (tone notes, name preferences, “keep Avestan terms”).
6. **Generate** → copy the prompt into Claude / ChatGPT / Gemini / etc.
7. Paste the agent’s Markdown into the matching translation path (or create the stub from Content → then replace).

---

## 7. Stub titles

Until the translation is real, stubs may use `TODO translate: …` in `title` (Review view flags them). Replace that title when the translation is done.
