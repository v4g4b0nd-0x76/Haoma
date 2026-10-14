#!/usr/bin/env python3
"""Generate the stylised map artwork in static/img/maps/.

    python3 tools/genmaps.py            # all maps
    python3 tools/genmaps.py persia     # just one

Geography: Natural Earth land / rivers / lakes (public domain) in tools/geo/.
Run `python3 tools/fetch_geo.py` once to download the 1:50m detail files; the
script falls back to the bundled 1:110m land if they are missing.

House style (inspired by the old Middle-earth and antique sea charts, kept in
our dark palette): ink-blue sea with shore ripples, olive land with grain,
gold coastline over a dark ink line, engraved mountains / hills / forests /
dunes / marshes, tapered rivers, curved hand-lettered labels with halos,
engraved monsters and ships, ladder border, ribbon cartouche, compass rose,
scale bar.  Pure SVG: no scripts, no external assets.

Art (monsters, ships, terrain symbols) lives in tools/mapart.py.
Outputs: <name>.svg and <name>-fa.svg for world, middle-east, persia, india,
aegean, scandinavia.  Pin positions are unchanged: they are % of the same lon/lat
box (see the printout at the end of a run).
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mapart as art  # noqa: E402

ROOT = os.path.dirname(HERE)
GEO = os.environ.get("GENMAPS_GEO", os.path.join(ROOT, "tools", "geo"))
OUT = os.environ.get("GENMAPS_OUT", os.path.join(ROOT, "static", "img", "maps"))

GOLD = "#d4b86e"
GOLD_DIM = "#8f7a43"
LAND, LAND2 = "#34452a", "#1b2714"
SEA, SEA2 = "#10283a", "#07131d"
RIPPLE = "#6fb0d0"
INKC = "#070c08"
SEA_TEXT = "#8fb8d2"
LAND_TEXT = "#e6d7ae"
FONT_EN = "Cinzel,Georgia,'Times New Roman',serif"
FONT_FA = "Vazirmatn,'Segoe UI',Tahoma,sans-serif"

# ---------------------------------------------------------------- geometry


class Frame:
    """Linear lon/lat -> pixel mapping.  Pin %-positions depend only on the lon/lat box,
    so changing the aspect (cos=True keeps shapes true at high latitude) never moves pins."""

    def __init__(self, box, w, cos=False, pad=16):
        self.box, self.w, self.pad = box, w, pad
        lon0, lon1, lat0, lat1 = box
        k = math.cos(math.radians((lat0 + lat1) / 2)) if cos else 1.0
        self.h = int(2 * pad + (lat1 - lat0) / ((lon1 - lon0) * k) * (w - 2 * pad))
        self.px = (w - 2 * pad) / (lon1 - lon0)
        self.py = (self.h - 2 * pad) / (lat1 - lat0)

    def xy(self, lon, lat):
        lon0, lon1, lat0, lat1 = self.box
        return self.pad + (lon - lon0) * self.px, self.pad + (lat1 - lat) * self.py


def pct(lon, lat, box):
    lon0, lon1, lat0, lat1 = box
    return (lon - lon0) / (lon1 - lon0) * 100, (lat1 - lat) / (lat1 - lat0) * 100


def clip_poly(pts, xmin, ymin, xmax, ymax):
    def run(p, inside, cut):
        out = []
        if not p:
            return out
        prev = p[-1]
        for cur in p:
            if inside(cur):
                if not inside(prev):
                    out.append(cut(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cut(prev, cur))
            prev = cur
        return out
    def ix(x):
        return lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / ((b[0] - a[0]) or 1e-9))
    def iy(y):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (y - a[1]) / ((b[1] - a[1]) or 1e-9), y)
    p = run(pts, lambda q: q[0] >= xmin, ix(xmin))
    p = run(p, lambda q: q[0] <= xmax, ix(xmax))
    p = run(p, lambda q: q[1] >= ymin, iy(ymin))
    return run(p, lambda q: q[1] <= ymax, iy(ymax))


def simplify(pts, tol):
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        m = math.hypot(dx, dy) or 1e-9
        best, idx = 0, -1
        for i in range(a + 1, b):
            d = abs((pts[i][0] - ax) * dy - (pts[i][1] - ay) * dx) / m
            if d > best:
                best, idx = d, i
        if best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def simplify_ring(pts, tol):
    """Douglas-Peucker for closed rings: split at the point farthest from the start so the
    baseline is never degenerate (first == last would otherwise collapse the whole ring)."""
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 4:
        return pts
    k = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
    return simplify(pts[:k + 1], tol)[:-1] + simplify(pts[k:] + [pts[0]], tol)[:-1]


def d_of(pts, close=False):
    return "M" + "L".join("%.1f %.1f" % p for p in pts) + ("Z" if close else "")


class Raster:
    """Even-odd scanline mask of the land, for 'is this point on land?' queries."""

    def __init__(self, w, h, rings):
        self.w, self.h = w, h
        self.rows = [bytearray(w) for _ in range(h)]
        xs = [[] for _ in range(h)]
        for ring in rings:
            n = len(ring)
            for i in range(n):
                x0, y0 = ring[i]
                x1, y1 = ring[(i + 1) % n]
                if y0 == y1:
                    continue
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                for y in range(max(0, int(math.ceil(y0))), min(h - 1, int(math.floor(y1))) + 1):
                    xs[y].append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
        for y, row in enumerate(xs):
            row.sort()
            for a, b in zip(row[0::2], row[1::2]):
                for x in range(max(0, int(math.ceil(a))), min(w - 1, int(math.floor(b))) + 1):
                    self.rows[y][x] = 1

    def land(self, x, y, m=0):
        for dx, dy in ((0, 0), (m, 0), (-m, 0), (0, m), (0, -m)):
            xi, yi = int(x + dx), int(y + dy)
            if not (0 <= xi < self.w and 0 <= yi < self.h and self.rows[yi][xi]):
                return False
        return True


# ---------------------------------------------------------------- data


_cache = {}


def load_geo(name):
    if name not in _cache:
        p = os.path.join(GEO, name + ".geojson")
        _cache[name] = json.load(open(p)) if os.path.exists(p) else None
    return _cache[name]


def pick_geo(res, kind):
    """kind: land | lakes | rivers_lake_centerlines; prefer the requested resolution."""
    for r in ((res, "110") if res != "110" else ("110",)):
        g = load_geo("ne_%sm_%s" % (r, kind))
        if g:
            return g, r
    return None, None


def polys(geo):
    for feat in geo["features"]:
        g = feat["geometry"]
        if not g:
            continue
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            yield feat.get("properties", {}), poly


def lines(geo):
    for feat in geo["features"]:
        g = feat["geometry"]
        if not g:
            continue
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]] if g["type"] == "LineString" else []):
            yield feat.get("properties", {}), ln


# ---------------------------------------------------------------- maps table
# box=(lon0, lon1, lat0, lat1).  Extra keys added for the new art:
#   cos        true-proportion aspect        res       "50" (detail) or "110"
#   forests / deserts / hills / marsh: (lon, lat, half-width deg, half-height deg)
#   ships: (kind, lon, lat, scale, flip)     ranges: mountain chains as lon/lat polylines
MAPS = {
    "world": dict(
        box=(-135, 225, -58, 84), w=1700, res="110", cos=False, cs=.5, gscale=.62,
        title={"en": "The World", "fa": "جهان"},
        labels=[
            ("NORTH AMERICA", -98, 46, 21, "r", 0), ("SOUTH AMERICA", -57, -13, 21, "r", 0),
            ("EUROPA", 14, 50, 19, "r", 0), ("AFRICA", 20, 4, 21, "r", 0), ("ASIA", 100, 48, 22, "r", 0),
            ("ARABIA", 45, 22, 15, "r", 0), ("PERSIA", 54, 32, 15, "r", 0), ("INDIA", 79, 22, 16, "r", 0),
            ("CHINA", 108, 33, 17, "r", 0), ("SCYTHIA", 60, 52, 15, "r", 0), ("SIBERIA", 100, 65, 17, "r", 0),
            ("AUSTRALIA", 134, -25, 17, "r", 0), ("GREENLAND", -42, 72, 14, "r", 0),
            ("ATLANTIC OCEAN", -32, 18, 16, "s", 0), ("INDIAN OCEAN", 76, -26, 16, "s", 0),
            ("PACIFIC OCEAN", 148, 2, 16, "s", 0), ("ARCTIC OCEAN", 100, 78, 15, "s", 0),
            ("MEDITERRANEAN SEA", 17, 34.5, 13, "s", 0), ("AMAZONIA", -62, -5, 13, "r", 0),
        ],
        ranges=[
            [(-123, 60), (-117, 53), (-112, 47), (-108, 40), (-106, 34)],
            [(-72, 10), (-77, 2), (-78, -8), (-72, -16), (-69, -26), (-71, -36), (-72, -48)],
            [(6, 45.5), (9.5, 46.5), (13, 46.8)], [(60, 68), (59, 61), (58, 55)],
            [(74, 35), (79, 32), (85, 28.5), (92, 28), (98, 28)], [(-9, 31), (-4, 33), (1, 35), (7, 36)],
            [(38, 44.5), (42, 43), (46, 42), (48, 41.5)], [(86, 50), (92, 49), (98, 50)],
            [(6, 60), (10, 63), (15, 67), (20, 69)], [(-84, 35), (-79, 38), (-74, 42)],
            [(78, 36), (88, 35.5), (98, 35)], [(36, 2), (35, -5)], [(37, 12), (39, 9)],
        ],
        forests=[(110, 60, 32, 4.5, 1), (-100, 56, 22, 4, 1), (-62, -4, 9, 6, 1), (22, 0, 7, 5, 1), (20, 63, 10, 3.5, 1),
                 (103, 16, 7, 6, 1), (-85, 38, 8, 5, 1), (45, 58, 15, 4, 1), (115, -2, 8, 3, 1)],
        deserts=[(8, 23, 22, 6, 1), (47, 22, 8, 5, 1), (104, 42, 10, 3, 1), (130, -26, 12, 5, 1), (22, -22, 4, 3, 1),
                 (84, 39, 5, 2, 1), (56, 33, 5, 3.5, 1), (71, 27, 3.5, 3, 1), (-114, 40, 5, 3, 1)],
        rivers=[
            [(31, 30.5), (31.5, 27), (32.5, 23), (33.5, 18), (34, 13), (33, 8), (32, 2), (30, -1)],
            [(-73, -4), (-68, -4), (-64, -5), (-60, -4), (-56, -3), (-52, -2), (-50, 0)],
            [(28, -6), (24, -4), (20, -3), (17, -4), (15, -6), (13, -6), (12, -6)],
            [(-95, 47), (-96, 43), (-95, 38), (-92, 34), (-91, 31), (-89, 29)],
            [(9, 48), (14, 47), (18, 46), (21, 45), (25, 45), (29, 45)], [(37, 57), (40, 55), (44, 52), (47, 48), (48, 45)],
            [(78, 30), (81, 26), (85, 25), (88, 24), (90, 23)], [(73, 34), (71, 31), (69, 27), (67, 24)],
            [(97, 32), (102, 29), (106, 29), (110, 30), (114, 31), (119, 32), (122, 31)],
            [(96, 35), (101, 36), (106, 35), (110, 35), (114, 37), (118, 38), (119, 37)],
        ],
        creatures=[("serpent", -38, 8, 2.3, 0, None), ("dragon", 78, 60, 1.9, 0, None), ("bird", 82, -12, 1.9, 0, None)],
        ships=[("longship", -28, 52, 1.5, 0), ("dhow", 66, 8, 1.5, 0), ("trireme", 18, 33.2, 1.1, 0),
               ("dhow", 120, 12, 1.2, 1), ("longship", -100, -40, 1.4, 1)],
        graticule=30,
    ),
    "middle-east": dict(
        box=(26, 60, 23, 41), w=1200, res="50", cos=True,
        title={"en": "Mesopotamia and the Levant", "fa": "بین‌النهرین و شام"},
        labels=[
            ("ANATOLIA", 32, 38.5, 17, "r", 0), ("LEVANT", 36.6, 34.6, 15, "r", 0),
            ("MESOPOTAMIA", 43.6, 34.4, 17, "r", 0), ("ARABIA", 44, 27.5, 17, "r", 0), ("PERSIA", 54.5, 32, 16, "r", 0),
            ("MEDITERRANEAN SEA", 31.5, 34.4, 13, "s", 0), ("BLACK SEA", 36.5, 41.4, 12, "s", 0),
            ("CASPIAN SEA", 51, 38, 13, "s", 0), ("RED SEA", 35.5, 26, 13, "s", 0),
            ("PERSIAN GULF", 49.5, 28.2, 13, "s", -18), ("AEGEAN", 25.5, 37.6, 12, "s", 0),
        ],
        ranges=[[(29, 37.4), (33, 37.6), (37, 37)], [(44.5, 37.5), (46.5, 33.5), (49, 31), (53, 28), (56, 27)],
                [(49, 36.6), (52, 36.4), (55.5, 36.6)], [(36, 34.6), (36.3, 33.4)], [(41, 43), (45, 42), (48, 41)],
                [(37, 28), (39.4, 24.6)]],
        forests=[(36, 36.6, 1.2, .7, 1), (36, 34, .5, 1, 1), (33, 37, 3, .6, 1), (51.5, 36.8, 3, .5, 1), (47, 34.5, 1.8, 2.2, 1), (43, 41, 3, 1, 1)],
        deserts=[(42, 26, 8, 4, 1), (40, 33, 3, 1.5, 1), (40, 28.5, 2.5, 1.3, 1), (33.5, 29, 1.5, 1, 1), (54, 33.5, 3, 2, 1)],
        marsh=[(47.2, 31.2, 1.2, .9, 1)],
        hills=[(34, 39, 4, 1.2, 1), (35.8, 33, .5, 1.5, 1), (45, 36, 1.4, 1.2, 1)],
        rivers=[[(38.6, 37.5), (40.5, 36.6), (42.5, 35), (44, 33.2), (45.4, 31.6), (47, 30.6), (48, 30.1)],
                [(38.2, 38.4), (40.5, 37.4), (42.6, 36.2), (43.5, 34.6), (44.6, 33), (45.6, 31.6), (47.4, 30.7)],
                [(31.2, 30.6), (31.6, 28.5), (32.6, 26), (33.6, 24), (34.4, 23)], [(35.7, 32.7), (35.6, 31.7), (35.5, 31.2)],
                [(47, 32.5), (48.5, 31.6), (49.5, 30.5)]],
        creatures=[("guardian", 36.05, 36.25, 1.45, 0, "HUMBABA"), ("dragon", 43.0, 35.2, 1.4, 0, "MUSHUSSU"),
                   ("bird", 48.6, 33.4, 1.4, 0, "ANZU")],
        ships=[("trireme", 33.5, 34.2, 1.0, 0), ("dhow", 51.5, 26.9, 1.0, 1), ("dhow", 37.6, 23.8, .9, 0), ("trireme", 30, 35.4, .9, 1)],
        graticule=5,
    ),
    "persia": dict(
        box=(42, 72, 24, 40), w=1200, res="50", cos=True,
        title={"en": "The Iranian Plateau", "fa": "فلات ایران"},
        labels=[
            ("MEDIA", 48.6, 35.2, 15, "r", 0), ("PERSIA", 54, 32.6, 17, "r", 0), ("PARTHIA", 58.6, 36.4, 15, "r", 0),
            ("ARIA", 64, 33.4, 14, "r", 0), ("KAVIR DESERT", 55.5, 34.4, 12, "r", -12),
            ("CASPIAN SEA", 51, 37.6, 13, "s", 0), ("PERSIAN GULF", 49.8, 29.4, 13, "s", -30),
            ("GULF OF OMAN", 58.5, 25.4, 13, "s", 0), ("ARABIAN SEA", 65, 25.4, 13, "s", 0), ("TRANSOXIANA", 64, 38.4, 13, "r", 0),
        ],
        ranges=[[(48.8, 36.4), (52, 36.2), (55.5, 36.5)], [(45, 36.5), (46.8, 33), (49.5, 30.5), (53, 28), (56, 26.8)],
                [(58, 38.4), (61.5, 37.4)], [(64, 35.5), (68, 35.2), (71, 35.5)], [(70, 38.6), (72, 37.4)]],
        forests=[(51.5, 36.6, 3, .6, 1), (55, 37.2, 2, .4, 1), (47.5, 33.5, 1.8, 2.8, 1), (44, 39.5, 2, 1, 1), (68, 35, 2.5, 1.5, 1)],
        deserts=[(54.5, 34.5, 4, 2.2, 1), (59, 30.5, 2.5, 3, 1), (60, 39, 5, 1, 1), (65, 30.5, 2, 2, 1), (64, 27.5, 4, 1, 1)],
        marsh=[(61.5, 31.3, .8, .7, 1)], hills=[(52, 31, 3, 1, 1), (66, 33, 2, 1, 1)],
        rivers=[[(54, 37.4), (56, 38), (58, 38.2)], [(65, 33.6), (63, 31.4), (61.4, 29.6), (60.6, 28.4)],
                [(46.6, 33.4), (48, 32.4), (49.4, 30.6)], [(72, 34.4), (71.4, 33), (71, 31.6)], [(49.6, 33.4), (51.6, 32.4), (53, 32.2)]],
        creatures=[("bird", 52.6, 36.7, 1.8, 0, "SIMORGH"), ("dragon", 46.3, 33.6, 1.6, 1, "DAHAKA"), ("demon", 63.5, 30.6, 1.5, 1, "DAEVA")],
        ships=[("dhow", 51, 27.4, 1.0, 0), ("dhow", 62, 24.7, .9, 1), ("dhow", 56.4, 26.2, .8, 0)],
        graticule=5,
    ),
    "india": dict(
        box=(64, 104, 5, 34), w=1200, res="50", cos=True,
        title={"en": "India and the Indus", "fa": "هند و سند"},
        labels=[
            ("INDIA", 78, 22.4, 20, "r", 0), ("HIMALAYA", 79, 31.6, 14, "r", -6), ("THAR DESERT", 71.4, 27, 13, "r", -20),
            ("DECCAN", 77, 17.6, 14, "r", 0), ("BENGAL", 89.4, 23, 13, "r", 0), ("ARABIAN SEA", 71.4, 15, 14, "s", -12),
            ("BAY OF BENGAL", 87, 15.4, 14, "s", -14), ("INDIAN OCEAN", 80, 7, 14, "s", 0),
        ],
        ranges=[[(72, 33.4), (76, 32.4), (80, 30.4), (84, 28.4), (88, 27), (92, 27), (96, 28)], [(74, 27), (75.6, 24.4), (76.6, 22.6)],
                [(73.4, 20), (75, 15), (76.4, 11)], [(79.4, 19.4), (82, 17.6), (84.4, 17)], [(70, 36), (74, 35.5)]],
        forests=[(75.5, 13, .8, 4, 1), (80, 20, 4, 2, 1), (82, 27.5, 6, .5, 1), (89.2, 22.2, 1.2, .4, 1), (94, 26.5, 3, 1.5, 1),
                 (80, 16, 2, 2, 1), (96, 20, 4, 4, 1)],
        deserts=[(71, 26.5, 3, 2.5, 1), (70, 23.8, 1.2, .5, 1)], marsh=[(89, 22.5, 1.5, .7, 1)],
        hills=[(77, 23, 3.5, .6, 1), (74.5, 26, 1, 2.5, 1)],
        rivers=[[(72.4, 34), (71.4, 31), (70, 28), (68.4, 25.4), (67.4, 24)], [(78.4, 30), (81, 26.4), (84.6, 25.4), (87.6, 24.4), (90, 23)],
                [(77.6, 30.4), (78.6, 27.4), (81, 26.4)], [(82, 29.4), (87, 27.4), (91, 27), (94.4, 27.4), (95.4, 25.4), (96, 24.4)],
                [(78.4, 19.6), (81.4, 17.6), (84, 16.6), (87, 16.6)], [(74.4, 17), (77.6, 16.4), (80.6, 15.6), (83.4, 15.6)]],
        creatures=[("bird", 80.2, 28.2, 1.7, 0, "GARUDA"), ("serpent", 86.8, 23.6, 1.5, 0, "NAGA"), ("serpent", 73.5, 9.5, 1.5, 1, "MAKARA")],
        ships=[("dhow", 69, 13, 1.1, 0), ("dhow", 88, 13, 1.0, 1), ("dhow", 82, 6.4, .9, 0)],
        graticule=5,
    ),
    "aegean": dict(
        box=(15, 39, 33.5, 45.5), w=1200, res="50", cos=True,
        title={"en": "The Aegean", "fa": "دریای اژه"},
        labels=[
            ("GREECE", 21.6, 40.4, 16, "r", 0), ("ANATOLIA", 32.4, 38.6, 16, "r", 0), ("THRACE", 25.6, 42, 13, "r", 0),
            ("CRETE", 24.6, 35.3, 12, "r", 0), ("CYPRUS", 33.2, 35, 12, "r", 0), ("AEGEAN SEA", 25.2, 38.4, 14, "s", -20),
            ("IONIAN SEA", 18.4, 38, 13, "s", -14), ("MEDITERRANEAN SEA", 19, 34.4, 13, "s", 0), ("BLACK SEA", 33.6, 43.4, 13, "s", 0),
            ("SEA OF MARMARA", 28.4, 40.6, 11, "s", -16),
        ],
        ranges=[[(20.8, 40.4), (21.8, 39), (22.4, 38)], [(29.6, 37.6), (33, 37.4), (36, 36.6)], [(24.6, 41.6), (27, 41.4)],
                [(17.6, 43.6), (19.4, 42.6), (20.6, 41.6)]],
        forests=[(21, 39.8, .9, 1.5, 1), (24, 42.4, 3, .5, 1), (31, 37.4, 3, .6, 1), (33, 41.3, 4, .5, 1), (24.5, 41.7, 1.5, .5, 1), (18, 43.5, 2, 1.5, 1)],
        hills=[(22.2, 37.5, .6, .7, 1), (32, 39, 3, 1, 1), (24.7, 35.3, 1, .2, 1)], deserts=[], marsh=[],
        rivers=[[(21, 44.8), (23, 45), (25, 45.2), (27.4, 45), (29, 45.2)], [(27.6, 38.4), (29, 37.6), (30.4, 37.4)], [(21.6, 42.6), (21.4, 41.4), (21.6, 40.6)]],
        creatures=[("serpent", 16.6, 38.2, 1.3, 0, "SCYLLA"), ("serpent", 19.6, 39.4, 1.2, 1, "PYTHON"),
                   ("minotaur", 25.4, 34.5, 1.2, 0, "MINOTAUR"), ("dragon", 29.9, 36.9, 1.15, 1, "CHIMERA")],
        ships=[("trireme", 24.4, 37.3, 1.0, 0), ("trireme", 19.5, 35.6, 1.0, 1), ("trireme", 27.2, 40.2, .8, 0), ("trireme", 22.8, 36, .8, 1)],
        graticule=5,
    ),
    "scandinavia": dict(
        box=(-24, 30, 51, 71), w=1350, res="50", cos=True,
        title={"en": "The North", "fa": "سرزمین شمال"},
        labels=[
            ("SCANDINAVIA", 13.6, 62.4, 17, "r", -16), ("FINLAND", 26, 63.4, 15, "r", 0), ("ICELAND", -19, 65.2, 14, "r", 0),
            ("DENMARK", 9.2, 56.2, 13, "r", 0), ("BRITAIN", -3.4, 54.4, 14, "r", -16), ("GALLIA", 3.4, 51.6, 13, "r", 0),
            ("BALTIC SEA", 19.4, 57.4, 13, "s", -14), ("NORTH SEA", 1.4, 55.6, 13, "s", -14),
            ("NORWEGIAN SEA", -3, 66.6, 13, "s", -34), ("KARELIA", 30, 64.4, 12, "r", 0),
        ],
        ranges=[[(5.6, 59.4), (7.6, 61.4), (11, 64), (14.6, 66.4), (17, 68.6)], [(-20, 64.6), (-17.6, 65.6)], [(-4.6, 56.6), (-3, 54.6)],
                [(-5.6, 57.6), (-4, 57.2)]],
        forests=[(18, 62, 8, 4, 1), (9, 61, 1.5, 2.5, 1), (28, 64, 2, 3, 1), (24, 57.5, 3, 1.5, 1), (12, 52.5, 5, 1.2, 1), (-4.5, 57, 1.4, 1, 1), (9.5, 56, 1, .6, 1)],
        hills=[(-3.5, 52.3, .7, .8, 1), (-6, 54, 1, .8, 1)], deserts=[], marsh=[(24, 66, 3, 1.2, 1)],
        rivers=[[(10.4, 59.6), (11, 60.6), (11.6, 61.4)], [(24.4, 67.6), (24.8, 66), (25.4, 65.4)], [(17.6, 51), (18.6, 52.6), (19, 54)], [(30, 60.6), (28.6, 60.4), (27.4, 60.4)]],
        creatures=[("serpent", 3.6, 58.6, 1.7, 0, "JORMUNGANDR"), ("wolf", 14.5, 60.3, 1.5, 1, "FENRIR"), ("dragon", 23, 66.5, 1.5, 0, "NIDHOGG")],
        ships=[("longship", 3.6, 53.4, 1.0, 0), ("longship", 19.6, 58.4, .9, 1), ("longship", -8, 62, 1.1, 0), ("longship", 12, 69.6, .9, 1)],
        graticule=5,
    ),
}

# monster variants chosen from the label (falls back to the generic kind)
VARIANT = {"SIMORGH": "simurgh", "GARUDA": "garuda", "ANZU": "anzu", "DAHAKA": "dahaka", "MUSHUSSU": "mushussu", "NIDHOGG": "wyrm",
           "CHIMERA": "dragon", "NAGA": "naga", "MAKARA": "makara", "SCYLLA": "scylla", "PYTHON": "serpent", "JORMUNGANDR": "serpent",
           "FENRIR": "wolf", "MINOTAUR": "minotaur", "HUMBABA": "humbaba", "DAEVA": "div"}

PINS = {
    "middle-east": [("Uruk", 45.67, 31.32), ("Ur", 46.1, 30.96), ("Babylon", 44.42, 32.54), ("Nineveh", 43.14, 36.36), ("Cedar Forest", 35.6, 34.1)],
    "persia": [("Damavand", 53.06, 35.95), ("Ecbatana", 48.51, 34.8), ("Susa", 48.25, 32.19), ("Persepolis", 52.89, 29.99), ("Balkh", 66.9, 36.76)],
    "india": [("Kailash", 81.25, 31.07), ("Hastinapur", 77.55, 29.02), ("Varanasi", 83.0, 25.32), ("Dwarka", 68.97, 22.24), ("Lanka", 80.4, 8.35)],
    "aegean": [("Olympus", 22.36, 40.09), ("Troy", 26.18, 39.96), ("Delphi", 22.5, 38.48), ("Athens", 23.73, 37.98), ("Knossos", 25.16, 35.3)],
    "scandinavia": [("Uppsala", 17.64, 59.86), ("Birka", 17.64, 59.34), ("Nidaros", 10.4, 63.43), ("Hedeby", 9.42, 54.52), ("Jotunheim", 8.0, 62.0)],
    "world": [("Mesopotamia", 44, 33), ("Persia", 55, 31.5), ("India", 79, 22), ("Greece", 22.5, 39), ("The North", 15, 62)],
}

FA = {
    "NORTH AMERICA": "آمریکای شمالی", "SOUTH AMERICA": "آمریکای جنوبی", "EUROPA": "اروپا", "AFRICA": "آفریقا", "ASIA": "آسیا",
    "ARABIA": "عربستان", "PERSIA": "ایران", "INDIA": "هند", "CHINA": "چین", "SCYTHIA": "سکاستان", "SIBERIA": "سیبری",
    "AUSTRALIA": "استرالیا", "GREENLAND": "گرینلند", "ATLANTIC OCEAN": "اقیانوس اطلس", "INDIAN OCEAN": "اقیانوس هند",
    "PACIFIC OCEAN": "اقیانوس آرام", "ARCTIC OCEAN": "اقیانوس منجمد شمالی", "MEDITERRANEAN SEA": "دریای مدیترانه", "AMAZONIA": "آمازونیا",
    "ANATOLIA": "آناتولی", "LEVANT": "شام", "MESOPOTAMIA": "بین‌النهرین", "BLACK SEA": "دریای سیاه", "CASPIAN SEA": "دریای خزر",
    "RED SEA": "دریای سرخ", "PERSIAN GULF": "خلیج فارس", "AEGEAN": "اژه", "MEDIA": "ماد", "PARTHIA": "پارت", "ARIA": "رخج",
    "KAVIR DESERT": "کویر", "TRANSOXIANA": "ماوراءالنهر", "GULF OF OMAN": "دریای عمان", "ARABIAN SEA": "دریای عرب",
    "HIMALAYA": "هیمالیا", "THAR DESERT": "صحرای تار", "DECCAN": "دکن", "BENGAL": "بنگال", "BAY OF BENGAL": "خلیج بنگال",
    "GREECE": "یونان", "THRACE": "تراکیه", "CRETE": "کرت", "CYPRUS": "قبرس", "IONIAN SEA": "دریای یونان", "SEA OF MARMARA": "دریای مرمره",
    "AEGEAN SEA": "دریای اژه", "SCANDINAVIA": "اسکاندیناوی", "FINLAND": "فنلاند", "ICELAND": "ایسلند", "DENMARK": "دانمارک",
    "BRITAIN": "بریتانیا", "GALLIA": "گل", "BALTIC SEA": "دریای بالتیک", "NORTH SEA": "دریای شمال", "NORWEGIAN SEA": "دریای نروژ",
    "KARELIA": "کارلیا", "SIMORGH": "سیمرغ", "DAHAKA": "ضحاک", "DAEVA": "دیو", "HUMBABA": "همبابا", "MUSHUSSU": "موشووشو",
    "ANZU": "آنزو", "GARUDA": "گارودا", "NAGA": "ناگا", "MAKARA": "ماکارا", "SCYLLA": "اسکیلا", "PYTHON": "پیتون",
    "MINOTAUR": "مینوتور", "CHIMERA": "کیمرا", "JORMUNGANDR": "یورمونگاندر", "FENRIR": "فنریر", "NIDHOGG": "نیدهوگر",
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- building blocks


def land_rings(fr, spec):
    """Screen-space land rings (clipped to the frame, simplified)."""
    geo, res = pick_geo(spec.get("res", "50"), "land")
    box, world = fr.box, (fr.box[1] - fr.box[0]) > 300
    rings = []
    m = 30
    for _, poly in polys(geo):
        for ring in poly:
            lats = [p[1] for p in ring]
            if max(lats) < box[2] - 3 or min(lats) > box[3] + 3:
                continue
            for shift in ((-360, 0, 360) if world else (0,)):
                pts = [fr.xy(lon + shift, lat) for lon, lat in ring]
                xs = [p[0] for p in pts]
                if max(xs) < -m or min(xs) > fr.w + m:
                    continue
                pts = clip_poly(pts, -m, -m, fr.w + m, fr.h + m)
                pts = simplify_ring(pts, .35 if res == "50" else .25)
                if len(pts) >= 3:
                    rings.append(pts)
    return rings, res


def river_paths(fr, spec):
    """Real rivers when the Natural Earth file exists, else the hand-placed ones."""
    out = []
    geo, res = pick_geo(spec.get("res", "50"), "rivers_lake_centerlines")
    if geo and not spec.get("rivers_manual"):
        for pr, ln in lines(geo):
            if "lake" in str(pr.get("featurecla", "")).lower():
                continue
            rank = pr.get("scalerank", 5)
            if rank is None or rank > (5 if res == "50" else 6):
                continue
            pts = [fr.xy(lon, lat) for lon, lat in ln]
            run, runs = [], []
            for p in pts:
                if -40 < p[0] < fr.w + 40 and -40 < p[1] < fr.h + 40:
                    run.append(p)
                elif len(run) > 1:
                    runs.append(run)
                    run = []
                else:
                    run = []
            if len(run) > 1:
                runs.append(run)
            for r in runs:
                r = simplify(r, .6)
                if len(r) > 1:
                    out.append((r, 1.0 + max(0, 5 - rank) * .24))
    else:
        for riv in spec.get("rivers", []):
            out.append(([fr.xy(lo, la) for lo, la in riv], 1.7))
    return out


def smooth(pts):
    return art.cr(pts, 4) if len(pts) > 2 else pts


def scatter(rng, fr, reg, gap, cap, ras, margin=3):
    lon, lat, rx, ry = reg[:4]
    cx, cy = fr.xy(lon, lat)
    rxp, ryp = rx * fr.px, ry * fr.py
    n = min(cap, int(math.pi * rxp * ryp / (gap * gap) * .6))
    pts, tries = [], 0
    while len(pts) < n and tries < n * 14:
        tries += 1
        a, r = rng.random() * 6.2832, math.sqrt(rng.random())
        x, y = cx + rxp * r * math.cos(a), cy + ryp * r * math.sin(a)
        if not ras.land(x, y, margin):
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < gap * gap * .8 for px, py in pts):
            continue
        pts.append((x, y))
    return pts


def mountains(rng, fr, rng_pts, unit, ras, gs):
    pts = [fr.xy(lo, la) for lo, la in rng_pts]
    seg = []
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / (gs * 11 * 1.7)))
        for i in range(n + 1):
            t = i / n
            seg.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, (b[0] - a[0]) / (L or 1), (b[1] - a[1]) / (L or 1)))
    out = []
    for x, y, tx, ty in seg:
        for row in (0, 1):
            off = (rng.random() - .5) * unit * .9 + (unit * .75 if row else 0)
            px, py = x - ty * off, y + tx * off
            if not ras.land(px, py, 2):
                continue
            s = gs * (.85 if row else 1.15) * (.8 + rng.random() * .5)
            out.append((py, "m%d" % rng.choice((1, 1, 2, 2, 3, 4)), px, s))
    return out


def est_w(text, size, lang):
    return len(text) * size * (.55 if lang == "fa" else .92)


def overlap(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def ladder(fr, g):
    """Alternating gold/ink cells between the outer and inner frame, one per graticule step."""
    lon0, lon1, lat0, lat1 = fr.box
    xs = [fr.pad] + [fr.xy(lo, lat0)[0] for lo in range(int(math.ceil(lon0 / g) * g), int(lon1) + 1, g) if lon0 < lo < lon1] + [fr.w - fr.pad]
    ys = [fr.pad] + [fr.xy(lon0, la)[1] for la in range(int(math.ceil(lat0 / g) * g), int(lat1) + 1, g) if lat0 < la < lat1] + [fr.h - fr.pad]
    ys = sorted(set(ys))
    o = []
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        f = GOLD if i % 2 == 0 else INKC
        o.append('<rect x="%.1f" y="7" width="%.1f" height="6" fill="%s"/><rect x="%.1f" y="%d" width="%.1f" height="6" fill="%s"/>' % (a, b - a, f, a, fr.h - 13, b - a, f))
    for i, (a, b) in enumerate(zip(ys, ys[1:])):
        f = GOLD if i % 2 == 0 else INKC
        o.append('<rect x="7" y="%.1f" width="6" height="%.1f" fill="%s"/><rect x="%d" y="%.1f" width="6" height="%.1f" fill="%s"/>' % (a, b - a, f, fr.w - 13, a, b - a, f))
    return "".join(o)


def compass(cx, cy, lang):
    o = ['<g transform="translate(%d %d)"><circle r="36" fill="#070b11" fill-opacity=".82" stroke="%s" stroke-width="1.2"/><circle r="31" fill="none" stroke="%s" stroke-width=".6"/>' % (cx, cy, GOLD, GOLD_DIM)]
    for k in range(16):
        ang = math.radians(k * 22.5 - 90)
        r = 33 if k % 4 == 0 else 24 if k % 2 == 0 else 15
        if k == 0:
            r = 38
        tip = (r * math.cos(ang), r * math.sin(ang))
        for sgn, fill in ((-1, GOLD), (1, "#3b3320")):
            b = ((6 if k % 2 == 0 else 3.6) * math.cos(ang + sgn * 1.05), (6 if k % 2 == 0 else 3.6) * math.sin(ang + sgn * 1.05))
            o.append('<path d="M0 0L%.1f %.1fL%.1f %.1fZ" fill="%s" stroke="%s" stroke-width=".5"/>' % (b[0], b[1], tip[0], tip[1], fill, GOLD_DIM))
    o.append('<circle r="3.2" fill="#070b11" stroke="%s" stroke-width=".9"/><text x="0" y="-43" text-anchor="middle" font-size="12" class="lb" fill="%s">%s</text></g>' % (GOLD, GOLD, "N" if lang == "en" else "ش"))
    return "".join(o)


def cartouche(x, y, text, lang):
    w = max(170, int(len(text) * (12 if lang == "fa" else 11.4)) + 56)
    h = 36
    o = ['<g><path d="M%d %dL%d %dL%d %dL%d %dZ" fill="#0c1218" stroke="%s" stroke-width=".9" opacity=".9"/>' % (x - 12, y + 6, x + 8, y + 6, x + 8, y + h + 6, x - 12, y + h + 6, GOLD_DIM)]
    o.append('<path d="M%d %dL%d %dL%d %dL%d %dZ" fill="#0c1218" stroke="%s" stroke-width=".9" opacity=".9"/>' % (x + w - 8, y + 6, x + w + 12, y + 6, x + w + 12, y + h + 6, x + w - 8, y + h + 6, GOLD_DIM))
    o.append('<path d="M%d %dh%d l12 %d l-12 %d h-%d l12 -%d Z" fill="#0a1017" fill-opacity=".93" stroke="%s" stroke-width="1.2"/>' % (x, y, w, h / 2, h / 2, w, h / 2, GOLD))
    o.append('<path d="M%d %dh%d M%d %dh%d" stroke="%s" stroke-width=".6" opacity=".7"/>' % (x + 14, y + 4, w - 28, x + 14, y + h - 4, w - 28, GOLD_DIM))
    o.append('<text class="lb" x="%d" y="%d" font-size="16" text-anchor="middle" letter-spacing=".12em">%s</text></g>' % (x + w // 2, y + 23, esc(text)))
    return "".join(o), w


def nice_km(target_px, px_per_deg, lat_ref):
    km_per_deg = 111.0 * math.cos(math.radians(lat_ref))
    raw = target_px / px_per_deg * km_per_deg
    return min((10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000), key=lambda c: abs(c - raw))


# ---------------------------------------------------------------- the map


def build(name, spec, lang):
    box = spec["box"]
    fr = Frame(box, spec["w"], spec.get("cos", False))
    w, h, pad = fr.w, fr.h, fr.pad
    rng = random.Random(sum(map(ord, name)))
    title = spec["title"][lang]
    unit = 13 * w / 1200
    gs = unit / 11.0 * spec.get("gscale", 1.0)   # glyph scale: symbols are ~12 units wide
    rings, res = land_rings(fr, spec)
    ras = Raster(w, h, rings)
    landd = "".join(d_of(r, True) for r in rings)
    o, A = [], None
    A = o.append

    A('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" role="img" aria-label="%s">' % (w, h, esc(title)))
    A('<!-- %s - generated by tools/genmaps.py (Natural Earth 1:%sm, public domain; art in tools/mapart.py). No scripts, no external assets. -->' % (esc(title), res))
    font = FONT_FA if lang == "fa" else FONT_EN
    A('<style>.lb{font-family:%s;fill:%s;letter-spacing:%s}.sl{font-family:%s;fill:%s;font-style:italic;letter-spacing:%s}'
      '.lb,.sl{paint-order:stroke fill;stroke:#06101a;stroke-width:3.6;stroke-linejoin:round}@media (prefers-reduced-motion:reduce){*{animation:none}}</style>'
      % (font, LAND_TEXT, "0" if lang == "fa" else ".16em", font, SEA_TEXT, "0" if lang == "fa" else ".16em"))
    A('<defs>')
    A('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (SEA, SEA2))
    A('<radialGradient id="shine" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#2a5a78" stop-opacity=".22"/><stop offset="1" stop-color="#2a5a78" stop-opacity="0"/></radialGradient>')
    A('<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9cb27a" stop-opacity=".16"/><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".34"/></linearGradient>')
    A('<radialGradient id="vign" cx="50%" cy="50%" r="75%"><stop offset="0.55" stop-color="#03050a" stop-opacity="0"/><stop offset="1" stop-color="#03050a" stop-opacity=".6"/></radialGradient>')
    A('<pattern id="wav" width="34" height="18" patternUnits="userSpaceOnUse"><path d="M0 10q8.5-10 17 0t17 0" fill="none" stroke="#4f86a6" stroke-width="1" opacity=".16"/></pattern>')
    A('<filter id="rough" filterUnits="userSpaceOnUse" x="-30" y="-30" width="%d" height="%d"><feTurbulence' % ((w + 60) // 2 * 2, (h + 60) // 2 * 2) + ''' type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.6" xChannelSelector="R" yChannelSelector="G"/></filter>''')
    A('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 .02  0 0 0 0 .03  0 0 0 0 .01  0 0 0 1.1 -.42"/></filter>')
    A('<path id="L" fill-rule="evenodd" clip-rule="evenodd" d="%s"/>' % landd)
    A('<clipPath id="lc"><use href="#L"/></clipPath><clipPath id="inner"><rect x="%d" y="%d" width="%d" height="%d" rx="3"/></clipPath>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    A(art.glyph_defs())
    A('</defs>')

    # sea
    A('<rect width="%d" height="%d" fill="url(#sea)"/><rect width="%d" height="%d" fill="url(#shine)"/>' % (w, h, w, h))
    A('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#wav)"/>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    A('<g clip-path="url(#inner)">')
    # graticule + rhumb lines
    g = spec["graticule"]
    gl = []
    lo = math.ceil(box[0] / g) * g
    while lo <= box[1]:
        gl.append("M%.1f %dV%d" % (fr.xy(lo, box[2])[0], pad, h - pad))
        lo += g
    la = math.ceil(box[2] / g) * g
    while la <= box[3]:
        gl.append("M%d %.1fH%d" % (pad, fr.xy(box[0], la)[1], w - pad))
        la += g
    A('<path d="%s" fill="none" stroke="#4a7692" stroke-width=".7" opacity=".3"/>' % "".join(gl))
    cx, cy = w - pad - 66, h - pad - 66
    A('<path d="%s" fill="none" stroke="%s" stroke-width=".7" opacity=".13"/>' % ("".join("M%d %dl%.0f %.0f" % (cx, cy, math.cos(k * math.pi / 8) * w, math.sin(k * math.pi / 8) * w) for k in range(16)), GOLD))

    # land (displaced together so every layer lines up)
    A('<g filter="url(#rough)">')
    for sw, op in ((22, .04), (15, .06), (9.5, .1), (5, .17)):          # shore ripples
        A('<use href="#L" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round" opacity="%s"/>' % (RIPPLE, sw, op))
    A('<use href="#L" fill="%s"/>' % LAND)
    A('<g clip-path="url(#lc)">')
    A('<rect width="%d" height="%d" fill="url(#shade)"/>' % (w, h))
    A('<rect width="%d" height="%d" filter="url(#grain)" opacity=".5"/>' % (w, h))
    A('<use href="#L" fill="none" stroke="#0a1208" stroke-width="12" opacity=".26"/>')    # inner shading rim
    # deserts, marsh, hills, forests
    dots = []
    glyphs = []
    for reg in spec.get("deserts", []):
        for x, y in scatter(rng, fr, reg, unit * .55, 520, ras, 0):
            dots.append("M%.1f %.1fh.01" % (x, y))
        for x, y in scatter(rng, fr, reg, unit * 2.2, 60, ras, 2):
            glyphs.append((y, "dn", x, gs * .95))
    if dots:
        A('<path d="%s" stroke="#a08c55" stroke-width="1.1" stroke-linecap="round" opacity=".5"/>' % "".join(dots))
    for reg in spec.get("marsh", []):
        for x, y in scatter(rng, fr, reg, unit * 1.2, 40, ras, 2):
            glyphs.append((y, "ms", x, gs * .9))
    for reg in spec.get("hills", []):
        for x, y in scatter(rng, fr, reg, unit * 1.7, 36, ras, 2):
            glyphs.append((y, "hl", x, gs * (.85 + rng.random() * .4)))
    for reg in spec.get("forests", []):
        for x, y in scatter(rng, fr, reg, unit * 1.15, 180, ras, 3):
            glyphs.append((y, rng.choice(("tp", "tp", "tp", "tr")), x, gs * (.75 + rng.random() * .3)))
    # lakes (carve over the land texture)
    lk, lres = pick_geo(spec.get("res", "50"), "lakes")
    if lk:
        ld = []
        for pr, poly in polys(lk):
            for ring in poly:
                if not any(box[0] - 2 < p[0] < box[1] + 2 and box[2] - 2 < p[1] < box[3] + 2 for p in ring[::6]):
                    continue
                pts = clip_poly([fr.xy(lo, la) for lo, la in ring], -20, -20, w + 20, h + 20)
                pts = simplify_ring(pts, .4)
                if len(pts) >= 3:
                    ld.append(d_of(pts, True))
        if ld:
            A('<path d="%s" fill="%s" stroke="#0a1208" stroke-width="2.4" opacity=".95"/><path d="%s" fill="none" stroke="%s" stroke-width=".9"/>' % ("".join(ld), SEA, "".join(ld), GOLD))
    # rivers
    for pts, wd in river_paths(fr, spec):
        d = d_of(smooth(pts))
        A('<path d="%s" fill="none" stroke="#06141c" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>' % (d, wd + 1.8))
        A('<path d="%s" fill="none" stroke="#6fb4d6" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round"/>' % (d, wd))
    for r in spec.get("ranges", []):
        glyphs += mountains(rng, fr, r, unit, ras, gs)
    glyphs.sort()
    A("".join('<use href="#%s" transform="translate(%.1f %.1f) scale(%.2f)"/>' % (gid, x, y, s) for y, gid, x, s in glyphs))
    A('</g>')
    # coastline: ink under gold
    A('<use href="#L" fill="none" stroke="#050a07" stroke-width="3.4" stroke-linejoin="round"/><use href="#L" fill="none" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/>' % GOLD)
    A('</g>')                                                          # /rough
    A('</g>')                                                          # /inner

    cart, tw = cartouche(pad + 18, pad + 14, title, lang)
    # things that occupy space (labels avoid them)
    S0 = w / 1200
    blocked = []
    for _, lo, la in PINS.get(name, []):
        x, y = fr.xy(lo, la)
        blocked.append((x - 22, y - 30, x + 22, y + 12))
    blocked += [(w - pad - 112, h - pad - 112, w - pad, h - pad), (pad, h - pad - 70, pad + 0.2 * w, h - pad), (pad, pad, pad + tw + 60, pad + 66)]

    # ships and monsters
    deco = []
    for kind, lo, la, s, flip in spec.get("ships", []):
        x, y = fr.xy(lo, la)
        S = s * 1.1 * S0 * spec.get("cs", 1.0)
        deco.append(art.creature(kind, x, y, S, bool(flip), .9))
        blocked.append((x - 34 * S, y - 28 * S, x + 34 * S, y + 14 * S))
    for kind, lo, la, s, flip, label in spec.get("creatures", []):
        kind = VARIANT.get(label, kind)
        x, y = fr.xy(lo, la)
        S = s * 1.15 * S0 * spec.get("cs", 1.0)
        deco.append(art.creature(kind, x, y, S, bool(flip), .94))
        blocked.append((x - 30 * S, y - 28 * S, x + 30 * S, y + 22 * S))
        if label:
            txt = label if lang == "en" else FA.get(label, label)
            deco.append('<text class="lb" x="%.0f" y="%.0f" font-size="%d" text-anchor="middle" opacity=".92">%s</text>' % (x, y + 30 * S + 12, 11 + int(S0), esc(txt)))
            blocked.append((x - 46, y + 30 * S - 2, x + 46, y + 30 * S + 16))
    A("".join(deco))

    # labels: curved baseline, halo, collision-avoiding
    placed, lab_defs, lab_txt = [], [], []
    for i, (text, lo, la, size, kind, rot) in enumerate(sorted(spec["labels"], key=lambda L: -L[3])):
        label = text if lang == "en" else FA.get(text, text)
        wp, hp = est_w(label, size, lang), size * 1.15
        x0, y0 = fr.xy(lo, la)
        best = None
        offs = sorted([(dx * wp * .45, dy * hp) for dx in (-1.6, -.8, 0, .8, 1.6) for dy in (-2, -1, 0, 1, 2)], key=lambda t: abs(t[0]) * .5 + abs(t[1]))
        for dx, dy in offs:
            x = min(max(x0 + dx, pad + wp / 2 + 10), w - pad - wp / 2 - 10)
            y = min(max(y0 + dy, pad + hp + 6), h - pad - hp - 6)
            th = math.radians(rot)
            bw, bh = abs(wp * math.cos(th)) + abs(hp * math.sin(th)), abs(wp * math.sin(th)) + abs(hp * math.cos(th))
            bb = (x - bw / 2, y - bh / 2 - 2, x + bw / 2, y + bh / 2)
            if not any(overlap(bb, q) for q in blocked + placed):
                best = (x, y, bb)
                break
        if best is None:
            best = (x0, y0, (x0 - wp / 2, y0 - hp, x0 + wp / 2, y0))
        x, y, bb = best
        placed.append(bb)
        th = math.radians(rot)
        L = wp / 2 + 14
        ux, uy = math.cos(th), math.sin(th)
        k = L * (.085 if kind == "r" else -.07)
        lab_defs.append('<path id="lp%d" d="M%.1f %.1fQ%.1f %.1f %.1f %.1f" fill="none"/>' % (i, x - ux * L, y - uy * L, x + uy * k, y - ux * k, x + ux * L, y + uy * L))
        cls = "lb" if kind == "r" else "sl"
        lab_txt.append('<text class="%s" font-size="%d" text-anchor="middle"><textPath href="#lp%d" startOffset="50%%">%s</textPath></text>' % (cls, size, i, esc(label)))
    A("<defs>%s</defs>" % "".join(lab_defs))
    A("".join(lab_txt))

    # frame, ladder, corners
    A('<rect width="%d" height="%d" fill="url(#vign)"/>' % (w, h))
    A('<rect x="7" y="7" width="%d" height="%d" fill="none" stroke="%s" stroke-width="1.6" rx="5"/>' % (w - 14, h - 14, GOLD))
    A(ladder(fr, g))
    A('<rect x="13" y="13" width="%d" height="%d" fill="none" stroke="%s" stroke-width="1" rx="3"/>' % (w - 26, h - 26, GOLD))
    A('<g fill="%s">%s</g>' % (GOLD, "".join('<path d="M%d %dl4 -9l4 9l-4 9z" transform="translate(%d %d)" opacity=".85"/>' % (-4, 0, x, y) for x, y in ((20, 20), (w - 20, 20), (20, h - 20), (w - 20, h - 20)))))
    A(cart)
    A(compass(w - pad - 56, h - pad - 56, lang))
    # scale bar
    ref_lat = (box[2] + box[3]) / 2
    km = nice_km(0.15 * (w - 2 * pad), fr.px, ref_lat)
    bar = km / (111.0 * math.cos(math.radians(ref_lat))) * fr.px
    sx, sy = pad + 26, h - pad - 30
    A('<g transform="translate(%.0f %.0f)" opacity=".92"><rect x="-3" y="-20" width="%.0f" height="34" rx="4" fill="#070b11" fill-opacity=".7"/>' % (sx, sy, bar + 6))
    for i in range(4):
        A('<rect x="%.1f" width="%.1f" height="4" fill="%s" stroke="%s" stroke-width=".6"/>' % (bar / 4 * i, bar / 4, GOLD if i % 2 == 0 else "#070b11", GOLD))
    A('<text class="lb" x="%.0f" y="-7" font-size="11" text-anchor="middle">%s</text></g>' % (bar / 2, ("%d km" % km) if lang == "en" else ("%d کیلومتر" % km)))
    A('</svg>')
    svg = "\n".join(o)
    out = os.path.join(OUT, name + ("" if lang == "en" else "-fa") + ".svg")
    with open(out, "w") as f:
        f.write(svg)
    import xml.dom.minidom as m
    m.parseString(svg)
    return out, len(svg), (w, h), res


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:]
    for name, spec in MAPS.items():
        if only and name not in only:
            continue
        for lang in ("en", "fa"):
            out, size, dim, res = build(name, spec, lang)
            print("%-34s %7d B  %-10s 1:%sm" % (os.path.relpath(out, ROOT), size, dim, res))
    print("\nreference pin coordinates (% of map box; unchanged by the new art):")
    for name, items in PINS.items():
        if only and name not in only:
            continue
        print(" ", name)
        for label, lon, lat in items:
            x, y = pct(lon, lat, MAPS[name]["box"])
            print("    %-14s x=%.1f%% y=%.1f%%" % (label, x, y))
