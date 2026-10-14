#!/usr/bin/env python3
"""Download the Natural Earth data used by genmaps.py into tools/geo/ (public domain).

    python3 tools/fetch_geo.py

1:110m land is enough for the world map; the 1:50m land, rivers and lakes give the
regional maps their islands, fjords, real river courses and lakes.  Files that
already exist are skipped.  Source: naturalearthdata.com (via the nvkelso/natural-earth-vector mirror).
"""
import os
import sys
import urllib.request

BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
FILES = ["ne_110m_land", "ne_110m_lakes", "ne_110m_rivers_lake_centerlines",
         "ne_50m_land", "ne_50m_lakes", "ne_50m_rivers_lake_centerlines"]
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geo")

os.makedirs(DEST, exist_ok=True)
for name in FILES:
    path = os.path.join(DEST, name + ".geojson")
    if os.path.exists(path):
        print("have  %s" % name)
        continue
    try:
        urllib.request.urlretrieve(BASE + name + ".geojson", path)
        print("got   %-36s %6d KB" % (name, os.path.getsize(path) // 1024))
    except Exception as e:  # noqa: BLE001
        print("FAIL  %s: %s" % (name, e))
        sys.exit(1)
