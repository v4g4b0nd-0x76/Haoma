#!/usr/bin/env python3
"""Download the Natural Earth data used by genmaps.py into tools/geo/ (public domain).

    python3 tools/fetch_geo.py

Land at 1:110m is enough for the world sheet; the regional sheets look much better with the
1:50m land, rivers and lakes (about 3.4 MB in total). Existing files are kept.
"""
import os
import sys
import urllib.request

BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
FILES = ["ne_110m_land", "ne_110m_rivers_lake_centerlines", "ne_110m_lakes",
         "ne_50m_land", "ne_50m_rivers_lake_centerlines", "ne_50m_lakes"]
DEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "geo")

if __name__ == "__main__":
    os.makedirs(DEST, exist_ok=True)
    for name in FILES:
        path = os.path.join(DEST, name + ".geojson")
        if os.path.exists(path):
            print("have  %s" % name)
            continue
        try:
            with urllib.request.urlopen(BASE + name + ".geojson", timeout=60) as r, open(path, "wb") as f:
                f.write(r.read())
            print("got   %s (%d KB)" % (name, os.path.getsize(path) // 1024))
        except Exception as e:          # noqa: BLE001
            print("FAIL  %s: %s" % (name, e))
            if os.path.exists(path):
                os.remove(path)
            if name == "ne_110m_land":
                sys.exit(1)
