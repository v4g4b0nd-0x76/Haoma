/* Culture atlas: section-aligned graph + focus dock + optional reading-path tour. */
(function () {
  var roots = document.querySelectorAll("[data-atlas-root]");
  if (!roots.length) return;

  var SEC_ORDER = ["characters", "traditions", "stories", "history", "episode"];
  var SEC_COLOR = {
    characters: null,
    traditions: "#c4a0d8",
    stories: "#93b9d1",
    history: "#c9a27a",
    episode: "#a88f56"
  };

  function accent() {
    return getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#e0a03a";
  }

  function secFill(sec) {
    return sec === "characters" ? accent() : (SEC_COLOR[sec] || accent());
  }

  function init(root) {
    var wrap = root.closest("[data-atlas]");
    var raw = wrap && wrap.querySelector("[data-atlas-json]");
    if (!raw) return;
    var data;
    try { data = JSON.parse(raw.textContent); } catch (e) { return; }

    var nodes = (data.nodes || []).map(function (n) {
      return {
        id: n.id, title: n.title, sec: n.sec || "characters", url: n.url,
        tagline: n.tagline || "",
        x: 0, y: 0, vx: 0, vy: 0, tx: 0, ty: 0
      };
    });
    if (!nodes.length) return;

    var byId = {};
    nodes.forEach(function (n) { byId[n.id] = n; });
    var links = (data.edges || []).map(function (e) {
      return { source: byId[e.source], target: byId[e.target] };
    }).filter(function (l) { return l.source && l.target; });
    var pathIds = (data.path || []).filter(function (id) { return byId[id]; });

    var tourBar = wrap.querySelector("[data-atlas-tour]");
    var tourRun = wrap.querySelector("[data-tour-run]");
    var tourStepEl = wrap.querySelector("[data-tour-step]");
    var dock = wrap.querySelector("[data-atlas-dock]");
    var dockSec = wrap.querySelector("[data-atlas-dock-sec]");
    var dockTitle = wrap.querySelector("[data-atlas-dock-title]");
    var dockTag = wrap.querySelector("[data-atlas-dock-tag]");
    var dockOpen = wrap.querySelector("[data-atlas-dock-open]");
    var dockClear = wrap.querySelector("[data-atlas-dock-clear]");
    var dockNeigh = wrap.querySelector("[data-atlas-dock-neigh]");
    var legend = wrap.querySelector("[data-atlas-legend]");
    var tourIdx = -1;

    var W = root.clientWidth || 640;
    var H = Math.max(400, Math.min(560, Math.round(W * 0.58)));
    root.style.height = H + "px";
    ["selectstart", "dragstart"].forEach(function (type) {
      root.addEventListener(type, function (e) { e.preventDefault(); });
    });

    /* ---- section columns: even x slots, even y within each column ---- */
    function layoutTargets() {
      var groups = {};
      SEC_ORDER.forEach(function (s) { groups[s] = []; });
      nodes.forEach(function (n) {
        var s = groups[n.sec] ? n.sec : "characters";
        if (!groups[s]) groups[s] = [];
        groups[s].push(n);
      });
      var cols = SEC_ORDER.filter(function (s) { return groups[s] && groups[s].length; });
      if (!cols.length) cols = ["characters"];
      var marginX = Math.min(90, W * 0.12);
      var marginY = Math.min(70, H * 0.14);
      var spanX = W - marginX * 2;
      var spanY = H - marginY * 2;
      var colW = spanX / cols.length;
      cols.forEach(function (sec, ci) {
        var list = groups[sec].slice().sort(function (a, b) {
          return a.title.localeCompare(b.title);
        });
        var n = list.length;
        var x = -W / 2 + marginX + colW * (ci + 0.5);
        list.forEach(function (node, ji) {
          var y = n === 1 ? 0 : (-H / 2 + marginY + (spanY * (ji + 0.5)) / n);
          node.tx = x;
          node.ty = y;
          if (node.fx == null) {
            node.x = x + (Math.random() - 0.5) * 8;
            node.y = y + (Math.random() - 0.5) * 8;
          }
        });
      });
      /* column headers as data for paint */
      return cols.map(function (sec, ci) {
        return { sec: sec, x: -W / 2 + marginX + colW * (ci + 0.5) };
      });
    }

    var colMeta = layoutTargets();

    if (legend) {
      var used = {};
      nodes.forEach(function (n) { used[n.sec] = 1; });
      legend.querySelectorAll("[data-sec]").forEach(function (li) {
        li.hidden = !used[li.getAttribute("data-sec")];
        var sw = li.querySelector(".atlas__swatch");
        if (sw) sw.style.background = secFill(li.getAttribute("data-sec"));
      });
    }

    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", (-W / 2) + " " + (-H / 2) + " " + W + " " + H);
    svg.setAttribute("class", "atlas__svg");
    svg.setAttribute("role", "presentation");
    svg.setAttribute("focusable", "false");
    root.appendChild(svg);

    var gWorld = document.createElementNS(svg.namespaceURI, "g");
    gWorld.setAttribute("class", "atlas__world");
    var gCols = document.createElementNS(svg.namespaceURI, "g");
    gCols.setAttribute("class", "atlas__cols");
    var gLinks = document.createElementNS(svg.namespaceURI, "g");
    gLinks.setAttribute("class", "atlas__links");
    var gTour = document.createElementNS(svg.namespaceURI, "g");
    gTour.setAttribute("class", "atlas__tour-links");
    var gNodes = document.createElementNS(svg.namespaceURI, "g");
    gNodes.setAttribute("class", "atlas__nodes");
    gWorld.appendChild(gCols);
    gWorld.appendChild(gLinks);
    gWorld.appendChild(gTour);
    gWorld.appendChild(gNodes);
    svg.appendChild(gWorld);

    /* faint vertical guides + section labels */
    var colLabelEls = colMeta.map(function (c) {
      var g = document.createElementNS(svg.namespaceURI, "g");
      g.setAttribute("class", "atlas__col");
      g.setAttribute("data-sec", c.sec);
      var line = document.createElementNS(svg.namespaceURI, "line");
      line.setAttribute("class", "atlas__col-line");
      line.setAttribute("x1", c.x); line.setAttribute("x2", c.x);
      line.setAttribute("y1", -H / 2 + 28); line.setAttribute("y2", H / 2 - 20);
      var lab = document.createElementNS(svg.namespaceURI, "text");
      lab.setAttribute("class", "atlas__col-label");
      lab.setAttribute("x", c.x); lab.setAttribute("y", -H / 2 + 18);
      lab.setAttribute("text-anchor", "middle");
      var legendLi = legend && legend.querySelector('[data-sec="' + c.sec + '"]');
      lab.textContent = legendLi ? (legendLi.getAttribute("data-label") || c.sec) : c.sec;
      g.appendChild(line);
      g.appendChild(lab);
      gCols.appendChild(g);
      return g;
    });

    var linkEls = links.map(function (l) {
      var path = document.createElementNS(svg.namespaceURI, "path");
      path.setAttribute("class", "atlas__link");
      gLinks.appendChild(path);
      return path;
    });
    /* Tour bridges: consecutive reading-path steps even when related: has no edge */
    var tourLinkEls = [];
    for (var ti = 0; ti < Math.max(0, pathIds.length - 1); ti++) {
      var tp = document.createElementNS(svg.namespaceURI, "path");
      tp.setAttribute("class", "atlas__link atlas__link--tour");
      gTour.appendChild(tp);
      tourLinkEls.push(tp);
    }

    var focus = null;
    var drag = null;
    var dragMoved = false;
    var dragStart = null;
    var capturing = false;
    var pan = null;
    var panX = 0, panY = 0;
    var scale = 1;
    var DRAG_THRESHOLD = 5;
    var lastTap = { id: null, t: 0 };
    var viewRaf = 0;

    function paintView() {
      gWorld.setAttribute("transform", "translate(" + panX + "," + panY + ") scale(" + scale + ")");
    }
    /* Pan/zoom paint is rAF-coalesced. Do not kick the force sim on pan —
       that was O(n²) every pointermove and crushed FPS on culture hubs. */
    function applyView(opts) {
      opts = opts || {};
      if (opts.now) {
        if (viewRaf) { cancelAnimationFrame(viewRaf); viewRaf = 0; }
        paintView();
      } else if (!viewRaf) {
        viewRaf = requestAnimationFrame(function () {
          viewRaf = 0;
          paintView();
        });
      }
      if (opts.sim && typeof kickSim === "function") {
        kickSim(opts.sim === true ? 0.25 : opts.sim);
      }
    }

    function openNode(n) {
      if (n && n.url) location.assign(n.url);
    }

    function pathPair(a, b) {
      for (var i = 0; i < pathIds.length - 1; i++) {
        if ((pathIds[i] === a && pathIds[i + 1] === b) || (pathIds[i] === b && pathIds[i + 1] === a)) return true;
      }
      return false;
    }

    function neighborIds(n) {
      var out = [];
      links.forEach(function (l) {
        if (l.source === n) out.push(l.target);
        else if (l.target === n) out.push(l.source);
      });
      return out;
    }

    function paintDock() {
      if (!dock) return;
      if (!focus) {
        dock.hidden = true;
        return;
      }
      dock.hidden = false;
      if (dockSec) {
        var li = legend && legend.querySelector('[data-sec="' + focus.sec + '"]');
        dockSec.textContent = li ? (li.getAttribute("data-label") || focus.sec) : focus.sec;
        dockSec.style.setProperty("--sec-c", secFill(focus.sec));
      }
      if (dockTitle) dockTitle.textContent = focus.title;
      if (dockTag) {
        dockTag.textContent = focus.tagline || "";
        dockTag.hidden = !focus.tagline;
      }
      if (dockOpen) {
        dockOpen.href = focus.url || "#";
        dockOpen.hidden = !focus.url;
      }
      if (dockNeigh) {
        var ns = neighborIds(focus);
        dockNeigh.innerHTML = "";
        if (ns.length) {
          ns.slice(0, 8).forEach(function (n) {
            var b = document.createElement("button");
            b.type = "button";
            b.className = "atlas__chip";
            b.textContent = n.title;
            b.onclick = function () { focus = n; paintFocus(); };
            dockNeigh.appendChild(b);
          });
        }
      }
    }

    function paintFocus() {
      var neigh = {};
      var pathSet = {};
      if (tourIdx >= 0 && pathIds.length) {
        pathIds.forEach(function (id) { pathSet[id] = 1; });
        neigh[pathIds[tourIdx]] = 1;
        if (pathIds[tourIdx - 1]) neigh[pathIds[tourIdx - 1]] = 1;
        if (pathIds[tourIdx + 1]) neigh[pathIds[tourIdx + 1]] = 1;
      } else if (focus) {
        neigh[focus.id] = 1;
        links.forEach(function (l) {
          if (l.source === focus) neigh[l.target.id] = 1;
          if (l.target === focus) neigh[l.source.id] = 1;
        });
      }
      nodeEls.forEach(function (g, i) {
        var n = nodes[i];
        var on = !focus && tourIdx < 0 || neigh[n.id] || (tourIdx >= 0 && pathSet[n.id]);
        g.classList.toggle("is-dim", !on && (focus || tourIdx >= 0));
        g.classList.toggle("is-focus", focus === n || (tourIdx >= 0 && pathIds[tourIdx] === n.id));
        g.classList.toggle("is-step", tourIdx >= 0 && pathSet[n.id]);
        g.classList.toggle("is-tour-here", tourIdx >= 0 && pathIds[tourIdx] === n.id);
      });
      linkEls.forEach(function (line, i) {
        var l = links[i];
        var onPath = pathPair(l.source.id, l.target.id);
        var on = !focus && tourIdx < 0 || l.source === focus || l.target === focus || (tourIdx >= 0 && onPath);
        line.classList.toggle("is-dim", !on && (focus || tourIdx >= 0));
        line.classList.toggle("is-hot", !!(focus && on && tourIdx < 0));
        line.classList.toggle("is-path", tourIdx >= 0 && onPath);
      });
      paintDock();
    }

    function tourHashUrl(step1based) {
      var base = location.pathname + location.search;
      return step1based ? base + "#atlas-tour-" + step1based : base;
    }
    function syncTourChrome() {
      var prev = wrap.querySelector("[data-tour-prev]");
      var next = wrap.querySelector("[data-tour-next]");
      if (prev) {
        prev.disabled = tourIdx <= 0;
        prev.setAttribute("aria-disabled", tourIdx <= 0 ? "true" : "false");
      }
      if (next) {
        var atEnd = tourIdx >= pathIds.length - 1;
        next.disabled = tourIdx < 0 || atEnd;
        next.setAttribute("aria-disabled", next.disabled ? "true" : "false");
      }
      gTour.classList.toggle("is-on", tourIdx >= 0);
      tourLinkEls.forEach(function (el, i) {
        var near = tourIdx >= 0 && (i === tourIdx - 1 || i === tourIdx);
        el.classList.toggle("is-here", near);
      });
    }
    function setTour(i) {
      if (!pathIds.length) return;
      i = Math.max(0, Math.min(pathIds.length - 1, i | 0));
      tourIdx = i;
      focus = byId[pathIds[i]] || null;
      if (tourBar) tourBar.hidden = false;
      if (tourRun) tourRun.hidden = false;
      var startBtn = wrap.querySelector("[data-tour-start]");
      if (startBtn) startBtn.hidden = true;
      if (tourStepEl) {
        if (focus) {
          var syn = focus.tagline ? " — " + focus.tagline : "";
          tourStepEl.textContent = (i + 1) + " / " + pathIds.length + ": " + focus.title + syn;
        } else {
          tourStepEl.textContent = (i + 1) + " / " + pathIds.length;
        }
      }
      syncTourChrome();
      paintFocus();
      try { history.replaceState(null, "", tourHashUrl(i + 1)); } catch (err) {}
    }

    function endTour() {
      tourIdx = -1;
      focus = null;
      if (tourRun) tourRun.hidden = true;
      var startBtn = wrap.querySelector("[data-tour-start]");
      if (startBtn) startBtn.hidden = false;
      syncTourChrome();
      paintFocus();
      try {
        if (/#atlas-tour/.test(location.hash)) history.replaceState(null, "", tourHashUrl(0));
      } catch (err) {}
    }

    /* Stale #atlas-tour-* after the reading path was cleared */
    if (!pathIds.length && /#atlas-tour/.test(location.hash)) {
      try { history.replaceState(null, "", tourHashUrl(0)); } catch (err) {}
    }

    if (tourBar && pathIds.length) {
      tourBar.hidden = false;
      var start = wrap.querySelector("[data-tour-start]");
      var prev = wrap.querySelector("[data-tour-prev]");
      var next = wrap.querySelector("[data-tour-next]");
      var open = wrap.querySelector("[data-tour-open]");
      var end = wrap.querySelector("[data-tour-end]");
      if (start) start.onclick = function () { setTour(0); };
      if (prev) prev.onclick = function () { if (tourIdx > 0) setTour(tourIdx - 1); };
      if (next) next.onclick = function () {
        if (tourIdx < 0) return;
        if (tourIdx < pathIds.length - 1) setTour(tourIdx + 1);
        else endTour();
      };
      if (open) open.onclick = function () { if (tourIdx >= 0) openNode(byId[pathIds[tourIdx]]); };
      if (end) end.onclick = endTour;
      var m = location.hash.match(/^#atlas-tour-(\d+)$/);
      if (m) {
        var step = Math.max(1, Math.min(pathIds.length, parseInt(m[1], 10))) - 1;
        setTour(step);
      } else {
        syncTourChrome();
      }
    }

    if (dockClear) dockClear.onclick = function () {
      if (tourIdx >= 0) return;
      focus = null;
      paintFocus();
    };
    if (dockOpen) dockOpen.addEventListener("click", function (e) {
      if (!focus || !focus.url) { e.preventDefault(); return; }
    });

    function nodeFromEvent(e) {
      var el = e.target;
      if (!el) return null;
      if (el.correspondingUseElement) el = el.correspondingUseElement;
      var g = el.closest ? el.closest(".atlas__node") : null;
      if (!g && el.parentNode && el.parentNode.classList && el.parentNode.classList.contains("atlas__node")) {
        g = el.parentNode;
      }
      if (!g || !gNodes.contains(g)) return null;
      var i = nodeEls.indexOf(g);
      return i < 0 ? null : nodes[i];
    }

    var nodeEls = nodes.map(function (n) {
      var g = document.createElementNS(svg.namespaceURI, "g");
      g.setAttribute("class", "atlas__node");
      g.setAttribute("data-sec", n.sec);
      g.setAttribute("data-url", n.url || "");
      g.setAttribute("tabindex", "0");
      g.setAttribute("role", "button");
      g.setAttribute("aria-label", n.title);
      var title = document.createElementNS(svg.namespaceURI, "title");
      title.textContent = n.title + (n.tagline ? " — " + n.tagline : "");
      g.appendChild(title);

      var hit = document.createElementNS(svg.namespaceURI, "circle");
      hit.setAttribute("r", 22);
      hit.setAttribute("fill", "transparent");
      hit.setAttribute("class", "atlas__hit");

      var ring = document.createElementNS(svg.namespaceURI, "circle");
      ring.setAttribute("r", n.sec === "characters" ? 11 : 9);
      ring.setAttribute("class", "atlas__ring");
      ring.setAttribute("fill", "none");

      var c = document.createElementNS(svg.namespaceURI, "circle");
      c.setAttribute("r", n.sec === "characters" ? 7 : 5.5);
      c.setAttribute("class", "atlas__dot");
      c.setAttribute("fill", secFill(n.sec));

      var t = document.createElementNS(svg.namespaceURI, "text");
      t.setAttribute("class", "atlas__label");
      t.setAttribute("dy", 22);
      t.setAttribute("text-anchor", "middle");
      var short = n.title.length > 28 ? n.title.slice(0, 26) + "…" : n.title;
      t.textContent = short;

      g.appendChild(hit);
      g.appendChild(ring);
      g.appendChild(c);
      g.appendChild(t);
      gNodes.appendChild(g);

      var clickTimer = null;
      function onActivate(ev) {
        if (dragMoved) return;
        var detail = ev.detail || 1;
        var now = Date.now();
        var isDbl = detail >= 2 || (lastTap.id === n.id && now - lastTap.t < 350);
        lastTap = { id: n.id, t: now };
        if (isDbl) {
          if (ev.preventDefault) ev.preventDefault();
          if (ev.stopPropagation) ev.stopPropagation();
          clearTimeout(clickTimer);
          openNode(n);
          return;
        }
        clearTimeout(clickTimer);
        clickTimer = setTimeout(function () {
          if (tourIdx >= 0) {
            var pi = pathIds.indexOf(n.id);
            if (pi >= 0) setTour(pi);
            else { focus = n; paintFocus(); }
          } else {
            focus = n;
            paintFocus();
          }
          if (ev.detail && document.activeElement === g) try { g.blur(); } catch (err) {}
        }, 220);
      }
      g.addEventListener("click", onActivate);
      g.addEventListener("dblclick", function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        clearTimeout(clickTimer);
        openNode(n);
      });
      g.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          clearTimeout(clickTimer);
          if (ev.shiftKey) openNode(n);
          else { focus = n; paintFocus(); }
        }
      });
      return g;
    });

    function clientToSvg(e) {
      var pt = svg.createSVGPoint();
      pt.x = e.clientX; pt.y = e.clientY;
      var ctm = svg.getScreenCTM();
      if (!ctm) return { x: 0, y: 0 };
      return pt.matrixTransform(ctm.inverse());
    }

    svg.addEventListener("pointerdown", function (e) {
      if (e.button !== 0) return;
      var n = nodeFromEvent(e);
      if (n) {
        drag = n;
        dragMoved = false;
        capturing = false;
        dragStart = { x: e.clientX, y: e.clientY };
        drag.fx = drag.x; drag.fy = drag.y;
        return;
      }
      /* pan empty canvas */
      pan = { x: e.clientX, y: e.clientY, ox: panX, oy: panY };
      dragMoved = false;
      try { svg.setPointerCapture(e.pointerId); } catch (err) {}
    });
    svg.addEventListener("pointermove", function (e) {
      if (drag) {
        if (dragStart && !dragMoved) {
          var dx = e.clientX - dragStart.x, dy = e.clientY - dragStart.y;
          if (dx * dx + dy * dy > DRAG_THRESHOLD * DRAG_THRESHOLD) {
            dragMoved = true;
            if (!capturing) {
              capturing = true;
              try { svg.setPointerCapture(e.pointerId); } catch (err) {}
            }
          }
        }
        if (!dragMoved) return;
        var p = clientToSvg(e);
        drag.fx = (p.x - panX) / scale;
        drag.fy = (p.y - panY) / scale;
        drag.x = drag.fx; drag.y = drag.fy;
        return;
      }
      if (pan) {
        panX = pan.ox + (e.clientX - pan.x);
        panY = pan.oy + (e.clientY - pan.y);
        if (Math.abs(e.clientX - pan.x) + Math.abs(e.clientY - pan.y) > DRAG_THRESHOLD) dragMoved = true;
        applyView();
      }
    });
    function endDrag(e) {
      if (drag) {
        /* snap dragged node toward column x */
        drag.tx = drag.x;
        drag.ty = drag.y;
        drag.fx = null; drag.fy = null;
        drag = null;
        dragStart = null;
        if (capturing) {
          try { svg.releasePointerCapture(e.pointerId); } catch (err) {}
        }
        capturing = false;
        setTimeout(function () { dragMoved = false; }, 0);
        return;
      }
      if (pan) {
        pan = null;
        try { svg.releasePointerCapture(e.pointerId); } catch (err) {}
        setTimeout(function () { dragMoved = false; }, 0);
      }
    }
    svg.addEventListener("pointerup", endDrag);
    svg.addEventListener("pointercancel", endDrag);

    svg.addEventListener("click", function (e) {
      if (nodeFromEvent(e)) return;
      if (dragMoved) return;
      if (tourIdx >= 0) return;
      focus = null;
      paintFocus();
    });

    function setZoom(next) {
      scale = Math.min(2.4, Math.max(0.5, next));
      applyView({ now: true });
    }
    root.addEventListener("wheel", function (e) {
      e.preventDefault();
      setZoom(scale * (e.deltaY > 0 ? 0.92 : 1.08));
    }, { passive: false });

    var zIn = wrap.querySelector("[data-atlas-zoom-in]");
    var zOut = wrap.querySelector("[data-atlas-zoom-out]");
    var zReset = wrap.querySelector("[data-atlas-reset]");
    if (zIn) zIn.onclick = function () { setZoom(scale * 1.15); };
    if (zOut) zOut.onclick = function () { setZoom(scale / 1.15); };
    if (zReset) zReset.onclick = function () {
      scale = 1; panX = 0; panY = 0;
      nodes.forEach(function (n) { n.fx = null; n.fy = null; });
      layoutTargets();
      applyView({ now: true, sim: 0.55 });
    };

    document.addEventListener("keydown", function (e) {
      if (tourIdx < 0 || !pathIds.length) return;
      var t = e.target;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      var rtl = getComputedStyle(document.documentElement).direction === "rtl";
      var goNext = e.key === "ArrowDown" || e.key === (rtl ? "ArrowLeft" : "ArrowRight");
      var goPrev = e.key === "ArrowUp" || e.key === (rtl ? "ArrowRight" : "ArrowLeft");
      if (goNext) {
        e.preventDefault();
        if (tourIdx < pathIds.length - 1) setTour(tourIdx + 1);
        else endTour();
      } else if (goPrev) {
        e.preventDefault();
        if (tourIdx > 0) setTour(tourIdx - 1);
        else endTour();
      } else if (e.key === "Escape") {
        e.preventDefault();
        endTour();
      }
    });

    function linkPath(a, b) {
      var mx = (a.x + b.x) / 2;
      var my = (a.y + b.y) / 2;
      var dx = b.x - a.x, dy = b.y - a.y;
      var bend = Math.min(36, Math.hypot(dx, dy) * 0.12);
      var cx = mx - dy * bend / (Math.hypot(dx, dy) || 1);
      var cy = my + dx * bend / (Math.hypot(dx, dy) || 1);
      return "M" + a.x + "," + a.y + " Q" + cx + "," + cy + " " + b.x + "," + b.y;
    }

    var alpha = 1;
    var simOn = false;
    var atlasVisible = true;
    function kickSim(boost) {
      alpha = Math.max(alpha, boost || 0.55);
      if (!simOn && atlasVisible) {
        simOn = true;
        requestAnimationFrame(tick);
      }
    }
    function tick() {
      if (!atlasVisible && !drag) { simOn = false; return; }
      alpha *= 0.94;
      var i, j, n, m, dx, dy, d2, d, f;
      /* soft pull toward column slots — keeps points aligned */
      for (i = 0; i < nodes.length; i++) {
        n = nodes[i];
        n.vx += (n.tx - n.x) * 0.06 * alpha;
        n.vy += (n.ty - n.y) * 0.06 * alpha;
      }
      /* within-column spacing */
      for (i = 0; i < nodes.length; i++) {
        n = nodes[i];
        for (j = i + 1; j < nodes.length; j++) {
          m = nodes[j];
          dx = n.x - m.x; dy = n.y - m.y;
          d2 = dx * dx + dy * dy || 0.01;
          d = Math.sqrt(d2);
          var same = n.sec === m.sec;
          var minD = same ? 52 : 40;
          if (d < minD) {
            f = ((minD - d) / d) * 0.35 * alpha;
            dx *= f; dy *= f;
            n.vx += dx; n.vy += dy; m.vx -= dx; m.vy -= dy;
          }
        }
      }
      /* mild link springs */
      for (i = 0; i < links.length; i++) {
        var l = links[i];
        dx = l.target.x - l.source.x; dy = l.target.y - l.source.y;
        d = Math.sqrt(dx * dx + dy * dy) || 0.01;
        f = (d - 160) * 0.008 * alpha;
        dx = (dx / d) * f; dy = (dy / d) * f;
        l.source.vx += dx; l.source.vy += dy;
        l.target.vx -= dx; l.target.vy -= dy;
      }
      for (i = 0; i < nodes.length; i++) {
        n = nodes[i];
        if (n.fx != null) { n.x = n.fx; n.y = n.fy; n.vx = 0; n.vy = 0; }
        else {
          n.vx *= 0.72; n.vy *= 0.72;
          n.x += n.vx; n.y += n.vy;
        }
      }
      for (i = 0; i < links.length; i++) {
        var L = links[i];
        linkEls[i].setAttribute("d", linkPath(L.source, L.target));
      }
      for (i = 0; i < tourLinkEls.length; i++) {
        var a = byId[pathIds[i]], b = byId[pathIds[i + 1]];
        if (a && b) tourLinkEls[i].setAttribute("d", linkPath(a, b));
      }
      for (i = 0; i < nodes.length; i++) {
        nodeEls[i].setAttribute("transform", "translate(" + nodes[i].x + "," + nodes[i].y + ")");
      }
      if (alpha < 0.018 && !drag) { simOn = false; return; }
      requestAnimationFrame(tick);
    }
    if ("IntersectionObserver" in window) {
      var simIo = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          atlasVisible = e.isIntersecting;
          if (atlasVisible) kickSim(0.35);
          else simOn = false;
        });
      }, { rootMargin: "40px", threshold: 0.02 });
      simIo.observe(wrap);
    }
    svg.addEventListener("pointerdown", function (e) {
      /* Wake sim for node drags only — panning the canvas needs no physics. */
      if (nodeFromEvent(e)) kickSim(0.5);
    }, true);
    applyView({ now: true });
    paintFocus();
    kickSim(1);
  }

  function boot() {
    roots.forEach(function (root) {
      if (root.dataset.atlasReady) return;
      var wrap = root.closest("[data-atlas]");
      if (!wrap) return;
      if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            if (!e.isIntersecting) return;
            io.disconnect();
            root.dataset.atlasReady = "1";
            init(root);
          });
        }, { rootMargin: "80px", threshold: 0.05 });
        io.observe(wrap);
      } else {
        root.dataset.atlasReady = "1";
        init(root);
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
