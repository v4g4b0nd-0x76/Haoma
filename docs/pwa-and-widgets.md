# PWA and home-screen “widgets”

Haoma is a **static Hugo site**. It can be a Progressive Web App (installable, offline shell + recently visited pages). It **cannot** ship Pinterest-style lock-screen or home-screen widgets on iPhone, iPad, Mac, or Android without a native app shell (WidgetKit / App Widgets).

## What we ship

| Feature | Status |
|---|---|
| Web App Manifest (`manifest.webmanifest`, per language) | Yes — name, icons, theme colours, `standalone` |
| Service worker (`static/sw.js`) | Yes — shell CSS/JS/fonts/brand icons + **last ~40 visited HTML pages** (network-first); **not** audio/video/library binaries |
| Soft update banner | Yes — “New version ready” / FA equivalent; user confirms refresh (no mid-read hard reload) |
| Install prompt (`beforeinstallprompt`) | Android / Chromium when criteria met; suppressed once installed / dismissed (localStorage) |
| iOS / iPadOS / Mac Safari | “Add to Home Screen” via Share sheet; soft tip in UI (not repeated in standalone) |
| Manifest **shortcuts** | Yes — Latest episodes, Stories, Reading list (`#reading-list`) |
| Continue reading | Yes — last path + scroll in localStorage (consent-gated); resume bar on home / standalone |
| Reader mode | Yes — larger type, calmer measure, calm / sepia / night tones; optional chrome hide on scroll (respects `prefers-reduced-motion`) |
| Reading list | Yes — save/unsave stories & episodes locally; header scribe-tablet icon |
| Media Session | Yes — play/pause (+ seek) metadata for existing `data-ha-player` audio |
| Apple touch icon + `apple-mobile-web-app-*` | Yes |
| True home/lock-screen widgets | **No** — requires native code |
| Offline entire site / library / media | **No** — deliberately capped |

## Android vs iOS (honest)

- **Android (Chrome-class):** Installable PWA with icon, splash/theme colour, manifest shortcuts (long-press app icon → Episodes / Stories / Reading list). Offline revisit of recently opened pages and shell assets.
- **iOS / iPadOS / Mac Safari:** Add to Home Screen works; standalone display is limited; **no** `beforeinstallprompt`; **no** home-screen widgets from the web; service workers work but storage/cache quotas and background behaviour are stricter (Safari may evict caches under pressure). Shortcuts in the webmanifest are mainly useful on Android.
- **Continue reading** is in-app (resume bar / last URL), not a live home-screen widget. Last culture is stored locally and cannot be injected into a static webmanifest.

## Shortcuts ≠ widgets

Manifest shortcuts are **deep links** from the installed app icon menu. They do not update with “latest episode” content on the home screen like a Pinterest widget.

### Optional: Shortcuts app + RSS (closest “widget-like” path without a native app)

1. Site RSS: language home `index.xml` (footer RSS link).
2. On iPhone: Shortcuts app → automation or widget that opens a fixed URL (`…/episodes/` or a specific episode).
3. Or use any RSS reader’s home-screen widget pointed at Haoma’s feed.

That still is not a Haoma-branded live widget; it is a URL/RSS shortcut.

## What we deliberately do not do

- Fake “widget” UI that claims lock-screen placement.
- Periodic Background Sync / Push for episode alerts (needs a server and push keys; out of scope for static Pages).
- Share Target API (useful later; needs careful origin/path setup under `/Haoma/`).
- Precaching the whole culture tree or library binaries.

## Cache-bust

When changing `static/sw.js` cache name or shell list, bump the `CACHE` / `SHELL_CACHE` / `PAGES_CACHE` strings inside `sw.js` and the `?v=` on `js/pwa.js` (and `js/study.js` / `css/style.css` when those change) in `layouts/_default/baseof.html`.
