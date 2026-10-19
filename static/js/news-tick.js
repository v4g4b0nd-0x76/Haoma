/* Header preview strip — cycles episodes/articles; dismiss in prefs/cookies. */
(function () {
  var root = document.getElementById("news-tick");
  if (!root) return;
  var H = window.haoma || {};
  var dataEl = document.getElementById("news-tick-data");
  var kindEl = root.querySelector("[data-ntick-kind]");
  var titleEl = root.querySelector("[data-ntick-title]");
  var linkEl = root.querySelector("[data-ntick-link]");
  var closeBtn = root.querySelector("[data-ntick-close]");
  var items = [];
  try {
    items = JSON.parse((dataEl && dataEl.textContent) || "[]");
    if (typeof items === "string") items = JSON.parse(items);
    if (!Array.isArray(items)) items = [];
  } catch (e) {
    items = [];
  }
  if (!items.length || !linkEl || !titleEl) return;

  var labels = {
    episode: root.getAttribute("data-label-episode") || "Episode",
    article: root.getAttribute("data-label-article") || "Article"
  };
  var ms = parseInt(root.getAttribute("data-interval"), 10) || 6000;
  if (ms < 2500) ms = 2500;

  function prefs() {
    return (H.getPrefs && H.getPrefs()) || {};
  }
  function savePrefs(P) {
    if (H.setPrefs) H.setPrefs(P);
  }
  function isClosed() {
    var P = prefs();
    if (P && P.hideNewsTick) return true;
    try {
      if (sessionStorage.getItem("haoma_hide_news_tick") === "1") return true;
    } catch (e) {}
    if (H.getCookie && H.getCookie("haoma_hide_tick") === "1") return true;
    return false;
  }
  function closeAndRemember() {
    root.hidden = true;
    root.setAttribute("aria-hidden", "true");
    if (timer) clearInterval(timer);
    var P = prefs();
    P.hideNewsTick = true;
    if (H.allowed && H.allowed()) {
      savePrefs(P);
      if (H.setCookie) H.setCookie("haoma_hide_tick", "1", 365 * 24 * 60 * 60);
    } else {
      try {
        sessionStorage.setItem("haoma_hide_news_tick", "1");
      } catch (e) {}
      if (H.setCookie) H.setCookie("haoma_hide_tick", "1", 90 * 24 * 60 * 60);
    }
  }

  if (isClosed()) {
    root.hidden = true;
    return;
  }

  function normPath(href) {
    try {
      var u = new URL(href, location.href);
      return (u.pathname || "/").replace(/\/+$/, "") || "/";
    } catch (e) {
      return "";
    }
  }
  var here = normPath(location.href);

  var i = 0;
  for (var s = 0; s < items.length; s++) {
    if (normPath(items[s].href) !== here) {
      i = s;
      break;
    }
  }
  var timer = null;
  var reduced = false;
  try {
    reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) {}

  function paint(idx) {
    var it = items[idx];
    if (!it) return;
    var kind = it.kind === "episode" ? "episode" : "article";
    root.setAttribute("data-kind", kind);
    if (kindEl) kindEl.textContent = labels[kind];
    titleEl.textContent = it.title || "";
    linkEl.href = it.href || "#";
    root.classList.remove("is-swap");
    void root.offsetWidth;
    root.classList.add("is-swap");
  }

  function next() {
    i = (i + 1) % items.length;
    paint(i);
  }

  paint(i);
  root.hidden = false;
  root.removeAttribute("aria-hidden");

  if (items.length > 1 && !reduced) {
    timer = setInterval(next, ms);
    root.addEventListener("mouseenter", function () {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    });
    root.addEventListener("mouseleave", function () {
      if (!timer && !root.hidden) timer = setInterval(next, ms);
    });
  }

  /* Same-page click: avoid reload that can flash a mid-layout header state. */
  linkEl.addEventListener("click", function (ev) {
    if (normPath(linkEl.href) === here) {
      ev.preventDefault();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", function (ev) {
      ev.preventDefault();
      ev.stopPropagation();
      closeAndRemember();
    });
  }
})();
