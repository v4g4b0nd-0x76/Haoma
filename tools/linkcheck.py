#!/usr/bin/env python3
"""Check every internal link in a built site.

    python3 tools/linkcheck.py                       # the default build
    python3 tools/linkcheck.py /tmp/opencode/out-repo --baseURL /repo/

A link is "internal" when it starts with the base prefix (or with "/"), and it
is broken when it does not resolve to a file in the output tree. Fragments are
checked too: `/page/#an-id` only passes if that page really has `id="an-id"`.
`data-href` is skipped on purpose -- it is read by the culture picker, not a link.
"""
import os
import re
import sys
from urllib.parse import unquote, urlsplit

DEFAULT = "/tmp/opencode/out-root"

# href/src/srcset, ignoring data-href so the picker's option targets are not judged
ATTR = re.compile(r'([a-zA-Z-]*)(?:href|src)="([^"]*)"')
ID = re.compile(r'\bid="([^"]+)"')


def collect(root, base):
    """every internal target in the build, as (file, url, fragment)"""
    out = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8").read()
            targets = []
            for attr, val in ATTR.findall(text):
                if attr:                       # data-href and friends
                    continue
                targets.append(val)
            for val in re.findall(r'srcset="([^"]*)"', text):
                targets += [p.strip().split(" ")[0] for p in val.split(",")]
            for t in targets:
                if t.startswith(("http://", "https://", "mailto:", "tel:",
                                 "data:", "//")):
                    continue
                parts = urlsplit(t)
                url = unquote(parts.path)
                if not url:
                    continue                   # pure fragment, checked below
                if base and url.startswith(base):
                    url = url[len(base):]
                elif not url.startswith("/"):
                    url = os.path.relpath(os.path.join(dirpath, url), root)
                    url = "/" + url.replace(os.sep, "/")
                out.append((path, url, parts.fragment))
    return out


def exists(root, url):
    """does this site path name a file? (a bare /a/b/ is /a/b/index.html)"""
    rel = unquote(url).lstrip("/")
    if not rel:
        return True                            # the site root
    direct = os.path.join(root, rel)
    if os.path.isfile(direct):
        return direct
    if rel.endswith("/"):
        idx = os.path.join(direct, "index.html")
        return idx if os.path.isfile(idx) else None
    for cand in (direct + ".html", os.path.join(direct, "index.html")):
        if os.path.isfile(cand):
            return cand
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = args[0] if args else DEFAULT
    base = ""
    for a in sys.argv[1:]:
        if a.startswith("--baseURL="):
            base = a.split("=", 1)[1]

    if not os.path.isdir(root):
        print("no such build: %s" % root)
        return 2

    links = collect(root, base)
    ids = {}
    broken = []
    for path, url, frag in links:
        target = exists(root, url)
        if not target:
            broken.append((os.path.relpath(path, root), url, "no such page"))
            continue
        if frag:
            if target not in ids:
                ids[target] = set(ID.findall(open(target, encoding="utf-8").read()))
            if frag not in ids[target]:
                broken.append((os.path.relpath(path, root), url + "#" + frag,
                               "no such anchor"))

    print("%d internal links across %d pages (baseURL %r)"
          % (len(links), len({p for p, _, _ in links}), base or "/"))
    if broken:
        seen = set()
        for src, url, why in broken:
            key = (src, url)
            if key in seen:
                continue
            seen.add(key)
            print("  BROKEN %s -> %s  (%s)" % (src, url, why))
        print("%d broken" % len(broken))
        return 1
    print("0 broken")
    return 0


if __name__ == "__main__":
    sys.exit(main())
