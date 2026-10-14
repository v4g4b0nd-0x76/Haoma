#!/usr/bin/env python3
"""Exercise the PDF export: one control per page, and a print sheet that keeps
the theme.

    python3 -m http.server 8123 --directory /tmp/opencode/out-root &
    UICHECK_URL=http://127.0.0.1:8123/ python3 tools/uicheck_pdf.py

Two things are checked, and neither needs a PDF file:

1. The control.  Every page that carries content has exactly one
   [data-act="pdf"], it has an accessible name, and pressing it calls
   window.print() exactly once.

2. The sheet.  The print stylesheet is inspected under
   Emulation.setEmulatedMedia(media="print"), which applies @media print
   without going anywhere near a printer.  The sheet must keep the page's own
   --bg and --text (the whole point of the export), hide the interactive
   chrome, and *unhide* what a tab strip or a scroll rail would otherwise keep
   off the paper.

Visibility is judged by getClientRects(), not by the element's own display: a
child of a display:none header still reports its own display, so it would look
"shown" while printing nothing at all.

A white body background under print media is the regression that matters: it
means the export would print a dark site onto white paper.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uicheck import connect, nocache, start, BASE  # noqa: E402

# route, human name -- one per page family that can be exported
ROUTES = [
    ("/", "home"),
    ("/fa/", "fa-home"),
    ("/guide/", "guide"),
    ("/fa/guide/", "fa-guide"),
    ("/cultures/iranian/characters/mehr/", "character"),
    ("/cultures/mesopotamian/stories/journey-to-the-cedar-forest/", "story"),
    ("/fa/cultures/iranian/characters/mehr/", "fa-character"),
    ("/library/", "library"),
]

# dropped from the sheet, and kept on it.  The breadcrumbs stay on purpose: a
# loose sheet needs to say where it came from.
GONE = [".top", "nav", "footer", ".tools", "aside.side", ".bg", ".motif"]
KEPT = [".crumbs"]

fails = []


def check(ok, label, detail=""):
    print("   %s %s%s" % ("ok  " if ok else "FAIL", label, ("  " + str(detail)) if detail else ""))
    if not ok:
        fails.append(label)


def rgb(css):
    """rgb()/rgba() -> 'r,g,b'; anything unusable -> ''."""
    if not css or "(" not in css or ")" not in css:
        return ""
    n = css[css.index("(") + 1:css.index(")")].split(",")
    try:
        return ",".join(str(int(round(float(x)))) for x in n[:3])
    except ValueError:
        return ""


def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) != 6:
        return ""
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def nav(p, url):
    p.call("Page.navigate", url=BASE.rstrip("/") + url)
    for _ in range(80):
        time.sleep(0.1)
        if p.js("document.readyState") == "complete":
            break
    time.sleep(0.4)


SCREEN = r"""
(function(){
  var b=document.querySelector('[data-act="pdf"]');
  var out={count:document.querySelectorAll('[data-act="pdf"]').length};
  if(!b) return out;
  out.name=(b.getAttribute('aria-label')||b.textContent||'').trim();
  out.title=(b.getAttribute('title')||'').trim();
  out.hidden=b.hidden;
  var r=b.getBoundingClientRect();
  out.visible=r.width>0&&r.height>0;
  out.named=b.tagName+' '+b.className;
  return out;
})()
"""

# Press the control with window.print stubbed, so the call can be counted.  The
# call is asynchronous: the button first waits for haomaPrintPrep() to decode
# lazy images and GIF stills, so the count is polled rather than read at once.
PRESS = r"""
(function(){
  window.__pn=0; window.__realPrint=window.print;
  window.print=function(){window.__pn++};
  document.querySelector('[data-act="pdf"]').click();
  return 1;
})()
"""
PRESS_DONE = "(function(){var n=window.__pn;if(n)window.print=window.__realPrint;return n})()"

# What the sheet carries once the PDF button's preparation has run: every
# image decoded (a lazy slide never loads by itself before the snapshot), and
# each GIF printed as its decoded first-frame still instead of the live file.
MEDIA = r"""
(function(){
  var o={imgs:0,blank:[],gifs:0,stills:0,gifHidden:0,slides:0,flatSlides:0};
  var root=document.querySelector('article')||document.querySelector('main')||document.body;
  [].slice.call(root.querySelectorAll('img')).forEach(function(m){
    if(!m.getClientRects().length)return;o.imgs++;
    var r=m.getBoundingClientRect();
    if(!m.complete||!m.naturalWidth||r.height<4)o.blank.push((m.getAttribute('src')||'').slice(0,40))});
  [].slice.call(document.querySelectorAll('img[data-gif]')).forEach(function(m){o.gifs++;
    var s=m.nextElementSibling;
    if(s&&s.classList.contains('gif-still')&&/^data:image\/png/.test(s.src)&&s.getBoundingClientRect().height>20)o.stills++;
    if(getComputedStyle(m).display==='none')o.gifHidden++});
  [].slice.call(document.querySelectorAll('.sm-slide')).forEach(function(e){o.slides++;
    if(e.getBoundingClientRect().height>20)o.flatSlides++});
  return o;
})()
"""

SHEET = r"""
(function(){
  var de=document.documentElement, body=document.body;
  var out={media:matchMedia('print').matches};
  function vis(sel){var e=document.querySelector(sel);
    return e ? (e.getClientRects().length ? 'shown' : 'hidden') : null}
  function disp(sel){var e=document.querySelector(sel);return e?getComputedStyle(e).display:null}
  // a list page has no <article>; the whole of <main> is the content there
  var root=document.querySelector('article')||document.querySelector('main');
  out.contentDisplay=root?getComputedStyle(root).display:null;
  out.contentColor=root?getComputedStyle(root).color:null;
  out.rootBg=getComputedStyle(de).getPropertyValue('--bg').trim();
  out.rootText=getComputedStyle(de).getPropertyValue('--text').trim();
  var bs=getComputedStyle(body);
  out.bodyBg=bs.backgroundColor;
  out.bodyColorAdjust=bs.webkitPrintColorAdjust||bs.printColorAdjust;
  out.bodyPadding=bs.padding;
  var hero=document.querySelector('.hero-art');
  out.heroAspect=hero?getComputedStyle(hero).aspectRatio:null;
  var cine=document.querySelector('.cine');
  out.cineH=cine?cine.getBoundingClientRect().height:null;
  out.panelsShown=[].slice.call(document.querySelectorAll('.tabpanel[hidden]'))
    .map(function(e){return getComputedStyle(e).display});
  out.tabsDisplay=disp('.tabs');
  out.railOverflow=(function(){var e=document.querySelector('.cards.rail');
    return e?getComputedStyle(e).overflowX:null})();
  out.gone={}; GONE.forEach(function(s){out.gone[s]=vis(s)});
  out.kept={}; KEPT.forEach(function(s){out.kept[s]=vis(s)});
  out.actShown=[].slice.call(document.querySelectorAll('[data-act]')).filter(function(e){
    return e.getClientRects().length}).length;
  out.pageMargins=[];
  [].slice.call(document.styleSheets).forEach(function(ss){
    var rules; try{rules=ss.cssRules}catch(e){return}
    if(!rules) return;
    [].slice.call(rules).forEach(function(r){
      if(r.constructor&&/CSSPageRule/.test(r.constructor.name)&&r.style)
        out.pageMargins.push(r.style.margin||r.style.marginTop||'');
    });
  });
  out.overflowX=de.scrollWidth-de.clientWidth;
  // myth map: must print at identity fit (no mid-pan zoom); notes readable
  var map=document.querySelector('.myth-map');
  if(map){
    var inner=map.querySelector('.myth-map__inner');
    var notes=map.closest('figure')?map.closest('figure').querySelector('.myth-map__print-notes'):null;
    out.map={
      present:true,
      transform:inner?getComputedStyle(inner).transform:'',
      notesDisplay:notes?getComputedStyle(notes).display:null,
      notesShown:notes?!!notes.getClientRects().length:null,
      popsHidden:[].slice.call(map.querySelectorAll('.myth-pin__pop,.myth-region__pop'))
        .every(function(e){return getComputedStyle(e).display==='none'})
    };
  } else { out.map={present:false}; }
  out.gifCount=document.querySelectorAll('[data-gif]').length;
  return out;
})()
""".replace("GONE", repr(GONE)).replace("KEPT", repr(KEPT))


def main():
    t = start()
    p = connect(t["webSocketDebuggerUrl"])
    nocache(p)
    p.call("Emulation.setDeviceMetricsOverride", width=1440, height=980,
           deviceScaleFactor=1, mobile=False)
    p.call("Emulation.setEmulatedMedia", media="screen")

    print("control")
    for url, name in ROUTES:
        nav(p, url)
        s = p.js(SCREEN)
        check(s["count"] == 1, "%s: exactly one export control" % name, s["count"])
        check(bool(s.get("name")), "%s: the control has an accessible name" % name, s.get("name"))
        check(bool(s.get("title")), "%s: the control explains itself" % name, s.get("title"))
        check(s.get("visible") and not s.get("hidden"),
              "%s: the control is visible on screen" % name, s.get("named"))
        p.js(PRESS)
        n = 0
        for _ in range(80):
            n = p.js(PRESS_DONE)
            if n:
                break
            time.sleep(0.1)
        time.sleep(0.3)
        n = p.js("window.__pn")
        check(n == 1, "%s: pressing it calls window.print() once" % name, n)

    print("sheet (print media)")
    for url, name in ROUTES:
        nav(p, url)
        p.call("Emulation.setEmulatedMedia", media="print")
        time.sleep(0.3)
        m = p.js(SHEET)
        p.call("Emulation.setEmulatedMedia", media="screen")

        check(m["media"], "%s: print media applies" % name)
        # the export must not turn into a white page
        check(m["bodyBg"] not in ("rgba(0, 0, 0, 0)", "rgb(255, 255, 255)", ""),
              "%s: body keeps a themed backdrop" % name, "%s (--bg %s)" % (m["bodyBg"], m["rootBg"]))
        check(rgb(m["bodyBg"]) == hex2rgb(m["rootBg"]),
              "%s: the backdrop is the page's own --bg" % name,
              "%s vs %s" % (rgb(m["bodyBg"]), m["rootBg"]))
        check(rgb(m["contentColor"]) == hex2rgb(m["rootText"]),
              "%s: text keeps the page's own colour" % name,
              "%s vs %s" % (m["contentColor"], m["rootText"]))
        check(m["bodyColorAdjust"] == "exact",
              "%s: backgrounds are forced to print" % name, m["bodyColorAdjust"])
        check(any(v.replace(" ", "").startswith("0") for v in (m["pageMargins"] or [])),
              "%s: @page margin is zeroed for full bleed" % name, m["pageMargins"])
        check(m["bodyPadding"] not in (None, "0px"),
              "%s: the inset comes from the body padding" % name, m["bodyPadding"])
        check(m["contentDisplay"] not in ("none", None),
              "%s: the content still prints" % name, m["contentDisplay"])
        check(m["overflowX"] <= 0, "%s: no horizontal overflow on paper" % name, m["overflowX"])

        for s in GONE:
            check(m["gone"].get(s) in ("hidden", None),
                  "%s: %s is off the sheet" % (name, s), m["gone"].get(s))
        for s in KEPT:
            check(m["kept"].get(s) in ("shown", None),
                  "%s: %s is kept for context" % (name, s), m["kept"].get(s))
        check(m["actShown"] == 0, "%s: no page control is printed" % name, m["actShown"])

        # nothing a tab strip or a scroll rail would otherwise hide
        check(all(v != "none" for v in m["panelsShown"]),
              "%s: hidden tab panels are flattened" % name, m["panelsShown"])
        if m["tabsDisplay"]:
            check(m["tabsDisplay"] == "flex", "%s: tab labels become plain text" % name, m["tabsDisplay"])
        if m["railOverflow"]:
            check(m["railOverflow"] == "visible",
                  "%s: scroll rails unclip every card" % name, m["railOverflow"])
        if m["heroAspect"]:
            check(m["heroAspect"].replace(" ", "") == "4/1",
                  "%s: the banner keeps its 4:1 scene" % name, m["heroAspect"])
        if m["cineH"]:
            check(m["cineH"] < 470, "%s: the hero cover is page-sized, not half a page" % name,
                  round(m["cineH"]))

        # map + GIF print behaviour (only asserted when the page carries them)
        mp = m.get("map") or {}
        if mp.get("present"):
            tr = (mp.get("transform") or "").replace(" ", "")
            check(tr in ("none", "matrix(1,0,0,1,0,0)", ""),
                  "%s: myth map prints unzoomed (identity transform)" % name, mp.get("transform"))
            if mp.get("notesDisplay") is not None:
                check(mp.get("notesDisplay") != "none" and mp.get("notesShown"),
                      "%s: pin/region print notes are visible" % name,
                      "%s shown=%s" % (mp.get("notesDisplay"), mp.get("notesShown")))
            check(mp.get("popsHidden"),
                  "%s: on-map hover pops stay off the sheet (notes list is canonical)" % name,
                  mp.get("popsHidden"))
        # run the PDF button's preparation, then look at the sheet again
        p.js("window.__prep=0;window.haomaPrintPrep().then(function(){window.__prep=1})")
        for _ in range(80):
            if p.js("window.__prep"):
                break
            time.sleep(0.1)
        p.call("Emulation.setEmulatedMedia", media="print")
        time.sleep(0.3)
        md = p.js(MEDIA)
        p.call("Emulation.setEmulatedMedia", media="screen")
        check(not md["blank"], "%s: every printed image is loaded and has height" % name, md["blank"])
        if md["gifs"]:
            check(md["stills"] == md["gifs"] and md["gifHidden"] == md["gifs"],
                  "%s: each GIF prints its decoded first frame" % name, md)
        if md["slides"]:
            check(md["flatSlides"] == md["slides"], "%s: every slide prints with its image" % name, md)

    print()
    if fails:
        print("%d FAILED:" % len(fails))
        for f in fails:
            print("   -", f)
        return 1
    print("all checks passed (%d routes)" % len(ROUTES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
