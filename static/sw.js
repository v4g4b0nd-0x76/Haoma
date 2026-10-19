/* Haoma service worker — cache shell assets for offline revisit.
   Scope is the directory that hosts this file (site root or /Haoma/).
   Does not cache large media (audio/video/library). Version: pwa-1 */
/* eslint-disable no-restricted-globals */
(function () {
  var CACHE = "haoma-shell-pwa-1";
  var SHELL = [
    "./",
    "css/style.css",
    "js/boot.js",
    "js/site.js",
    "js/search.js",
    "js/stories.js",
    "js/news-tick.js",
    "img/brand/favicon.svg",
    "img/brand/favicon-192.png",
    "img/brand/apple-touch-icon.png",
    "manifest.webmanifest"
  ];

  self.addEventListener("install", function (event) {
    event.waitUntil(
      caches
        .open(CACHE)
        .then(function (cache) {
          return cache.addAll(
            SHELL.map(function (p) {
              return new URL(p, self.registration.scope).href;
            })
          );
        })
        .then(function () {
          return self.skipWaiting();
        })
        .catch(function () {
          /* partial shell OK — network will fill gaps */
          return self.skipWaiting();
        })
    );
  });

  self.addEventListener("activate", function (event) {
    event.waitUntil(
      caches
        .keys()
        .then(function (keys) {
          return Promise.all(
            keys
              .filter(function (k) {
                return k.indexOf("haoma-shell-") === 0 && k !== CACHE;
              })
              .map(function (k) {
                return caches.delete(k);
              })
          );
        })
        .then(function () {
          return self.clients.claim();
        })
    );
  });

  function isShellAsset(url) {
    var path = url.pathname || "";
    if (/\.(?:css|js|woff2|svg|png|ico|webmanifest)(?:$|\?)/i.test(path)) return true;
    if (/\/fonts\//.test(path)) return true;
    if (/\/img\/brand\//.test(path)) return true;
    return false;
  }

  function isHeavy(url) {
    var path = url.pathname || "";
    return /\/(?:audio|video|library)\//.test(path) || /\.(?:mp3|mp4|webm|pdf|epub)(?:$|\?)/i.test(path);
  }

  self.addEventListener("fetch", function (event) {
    var req = event.request;
    if (req.method !== "GET") return;
    var url;
    try {
      url = new URL(req.url);
    } catch (e) {
      return;
    }
    if (url.origin !== self.location.origin) return;
    if (isHeavy(url)) return;

    /* HTML / navigations: network first, cached shell fallback */
    if (req.mode === "navigate" || (req.headers.get("accept") || "").indexOf("text/html") !== -1) {
      event.respondWith(
        fetch(req)
          .then(function (res) {
            var copy = res.clone();
            caches.open(CACHE).then(function (c) {
              c.put(req, copy);
            });
            return res;
          })
          .catch(function () {
            return caches.match(req).then(function (hit) {
              return hit || caches.match(new URL("./", self.registration.scope).href);
            });
          })
      );
      return;
    }

    /* CSS/JS/fonts/icons: cache first, then network */
    if (isShellAsset(url)) {
      event.respondWith(
        caches.match(req).then(function (hit) {
          var net = fetch(req)
            .then(function (res) {
              if (res && res.ok) {
                var copy = res.clone();
                caches.open(CACHE).then(function (c) {
                  c.put(req, copy);
                });
              }
              return res;
            })
            .catch(function () {
              return hit;
            });
          return hit || net;
        })
      );
    }
  });
})();
