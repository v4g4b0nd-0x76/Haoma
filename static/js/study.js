/* Study helpers: continue reading + scroll, reader mode, reading list (consent-gated). */
(function () {
  var D = document.documentElement;
  var H = window.haoma || {};
  var SAVE_KEY = "haoma_saved";
  var RESUME_KEY = "haoma_resume";
  var SAVE_CAP = 60;
  var SCROLL_MIN = 80;
  var reduced = false;
  try {
    reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) {}

  function allowed() {
    return H.allowed ? H.allowed() : false;
  }

  function readLS(k) {
    try {
      return localStorage.getItem(k);
    } catch (e) {
      return null;
    }
  }
  function writeLS(k, v) {
    try {
      localStorage.setItem(k, v);
    } catch (e) {}
  }
  function clearLS(k) {
    try {
      localStorage.removeItem(k);
    } catch (e) {}
  }

  function pathNow() {
    return (location.pathname || "/").replace(/\/+/g, "/") || "/";
  }

  function isHomePath(p) {
    p = (p || "/").replace(/\/+/g, "/");
    return p === "/" || p === "/fa" || p === "/fa/" || /^\/(en\/?)?$/.test(p) || /\/Haoma\/?(fa\/?)?$/.test(p);
  }

  function isStandalone() {
    try {
      if (window.matchMedia("(display-mode: standalone)").matches) return true;
    } catch (e) {}
    return !!(window.navigator && window.navigator.standalone);
  }

  function attr(name, fallback) {
    return D.getAttribute(name) || fallback || "";
  }

  /* ---------- resume + scroll ---------- */
  function loadResume() {
    if (!allowed()) return null;
    var raw = readLS(RESUME_KEY);
    if (!raw) return null;
    try {
      var o = JSON.parse(raw);
      return o && o.path ? o : null;
    } catch (e) {
      return null;
    }
  }

  function saveResume(partial) {
    if (!allowed()) return;
    var cur = loadResume() || {};
    var next = {
      path: partial.path != null ? partial.path : cur.path || pathNow(),
      scroll: partial.scroll != null ? partial.scroll : cur.scroll || 0,
      title: partial.title != null ? partial.title : cur.title || document.title || "",
      culture: partial.culture != null ? partial.culture : cur.culture || D.dataset.culture || "",
      ts: Date.now()
    };
    if (!next.path || isHomePath(next.path)) return;
    if (next.path.length > 400) return;
    writeLS(RESUME_KEY, JSON.stringify(next));
    if (H.setLast) H.setLast(next.path);
  }

  function rememberScroll() {
    if (!allowed()) return;
    var y = window.scrollY || window.pageYOffset || 0;
    if (isHomePath(pathNow())) return;
    saveResume({
      path: pathNow(),
      scroll: Math.round(y),
      title: (document.querySelector("main article h1") || {}).textContent || document.title || "",
      culture: D.dataset.culture || D.dataset.pick || ""
    });
  }

  var scrollTimer = null;
  function onScrollRemember() {
    if (scrollTimer) return;
    scrollTimer = window.setTimeout(function () {
      scrollTimer = null;
      rememberScroll();
    }, reduced ? 200 : 450);
  }

  function restoreScroll() {
    if (!allowed()) return;
    var r = loadResume();
    if (!r || !r.path || r.path !== pathNow()) return;
    var y = +r.scroll || 0;
    if (y < SCROLL_MIN) return;
    var go = function () {
      var max = Math.max(0, (document.documentElement.scrollHeight || 0) - (window.innerHeight || 0));
      if (y > max + 40) return;
      window.scrollTo(0, Math.min(y, max));
    };
    if (reduced) go();
    else window.requestAnimationFrame(function () {
      window.setTimeout(go, 60);
    });
  }

  function enhanceResumeBar() {
    var resume = document.getElementById("resume-bar");
    var link = document.getElementById("resume-link");
    var text = resume && resume.querySelector(".resume__text");
    if (!resume || !link || !allowed()) return;
    var r = loadResume();
    var last = (r && r.path) || (H.getLast && H.getLast()) || "";
    if (!last || last === pathNow()) {
      resume.hidden = true;
      return;
    }
    var show = isHomePath(pathNow()) || isStandalone();
    if (!show) {
      resume.hidden = true;
      return;
    }
    try {
      if (sessionStorage.getItem("haoma-resume-hide") === "1") {
        resume.hidden = true;
        return;
      }
    } catch (e) {}
    link.href = last;
    if (text) {
      var label = attr("data-study-continue", text.textContent);
      if (r && r.title) {
        text.textContent = label;
        link.setAttribute("title", r.title);
      } else {
        text.textContent = label;
      }
    }
    var goLabel = attr("data-study-continue-go", "");
    if (goLabel) link.textContent = goLabel;
    resume.hidden = false;
  }

  /* ---------- reading list ---------- */
  function loadSaved() {
    if (!allowed()) return [];
    var raw = readLS(SAVE_KEY);
    if (!raw) return [];
    try {
      var arr = JSON.parse(raw);
      return Array.isArray(arr) ? arr : [];
    } catch (e) {
      return [];
    }
  }

  function persistSaved(arr) {
    if (!allowed()) return;
    writeLS(SAVE_KEY, JSON.stringify(arr.slice(0, SAVE_CAP)));
  }

  function isSaved(path) {
    path = path || pathNow();
    return loadSaved().some(function (x) {
      return x && x.k === path;
    });
  }

  function toggleSave(entry) {
    if (!allowed() || !entry || !entry.k) return false;
    var list = loadSaved();
    var i = -1;
    list.forEach(function (x, idx) {
      if (x && x.k === entry.k) i = idx;
    });
    if (i >= 0) {
      list.splice(i, 1);
      persistSaved(list);
      return false;
    }
    list.unshift({
      k: entry.k,
      t: entry.t || "",
      c: entry.c || "",
      kind: entry.kind || "art",
      ts: Date.now()
    });
    persistSaved(list);
    return true;
  }

  function paintSaveButtons() {
    var onLabel = attr("data-study-saved", "Saved");
    var offLabel = attr("data-study-save", "Save");
    [].slice.call(document.querySelectorAll("[data-save]")).forEach(function (btn) {
      var k = btn.getAttribute("data-save-path") || pathNow();
      var on = isSaved(k);
      btn.classList.toggle("is-saved", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      btn.setAttribute("aria-label", on ? onLabel : offLabel);
      btn.title = on ? onLabel : offLabel;
    });
  }

  function entryFromButton(btn) {
    return {
      k: btn.getAttribute("data-save-path") || pathNow(),
      t: btn.getAttribute("data-save-title") || (document.querySelector("main article h1") || {}).textContent || document.title || "",
      c: btn.getAttribute("data-save-culture") || D.dataset.culture || "",
      kind: btn.getAttribute("data-save-kind") || "art"
    };
  }

  function bindSaveButtons() {
    document.addEventListener("click", function (e) {
      var btn = e.target.closest && e.target.closest("[data-save]");
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      if (!allowed()) {
        var banner = document.getElementById("cookie-banner");
        if (banner) {
          banner.hidden = false;
          document.body.classList.add("has-cookie");
        }
        return;
      }
      toggleSave(entryFromButton(btn));
      paintSaveButtons();
      renderList();
    });
  }

  function renderList() {
    var list = document.getElementById("rlist-list");
    var empty = document.getElementById("rlist-empty");
    if (!list) return;
    list.innerHTML = "";
    var items = loadSaved();
    if (empty) empty.hidden = items.length > 0;
    items.forEach(function (it) {
      if (!it || !it.k) return;
      var li = document.createElement("li");
      li.className = "rlist__item";
      var a = document.createElement("a");
      a.href = it.k;
      a.className = "rlist__link";
      a.textContent = it.t || it.k;
      var rm = document.createElement("button");
      rm.type = "button";
      rm.className = "rlist__rm";
      rm.setAttribute("data-save", "");
      rm.setAttribute("data-save-path", it.k);
      rm.setAttribute("data-save-title", it.t || "");
      rm.setAttribute("data-save-culture", it.c || "");
      rm.setAttribute("data-save-kind", it.kind || "art");
      rm.setAttribute("aria-label", attr("data-study-unsave", "Remove"));
      rm.textContent = "×";
      li.appendChild(a);
      li.appendChild(rm);
      list.appendChild(li);
    });
  }

  function openList(on) {
    var panel = document.getElementById("rlist-panel");
    var btn = document.getElementById("rlist-open");
    if (!panel || !btn) return;
    panel.hidden = !on;
    btn.setAttribute("aria-expanded", on ? "true" : "false");
    if (on) {
      renderList();
      paintSaveButtons();
      var close = document.getElementById("rlist-close");
      if (close) close.focus();
    }
  }

  function bindListUI() {
    var btn = document.getElementById("rlist-open");
    var panel = document.getElementById("rlist-panel");
    var close = document.getElementById("rlist-close");
    if (btn) {
      btn.addEventListener("click", function () {
        openList(btn.getAttribute("aria-expanded") !== "true");
      });
    }
    if (close) close.addEventListener("click", function () {
      openList(false);
      if (btn) btn.focus();
    });
    if (panel) {
      panel.addEventListener("click", function (e) {
        if (e.target === panel) openList(false);
      });
    }
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") openList(false);
    });
    if (location.hash === "#reading-list" || location.hash === "#rlist") {
      openList(true);
      try {
        history.replaceState(null, "", location.pathname + location.search);
      } catch (err) {}
    }
  }

  /* ---------- reader mode ---------- */
  var TONES = ["", "calm", "sepia", "night"];

  function applyReader(prefs) {
    var on = !!prefs.reader;
    var tone = prefs.readerTone || "calm";
    if (!on) {
      D.removeAttribute("data-reader");
      D.removeAttribute("data-reader-tone");
      D.classList.remove("reader-chrome-hide");
      return;
    }
    D.setAttribute("data-reader", "1");
    D.setAttribute("data-reader-tone", tone === "calm" ? "calm" : tone);
  }

  function cycleReader() {
    if (!H.getPrefs || !H.setPrefs) return;
    var P = H.getPrefs() || {};
    var cur = P.reader ? (P.readerTone || "calm") : "";
    var idx = TONES.indexOf(cur);
    if (idx < 0) idx = 0;
    idx = (idx + 1) % TONES.length;
    var next = TONES[idx];
    if (!next) {
      P.reader = false;
      P.readerTone = "calm";
    } else {
      P.reader = true;
      P.readerTone = next;
    }
    H.setPrefs(P);
    applyReader(P);
    paintReaderBtn(P);
  }

  function paintReaderBtn(P) {
    var btn = document.querySelector('[data-act="reader"]');
    if (!btn) return;
    var on = !!(P && P.reader);
    btn.classList.toggle("is-on", on);
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    var tip = attr("data-study-reader", "Reader mode");
    if (on && P.readerTone && P.readerTone !== "calm") {
      tip = tip + " · " + P.readerTone;
    }
    btn.title = tip;
    btn.setAttribute("aria-label", tip);
  }

  function bindReaderChrome() {
    if (reduced) return;
    var lastY = window.scrollY || 0;
    var ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (!D.hasAttribute("data-reader") || ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          ticking = false;
          var y = window.scrollY || 0;
          if (y < 48) {
            D.classList.remove("reader-chrome-hide");
          } else if (y > lastY + 8) {
            D.classList.add("reader-chrome-hide");
          } else if (y < lastY - 8) {
            D.classList.remove("reader-chrome-hide");
          }
          lastY = y;
        });
      },
      { passive: true }
    );
  }

  function bindReaderAct() {
    document.querySelectorAll('[data-act="reader"]').forEach(function (b) {
      b.addEventListener("click", function () {
        cycleReader();
      });
    });
    var P = (H.getPrefs && H.getPrefs()) || {};
    applyReader(P);
    paintReaderBtn(P);
  }

  /* ---------- boot hooks ---------- */
  function clearStudy() {
    clearLS(SAVE_KEY);
    clearLS(RESUME_KEY);
  }

  if (H) {
    H.clearStudy = clearStudy;
    H.toggleSave = toggleSave;
    H.isSaved = isSaved;
  }

  if (isStandalone()) {
    document.body.classList.add("is-standalone");
    D.setAttribute("data-standalone", "1");
  }

  function init() {
    bindSaveButtons();
    bindListUI();
    bindReaderAct();
    bindReaderChrome();
    paintSaveButtons();
    renderList();
    if (!isHomePath(pathNow())) {
      saveResume({
        path: pathNow(),
        scroll: Math.round(window.scrollY || 0),
        title: (document.querySelector("main article h1") || {}).textContent || document.title || "",
        culture: D.dataset.culture || D.dataset.pick || ""
      });
    }
    restoreScroll();
    enhanceResumeBar();
    window.addEventListener("scroll", onScrollRemember, { passive: true });
    window.addEventListener("pagehide", rememberScroll);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
