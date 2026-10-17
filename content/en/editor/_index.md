---
title: "How to edit Haoma"
tagline: "Web editor (Codespace) and desktop binary — no IDE required"
grade: guide
reviewed: 2026-10-17
sources:
  - "Haoma project documentation (this repository)"
---

You can edit Haoma in two ways: in the **browser** (recommended if you do not want to install tools), or with a **desktop binary** on your computer. Both use the same editor: drafts, live preview, map studio, and **Publish & PR**.

## 1. Web editor (easiest)

Works in Chrome, Firefox, Safari, or Edge. You only need a free GitHub account.

1. Open the launcher: [**/tools/**](/tools/) on this site  
   (live site: <https://v4g4b0nd-0x76.github.io/Haoma/tools/>).
2. Click **Open editor**.
3. Sign in with GitHub if asked.
4. Wait while a private workspace (Codespace) starts — often under a minute when prebuilds are ready.
5. The editor opens in a **new browser tab** by itself.

Then:

- Edit pages, themes, or maps in the left/main panels.
- Use **Save** when you want changes written into the project (until then they stay as drafts).
- Use **Publish & PR** to push a branch and open a pull request.

If the preview pane stays blank, open the **Ports** tab in the Codespace and open port **1313**.

> The live website itself is read-only. Only your Codespace (or a local editor) can change files.

## 2. Desktop binary (offline / no Python)

Use this when you prefer working on your own machine without installing Python.

### Download

1. Open **[Releases](https://github.com/v4g4b0nd-0x76/Haoma/releases)** on GitHub.
2. Open the latest release tagged `editor-v…` (for example `editor-v1.0.0`).
3. Under **Assets**, download the file for your system:

| Your computer | File to download |
|---|---|
| Linux (64-bit) | `haoma-editor-linux-amd64` |
| Windows (64-bit) | `haoma-editor-windows-amd64.exe` |
| macOS (Intel/Apple with Rosetta or amd64 build) | `haoma-editor-macos-amd64` |

### Where to put it

The binary must find the Haoma project (the folder that contains `hugo.toml`).

**Recommended layout:**

```text
Haoma/                          ← git clone of this repository
  hugo.toml
  content/
  …
  haoma-editor-linux-amd64      ← binary here (same folder as hugo.toml)
```

Or keep the binary anywhere and set an environment variable:

- `HAOMA_ROOT` = full path to the project folder (the one with `hugo.toml`).

### Still required on your computer

The binary replaces **Python only**. You still need:

1. **[Hugo Extended](https://gohugo.io/installation/)** ≥ 0.139 (`hugo version` should say `extended`)
2. **git**

### Run it

**Linux / macOS**

```bash
cd /path/to/Haoma
chmod +x haoma-editor-linux-amd64   # once
./haoma-editor-linux-amd64
```

**Windows**

1. Clone or download the Haoma repo.
2. Put `haoma-editor-windows-amd64.exe` in that folder (next to `hugo.toml`).
3. Double-click the `.exe`, or run it from PowerShell / Command Prompt.

Your browser should open `http://localhost:8765/` (the terminal also prints the address).

### If the browser does not open

Open this address yourself: [http://localhost:8765/](http://localhost:8765/)

### Stop the editor

Press `Ctrl+C` in the terminal window where it is running. On Windows, close that window if you started it by double-click.

## 3. Optional: Python from the repo

If you already develop on the repo:

```bash
git clone https://github.com/v4g4b0nd-0x76/Haoma
cd Haoma
python tools/editor.py
```

Same UI as the binary and the web Codespace.

## Which should I use?

| Situation | Use |
|---|---|
| No install, edit from any computer | **Web editor** (`/tools/`) |
| Offline, or you already clone the repo | **Desktop binary** |
| You are comfortable with Python | `python tools/editor.py` |

## Need help?

- Report a problem: use **Report a correction** on any page, or open a GitHub issue.
- Full technical notes for contributors: see `README.md` §5 and §10 in the repository.
