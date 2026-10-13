#!/usr/bin/env python3
"""Report structural differences between the EN and FA trees.

Word counts drift between languages and are *not* a bug; what must match is the
structure: the file set, heading depth, link targets (ignoring the /fa/ prefix),
the shortcode sequence and its static parameters, and the pin/region counts.
Exit 1 when anything structural differs.

    python3 tools/parity.py            # summary
    python3 tools/parity.py -v         # also print every file that matches
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN, FA = "content/en", "content/fa"
SHORT = re.compile(r"\{\{[<%]\s*([a-zA-Z][\w-]*)([^>]*?)[>%]\}\}", re.S)
HEADING = re.compile(r"^(#{1,6})\s+\S.*$", re.M)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)|href=\"([^\"]+)\"")
ATTR = re.compile(r'([a-zA-Z][\w-]*)="([^"]*)"')
PIN = re.compile(r"^\s*pin\s", re.M)
REGION = re.compile(r"^\s*region\s", re.M)
FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
FMKEY = re.compile(r"^([A-Za-z][\w-]*):", re.M)
SOURCES = re.compile(r"^sources:\s*\[(.*)\]\s*$", re.M)
SOURCES_BLOCK = re.compile(r"^sources:\s*\n((?:\s+-\s+.*\n?)+)", re.M)
SOURCES_EMPTY = re.compile(r"^sources:\s*$", re.M)
# media paths referenced by slider / figure / scrollplay bodies (caption text follows |)
MEDIA = re.compile(r"^([A-Za-z0-9_./-]+\.(?:png|jpe?g|gif|webp|svg|mp4|webm|mp3))\s*\|", re.M)
# params whose value is prose or artwork and legitimately differs per language
DYN = {"label", "note", "caption", "text", "title", "src", "id", "quote", "by",
       "name", "w", "rowspan", "side", "cols", "rows", "gap", "align", "path",
       "source", "lang", "href", "alt"}


def tree(d):
    out = set()
    for dp, _, fn in os.walk(os.path.join(ROOT, d)):
        for f in fn:
            if f.endswith(".md"):
                out.add(os.path.relpath(os.path.join(dp, f), os.path.join(ROOT, d)))
    return out


def read(d, rel):
    with open(os.path.join(ROOT, d, rel), encoding="utf-8") as fh:
        return fh.read()


def normlink(v):
    """FA pages link to their own tree; drop the prefix so both sides compare."""
    if v.startswith("#") or "://" in v or v.startswith("mailto:"):
        return v
    return re.sub(r"^/fa/", "/", v)


def n_sources(text):
    """How many sources a page cites. Values are translated, the count is not."""
    fm = FM.match(text)
    if not fm:
        return None
    b = fm.group(1)
    on = SOURCES.search(b)
    if on:
        v = on.group(1).strip()
        if not v:
            return 0
        return len(re.split(r'"\s*,\s*"', v.strip('"')))
    blk = SOURCES_BLOCK.search(b)
    if blk:
        return len(re.findall(r"^\s+-\s+", blk.group(1), re.M))
    if SOURCES_EMPTY.search(b):
        return 0
    return None


def structure(text):
    fm = FM.match(text)
    fmkeys = sorted(FMKEY.findall(fm.group(1))) if fm else []
    heads = [len(m.group(1)) for m in HEADING.finditer(text)]
    links = sorted(normlink(v or v2)
                   for m in LINK.finditer(text) for v, v2 in [m.groups()])
    shorts = []
    for m in SHORT.finditer(text):
        shorts.append((m.group(1),
                       tuple(sorted((k, v) for k, v in ATTR.findall(m.group(2))
                                    if k not in DYN))))
    body = FM.sub("", text, count=1)
    return fmkeys, heads, links, shorts, len(PIN.findall(body)), \
        len(REGION.findall(body)), len(body.split()), n_sources(text), \
        sorted(MEDIA.findall(body))


def i18n_keys():
    """Both language files must define the same keys, or strings fall back to English."""
    out = {}
    d = os.path.join(ROOT, "i18n")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not f.endswith((".toml", ".yaml", ".json")):
            continue
        lang = f.rsplit(".", 1)[0]
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            out[lang] = set(re.findall(r"^\[([\w.-]+)\]\s*$", fh.read(), re.M))
    return out


# English that legitimately appears in a template regardless of language:
# licences, formats, code identifiers, and connectives used as punctuation.
LICENCE_OK = set("""CC BY-SA MIT RSS HTTP HTTPS HTML CSS SVG PNG GIF JPEG MP4 WEBM
MP3 WOFF TTF OSS README API URL FAQ ID UTF UTC AM PM PDF N
and the of a an in on for to with""".split())

LAYTEXT = re.compile(r">([^<>{}]+)<")


def layout_english():
    """Visible English baked into a template: the same on every language page."""
    hits = []
    d = os.path.join(ROOT, "layouts")
    if not os.path.isdir(d):
        return hits
    for dp, _, fs in os.walk(d):
        for f in fs:
            if not f.endswith((".html", ".xml")):
                continue
            p = os.path.join(dp, f)
            txt = open(p, encoding="utf-8").read()
            txt = re.sub(r"\{\{[\s\S]*?\}\}", " ", txt)  # every Go action is a variable
            for m in LAYTEXT.finditer(txt):
                for w in re.findall(r"\b[A-Za-z][A-Za-z'’-]{2,}\b", m.group(1)):
                    if w in LICENCE_OK or w.lower() in {x.lower() for x in LICENCE_OK}:
                        continue
                    hits.append((os.path.relpath(p, ROOT), w, m.group(1).strip()[:60]))
    return hits


def main():
    verbose = "-v" in sys.argv
    en, fa = tree(EN), tree(FA)
    bad = 0

    langs = i18n_keys()
    if langs:
        names = sorted(langs)
        base = langs[names[0]]
        for other in names[1:]:
            for k in sorted(base - langs[other]):
                print("MISSING i18n  [%s] has no %r in %s" % (names[0], k, other))
                bad += 1
            for k in sorted(langs[other] - base):
                print("MISSING i18n  [%s] has no %r in %s" % (other, k, names[0]))
                bad += 1

    seen = set()
    for f, w, ctx in layout_english():
        if (f, w) in seen:
            continue
        seen.add((f, w))
        print("HARDCODED    %-40s %r in %s" % (f, w, ctx))
        bad += 1

    for rel in sorted(en - fa):
        print("MISSING FA   ", rel); bad += 1
    for rel in sorted(fa - en):
        print("MISSING EN   ", rel); bad += 1

    for rel in sorted(en & fa):
        try:
            te, tf = read(EN, rel), read(FA, rel)
        except UnicodeDecodeError as e:
            print("UNREADABLE   ", rel, e); bad += 1; continue
        ke, he, le, se, pe, re_, we, sse, me = structure(te)
        kf, hf, lf, sf, pf, rf, wf, ssf, mf = structure(tf)
        probs = []
        if ke != kf:
            probs.append("front matter keys EN=%s FA=%s" % (ke, kf))
        if he != hf:
            probs.append("heading depths EN=%s FA=%s" % (he, hf))
        if le != lf:
            probs.append("links only-EN=%s only-FA=%s"
                         % ([x for x in le if x not in lf],
                            [x for x in lf if x not in le]))
        if len(se) != len(sf):
            probs.append("shortcode count %d vs %d" % (len(se), len(sf)))
            for i, a in enumerate(se):
                probs.append("  EN #%d %s %s" % (i, a[0], a[1]))
            for i, a in enumerate(sf):
                probs.append("  FA #%d %s %s" % (i, a[0], a[1]))
        else:
            for i, (a, b) in enumerate(zip(se, sf)):
                if a[0] != b[0]:
                    probs.append("shortcode #%d kind %s vs %s" % (i, a[0], b[0]))
                elif a[1] != b[1]:
                    probs.append("shortcode #%d %s params EN=%s FA=%s"
                                 % (i, a[0], a[1], b[1]))
        if pe != pf:
            probs.append("pin lines %d vs %d" % (pe, pf))
        if re_ != rf:
            probs.append("region lines %d vs %d" % (re_, rf))
        if sse != ssf:
            probs.append("sources cited EN=%s FA=%s" % (sse, ssf))
        if me != mf:
            probs.append("media paths only-EN=%s only-FA=%s"
                         % ([x for x in me if x not in mf],
                            [x for x in mf if x not in me]))
        # one side a stub, the other not (small symmetric diffs are fine)
        if (we < 25) != (wf < 25):
            probs.append("one side is a stub: EN %d vs FA %d words" % (we, wf))
        elif abs(we - wf) > 60 and abs(we - wf) > 0.45 * max(we, wf):
            probs.append("body size EN %d vs FA %d words" % (we, wf))
        if probs:
            bad += len(probs)
            print("DIFF %-46s" % rel)
            for p in probs:
                print("      -", p)
        elif verbose:
            print("ok   ", rel, "(%d/%d words)" % (we, wf))
    print("\n%d difference(s)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
