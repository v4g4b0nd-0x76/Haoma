/* Stories carousel — centered card, infinite wrap, shuffle, swipe + keyboard + dots. */
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

  /* Fisher–Yates */
  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function init(rail) {
    var track = rail.querySelector("[data-story-track]");
    var viewport = rail.querySelector(".story-rail__viewport");
    var status = rail.querySelector("[data-story-status]");
    if (!track || !viewport) return;

    var cards = [];
    var dots = [];
    var n = 0;
    var i = 0;
    var busy = false;
    var stepsSinceShuffle = 0;
    var mqSide = null;
    try {
      mqSide = matchMedia("(min-width: 720px)");
    } catch (e) {}

    function refreshRefs() {
      cards = Q(".story-card", track);
      dots = Q(".story-rail__dot", rail);
      n = cards.length;
    }

    function applyOrder(ordered) {
      ordered.forEach(function (c) {
        track.appendChild(c);
      });
      var dotsHost = rail.querySelector(".story-rail__dots");
      if (dotsHost && dots.length === ordered.length) {
        ordered.forEach(function (c) {
          var title = "";
          var tEl = c.querySelector(".story-card__title");
          if (tEl) title = (tEl.textContent || "").trim();
          var match = null;
          for (var d = 0; d < dots.length; d++) {
            if (dots[d].getAttribute("aria-label") === title) {
              match = dots[d];
              break;
            }
          }
          if (match) dotsHost.appendChild(match);
        });
      }
      refreshRefs();
      cards.forEach(function (c, k) {
        c.setAttribute("data-story-i", String(k));
      });
      dots.forEach(function (d, k) {
        d.setAttribute("data-story-go", String(k));
      });
    }

    function reshuffle(keepCurrent) {
      refreshRefs();
      if (n < 2) return;
      var current = keepCurrent && cards[i] ? cards[i] : null;
      var ordered = shuffle(cards);
      if (current) {
        ordered = ordered.filter(function (c) {
          return c !== current;
        });
        ordered.unshift(current);
      }
      applyOrder(ordered);
      i = 0;
      stepsSinceShuffle = 0;
      track.style.setProperty("--story-i", "0");
      mark(0);
    }

    function syncNavA11y() {
      var side = mqSide && mqSide.matches;
      Q(".story-rail__nav--side", rail).forEach(function (b) {
        b.hidden = !side;
        b.setAttribute("aria-hidden", side ? "false" : "true");
        b.tabIndex = side ? 0 : -1;
      });
      Q(".story-rail__nav--bar", rail).forEach(function (b) {
        b.hidden = !!side;
        b.setAttribute("aria-hidden", side ? "true" : "false");
        b.tabIndex = side ? -1 : 0;
      });
    }

    function mark(idx) {
      cards.forEach(function (c, k) {
        var on = k === idx;
        c.classList.toggle("is-active", on);
        c.setAttribute("aria-hidden", on ? "false" : "true");
        if (on) c.removeAttribute("inert");
        else c.setAttribute("inert", "");
        Q("a", c).forEach(function (a) {
          if (on) a.removeAttribute("tabindex");
          else a.tabIndex = -1;
        });
      });
      dots.forEach(function (d, k) {
        var on = k === idx;
        d.classList.toggle("is-on", on);
        d.setAttribute("aria-current", on ? "true" : "false");
      });
      if (status) {
        var title = "";
        var tEl = cards[idx] && cards[idx].querySelector(".story-card__title");
        if (tEl) title = (tEl.textContent || "").trim();
        status.textContent = title;
      }
    }

    function finishMove(shouldReshuffle) {
      if (shouldReshuffle) {
        reshuffle(true);
      }
      busy = false;
      rail.removeAttribute("data-animating");
    }

    function go(next, dir) {
      if (n < 2 || busy) return;

      var step = dir || 0;
      var target;
      if (step) {
        target = ((i + step) % n + n) % n;
      } else {
        target = ((next % n) + n) % n;
        if (target === i) return;
        if (i === n - 1 && target === 0) step = 1;
        else if (i === 0 && target === n - 1) step = -1;
        else step = target > i ? 1 : -1;
      }
      if (target === i) return;

      var from = i;
      var wrapping =
        (from === n - 1 && target === 0 && step === 1) ||
        (from === 0 && target === n - 1 && step === -1);

      i = target;
      busy = true;
      stepsSinceShuffle += 1;
      var lapDone = stepsSinceShuffle >= n || wrapping;

      rail.dataset.storyDir = String(step);
      /* Skip long slide across the deck when wrapping end↔start */
      if (wrapping && !reduced) {
        rail.setAttribute("data-animating", "0");
        track.style.setProperty("--story-i", String(i));
        mark(i);
        window.setTimeout(function () {
          finishMove(true);
        }, 40);
        return;
      }

      track.style.setProperty("--story-i", String(i));
      mark(i);

      if (reduced) {
        finishMove(lapDone);
        return;
      }
      rail.setAttribute("data-animating", "1");
      window.setTimeout(function () {
        finishMove(lapDone);
      }, 740);
    }

    refreshRefs();
    if (n < 1) return;
    if (n === 1) {
      mark(0);
      return;
    }

    /* Initial shuffle each page load */
    applyOrder(shuffle(cards));
    i = 0;
    stepsSinceShuffle = 0;
    track.style.setProperty("--story-i", "0");
    mark(0);
    syncNavA11y();
    if (mqSide) {
      if (mqSide.addEventListener) mqSide.addEventListener("change", syncNavA11y);
      else if (mqSide.addListener) mqSide.addListener(syncNavA11y);
    }

    /* Prev/next buttons keep fixed semantics; RTL already swaps their sides in layout.
       Do not invert click direction here (avoids double-flip with mirrored DOM). */
    Q("[data-story-dir]", rail).forEach(function (b) {
      b.addEventListener("click", function () {
        var d = +b.getAttribute("data-story-dir") || 0;
        go(i + d, d);
      });
    });

    var dotsHost = rail.querySelector(".story-rail__dots");
    if (dotsHost) {
      dotsHost.addEventListener("click", function (e) {
        var d = e.target && e.target.closest ? e.target.closest("[data-story-go]") : null;
        if (!d || !dotsHost.contains(d)) return;
        var k = +d.getAttribute("data-story-go");
        if (!isNaN(k)) go(k);
      });
    }

    rail.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      var t = e.target;
      if (!rail.contains(t)) return;
      var tag = (t.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select" || t.isContentEditable)
        return;
      e.preventDefault();
      var d = e.key === "ArrowRight" ? 1 : -1;
      if (isRtl(rail)) d = -d;
      go(i + d, d);
    });

    /* Swipe on the card body (which is an <a>). Ignore only chrome controls /
       secondary links; suppress click after a successful swipe. */
    function isSwipeBlocked(t) {
      if (!t || !t.closest) return true;
      return !!t.closest(".story-rail__nav, .story-rail__dot, .story-card__more a");
    }

    var startX = 0;
    var startY = 0;
    var dragging = false;
    var axis = "";
    var pid = null;
    var didSwipe = false;

    function onDown(e) {
      if (e.button != null && e.button !== 0) return;
      if (isSwipeBlocked(e.target)) return;
      dragging = true;
      didSwipe = false;
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
        rail.removeAttribute("data-dragging");
        track.style.removeProperty("--story-drag");
        return;
      }
      e.preventDefault();
      var pull = isRtl(rail) ? -dx : dx;
      track.style.setProperty("--story-drag", pull + "px");
      rail.dataset.dragging = "1";
    }
    function onUp(e) {
      if (!dragging && !rail.dataset.dragging) return;
      dragging = false;
      rail.removeAttribute("data-dragging");
      var dx = (e.clientX != null ? e.clientX : startX) - startX;
      track.style.removeProperty("--story-drag");
      try {
        if (pid != null) viewport.releasePointerCapture(pid);
      } catch (err) {}
      pid = null;
      if (axis !== "x") {
        axis = "";
        return;
      }
      axis = "";
      var pull = isRtl(rail) ? -dx : dx;
      var thresh = Math.min(56, Math.max(40, viewport.clientWidth * 0.14));
      if (pull <= -thresh) {
        didSwipe = true;
        go(i + 1, 1);
      } else if (pull >= thresh) {
        didSwipe = true;
        go(i - 1, -1);
      }
    }

    viewport.addEventListener(
      "click",
      function (e) {
        if (!didSwipe) return;
        didSwipe = false;
        e.preventDefault();
        e.stopPropagation();
      },
      true
    );

    if (window.PointerEvent) {
      viewport.addEventListener("pointerdown", onDown);
      viewport.addEventListener("pointermove", onMove);
      viewport.addEventListener("pointerup", onUp);
      viewport.addEventListener("pointercancel", onUp);
    } else {
      var tx = 0,
        ty = 0,
        tax = "";
      viewport.addEventListener(
        "touchstart",
        function (e) {
          if (!e.touches || !e.touches[0]) return;
          if (isSwipeBlocked(e.target)) return;
          tx = e.touches[0].clientX;
          ty = e.touches[0].clientY;
          tax = "";
          didSwipe = false;
          rail.dataset.dragging = "1";
        },
        { passive: true }
      );
      viewport.addEventListener(
        "touchmove",
        function (e) {
          if (!rail.dataset.dragging || !e.touches || !e.touches[0]) return;
          var dx = e.touches[0].clientX - tx;
          var dy = e.touches[0].clientY - ty;
          if (!tax) {
            if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
            tax = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
          }
          if (tax === "y") {
            rail.removeAttribute("data-dragging");
            track.style.removeProperty("--story-drag");
            return;
          }
          var pull = isRtl(rail) ? -dx : dx;
          track.style.setProperty("--story-drag", pull + "px");
        },
        { passive: true }
      );
      viewport.addEventListener("touchend", function (e) {
        if (!rail.dataset.dragging && tax !== "x") return;
        rail.removeAttribute("data-dragging");
        track.style.removeProperty("--story-drag");
        if (tax !== "x" || !e.changedTouches || !e.changedTouches[0]) {
          tax = "";
          return;
        }
        var dx = e.changedTouches[0].clientX - tx;
        var pull = isRtl(rail) ? -dx : dx;
        var thresh = Math.min(56, Math.max(40, viewport.clientWidth * 0.14));
        tax = "";
        if (pull <= -thresh) {
          didSwipe = true;
          go(i + 1, 1);
        } else if (pull >= thresh) {
          didSwipe = true;
          go(i - 1, -1);
        }
      });
    }
  }

  Q(".story-rail--carousel").forEach(init);
})();
