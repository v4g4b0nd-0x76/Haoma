/* Home: light scroll-reveal per panel (tablet+). Avoids snap/blur jank. */
(function () {
  if (!document.body || !document.body.classList.contains("is-home")) return;
  var reduced = false;
  var wide = false;
  try {
    reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) {}
  try {
    wide = matchMedia("(min-width: 768px)").matches;
  } catch (e) {}
  if (reduced || !wide || !("IntersectionObserver" in window)) return;

  var panels = [].slice.call(document.querySelectorAll("[data-home-panel], .home-panel"));
  if (!panels.length) return;

  /* One reveal per section — fewer simultaneous transitions while scrolling */
  panels.forEach(function (p) {
    if (p.classList.contains("cine")) return;
    p.classList.add("home-reveal");
  });

  var pending = panels.filter(function (p) {
    return p.classList.contains("home-reveal");
  });
  if (!pending.length) return;

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target;
        /* rAF: apply class on next frame so it doesn't fight the scroll sample */
        requestAnimationFrame(function () {
          el.classList.add("is-in");
        });
        io.unobserve(el);
      });
    },
    { root: null, rootMargin: "12% 0px -8% 0px", threshold: 0.08 }
  );

  pending.forEach(function (p) {
    io.observe(p);
  });

  /* If already on-screen at load, reveal without waiting for a stuttery first scroll */
  requestAnimationFrame(function () {
    pending.forEach(function (p) {
      var r = p.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.92 && r.bottom > 0) {
        p.classList.add("is-in");
        io.unobserve(p);
      }
    });
  });
})();
