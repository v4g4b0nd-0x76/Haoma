/* Haoma service worker — shell assets + recently visited HTML.
   Scope is the directory that hosts this file (site root or /Haoma/).
   Does not cache large media (audio/video/library). Version: pwa-2 */
/* eslint-disable no-restricted-globals */
(function () {
  var SHELL_CACHE = "haoma-shell-pwa-2";
  var PAGES_CACHE = "haoma-pages-pwa-2";
  var MAX_PAGES = 40;
  var SHELL = [
    "./",
    "css/style.css",
    "js/boot.js",
    "js/site.js",
    "js/search.js",
    "js/stories.js",
    "js/news-tick.js",
    "js/pwa.js",
    "js/study.js",
    "img/brand/favicon.svg",
    "img/brand/favicon-192.png",
    "img/brand/apple-touch-icon.png",
    "manifest.webmanifest"
  ];

  self.addEventListener("install", function (event) {
    event.waitUntil(
      caches
        .open(SHELL_CACHE)
        .then(function (cache) {
          return cache.addAll(
            SHELL.map(function (p) {
              return new URL(p, self.registration.scope).href;
            })
          );
        })
        .catch(function () {
          /* partial shell OK — network will fill gaps */
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
                return (
                  (k.indexOf("haoma-shell-") === 0 || k.indexOf("haoma-pages-") === 0) &&
                  k !== SHELL_CACHE &&
                  k !== PAGES_CACHE
                );
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

  self.addEventListener("message", function (event) {
    var data = event.data;
    if (data && data.type === "SKIP_WAITING") {
      self.skipWaiting();
    }
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

  function trimPagesCache(cache) {
    return cache.keys().then(function (keys) {
      if (keys.length <= MAX_PAGES) return;
      var drop = keys.length - MAX_PAGES;
      var chain = Promise.resolve();
      keys.slice(0, drop).forEach(function (req) {
        chain = chain.then(function () {
          return cache.delete(req);
        });
      });
      return chain;
    });
  }

  function putPage(req, res) {
    if (!res || !res.ok) return;
    var copy = res.clone();
    caches.open(PAGES_CACHE).then(function (c) {
      c.put(req, copy).then(function () {
        return trimPagesCache(c);
      });
    });
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

    /* HTML / navigations: network first, cache visited pages, shell fallback */
    if (req.mode === "navigate" || (req.headers.get("accept") || "").indexOf("text/html") !== -1) {
      event.respondWith(
        fetch(req)
          .then(function (res) {
            putPage(req, res);
            return res;
          })
          .catch(function () {
            return caches.match(req).then(function (hit) {
              if (hit) return hit;
              return caches.open(PAGES_CACHE).then(function (c) {
                return c.match(req).then(function (pageHit) {
                  return (
                    pageHit ||
                    caches.match(new URL("./", self.registration.scope).href)
                  );
                });
              });
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
                caches.open(SHELL_CACHE).then(function (c) {
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
