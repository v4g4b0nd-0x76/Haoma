/* PWA: register service worker, soft update banner, install tip (suppressed in standalone). */
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

  function tipKey() {
    return "haoma_pwa_tip";
  }

  function tipSeen() {
    try {
      if (localStorage.getItem(tipKey()) === "1") return true;
    } catch (e) {}
    try {
      return sessionStorage.getItem(tipKey()) === "1";
    } catch (e2) {
      return false;
    }
  }

  function markSeen() {
    try {
      localStorage.setItem(tipKey(), "1");
    } catch (e) {}
    try {
      sessionStorage.setItem(tipKey(), "1");
    } catch (e2) {}
  }

  function banner(html, id) {
    id = id || "pwa-banner";
    if (document.getElementById(id)) return null;
    var el = document.createElement("div");
    el.id = id;
    el.className = "pwa-banner";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-live", "polite");
    el.innerHTML = html;
    document.body.appendChild(el);
    var close = el.querySelector("[data-pwa-dismiss]");
    if (close) {
      close.addEventListener("click", function () {
        if (id === "pwa-banner") markSeen();
        el.remove();
      });
    }
    return el;
  }

  function registerSW() {
    if (!("serviceWorker" in navigator)) return;
    var root = siteRoot();
    var swUrl = new URL("sw.js", root.href).href;
    navigator.serviceWorker
      .register(swUrl, { scope: root.pathname })
      .then(function (reg) {
        watchUpdates(reg);
      })
      .catch(function () {});
  }

  function watchUpdates(reg) {
    function showUpdate() {
      if (!reg.waiting) return;
      if (document.getElementById("pwa-update")) return;
      var tBody =
        document.documentElement.getAttribute("data-pwa-update") ||
        "A new version is ready.";
      var tGo =
        document.documentElement.getAttribute("data-pwa-update-go") || "Refresh";
      var tLater =
        document.documentElement.getAttribute("data-pwa-later") || "Not now";
      var el = banner(
        '<div class="pwa-banner__inner">' +
          '<p class="pwa-banner__text">' +
          tBody +
          "</p>" +
          '<div class="pwa-banner__acts">' +
          '<button type="button" class="pwa-banner__go" data-pwa-refresh>' +
          tGo +
          "</button>" +
          '<button type="button" class="pwa-banner__skip" data-pwa-dismiss>' +
          tLater +
          "</button>" +
          "</div></div>",
        "pwa-update"
      );
      if (!el) return;
      var go = el.querySelector("[data-pwa-refresh]");
      if (go) {
        go.addEventListener("click", function () {
          var waiting = reg.waiting;
          if (!waiting) {
            el.remove();
            return;
          }
          var reloaded = false;
          navigator.serviceWorker.addEventListener("controllerchange", function () {
            if (reloaded) return;
            reloaded = true;
            location.reload();
          });
          waiting.postMessage({ type: "SKIP_WAITING" });
          el.remove();
        });
      }
    }

    if (reg.waiting) showUpdate();

    reg.addEventListener("updatefound", function () {
      var nw = reg.installing;
      if (!nw) return;
      nw.addEventListener("statechange", function () {
        if (nw.state === "installed" && navigator.serviceWorker.controller) {
          showUpdate();
        } else if (nw.state === "installed" && !navigator.serviceWorker.controller) {
          /* first install — activate without interrupting a read */
          if (reg.waiting) reg.waiting.postMessage({ type: "SKIP_WAITING" });
        }
      });
    });

    /* periodic check when tab is visible again */
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible") {
        try {
          reg.update();
        } catch (e) {}
      }
    });
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
        if (tipSeen() || document.getElementById("pwa-banner") || document.getElementById("pwa-update")) return;
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
