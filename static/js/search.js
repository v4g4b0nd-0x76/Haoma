/* Site search — AND token match, title > tagline > body; max 8 hits. */
(function () {
  var box = document.getElementById("site-search");
  if (!box) return;
  var input = box.querySelector(".search__input");
  var panel = box.querySelector(".search__panel");
  var list = box.querySelector(".search__list");
  var status = box.querySelector(".search__status");
  var openBtn = box.querySelector(".search__open");
  var closeBtn = box.querySelector(".search__close");
  var data = null;
  var loading = null;
  var active = -1;
  var MAX = 8;
  var MIN_Q = 2;

  function idxUrl() {
    var link = document.querySelector('link[rel="alternate"][type="application/json"][href*="search"]');
    if (link && link.href) return link.href;
    /* brand.href is absolute (works under /Haoma/ on Pages). getAttribute +
       new URL(..., "/fa/") throws and the old catch pointed at /fa/search.json. */
    var brand = document.querySelector(".brand[href]");
    var base = (brand && brand.href) || document.baseURI || location.href;
    try {
      return new URL("search.json", base.endsWith("/") ? base : base.replace(/\/?$/, "/") ).href;
    } catch (e) {
      return new URL("search.json", location.href).href;
    }
  }

  function load() {
    if (data) return Promise.resolve(data);
    if (loading) return loading;
    loading = fetch(idxUrl(), { credentials: "same-origin" })
      .then(function (r) { if (!r.ok) throw new Error("index " + r.status); return r.json(); })
      .then(function (j) { data = j.items || []; return data; })
      .catch(function () { data = []; return data; });
    return loading;
  }

  function tokens(q) {
    return q.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, " ").split(/\s+/).filter(function (t) { return t.length >= MIN_Q || (t.length >= 1 && /[\u0600-\u06FF]/.test(t)); });
  }

  function score(item, toks) {
    var t = (item.t || "").toLowerCase();
    var g = (item.g || "").toLowerCase();
    var b = (item.b || "").toLowerCase();
    var m = (item.m || "").toLowerCase();
    var s = 0;
    for (var i = 0; i < toks.length; i++) {
      var w = toks[i];
      var hit = false;
      if (t === w) { s += 120; hit = true; }
      else if (t.indexOf(w) === 0) { s += 90; hit = true; }
      else if (t.indexOf(w) >= 0) { s += 55; hit = true; }
      if (g.indexOf(w) >= 0) { s += 28; hit = true; }
      if (m.indexOf(w) >= 0) { s += 35; hit = true; }
      if (b.indexOf(w) >= 0) { s += 10; hit = true; }
      if (!hit) return 0; /* AND: every token must match somewhere */
    }
    if (item.k === "episode") s += 2;
    if (item.k === "characters" || item.k === "stories" || item.k === "history") s += 4;
    return s;
  }

  function snippet(item, toks) {
    var src = item.g || item.b || "";
    if (!src) return "";
    var low = src.toLowerCase();
    var at = -1;
    for (var i = 0; i < toks.length; i++) {
      var p = low.indexOf(toks[i]);
      if (p >= 0 && (at < 0 || p < at)) at = p;
    }
    if (at < 0) return src.slice(0, 100);
    var a = Math.max(0, at - 32);
    var out = (a ? "…" : "") + src.slice(a, a + 110) + (a + 110 < src.length ? "…" : "");
    return out;
  }

  function kindLabel(k) {
    var map = { characters: "character", stories: "story", history: "history", episode: "episode", culture: "culture", section: "section", page: "page" };
    return map[k] || k || "page";
  }

  function render(hits, toks) {
    active = hits.length ? 0 : -1;
    if (!hits.length) {
      list.innerHTML = "";
      status.textContent = toks.length ? (status.dataset.empty || "No matches") : "";
      return;
    }
    status.textContent = "";
    list.innerHTML = hits.map(function (h, i) {
      var sn = snippet(h.item, toks);
      return '<li role="option" class="search__hit' + (i === 0 ? " is-active" : "") + '" data-i="' + i + '" data-u="' + h.item.u.replace(/"/g, "&quot;") + '">' +
        '<span class="search__kind">' + kindLabel(h.item.k) + (h.item.c ? " · " + h.item.c : "") + "</span>" +
        '<span class="search__title"></span>' +
        (sn ? '<span class="search__snip"></span>' : "") +
        "</li>";
    }).join("");
    [].forEach.call(list.children, function (li, i) {
      li.querySelector(".search__title").textContent = hits[i].item.t;
      var snEl = li.querySelector(".search__snip");
      if (snEl) snEl.textContent = snippet(hits[i].item, toks);
      li.onmousedown = function (e) { e.preventDefault(); go(hits[i].item.u); };
    });
  }

  function run() {
    var toks = tokens(input.value || "");
    if (!toks.length) { render([], []); return; }
    load().then(function (items) {
      var scored = [];
      for (var i = 0; i < items.length; i++) {
        var sc = score(items[i], toks);
        if (sc > 0) scored.push({ item: items[i], s: sc });
      }
      scored.sort(function (a, b) { return b.s - a.s || a.item.t.localeCompare(b.item.t); });
      render(scored.slice(0, MAX), toks);
    });
  }

  function go(u) {
    if (u) location.href = u;
  }

  function setOpen(on) {
    box.classList.toggle("is-open", on);
    panel.hidden = !on;
    openBtn.setAttribute("aria-expanded", on ? "true" : "false");
    if (on) {
      load();
      setTimeout(function () { input.focus(); input.select(); }, 10);
    } else {
      active = -1;
    }
  }

  function move(d) {
    var hits = list.querySelectorAll(".search__hit");
    if (!hits.length) return;
    active = (active + d + hits.length) % hits.length;
    [].forEach.call(hits, function (h, i) { h.classList.toggle("is-active", i === active); });
    hits[active].scrollIntoView({ block: "nearest" });
  }

  openBtn.addEventListener("click", function () { setOpen(!box.classList.contains("is-open")); });
  if (closeBtn) closeBtn.addEventListener("click", function () { setOpen(false); openBtn.focus(); });
  input.addEventListener("input", run);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { e.preventDefault(); setOpen(false); openBtn.focus(); return; }
    if (e.key === "ArrowDown") { e.preventDefault(); move(1); return; }
    if (e.key === "ArrowUp") { e.preventDefault(); move(-1); return; }
    if (e.key === "Enter") {
      e.preventDefault();
      var hit = list.querySelector(".search__hit.is-active") || list.querySelector(".search__hit");
      if (hit) go(hit.getAttribute("data-u"));
    }
  });
  document.addEventListener("click", function (e) {
    if (box.classList.contains("is-open") && !box.contains(e.target)) setOpen(false);
  });

  window.haomaSearchOpen = function () { setOpen(true); };
  window.haomaSearchClose = function () { setOpen(false); };
})();
