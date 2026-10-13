#!/usr/bin/env python3
"""Measure grid, alignment and spacing across the built site.

    python3 -m http.server 8123 --directory /tmp/opencode/out-root &
    UICHECK_URL=http://127.0.0.1:8123/ python3 tools/uicheck_layout.py

Reports, per page: horizontal overflow, the content container's width and
centre, the reading column's left edge, heading rhythm, and the gap between
grid items. Anything that drifts between pages of the same kind is a standard
violation, so the totals are summarised at the end.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uicheck import connect, nocache, start, BASE  # noqa: E402

# every route we judge layout on, and which family it belongs to
ROUTES = [
    ("home", "/"),
    ("cultures", "/cultures/"),
    ("culture", "/cultures/iranian/"),
    ("section", "/cultures/iranian/characters/"),
    ("character", "/cultures/iranian/characters/mehr/"),
    ("story", "/cultures/iranian/stories/two-spirits/"),
    ("episodes", "/episodes/"),
    ("episode", "/episodes/001-first-giant/"),
    ("guide", "/guide/"),
    ("typography", "/guide/typography/"),
    ("library", "/library/"),
    ("about", "/about/"),
    ("fa-home", "/fa/"),
    ("fa-culture", "/fa/cultures/iranian/"),
    ("fa-character", "/fa/cultures/iranian/characters/mehr/"),
    ("fa-guide", "/fa/guide/"),
]

MEASURE = r"""
(function(){
  var de=document.documentElement;
  function b(s){var e=document.querySelector(s);if(!e)return null;var r=e.getBoundingClientRect();
    return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}}
  function cs(s,p){var e=document.querySelector(s);if(!e)return null;return getComputedStyle(e)[p]}
  var out={};
  out.overflowX = de.scrollWidth - de.clientWidth;
  out.dir = de.dir || (de.closest('[dir]')?de.closest('[dir]').dir:'ltr');
  ['.layout','.wrap','.hero','article','.hero-art','.cine','.cards','.panels','.motif']
    .forEach(function(s){var r=b(s); if(r) out[s]=r});
  out.h1 = cs('article h1','fontSize');
  out.h1mt = cs('article h1','marginTop');
  out.h2mt = cs('article h2','marginTop');
  out.h2mb = cs('article h2','marginBottom');
  out.pmb  = cs('article p','marginBottom');
  out.lh   = cs('article','lineHeight');
  out.gapLayout = cs('.layout','gap');
  out.gapCards  = cs('.cards','gap');
  out.padLayout = cs('.layout','padding');
  out.readFont  = cs('article','fontSize');
  // a prose line must never run past the reading column, even in a wide article
  out.prose = [].slice.call(document.querySelectorAll('article>p,article>ul,article>ol'))
    .slice(0,6).map(function(e){return Math.round(e.getBoundingClientRect().width)});
  // tokens that a stray brace elsewhere in the file can silently kill
  var R=getComputedStyle(document.documentElement);
  out.tokens={};
  ['--shell','--aside','--hero-h','--s3','--read'].forEach(function(k){
    out.tokens[k]=(R.getPropertyValue(k)||'').trim()});
  out.bodyBoxSizing=getComputedStyle(document.body).boxSizing;
  // first block's start edge inside the reading column, and every h2's start edge
  var a=document.querySelector('article');
  if(a){
    var kids=[].slice.call(a.children);
    out.edges = kids.slice(0,14).map(function(k){
      var r=k.getBoundingClientRect();
      return {t:(k.tagName+'.'+(k.className||'')).slice(0,26),
              x:Math.round(r.x), w:Math.round(r.width)};
    });
    out.h2x = [].slice.call(a.querySelectorAll('h2')).map(function(h){return Math.round(h.getBoundingClientRect().x)});
    out.maxRight = Math.max.apply(null, kids.map(function(k){
      return Math.round(k.getBoundingClientRect().right)}).filter(function(n){return n>0}));
  }
  return out;
})()
"""


def nav(p, url):
    p.call("Page.navigate", url=BASE.rstrip("/") + url)
    for _ in range(60):
        time.sleep(0.12)
        if p.js("document.readyState") == "complete":
            break
    time.sleep(0.35)


def main():
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 1440
    h = int(sys.argv[2]) if len(sys.argv) > 2 else 980
    t = start()
    p = connect(t["webSocketDebuggerUrl"])
    nocache(p)
    p.call("Emulation.setDeviceMetricsOverride", width=w, height=h,
           deviceScaleFactor=1, mobile=False)
    rows = []
    for name, url in ROUTES:
        nav(p, url)
        m = p.js(MEASURE)
        rows.append((name, m))
    for name, m in rows:
        lay = m.get(".layout") or {}
        art = m.get("article") or {}
        print("%-13s ov=%+d  layout w=%-5s x=%-4s  article w=%-5s x=%-4s  h1=%-7s h2mt=%-6s"
              % (name, m.get("overflowX", 0), lay.get("w"), lay.get("x"),
                 art.get("w"), art.get("x"), m.get("h1"), m.get("h2mt")))
    print()
    # containers that should agree with each other
    widths, tops, lefts = {}, {}, {}
    for name, m in rows:
        for key in (".layout", ".wrap", ".hero", ".cards", ".panels"):
            if key in m:
                widths.setdefault(key, set()).add(m[key]["w"])
                lefts.setdefault(key, set()).add(m[key]["x"])
        if "article" in m:
            tops.setdefault("article-x", set()).add(m["article"]["x"])
    print("container widths (should be a single value per selector):")
    for k, v in sorted(widths.items()):
        flag = "   <-- INCONSISTENT" if len(v) > 1 else ""
        print("   %-10s %s%s" % (k, sorted(v), flag))
    print("container left edges:")
    for k, v in sorted(lefts.items()):
        flag = "   <-- INCONSISTENT" if len(v) > 1 else ""
        print("   %-10s %s%s" % (k, sorted(v), flag))
    print()
    print("heading rhythm / paragraph spacing:")
    for name, m in rows:
        print("   %-13s h1=%-8s h1mt=%-6s h2mt=%-7s h2mb=%-5s pmb=%-5s lh=%s"
              % (name, m.get("h1"), m.get("h1mt"), m.get("h2mt"),
                 m.get("h2mb"), m.get("pmb"), m.get("lh")))
    print()
    print("tokens / invariants (a stray `}` earlier in the file can silently kill these):")
    bad = 0
    seen = set()
    for name, m in rows:
        t = m.get("tokens") or {}
        seen.add(tuple(sorted(t.items())))
        if not t.get("--shell") or not t.get("--hero-h") or not t.get("--s3"):
            print("   !! %s missing tokens: %s" % (name, t)); bad += 1
        if m.get("bodyBoxSizing") != "border-box":
            print("   !! %s body box-sizing = %s" % (name, m.get("bodyBoxSizing"))); bad += 1
    if len(seen) > 1:
        print("   !! token values differ between pages: %s" % (seen,)); bad += 1
    if not bad:
        print("   all tokens defined, box-sizing:border-box on every page")

    print()
    print("alignment (measured from the shell's reading-direction start edge,")
    print("          so a mirrored RTL page is judged on the same footing as LTR):")
    boxes = {}
    for key in (".layout", ".wrap"):
        for _, m in rows:
            if key in m:
                boxes.setdefault(key, set()).add((m[key]["x"], m[key]["w"], m.get("dir")))
    for key, v in sorted(boxes.items()):
        xs = {t[0] for t in v}
        ws = {t[1] for t in v}
        print("   %-8s x=%s w=%s dir=%s" % (key, sorted(xs), sorted(ws), sorted({t[2] for t in v})))
        if len(xs) > 1 or len(ws) > 1:
            print("   !! %s does not share one box" % key); bad += 1

    def rail(m):
        """distance from the shell's inline-start content edge to the article's
        inline-start edge -- 210px side rail + 40px gap when a nav is present"""
        b = m.get(".layout") or m.get(".wrap")
        a = m.get("article")
        if not b or not a:
            return None
        edge = b["x"] + 24                      # content box, gutter 24px
        if m.get("dir") == "rtl":
            edge = b["x"] + b["w"] - 24
            start = a["x"] + a["w"]             # RTL reads from the right
        else:
            start = a["x"]
        return (start - edge) if m.get("dir") != "rtl" else (edge - start)

    buckets = {"normal": [], "wide": []}
    for name, m in rows:
        a = m.get("article")
        if a:
            buckets["wide" if a["w"] > 900 else "normal"].append((name, a["w"], a["x"], m.get("dir"), rail(m)))
    print("   prose measure (<= the reading column):")
    worst = 0
    for name, m in rows:
        pw = m.get("prose") or []
        if pw:
            worst = max(worst, max(pw))
            print("        %-13s %s%s" % (name, pw,
                  "  <-- PROSE PAST THE COLUMN" if max(pw) > 772 else ""))
    if worst > 772:
        print("   !! widest prose line is %spx, past the %spx column" % (worst, 772)); bad += 1
    for label in ("normal", "wide"):
        items = buckets[label]
        if not items:
            continue
        offs = {t[4] for t in items}
        flag = "  <-- COLUMN START DRIFT" if len(offs) > 1 else "  ok"
        print("   %-7s widths=%-12s rail offsets=%s%s"
              % (label, sorted({t[1] for t in items}), sorted(offs), flag))
        for name, w, x, d, r in items:
            print("        %-13s w=%-5s x=%-5s dir=%-3s rail=%s" % (name, w, x, d, r))
        if len(offs) > 1:
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
