/* Culture atlas: lightweight 2D force graph (no external deps). */
(function () {
  var roots = document.querySelectorAll("[data-atlas-root]");
  if (!roots.length) return;

  var SEC_COLOR = {
    characters: null, /* filled from --accent */
    stories: "#93b9d1",
    history: "#c9a27a",
    episode: "#a88f56"
  };

  function accent() {
    return getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#e0a03a";
  }

  function init(root) {
    var wrap = root.closest("[data-atlas]");
    var raw = wrap && wrap.querySelector("[data-atlas-json]");
    if (!raw) return;
    var data;
    try { data = JSON.parse(raw.textContent); } catch (e) { return; }
    var nodes = (data.nodes || []).map(function (n, i) {
      var a = (i / Math.max(1, data.nodes.length)) * Math.PI * 2;
      return {
        id: n.id, title: n.title, sec: n.sec || "characters", url: n.url,
        x: Math.cos(a) * 165, y: Math.sin(a) * 165, vx: 0, vy: 0
      };
    });
    if (!nodes.length) return;
    var byId = {};
    nodes.forEach(function (n) { byId[n.id] = n; });
    var links = (data.edges || []).map(function (e) {
      return { source: byId[e.source], target: byId[e.target] };
    }).filter(function (l) { return l.source && l.target; });

    var W = root.clientWidth || 640;
    var H = Math.max(360, Math.min(520, Math.round(W * 0.55)));
    root.style.height = H + "px";
    /* Kill default text-select / drag / caret inside the atlas */
    ["selectstart", "dragstart"].forEach(function (type) {
      root.addEventListener(type, function (e) { e.preventDefault(); });
    });
    root.addEventListener("mousedown", function (e) {
      if (e.detail > 1) e.preventDefault(); /* no word-select on double-click */
    });

    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", (-W / 2) + " " + (-H / 2) + " " + W + " " + H);
    svg.setAttribute("class", "atlas__svg");
    svg.setAttribute("role", "presentation");
    svg.setAttribute("focusable", "false");
    root.appendChild(svg);

    var gWorld = document.createElementNS(svg.namespaceURI, "g");
    gWorld.setAttribute("class", "atlas__world");
    var gLinks = document.createElementNS(svg.namespaceURI, "g");
    gLinks.setAttribute("class", "atlas__links");
    var gNodes = document.createElementNS(svg.namespaceURI, "g");
    gNodes.setAttribute("class", "atlas__nodes");
    gWorld.appendChild(gLinks);
    gWorld.appendChild(gNodes);
    svg.appendChild(gWorld);

    var linkEls = links.map(function (l) {
      var line = document.createElementNS(svg.namespaceURI, "line");
      line.setAttribute("class", "atlas__link");
      gLinks.appendChild(line);
      return line;
    });

    var focus = null;
    var drag = null;
    var dragMoved = false;
    var dragStart = null;
    var capturing = false;
    var scale = 1;
    var DRAG_THRESHOLD = 5;
    var lastTap = { id: null, t: 0 };

    function openNode(n) {
      if (n && n.url) location.assign(n.url);
    }

    function paintFocus() {
      var neigh = {};
      if (focus) {
        neigh[focus.id] = 1;
        links.forEach(function (l) {
          if (l.source === focus) neigh[l.target.id] = 1;
          if (l.target === focus) neigh[l.source.id] = 1;
        });
      }
      nodeEls.forEach(function (g, i) {
        var on = !focus || neigh[nodes[i].id];
        g.classList.toggle("is-dim", !on);
        g.classList.toggle("is-focus", focus === nodes[i]);
      });
      linkEls.forEach(function (line, i) {
        var l = links[i];
        var on = !focus || l.source === focus || l.target === focus;
        line.classList.toggle("is-dim", !on);
        line.classList.toggle("is-hot", !!(focus && on));
      });
    }

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
      g.setAttribute("role", "link");
      g.setAttribute("aria-label", n.title);
      var title = document.createElementNS(svg.namespaceURI, "title");
      title.textContent = n.title + " — double-click to open";
      g.appendChild(title);
      /* Invisible hit pad so labels/near-misses still register */
      var hit = document.createElementNS(svg.namespaceURI, "circle");
      hit.setAttribute("r", 18);
      hit.setAttribute("fill", "transparent");
      hit.setAttribute("class", "atlas__hit");
      var c = document.createElementNS(svg.namespaceURI, "circle");
      c.setAttribute("r", n.sec === "characters" ? 7 : 5.5);
      var fill = n.sec === "characters" ? accent() : (SEC_COLOR[n.sec] || accent());
      c.setAttribute("fill", fill);
      var t = document.createElementNS(svg.namespaceURI, "text");
      t.setAttribute("dy", -12);
      t.setAttribute("text-anchor", "middle");
      t.textContent = n.title;
      g.appendChild(hit);
      g.appendChild(c);
      g.appendChild(t);
      gNodes.appendChild(g);

      /* detail===2 (and a manual fallback) opens; single click highlights after a short delay */
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
          focus = n;
          paintFocus();
          /* Drop browser focus box after pointer select; keyboard keeps :focus-visible */
          if (ev.detail && document.activeElement === g) try { g.blur(); } catch (err) {}
        }, 280);
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
          openNode(n);
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
      if (!n) return;
      drag = n;
      dragMoved = false;
      capturing = false;
      dragStart = { x: e.clientX, y: e.clientY };
      drag.fx = drag.x; drag.fy = drag.y;
    });
    svg.addEventListener("pointermove", function (e) {
      if (!drag) return;
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
      drag.fx = p.x / scale; drag.fy = p.y / scale;
      drag.x = drag.fx; drag.y = drag.fy;
    });
    function endDrag(e) {
      if (!drag) return;
      drag.fx = null; drag.fy = null;
      drag = null;
      dragStart = null;
      if (capturing) {
        try { svg.releasePointerCapture(e.pointerId); } catch (err) {}
      }
      capturing = false;
      /* keep dragMoved true until after the click that follows pointerup */
      setTimeout(function () { dragMoved = false; }, 0);
    }
    svg.addEventListener("pointerup", endDrag);
    svg.addEventListener("pointercancel", endDrag);

    /* Click empty parchment to clear focus */
    svg.addEventListener("click", function (e) {
      if (nodeFromEvent(e)) return;
      if (dragMoved) return;
      focus = null;
      paintFocus();
    });

    root.addEventListener("wheel", function (e) {
      e.preventDefault();
      scale = Math.min(2.4, Math.max(0.45, scale * (e.deltaY > 0 ? 0.92 : 1.08)));
      gWorld.setAttribute("transform", "scale(" + scale + ")");
    }, { passive: false });

    var alpha = 1;
    function tick() {
      alpha *= 0.96;
      if (alpha < 0.02 && !drag) { alpha = 0.02; }
      var i, j, n, m, dx, dy, d2, d, f;
      for (i = 0; i < nodes.length; i++) {
        n = nodes[i];
        for (j = i + 1; j < nodes.length; j++) {
          m = nodes[j];
          dx = n.x - m.x; dy = n.y - m.y;
          d2 = dx * dx + dy * dy || 0.01;
          d = Math.sqrt(d2);
          f = (1500 / d2) * alpha;
          dx = (dx / d) * f; dy = (dy / d) * f;
          n.vx += dx; n.vy += dy; m.vx -= dx; m.vy -= dy;
        }
      }
      for (i = 0; i < links.length; i++) {
        var l = links[i];
        dx = l.target.x - l.source.x; dy = l.target.y - l.source.y;
        d = Math.sqrt(dx * dx + dy * dy) || 0.01;
        f = (d - 135) * 0.035 * alpha;
        dx = (dx / d) * f; dy = (dy / d) * f;
        l.source.vx += dx; l.source.vy += dy;
        l.target.vx -= dx; l.target.vy -= dy;
      }
      for (i = 0; i < nodes.length; i++) {
        n = nodes[i];
        n.vx += (-n.x) * 0.007 * alpha;
        n.vy += (-n.y) * 0.007 * alpha;
        if (n.fx != null) { n.x = n.fx; n.y = n.fy; n.vx = 0; n.vy = 0; }
        else {
          n.vx *= 0.85; n.vy *= 0.85;
          n.x += n.vx; n.y += n.vy;
        }
      }
      for (i = 0; i < links.length; i++) {
        var L = links[i], el = linkEls[i];
        el.setAttribute("x1", L.source.x); el.setAttribute("y1", L.source.y);
        el.setAttribute("x2", L.target.x); el.setAttribute("y2", L.target.y);
      }
      for (i = 0; i < nodes.length; i++) {
        nodeEls[i].setAttribute("transform", "translate(" + nodes[i].x + "," + nodes[i].y + ")");
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  roots.forEach(init);
})();
