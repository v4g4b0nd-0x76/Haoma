"""Scenario: drives the myth map studio in a headless browser and prints the generated shortcode."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uicheck import BASE, connect, nocache, start  # noqa: E402

OUT = "/tmp/opencode/"


def main():
    pg = connect(start()["webSocketDebuggerUrl"])
    pg.call("Page.enable")
    pg.call("Runtime.enable")
    pg.call("Emulation.setDeviceMetricsOverride", width=1440, height=980,
            deviceScaleFactor=1, mobile=False)
    pg.call("Page.navigate", url=BASE)
    time.sleep(3)
    print("loaded:", pg.js("document.title"))

    print("openFile:", pg.js("typeof openFile, typeof bMap, typeof cur"))
    pg.js("openFile('content/en/cultures/iranian/_index.md')")
    time.sleep(1.5)
    print("cursor at a map? textarea len:", pg.js("document.querySelector('#ta').value.length"))

    # place the caret inside the existing map block, then open the studio
    pg.js("(function(){var t=document.querySelector('#ta');var v=t.value;"
          "var i=v.indexOf('{{< map');t.focus();t.setSelectionRange(i+10,i+10)})()")
    time.sleep(0.3)
    pg.js("document.querySelector('#iM').click()")
    time.sleep(1.2)
    print("modal:", pg.js("!!document.querySelector('.mdl.wide')"),
          "title:", pg.js("(document.querySelector('.mh b')||{}).textContent"))
    print("chooser:", pg.js("(function(){var s=document.querySelector('#mp_which');"
                            "return s?[...s.options].map(o=>o.textContent):null})()"))
    print("art buttons:", pg.js("document.querySelectorAll('#mp_arts button').length"),
          "labels:", pg.js("[...document.querySelectorAll('#mp_arts button b')].map(b=>b.textContent)"))
    print("accent:", pg.js("getComputedStyle(document.querySelector('.mdl')).getPropertyValue('--a').trim()"))
    print("pins listed:", pg.js("document.querySelectorAll('#ms_p1 .mrow').length"),
          "regions:", pg.js("document.querySelectorAll('#ms_p2 .mrow').length"))
    print("canvas box:", pg.js("(function(){var c=document.querySelector('.ms-canvas');"
                               "if(!c)return null;var r=c.getBoundingClientRect();"
                               "return [Math.round(r.width),Math.round(r.height),"
                               "Math.round(r.width/r.height*1000)/1000, Math.round(1200/654*1000)/1000]})()"))
    print("pin labels shown:", pg.js("document.querySelectorAll('.ms-pins .mpin .l').length"))
    pg.shot(OUT + "ms-open.png")

    # --- click on the map to drop a pin ---
    b = pg.box(".ms-canvas")
    pg.tap(b["x"] + b["w"] * 0.31, b["y"] + b["h"] * 0.72)
    time.sleep(0.5)
    print("pins after click:", pg.js("document.querySelectorAll('.ms-pins .mpin').length"),
          "rows:", pg.js("document.querySelectorAll('#ms_p1 .mrow').length"),
          "form open:", pg.js("!!document.querySelector('#ms_p1 .mform')"),
          "readout:", pg.js("(document.querySelector('#mp_pos')||{}).textContent"))
    pg.shot(OUT + "ms-pin.png")

    # --- drag it ---
    x, y = b["x"] + b["w"] * 0.31, b["y"] + b["h"] * 0.72
    pg.move(x, y)
    for k in ("mousePressed",):
        pg.call("Input.dispatchMouseEvent", type=k, x=x, y=y, button="left", clickCount=1)
    for i in range(8):
        pg.move(x + 12 * (i + 1), y - 6 * (i + 1))
        time.sleep(0.02)
    pg.call("Input.dispatchMouseEvent", type="mouseReleased", x=x + 96, y=y - 48,
            button="left", clickCount=1)
    time.sleep(0.4)
    print("readout after drag:", pg.js("(document.querySelector('#mp_pos')||{}).textContent"))

    # label the new pin
    pg.js("(function(){var i=document.querySelector('#ms_p1 .mform [data-f=label]');"
          "i.value='Test place';i.dispatchEvent(new Event('input',{bubbles:true}))})()")
    time.sleep(0.3)
    print("row label:", pg.js("(document.querySelector('#ms_p1 .mrow.on>b')||{}).textContent"),
          "| pin label:", pg.js("(document.querySelector('.mpin.on .l')||{}).textContent"))
    pg.shot(OUT + "ms-pindrag.png")

    # --- region workflow ---
    pg.js("document.querySelector('[data-mo=region]').click()")
    time.sleep(0.4)
    print("region mode: drawbar=", pg.js("document.querySelector('#mp_draw').style.display"),
          "newBtn=", pg.js("document.querySelector('#mp_new').style.display"),
          "undo=", pg.js("document.querySelector('#mp_undo').style.display"))
    print("hint:", pg.js("document.querySelector('#mp_hint').textContent"))
    # click a shaded area -> selects that region (no border started yet)
    pg.tap(b["x"] + b["w"] * 0.45, b["y"] + b["h"] * 0.60)
    time.sleep(0.4)
    print("select via map:", pg.js("document.querySelectorAll('.mvert').length"), "verts | form label:",
          pg.js("(document.querySelector('#ms_p2 .mform [data-f=label]')||{}).value"))
    # start a border explicitly, then add corners inside an existing region
    pg.js("document.querySelector('#mp_new').click()")
    time.sleep(0.3)
    for fx, fy in ((0.62, 0.22), (0.78, 0.30), (0.80, 0.48), (0.64, 0.52)):
        pg.tap(b["x"] + b["w"] * fx, b["y"] + b["h"] * fy)
        time.sleep(0.15)
    print("draft:", pg.js("document.querySelector('#mp_dcount').textContent"),
          "verts:", pg.js("document.querySelectorAll('.mvert').length"),
          "close enabled:", pg.js("!document.querySelector('#mp_fin').disabled"))
    pg.shot(OUT + "ms-region.png")
    pg.js("document.querySelector('#mp_fin').click()")
    time.sleep(0.5)
    print("regions now:", pg.js("document.querySelectorAll('#ms_p2 .mrow').length"),
          "polygons:", pg.js("document.querySelectorAll('.mpoly').length"))
    pg.shot(OUT + "ms-region2.png")

    # --- settings: pulse + route + fa artwork ---
    pg.js("var s=document.querySelector('#mp_ro');s.value='auto';s.dispatchEvent(new Event('change',{bubbles:true}))")
    pg.js("var s=document.querySelector('#mp_pu');s.value='0';s.dispatchEvent(new Event('change',{bubbles:true}))")
    time.sleep(0.4)
    print("route polyline:", pg.js("document.querySelectorAll('.mroute').length"))

    pg.shot(OUT + "ms-final.png")

    # --- OK ---
    pg.js("document.querySelector('.mdl .ok').click()")
    time.sleep(0.8)
    print("modal closed:", pg.js("!document.querySelector('.mdl')"))
    txt = pg.js("(function(){var t=document.querySelector('#ta');var v=t.value;"
                "var i=v.indexOf('{{< map');return v.slice(i, i+2600)})()")
    print("---- generated ----")
    print(txt)

    # round-trip: reopen the same map and confirm it parses back
    pg.js("(function(){var t=document.querySelector('#ta');var i=t.value.indexOf('{{< map');"
          "t.focus();t.setSelectionRange(i+10,i+10)})()")
    pg.js("document.querySelector('#iM').click()")
    time.sleep(1.0)
    print("reopen pins:", pg.js("document.querySelectorAll('#ms_p1 .mrow').length"),
          "regions:", pg.js("document.querySelectorAll('#ms_p2 .mrow').length"),
          "art:", pg.js("(document.querySelector('#mp_arts button.on b')||{}).textContent"))
    pg.shot(OUT + "ms-reopen.png")
    pg.js("document.querySelector('.mdl .cn').click()")

    # --- new map path (no caret in a map) ---
    pg.js("(function(){var t=document.querySelector('#ta');t.focus();t.setSelectionRange(0,0)})()")
    pg.js("document.querySelector('#iM').click()")
    time.sleep(1.0)
    print("new-map modal:", pg.js("(document.querySelector('.mh b')||{}).textContent"),
          "| ok label:", pg.js("(document.querySelector('.mdl .ok')||{}).textContent"),
          "| chooser:", pg.js("!!document.querySelector('#mp_which')"))
    pg.shot(OUT + "ms-new.png")
    pg.js("document.querySelector('.mdl .cn').click()")

    # --- escape cancels an in-progress border ---
    pg.js("(function(){var t=document.querySelector('#ta');var i=t.value.indexOf('{{< map');"
          "t.focus();t.setSelectionRange(i+10,i+10)})()")
    pg.js("document.querySelector('#iM').click()")
    time.sleep(0.9)
    pg.js("document.querySelector('[data-mo=region]').click()")
    pg.js("document.querySelector('#mp_new').click()")
    time.sleep(0.3)
    bb = pg.box(".ms-canvas")
    pg.tap(bb["x"] + bb["w"] * 0.5, bb["y"] + bb["h"] * 0.5)
    time.sleep(0.3)
    print("draft before esc:", pg.js("document.querySelector('#mp_dcount').textContent"))
    pg.call("Input.dispatchKeyEvent", type="keyDown", key="Escape", code="Escape", windowsVirtualKeyCode=27)
    pg.call("Input.dispatchKeyEvent", type="keyUp", key="Escape", code="Escape", windowsVirtualKeyCode=27)
    time.sleep(0.4)
    print("draft after esc:", repr(pg.js("document.querySelector('#mp_dcount').textContent")),
          "modal still open:", pg.js("!!document.querySelector('.mdl')"))
    # switch to a different map via the chooser, then to the FA artwork
    pg.js("(function(){var s=document.querySelector('#mp_which');s.value='-1';"
          "s.dispatchEvent(new Event('change',{bubbles:true}))})()")
    time.sleep(0.4)
    print("after New map: pins", pg.js("document.querySelectorAll('#ms_p1 .mrow').length"),
          "art on:", pg.js("(document.querySelector('#mp_arts .on b')||{}).textContent"),
          "id field:", repr(pg.js("document.querySelector('#mp_id').value")))
    pg.js("var s=document.querySelector('#mp_lang');s.value='fa';s.dispatchEvent(new Event('change',{bubbles:true}))")
    time.sleep(0.8)
    print("fa mode: lang", pg.js("document.querySelector('#mp_lang').value"),
          "art on:", pg.js("(document.querySelector('#mp_arts .on b')||{}).textContent"))
    pg.shot(OUT + "ms-fa.png")
    pg.js("document.querySelector('.mdl .cn').click()")

    # --- FA page opens the studio in Farsi-label mode ---
    pg.js("openFile('content/fa/cultures/iranian/_index.md')")
    time.sleep(1.5)
    pg.js("(function(){var t=document.querySelector('#ta');var i=t.value.indexOf('{{< map');"
          "t.focus();t.setSelectionRange(i+10,i+10)})()")
    pg.js("document.querySelector('#iM').click()")
    time.sleep(1.2)
    print("FA page: lang", pg.js("document.querySelector('#mp_lang').value"),
          "art on:", pg.js("(document.querySelector('#mp_arts .on b')||{}).textContent"),
          "src:", pg.js("(function(){var b=document.querySelector('#mp_arts .on');return b&&b.dataset.s})()"))
    print("FA pins/regions:", pg.js("document.querySelectorAll('#ms_p1 .mrow').length"),
          pg.js("document.querySelectorAll('#ms_p2 .mrow').length"))
    pg.shot(OUT + "ms-fapage.png")
    pg.js("document.querySelector('.mdl .cn').click()")

    # --- other builders still work after the modal() signature change ---
    pg.js("document.querySelector('#iF').click()")
    time.sleep(0.6)
    print("figure modal:", pg.js("(document.querySelector('.mh b')||{}).textContent"),
          "| ok:", pg.js("(document.querySelector('.mdl .ok')||{}).textContent"),
          "| wide:", pg.js("!!document.querySelector('.mdl.wide')"))
    pg.js("document.querySelector('.mdl .cn').click()")
    time.sleep(0.3)

    # --- cleanup: drop the in-memory/persisted draft this test created ---
    pg.js("discardPaths(['content/en/cultures/iranian/_index.md','content/fa/cultures/iranian/_index.md'])")
    time.sleep(1.5)
    print("drafts left:", pg.js("drafts.size"))


if __name__ == "__main__":
    main()
