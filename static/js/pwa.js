/* PWA: register service worker, soft install prompt (Android), iOS tip. */
(function () {
  var reduced = false;
  try {
    reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) {}

  /* Site root from a root-relative asset (works under /Haoma/ and /Haoma/fa/). */
  function siteRoot() {
    var css = document.querySelector('link[rel="stylesheet"][href*="style.css"]');
    if (css && css.href) {
      try {
        var u = new URL(css.href);
        u.search = "";
        u.hash = "";
        u.pathname = u.pathname.replace(/\/css\/[^/]*$/, "/");
        return u;
      } catch (e) {}
    }
    var brand = document.querySelector(".brand[href]");
    if (brand && brand.href) {
      try {
        var b = new URL(brand.href);
        if (!b.pathname.endsWith("/")) b.pathname += "/";
        return b;
      } catch (e2) {}
    }
    try {
      return new URL("./", document.baseURI || location.href);
    } catch (e3) {
      return new URL(location.origin + "/");
    }
  }

  function registerSW() {
    if (!("serviceWorker" in navigator)) return;
    var root = siteRoot();
    var swUrl = new URL("sw.js", root.href).href;
    navigator.serviceWorker.register(swUrl, { scope: root.pathname }).catch(function () {});
  }

  function dismissKey() {
    return "haoma_pwa_tip";
  }

  function tipSeen() {
    try {
      return sessionStorage.getItem(dismissKey()) === "1";
    } catch (e) {
      return false;
    }
  }

  function markSeen() {
    try {
      sessionStorage.setItem(dismissKey(), "1");
    } catch (e) {}
  }

  function isStandalone() {
    try {
      if (window.matchMedia("(display-mode: standalone)").matches) return true;
    } catch (e) {}
    return !!(window.navigator && window.navigator.standalone);
  }

  function isIos() {
    var ua = navigator.userAgent || "";
    return /iPad|iPhone|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  }

  function banner(html) {
    if (document.getElementById("pwa-banner")) return null;
    var el = document.createElement("div");
    el.id = "pwa-banner";
    el.className = "pwa-banner";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-live", "polite");
    el.innerHTML = html;
    document.body.appendChild(el);
    var close = el.querySelector("[data-pwa-dismiss]");
    if (close) {
      close.addEventListener("click", function () {
        markSeen();
        el.remove();
      });
    }
    return el;
  }

  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
    if (isStandalone() || tipSeen()) return;
    var tInstall = document.documentElement.getAttribute("data-pwa-install") || "Install Haoma";
    var tLater = document.documentElement.getAttribute("data-pwa-later") || "Not now";
    var tBody = document.documentElement.getAttribute("data-pwa-body") || "";
    var el = banner(
      '<div class="pwa-banner__inner">' +
        '<p class="pwa-banner__text">' +
        tBody +
        "</p>" +
        '<div class="pwa-banner__acts">' +
        '<button type="button" class="pwa-banner__go" data-pwa-install>' +
        tInstall +
        "</button>" +
        '<button type="button" class="pwa-banner__skip" data-pwa-dismiss>' +
        tLater +
        "</button>" +
        "</div></div>"
    );
    if (!el) return;
    var go = el.querySelector("[data-pwa-install]");
    if (go) {
      go.addEventListener("click", function () {
        markSeen();
        var prompt = deferred;
        deferred = null;
        el.remove();
        if (!prompt) return;
        prompt.prompt();
      });
    }
  });

  function maybeIosTip() {
    if (!isIos() || isStandalone() || tipSeen()) return;
    var tBody = document.documentElement.getAttribute("data-pwa-ios") || "";
    var tLater = document.documentElement.getAttribute("data-pwa-later") || "Not now";
    if (!tBody) return;
    window.setTimeout(
      function () {
        if (tipSeen() || document.getElementById("pwa-banner")) return;
        banner(
          '<div class="pwa-banner__inner">' +
            '<p class="pwa-banner__text">' +
            tBody +
            "</p>" +
            '<div class="pwa-banner__acts">' +
            '<button type="button" class="pwa-banner__skip" data-pwa-dismiss>' +
            tLater +
            "</button>" +
            "</div></div>"
        );
      },
      reduced ? 400 : 2800
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      registerSW();
      maybeIosTip();
    });
  } else {
    registerSW();
    maybeIosTip();
  }
})();
