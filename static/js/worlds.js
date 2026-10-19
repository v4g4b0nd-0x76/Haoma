/* Home “Choose your world” — one culture slide; section atmosphere follows culture. */
(function () {
  var Q = function (s, r) {
    return [].slice.call((r || document).querySelectorAll(s));
  };
  var reduced = false;
  try {
    reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) {}

  function isRtl(el) {
    return getComputedStyle(el).direction === "rtl";
  }

  function init(root) {
    var track = root.querySelector("[data-world-track]");
    var viewport = root.querySelector(".world-viewport");
    var slides = Q(".world-slide", track);
    var dots = Q(".world-dot", root);
    var status = root.querySelector("[data-world-status]");
    var n = slides.length;
    if (!track || !viewport || n < 1) return;

    var i = 0;
    var busy = false;

    function paintCulture(idx) {
      var s = slides[idx];
      if (!s) return;
      var c = s.getAttribute("data-culture") || "";
      if (c) root.setAttribute("data-culture", c);
      else root.removeAttribute("data-culture");
      if (status) {
        var t = s.querySelector("h3");
        status.textContent = t ? (t.textContent || "").trim() : "";
      }
    }

    function mark(idx) {
      slides.forEach(function (s, k) {
        var on = k === idx;
        s.classList.toggle("is-active", on);
        s.setAttribute("aria-hidden", on ? "false" : "true");
        if (on) s.removeAttribute("inert");
        else s.setAttribute("inert", "");
        Q("a", s).forEach(function (a) {
          if (on) a.removeAttribute("tabindex");
          else a.tabIndex = -1;
        });
      });
      dots.forEach(function (d, k) {
        var on = k === idx;
        d.classList.toggle("is-on", on);
        d.setAttribute("aria-current", on ? "true" : "false");
      });
      paintCulture(idx);
    }

    function go(next, dir) {
      next = ((next % n) + n) % n;
      if (next === i || busy) return;
      var from = i;
      var step = dir;
      if (!step) step = next > from ? 1 : -1;
      if (Math.abs(next - from) > n / 2) step = -step;
      if ((from === n - 1 && next === 0) || (from === 0 && next === n - 1)) {
        step = from === n - 1 ? 1 : -1;
      }
      i = next;
      busy = true;
      root.dataset.worldDir = String(step);
      track.style.setProperty("--world-i", String(i));
      mark(i);
      var done = function () {
        busy = false;
        root.removeAttribute("data-animating");
      };
      if (reduced) {
        done();
        return;
      }
      root.setAttribute("data-animating", "1");
      window.setTimeout(done, 800);
    }

    track.style.setProperty("--world-i", "0");
    mark(0);

    /* Buttons keep fixed prev/next semantics; RTL layout already mirrors placement. */
    Q("[data-world-dir]", root).forEach(function (b) {
      b.addEventListener("click", function () {
        var d = +b.getAttribute("data-world-dir") || 0;
        go(i + d, d);
      });
    });
    dots.forEach(function (d) {
      d.addEventListener("click", function () {
        var k = +d.getAttribute("data-world-go");
        if (!isNaN(k)) go(k);
      });
    });

    root.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      var t = e.target;
      if (!root.contains(t)) return;
      var tag = (t.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select" || t.isContentEditable)
        return;
      e.preventDefault();
      var d = e.key === "ArrowRight" ? 1 : -1;
      if (isRtl(root)) d = -d;
      go(i + d, d);
    });

    var startX = 0;
    var startY = 0;
    var dragging = false;
    var axis = "";
    var pid = null;

    function onDown(e) {
      if (e.button != null && e.button !== 0) return;
      if (e.target.closest && e.target.closest("a,button")) return;
      dragging = true;
      axis = "";
      pid = e.pointerId;
      startX = e.clientX;
      startY = e.clientY;
      try {
        viewport.setPointerCapture(pid);
      } catch (err) {}
    }
    function onMove(e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      var dy = e.clientY - startY;
      if (!axis) {
        if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
        axis = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
      }
      if (axis === "y") {
        dragging = false;
        return;
      }
      e.preventDefault();
      var pull = isRtl(root) ? -dx : dx;
      track.style.setProperty("--world-drag", pull + "px");
      root.dataset.dragging = "1";
    }
    function onUp(e) {
      if (!dragging && !root.dataset.dragging) return;
      dragging = false;
      root.removeAttribute("data-dragging");
      var dx = e.clientX - startX;
      track.style.removeProperty("--world-drag");
      try {
        if (pid != null) viewport.releasePointerCapture(pid);
      } catch (err) {}
      pid = null;
      if (axis !== "x") {
        axis = "";
        return;
      }
      axis = "";
      var pull = isRtl(root) ? -dx : dx;
      var thresh = Math.min(72, viewport.clientWidth * 0.18);
      if (pull <= -thresh) go(i + 1, 1);
      else if (pull >= thresh) go(i - 1, -1);
    }

    if (window.PointerEvent) {
      viewport.addEventListener("pointerdown", onDown);
      viewport.addEventListener("pointermove", onMove);
      viewport.addEventListener("pointerup", onUp);
      viewport.addEventListener("pointercancel", onUp);
    }
  }

  Q("[data-world-slider]").forEach(init);
})();
