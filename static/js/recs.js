/* Continue exploring — consent-gated localStorage reads + related.json graph. */
(function () {
  var mount = document.getElementById("haoma-recs");
  if (!mount) return;

  var H = window.haoma || {};
  var KEY = "haoma_reads";
  var CAP = 30;
  var MAX_CARDS = 6;

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

  function normPath(p) {
    p = String(p || "").split("?")[0].split("#")[0];
    p = p.replace(/\/+/g, "/");
    if (!p) return "";
    /* strip language prefix and optional repo base (/Haoma/) */
    p = p.replace(/^\/(?:fa|en)(?=\/)/, "");
    var brand = document.querySelector(".brand[href]");
    if (brand) {
      try {
        var base = new URL(brand.href).pathname.replace(/\/$/, "");
        if (base && base !== "/" && p.indexOf(base + "/") === 0) p = p.slice(base.length);
      } catch (e) {}
    }
    if (p.charAt(0) !== "/") p = "/" + p;
    if (p.length > 1 && p.slice(-1) !== "/") p += "/";
    return p;
  }

  function loadReads() {
    if (!allowed()) return [];
    var raw = readLS(KEY);
    if (!raw) return [];
    try {
      var arr = JSON.parse(raw);
      return Array.isArray(arr) ? arr : [];
    } catch (e) {
      return [];
    }
  }

  function saveReads(arr) {
    if (!allowed()) return;
    writeLS(KEY, JSON.stringify(arr.slice(0, CAP)));
  }

  function record(entry) {
    if (!allowed() || !entry || !entry.k) return;
    var list = loadReads().filter(function (x) {
      return x && x.k !== entry.k;
    });
    list.unshift({
      k: entry.k,
      t: entry.t || "",
      c: entry.c || "",
      m: entry.m || [],
      ts: Date.now()
    });
    saveReads(list);
  }

  /* Expose clear for consent deny (boot hooks via haoma.clearReads if set). */
  H.clearReads = function () {
    clearLS(KEY);
  };
  window.haoma = H;

  var pageKey = normPath(mount.getAttribute("data-path") || "");
  var pageCult = mount.getAttribute("data-culture") || "";
  var pageTitle = mount.getAttribute("data-title") || "";
  var pageThemes = (mount.getAttribute("data-themes") || "")
    .split(/\s+/)
    .filter(Boolean);

  if (pageKey && pageKey.indexOf("/cultures/") === 0 && pageKey.split("/").length > 4) {
    record({ k: pageKey, t: pageTitle, c: pageCult, m: pageThemes });
  } else if (pageKey && pageKey.indexOf("/episodes/") === 0) {
    record({ k: pageKey, t: pageTitle, c: pageCult, m: pageThemes });
  }

  function idxUrl() {
    var link = document.querySelector('link[rel="alternate"][type="application/json"][title="related"]');
    if (link && link.href) return link.href;
    var brand = document.querySelector(".brand[href]");
    var base = (brand && brand.href) || document.baseURI || location.href;
    try {
      return new URL("related.json", base.endsWith("/") ? base : base.replace(/\/?$/, "/")).href;
    } catch (e) {
      return new URL("related.json", location.href).href;
    }
  }

  function parseFeatured() {
    try {
      return JSON.parse(mount.getAttribute("data-featured") || "[]") || [];
    } catch (e) {
      return [];
    }
  }

  function scorePage(p, reads, readKeys, inbound) {
    if (!p || !p.k || readKeys[p.k] || p.k === pageKey) return 0;
    var s = 0;
    var i, r, j, th;
    /* Bidirectional related edges to anything already read */
    for (i = 0; i < reads.length; i++) {
      r = reads[i];
      if (!r || !r.k) continue;
      if ((p.r || []).indexOf(r.k) >= 0) s += 12;
      if (inbound[r.k] && inbound[r.k][p.k]) s += 12;
      if (p.c && r.c && p.c === r.c) s += 3;
      if (r.m && p.m) {
        for (j = 0; j < r.m.length; j++) {
          if (p.m.indexOf(r.m[j]) >= 0) s += 4;
        }
      }
    }
    if (pageCult && p.c === pageCult) s += 2;
    if (pageThemes.length && p.m) {
      for (j = 0; j < pageThemes.length; j++) {
        th = pageThemes[j];
        if (p.m.indexOf(th) >= 0) s += 3;
      }
    }
    if ((p.r || []).indexOf(pageKey) >= 0) s += 8;
    if (inbound[pageKey] && inbound[pageKey][p.k]) s += 8;
    return s;
  }

  function buildInbound(pages) {
    var map = {};
    pages.forEach(function (p) {
      (p.r || []).forEach(function (tgt) {
        if (!map[tgt]) map[tgt] = {};
        map[tgt][p.k] = true;
      });
    });
    return map;
  }

  function cardHtml(p) {
    var title = p.t || "";
    var tip = p.g || "";
    var href = p.u || "#";
    var cult = p.c || "";
    return (
      '<li class="card card--art card--rec" data-culture="' +
      cult.replace(/"/g, "") +
      '">' +
      '<a class="art art--fall" href="' +
      href +
      '" tabindex="-1" aria-hidden="true">' +
      '<span class="art-fall" aria-hidden="true"></span>' +
      '<span class="art-lattice" aria-hidden="true"></span>' +
      '<span class="art-seal" aria-hidden="true"></span></a>' +
      '<div class="body"><div class="card-top"><span class="card-kind">' +
      (mount.getAttribute("data-i18n-cta") || "Read") +
      "</span></div>" +
      "<h3><a href=\"" +
      href +
      '">' +
      title.replace(/</g, "&lt;") +
      "</a></h3>" +
      (tip ? "<p>" + tip.replace(/</g, "&lt;") + "</p>" : "") +
      '<span class="card-go" aria-hidden="true"></span></div></li>'
    );
  }

  function render(pages) {
    var list = mount.querySelector("[data-recs-list]");
    var empty = mount.querySelector("[data-recs-empty]");
    if (!list) return;

    var reads = loadReads();
    var readKeys = {};
    reads.forEach(function (r) {
      if (r && r.k) readKeys[r.k] = true;
    });
    var inbound = buildInbound(pages);
    var scored = pages
      .map(function (p) {
        return { p: p, s: scorePage(p, reads, readKeys, inbound) };
      })
      .filter(function (x) {
        return x.s > 0;
      })
      .sort(function (a, b) {
        return b.s - a.s;
      });

    var picked = scored.slice(0, MAX_CARDS).map(function (x) {
      return x.p;
    });

    /* Fallback: featured from same culture (no personal history needed) */
    if (!picked.length) {
      var feat = parseFeatured();
      var seen = {};
      if (pageKey) seen[pageKey] = true;
      picked = feat
        .filter(function (f) {
          if (!f || !f.k || seen[f.k]) return false;
          seen[f.k] = true;
          return true;
        })
        .slice(0, MAX_CARDS);
    }

    if (!picked.length) {
      mount.hidden = true;
      if (empty) empty.hidden = false;
      return;
    }

    list.innerHTML = picked.map(cardHtml).join("");
    mount.hidden = false;
    if (empty) empty.hidden = true;
  }

  fetch(idxUrl(), { credentials: "same-origin" })
    .then(function (r) {
      if (!r.ok) throw new Error("related " + r.status);
      return r.json();
    })
    .then(function (j) {
      render(j.pages || []);
    })
    .catch(function () {
      render([]);
    });
})();
