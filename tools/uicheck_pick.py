#!/usr/bin/env python3
"""Exercise the culture picker in the top bar (a custom listbox, not a <select>).

    python3 -m http.server 8123 --directory /tmp/opencode/out-root &
    UICHECK_URL=http://127.0.0.1:8123/ python3 tools/uicheck_pick.py

What it asserts, in the order the user meets it:

  * the trigger shows the culture in force, tinted with that culture's colour
  * opening reveals one general box (all cultures) above the five cultures
  * hovering an option lights it up in that culture's own main colour
  * the keyboard drives it (arrows move, Enter picks, Escape closes)
  * picking navigates to that culture, and the trigger follows the theme
  * in Farsi the panel opens toward the page centre, not off the edge

Screenshots land next to this run's output so the design can be eyeballed.
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uicheck import BASE, connect, nocache, start  # noqa: E402

SHOTS = os.environ.get("PICK_SHOTS", "/tmp/opencode")

THEMES = json.load(open(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "themes.json"), encoding="utf-8"))

fails = []


def check(ok, label, detail=""):
    print("   %s %s%s" % ("ok  " if ok else "FAIL", label, ("  " + str(detail)) if detail else ""))
    if not ok:
        fails.append(label)


def open_picker(p):
    b = p.box("#cpick-btn")
    p.tap(b["x"] + b["w"] / 2, b["y"] + b["h"] / 2)
    time.sleep(0.3)


def nav(p, url, wait=0.5):
    p.call("Page.navigate", url=BASE.rstrip("/") + url)
    for _ in range(60):
        time.sleep(0.1)
        if p.js("document.readyState") == "complete":
            break
    time.sleep(wait)


def rgb(css):
    """#rrggbb from whatever Chrome hands back: rgb(), rgba() or color(srgb r g b).
    The last form is what color-mix() computes to, and its channels are 0-1."""
    if not css or "(" not in css:
        return ""
    n = [float(x) for x in re.findall(r"-?\d*\.?\d+", css[css.index("(") + 1:])]
    if not n:
        return ""
    if max(n) <= 1.0:
        n = [x * 255 for x in n]
    return "#%02x%02x%02x" % tuple(int(round(x)) for x in n[:3])


def main():
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 1440
    t = start()
    p = connect(t["webSocketDebuggerUrl"])
    nocache(p)
    p.call("Emulation.setDeviceMetricsOverride", width=w, height=900,
           deviceScaleFactor=1, mobile=False)

    # ---- the trigger shows the culture in force -------------------------------
    print("trigger")
    nav(p, "/cultures/iranian/")
    cur = p.js("""(function(){var b=document.getElementById('cpick-btn'),
      c=document.getElementById('culture-pick');
      return {name:b.querySelector('.cpick__name').textContent,
              c:getComputedStyle(c).getPropertyValue('--c').trim(),
              accent:getComputedStyle(b).borderTopColor,
              label:b.getAttribute('aria-label'), expanded:b.getAttribute('aria-expanded')};})()""")
    check(cur["name"] == "Iranian", "trigger names the culture", cur["name"])
    check(cur["c"].lower() == THEMES["iranian"]["accent"].lower(),
          "trigger tinted with that culture's colour", "%s vs %s" % (cur["c"], THEMES["iranian"]["accent"]))
    iranian_border = cur["accent"]
    check(cur["label"], "trigger keeps an accessible name", cur["label"])
    check(cur["expanded"] == "false", "starts closed", cur["expanded"])
    p.shot(os.path.join(SHOTS, "pick-closed.png"),
           clip={"x": 0, "y": 0, "width": w, "height": 150, "scale": 1})

    # ---- opening --------------------------------------------------------------
    print("open")
    open_picker(p)
    st = p.js("""(function(){var l=document.getElementById('cpick-list');
      return {hidden:l.hidden, opts:l.querySelectorAll('.cpick__opt').length,
              first:l.querySelector('.cpick__opt').dataset.pick,
              firstC:getComputedStyle(l.querySelector('.cpick__opt')).getPropertyValue('--c').trim(),
              general:!!l.querySelector('.cpick__opt--all'),
              expanded:document.getElementById('cpick-btn').getAttribute('aria-expanded')};})()""")
    check(not st["hidden"], "list opens")
    check(st["expanded"] == "true", "aria-expanded follows")
    check(st["opts"] == 6, "one general box plus five cultures", st["opts"])
    check(st["first"] == "base", "the general box is listed first", st["first"])
    check(st["general"], "the general box is marked as such")
    check(st["firstC"].lower() == THEMES["base"]["accent"].lower(),
          "the general box is neutral, not a culture colour", st["firstC"])
    p.shot(os.path.join(SHOTS, "pick-open.png"),
           clip={"x": 0, "y": 0, "width": w, "height": 420, "scale": 1})

    # ---- each option lights up in its own colour on hover ---------------------
    print("hover")
    for key in ("mesopotamian", "norse", "greek", "indian"):
        box = p.box('.cpick__opt[data-pick="%s"]' % key)
        p.move(box["x"] + box["w"] / 2, box["y"] + box["h"] / 2)
        time.sleep(0.3)
        hov = p.js("""(function(){var o=document.querySelector('.cpick__opt[data-pick="%s"]'),
            s=getComputedStyle(o),g=getComputedStyle(o.querySelector('.cpick__sig'));
          return {bg:s.backgroundColor, bar:getComputedStyle(o,'::before').transform,
                  sig:getComputedStyle(o.querySelector('.cpick__sig'),'::after').backgroundColor,
                  chip:g.backgroundColor, dot:getComputedStyle(o.querySelector('.cpick__dot')).backgroundColor,
                  nameColor:getComputedStyle(o.querySelector('.cpick__name')).color};})()""" % key)
        want = THEMES[key]["accent"].lower()
        check(rgb(hov["dot"]) == want, "%s option shows its own colour dot" % key, hov["dot"])
        check(rgb(hov["sig"]) == want, "%s sigil motif is that colour" % key, hov["sig"])
        check(hov["chip"] not in ("rgba(0, 0, 0, 0)", "transparent"),
              "%s sigil chip is tinted, not a bare ring" % key, hov["chip"])
        check(hov["bg"] not in ("rgba(0, 0, 0, 0)", "transparent"),
              "%s row washes with that colour on hover" % key, hov["bg"])
        check(hov["nameColor"] != "rgb(201, 204, 211)",
              "%s label takes the colour on hover" % key, hov["nameColor"])
    p.shot(os.path.join(SHOTS, "pick-hover.png"),
           clip={"x": 0, "y": 0, "width": w, "height": 420, "scale": 1})

    # ---- keyboard -------------------------------------------------------------
    print("keyboard")
    p.js("document.getElementById('cpick-btn').focus()")
    p.js("(function(){var e=new KeyboardEvent('keydown',{key:'Escape',bubbles:true});"
         "document.getElementById('cpick-list').dispatchEvent(e);return 1})()")
    time.sleep(0.2)
    check(p.js("document.getElementById('cpick-list').hidden"), "Escape closes the list")
    p.js("(function(){var e=new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true});"
         "document.getElementById('cpick-btn').dispatchEvent(e);return 1})()")
    time.sleep(0.25)
    check(not p.js("document.getElementById('cpick-list').hidden"), "ArrowDown opens the list")
    check(p.js("document.activeElement.dataset.pick"), "focus lands on an option",
          p.js("document.activeElement.dataset.pick"))
    for _ in range(3):
        p.js("(function(){var e=new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true});"
             "document.getElementById('cpick-list').dispatchEvent(e);return 1})()")
        time.sleep(0.12)
    landed = p.js("document.activeElement.dataset.pick")
    check(landed not in ("", None), "arrows keep moving focus", landed)
    p.js("(function(){var e=new KeyboardEvent('keydown',{key:'Escape',bubbles:true});"
         "document.getElementById('cpick-list').dispatchEvent(e);return 1})()")
    time.sleep(0.2)
    check(p.js("document.activeElement.id") == "cpick-btn", "Escape returns focus to the trigger")

    # ---- picking navigates, and the trigger follows ---------------------------
    print("choose")
    nav(p, "/")
    open_picker(p)
    box = p.box('.cpick__opt[data-pick="norse"]')
    p.tap(box["x"] + box["w"] / 2, box["y"] + box["h"] / 2)
    time.sleep(1.2)
    check("/cultures/norse" in p.js("location.pathname"), "picking a culture goes to its page",
          p.js("location.pathname"))
    after = p.js("""(function(){var c=document.getElementById('culture-pick');
      return {name:document.querySelector('#cpick-btn .cpick__name').textContent,
              c:getComputedStyle(c).getPropertyValue('--c').trim(),
              border:getComputedStyle(document.getElementById('cpick-btn')).borderTopColor,
              theme:document.documentElement.dataset.culture};})()""")
    check(after["name"] == "Norse", "the trigger names the chosen culture", after["name"])
    check(after["c"].lower() == THEMES["norse"]["accent"].lower(),
          "the trigger takes the new culture's colour", after["c"])
    check(after["theme"] == "norse", "the page theme switched to that culture", after["theme"])
    check(after["border"] != iranian_border,
          "the trigger's frame really follows the culture", "%s -> %s"
          % (iranian_border, after["border"]))

    # ---- Farsi: the panel opens toward the centre ------------------------------
    print("farsi")
    nav(p, "/fa/cultures/iranian/")
    open_picker(p)
    geo = p.js("""(function(){var l=document.getElementById('cpick-list').getBoundingClientRect(),
        b=document.getElementById('cpick-btn').getBoundingClientRect();
      return {dir:document.documentElement.dir, lang:document.documentElement.lang,
              listX:Math.round(l.x), listRight:Math.round(l.right),
              btnX:Math.round(b.x), btnRight:Math.round(b.right),
              vw:document.documentElement.clientWidth,
              first:document.querySelector('.cpick__opt .cpick__name').textContent};})()""")
    check(geo["lang"] == "fa" and geo["dir"] == "rtl", "the Farsi page is rtl", geo)
    check(geo["listX"] >= 0 and geo["listRight"] <= geo["vw"],
          "the panel stays inside the viewport", geo)
    # it hangs off the trigger's inline-end edge, which is its left edge in RTL --
    # that is what makes it open toward the middle of the page rather than off it
    edge = geo["listX"] if geo["dir"] == "rtl" else geo["listRight"]
    want = geo["btnX"] if geo["dir"] == "rtl" else geo["btnRight"]
    check(abs(edge - want) < 2, "the panel hangs off the trigger's inline-end edge",
          "%s vs %s (dir=%s)" % (edge, want, geo["dir"]))
    p.shot(os.path.join(SHOTS, "pick-fa.png"),
           clip={"x": 0, "y": 0, "width": w, "height": 420, "scale": 1})

    print()
    if fails:
        print("%d FAILED: %s" % (len(fails), fails))
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
