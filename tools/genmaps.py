#!/usr/bin/env python3
"""Generate the stylised map artwork in static/img/maps/.

    python3 tools/genmaps.py

Geography comes from the Natural Earth 1:110m land / rivers data (public domain,
stored in tools/geo/).  Everything else - palette, cartouche, compass, mountain
hatches, labels - is the house art direction: dark sea, olive land, gold
coastline, no external assets.

Outputs (for each map: <name>.svg in English and <name>-fa.svg in Farsi):
    world  middle-east  persia  india  aegean  scandinavia

Run this again after editing the MAPS table; it only rewrites those files.
Nothing else in the repo is touched.
"""
import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.path.join(ROOT, "tools", "geo", "ne_110m_land.geojson")
OUT = os.path.join(ROOT, "static", "img", "maps")

GOLD = "#c9a45c"
LAND = "#26331f"
LAND2 = "#171d12"
SEA = "#101c28"
SEA2 = "#070d15"
TEXT = "#d8c9a8"
SEA_TEXT = "#7fa3bd"

# ---------------------------------------------------------------- projections


def project(lon, lat, box, w, h, pad):
    lon0, lon1, lat0, lat1 = box
    x = pad + (lon - lon0) / (lon1 - lon0) * (w - 2 * pad)
    y = pad + (lat1 - lat) / (lat1 - lat0) * (h - 2 * pad)
    return x, y


def pct(lon, lat, box):
    """Pin position in % of the map box (what the map shortcode wants)."""
    lon0, lon1, lat0, lat1 = box
    return (lon - lon0) / (lon1 - lon0) * 100, (lat1 - lat) / (lat1 - lat0) * 100


# ---------------------------------------------------------------- geometry


def ring_path(ring, box, w, h, pad, copies=(-360, 0, 360)):
    """Path for one ring; drawn 3x so anything crossing the antimeridian stays joined."""
    d = []
    for shift in copies:
        pts = []
        for lon, lat in ring:
            x, y = project(lon + shift, lat, box, w, h, pad)
            pts.append("%.1f %.1f" % (x, y))
        if pts:
            d.append("M" + "L".join(pts) + "Z")
    return "".join(d)


def poly_path(points, box, w, h, pad, close=False):
    pts = [project(lon, lat, box, w, h, pad) for lon, lat in points]
    d = "M" + "L".join("%.1f %.1f" % p for p in pts)
    return d + ("Z" if close else "")


def chevrons(points, box, w, h, pad, step=16):
    """Mountain hatch: little peaks walked along a lon/lat line."""
    out = []
    total = 0.0
    acc = 0.0
    prev = None
    for lon, lat in points:
        p = project(lon, lat, box, w, h, pad)
        if prev:
            seg = math.hypot(p[0] - prev[0], p[1] - prev[1])
            total += seg
        prev = p
    prev = None
    for lon, lat in points:
        p = project(lon, lat, box, w, h, pad)
        if prev:
            seg = math.hypot(p[0] - prev[0], p[1] - prev[1])
            dx, dy = (p[0] - prev[0]) / (seg or 1), (p[1] - prev[1]) / (seg or 1)
            while acc < seg:
                t = acc / (seg or 1)
                x = prev[0] + dx * acc
                y = prev[1] + dy * acc
                nx, ny = -dy, dx  # perpendicular
                s = 4.6
                out.append("M%.1f %.1fL%.1f %.1fL%.1f %.1f" % (
                    x - nx * s + dx * 0.5, y - ny * s + dy * 0.5,
                    x + dx * s, y + dy * s,
                    x + nx * s + dx * 0.5, y + ny * s + dy * 0.5))
                acc += step
            acc -= seg
        prev = p
    return "".join(out)


# ---------------------------------------------------------------- the maps

MAPS = {
    # name: box(lon0, lon1, lat0, lat1), titles, labels, ranges, rivers
    "world": dict(
        box=(-135, 225, -58, 84), w=1700, center=20,
        title={"en": "The World", "fa": "جهان"},
        labels=[
            ("NORTH AMERICA", -84, 44, 21, "r", 0),
            ("SOUTH AMERICA", -52, -12, 21, "r", 0),
            ("EUROPA", 14, 50, 19, "r", 0),
            ("AFRICA", 20, 4, 21, "r", 0),
            ("ASIA", 100, 48, 22, "r", 0),
            ("ARABIA", 45, 22, 15, "r", 0),
            ("PERSIA", 54, 32, 15, "r", 0),
            ("INDIA", 79, 22, 16, "r", 0),
            ("CHINA", 108, 33, 17, "r", 0),
            ("SCYTHIA", 60, 52, 15, "r", 0),
            ("SIBERIA", 100, 65, 17, "r", 0),
            ("AUSTRALIA", 134, -25, 17, "r", 0),
            ("GREENLAND", -42, 72, 14, "r", 0),
            ("ATLANTIC OCEAN", -32, 18, 16, "s", 0),
            ("INDIAN OCEAN", 76, -26, 16, "s", 0),
            ("PACIFIC OCEAN", 148, 2, 16, "s", 0),
            ("ARCTIC OCEAN", 100, 78, 15, "s", 0),
            ("MEDITERRANEAN SEA", 17, 34.5, 13, "s", 0),
            ("AMAZONIA", -62, -5, 13, "r", 0),
        ],
        ranges=[],
        rivers=[
            # Nile
            [(31, 30.5), (31.5, 27), (32.5, 23), (33.5, 18), (34, 13), (33, 8), (32, 2), (30, -1)],
            # Amazon
            [(-73, -4), (-68, -4), (-64, -5), (-60, -4), (-56, -3), (-52, -2), (-50, 0)],
            # Congo
            [(28, -6), (24, -4), (20, -3), (17, -4), (15, -6), (13, -6), (12, -6)],
            # Mississippi
            [(-95, 47), (-96, 43), (-95, 38), (-92, 34), (-91, 31), (-89, 29)],
            # Danube
            [(9, 48), (14, 47), (18, 46), (21, 45), (25, 45), (29, 45)],
            # Rhine
            [(9, 47), (8, 45), (7, 43), (6, 41)],
            # Volga
            [(37, 57), (40, 55), (44, 52), (47, 48), (48, 46), (48, 45)],
            # Ganges
            [(78, 30), (81, 26), (85, 25), (88, 24), (90, 23)],
            # Indus
            [(73, 34), (71, 31), (69, 27), (67, 24)],
            # Yangtze
            [(97, 32), (102, 29), (106, 29), (110, 30), (114, 31), (119, 32), (122, 31)],
            # Yellow
            [(96, 35), (101, 36), (106, 35), (110, 35), (114, 37), (118, 38), (119, 37)],
            # Ob
            [(75, 52), (73, 57), (70, 62), (68, 66), (69, 70)],
            # Yenisei
            [(92, 52), (88, 57), (85, 62), (83, 68), (82, 72)],
            # Lena
            [(108, 53), (112, 58), (116, 63), (122, 68), (127, 72)],
            # Paraná
            [(-50, -18), (-53, -22), (-56, -27), (-58, -31), (-59, -34)],
            # Murray
            [(147, -36), (144, -34), (141, -33), (139, -34), (137, -35)],
        ],
        # mythical beasts (decorative - the world sheet stays unlabelled)
        creatures=[
            ("serpent", -38, 8, 2.1, 0),
            ("dragon", 76, 59, 1.9, 1),
            ("bird", 80, -10, 1.8, 0),
        ],
        graticule=30,
    ),
    "middle-east": dict(
        box=(26, 60, 23, 41), w=1200, center=32,
        title={"en": "Mesopotamia and the Levant", "fa": "بین‌النهرین و شام"},
        labels=[
            ("ANATOLIA", 32, 38.5, 17, "r", 0),
            ("LEVANT", 36.6, 34.6, 15, "r", 0),
            ("MESOPOTAMIA", 43.6, 34.4, 17, "r", 0),
            ("ARABIA", 44, 27.5, 17, "r", 0),
            ("PERSIA", 54.5, 32, 16, "r", 0),
            ("MEDITERRANEAN SEA", 31.5, 34.4, 13, "s", 0),
            ("BLACK SEA", 36.5, 41.4, 12, "s", 0),
            ("CASPIAN SEA", 51, 38, 13, "s", 0),
            ("RED SEA", 35.5, 26, 13, "s", 0),
            ("PERSIAN GULF", 49.5, 28.2, 13, "s", -18),
            ("AEGEAN", 25.5, 37.6, 12, "s", 0),
        ],
        ranges=[
            [(29, 37.4), (33, 37.6), (37, 37)],
            [(44.5, 37.5), (46.5, 33.5), (49, 31), (53, 28), (56, 27)],
            [(49, 36.6), (52, 36.4), (55.5, 36.6)],
        ],
        rivers=[
            # Tigris
            [(38.6, 37.5), (40.5, 36.6), (42.5, 35), (44, 33.2), (45.4, 31.6), (47, 30.6), (48, 30.1)],
            # Euphrates
            [(38.2, 38.4), (40.5, 37.4), (42.6, 36.2), (43.5, 34.6), (44.6, 33), (45.6, 31.6), (47.4, 30.7)],
            # Nile
            [(31.2, 30.6), (31.6, 28.5), (32.6, 26), (33.6, 24), (34.4, 23)],
            # Jordan
            [(35.7, 32.7), (35.6, 31.7), (35.5, 31.2)],
            # Karun
            [(47, 32.5), (48.5, 31.6), (49.5, 30.5)],
        ],
        creatures=[
            ("guardian", 36.05, 36.25, 1.55, 0, "HUMBABA"),   # the Amanus cedar belt
            ("dragon", 45.6, 32.9, 1.5, 0, "MUSHUSSU"),       # Babylon's gate-dragon
            ("bird", 47.6, 31.0, 1.45, 0, "ANZU"),
        ],
        graticule=5,
    ),
    "persia": dict(
        box=(42, 72, 24, 40), w=1200, center=32,
        title={"en": "The Iranian Plateau", "fa": "فلات ایران"},
        labels=[
            ("MEDIA", 48.6, 35.2, 15, "r", 0),
            ("PERSIA", 54, 32.6, 17, "r", 0),
            ("PARTHIA", 58.6, 36.4, 15, "r", 0),
            ("ARIA", 64, 33.4, 14, "r", 0),
            ("KAVIR DESERT", 55.5, 34.4, 12, "r", -12),
            ("CASPIAN SEA", 51, 37.6, 13, "s", 0),
            ("PERSIAN GULF", 49.8, 29.4, 13, "s", -30),
            ("GULF OF OMAN", 58.5, 25.4, 13, "s", 0),
            ("ARABIAN SEA", 65, 25.4, 13, "s", 0),
            ("TRANSOXIANA", 64, 38.4, 13, "r", 0),
        ],
        ranges=[
            [(48.8, 36.4), (52, 36.2), (55.5, 36.5)],
            [(45, 36.5), (46.8, 33), (49.5, 30.5), (53, 28), (56, 26.8)],
            [(58, 38.4), (61.5, 37.4)],
            [(64, 35.5), (68, 35.2), (71, 35.5)],
        ],
        rivers=[
            # Atrek
            [(54, 37.4), (56, 38), (58, 38.2)],
            # Helmand
            [(65, 33.6), (63, 31.4), (61.4, 29.6), (60.6, 28.4)],
            # Karun
            [(46.6, 33.4), (48, 32.4), (49.4, 30.6)],
            # Indus (upper)
            [(72, 34.4), (71.4, 33), (71, 31.6)],
            # Zayandeh (Isfahan)
            [(49.6, 33.4), (51.6, 32.4), (53, 32.2)],
        ],
        creatures=[
            ("bird", 52.6, 36.7, 1.9, 0, "SIMORGH"),          # over the Alborz
            ("dragon", 46.3, 33.6, 1.7, 1, "DAHAKA"),          # the Zagros worm
            ("demon", 63.5, 30.6, 1.5, 1, "DAEVA"),
        ],
        graticule=5,
    ),
    "india": dict(
        box=(64, 104, 5, 34), w=1200, center=32,
        title={"en": "India and the Indus", "fa": "هند و سند"},
        labels=[
            ("INDIA", 78, 22.4, 20, "r", 0),
            ("HIMALAYA", 79, 31.6, 14, "r", -6),
            ("THAR DESERT", 71.4, 27, 13, "r", -20),
            ("DECCAN", 77, 17.6, 14, "r", 0),
            ("BENGAL", 89.4, 23, 13, "r", 0),
            ("ARABIAN SEA", 71.4, 15, 14, "s", -12),
            ("BAY OF BENGAL", 87, 15.4, 14, "s", -14),
            ("INDIAN OCEAN", 80, 7, 14, "s", 0),
        ],
        ranges=[
            [(72, 33.4), (76, 32.4), (80, 30.4), (84, 28.4), (88, 27), (92, 27)],
            [(74, 27), (75.6, 24.4), (76.6, 22.6)],
            [(73.4, 20), (75, 15), (76.4, 11)],
            [(79.4, 19.4), (82, 17.6), (84.4, 17)],
        ],
        rivers=[
            # Indus
            [(72.4, 34), (71.4, 31), (70, 28), (68.4, 25.4), (67.4, 24)],
            # Ganges
            [(78.4, 30), (81, 26.4), (84.6, 25.4), (87.6, 24.4), (90, 23)],
            # Yamuna
            [(77.6, 30.4), (78.6, 27.4), (81, 26.4)],
            # Brahmaputra
            [(82, 29.4), (87, 27.4), (91, 27), (94.4, 27.4), (95.4, 25.4), (96, 24.4)],
            # Godavari
            [(78.4, 19.6), (81.4, 17.6), (84, 16.6), (87, 16.6)],
            # Krishna
            [(74.4, 17), (77.6, 16.4), (80.6, 15.6), (83.4, 15.6)],
        ],
        creatures=[
            ("bird", 80.2, 28.2, 1.8, 0, "GARUDA"),
            ("serpent", 86.8, 23.6, 1.7, 0, "NAGA"),           # the Ganges delta
            ("serpent", 73.5, 9.5, 1.6, 1, "MAKARA"),          # Arabian Sea
        ],
        graticule=5,
    ),
    "aegean": dict(
        box=(15, 39, 33.5, 45.5), w=1200, center=30,
        title={"en": "The Aegean", "fa": "دریای اژه"},
        labels=[
            ("GREECE", 21.6, 40.4, 16, "r", 0),
            ("ANATOLIA", 32.4, 38.6, 16, "r", 0),
            ("THRACE", 25.6, 42, 13, "r", 0),
            ("CRETE", 24.6, 35.3, 12, "r", 0),
            ("CYPRUS", 33.2, 35, 12, "r", 0),
            ("AEGEAN SEA", 25.2, 38.4, 14, "s", -20),
            ("IONIAN SEA", 18.4, 38, 13, "s", -14),
            ("MEDITERRANEAN SEA", 19, 34.4, 13, "s", 0),
            ("BLACK SEA", 33.6, 43.4, 13, "s", 0),
            ("SEA OF MARMARA", 28.4, 40.6, 11, "s", -16),
        ],
        ranges=[
            [(20.8, 40.4), (21.8, 39), (22.4, 38)],
            [(29.6, 37.6), (33, 37.4), (36, 36.6)],
            [(24.6, 41.6), (27, 41.4)],
            [(17.6, 43.6), (19.4, 42.6), (20.6, 41.6)],
        ],
        rivers=[
            # Danube (lower)
            [(21, 44.8), (23, 45), (25, 45.2), (27.4, 45), (29, 45.2)],
            # Menderes
            [(27.6, 38.4), (29, 37.6), (30.4, 37.4)],
            # Vardar
            [(21.6, 42.6), (21.4, 41.4), (21.6, 40.6)],
        ],
        creatures=[
            ("serpent", 16.4, 38.3, 1.35, 0, "SCYLLA"),        # the Messina strait
            ("serpent", 22.1, 39.1, 1.3, 1, "PYTHON"),         # Delphi's dragon
            ("minotaur", 25.9, 35.3, 1.3, 0, "MINOTAUR"),     # Knossos
            ("dragon", 29.9, 36.9, 1.25, 1, "CHIMERA"),        # Lycia
        ],
        graticule=5,
    ),
    "scandinavia": dict(
        box=(-24, 30, 51, 71), w=1350, center=0,
        title={"en": "The North", "fa": "سرزمین شمال"},
        labels=[
            ("SCANDINAVIA", 13.6, 62.4, 17, "r", -16),
            ("FINLAND", 26, 63.4, 15, "r", 0),
            ("ICELAND", -19, 65.2, 14, "r", 0),
            ("DENMARK", 9.2, 56.2, 13, "r", 0),
            ("BRITAIN", -3.4, 54.4, 14, "r", -16),
            ("GALLIA", 3.4, 51.6, 13, "r", 0),
            ("BALTIC SEA", 19.4, 57.4, 13, "s", -14),
            ("NORTH SEA", 1.4, 55.6, 13, "s", -14),
            ("NORWEGIAN SEA", -3, 66.6, 13, "s", -34),
            ("KARELIA", 30, 64.4, 12, "r", 0),
        ],
        ranges=[
            [(5.6, 59.4), (7.6, 61.4), (11, 64), (14.6, 66.4), (17, 68.6)],
            [(-20, 64.6), (-17.6, 65.6)],
            [(-4.6, 56.6), (-3, 54.6)],
        ],
        rivers=[
            # Glomma
            [(10.4, 59.6), (11, 60.6), (11.6, 61.4)],
            # Kemi
            [(24.4, 67.6), (24.8, 66), (25.4, 65.4)],
            # Vistula
            [(17.6, 51), (18.6, 52.6), (19, 54)],
            # Neva
            [(30, 60.6), (28.6, 60.4), (27.4, 60.4)],
        ],
        creatures=[
            ("serpent", 3.6, 58.6, 1.75, 0, "JORMUNGANDR"),    # the Skagerrak
            ("wolf", 14.5, 60.3, 1.55, 1, "FENRIR"),
            ("dragon", 23, 66.5, 1.6, 0, "NIDHOGG"),
        ],
        graticule=5,
    ),
}

FA = {
    "NORTH AMERICA": "آمریکای شمالی", "SOUTH AMERICA": "آمریکای جنوبی", "EUROPA": "اروپا",
    "AFRICA": "آفریقا", "ASIA": "آسیا", "ARABIA": "عربستان", "PERSIA": "ایران",
    "INDIA": "هند", "CHINA": "چین", "SCYTHIA": "سکاستان", "SIBERIA": "سیبری",
    "AUSTRALIA": "استرالیا", "GREENLAND": "گرینلند", "ATLANTIC OCEAN": "اقیانوس اطلس",
    "INDIAN OCEAN": "اقیانوس هند", "PACIFIC OCEAN": "اقیانوس آرام", "ARCTIC OCEAN": "اقیانوس منجمد شمالی",
    "MEDITERRANEAN SEA": "دریای مدیترانه", "AMAZONIA": "آمازونیا",
    "ANATOLIA": "آناتولی", "LEVANT": "شام", "MESOPOTAMIA": "بین‌النهرین",
    "BLACK SEA": "دریای سیاه", "CASPIAN SEA": "دریای خزر", "RED SEA": "دریای سرخ",
    "PERSIAN GULF": "خلیج فارس", "AEGEAN": "اژه", "MEDIA": "ماد", "PARTHIA": "پارت",
    "ARIA": "رخج", "KAVIR DESERT": "کویر", "TRANSOXIANA": "ماوراءالنهر",
    "GULF OF OMAN": "دریای عمان", "ARABIAN SEA": "دریای عرب",
    "HIMALAYA": "هیمالیا", "THAR DESERT": "صحرای تار", "DECCAN": "دکن",
    "BENGAL": "بنگال", "BAY OF BENGAL": "خلیج بنگال", "INDIAN OCEAN ": "اقیانوس هند",
    "GREECE": "یونان", "THRACE": "تراکیه", "CRETE": "کرت", "CYPRUS": "قبرس",
    "IONIAN SEA": "دریای یونان", "SEA OF MARMARA": "دریای مرمره",
    "SCANDINAVIA": "اسکاندیناوی", "FINLAND": "فنلاند", "ICELAND": "ایسلند",
    "DENMARK": "دانمارک", "BRITAIN": "بریتانیا", "GALLIA": "گل",
    "BALTIC SEA": "دریای بالتیک", "NORTH SEA": "دریای شمال", "NORWEGIAN SEA": "دریای نروژ",
    "KARELIA": "کارلیا",
    # mythical creatures
    "SIMORGH": "سیمرغ", "DAHAKA": "ضحاک", "DAEVA": "دیو", "HUMBABA": "همبابا",
    "MUSHUSSU": "موشووشو", "ANZU": "آنزو", "GARUDA": "گارودا", "NAGA": "ناگا",
    "MAKARA": "ماکارا", "SCYLLA": "اسکیلا", "PYTHON": "پیتون", "MINOTAUR": "مینوتور",
    "CHIMERA": "کیمرا", "JORMUNGANDR": "یورمونگاندر", "FENRIR": "فنریر",
    "NIDHOGG": "نیدهوگر",
}

# ---------------------------------------------------------------- creature art
# "Here be monsters": thin antique-engraving line art, centred on the origin and
# facing +x, drawn in a ~28-unit box; placed per MAPS["creatures"] entry.
# Fine strokes (0.7-1.35 units) over open outlines with interior detail — belly
# scutes, feather ribs, horn ridges, facial lines — so the beasts read crisply
# against both sea and land at map scale.
CREATURE_ART = {
    "serpent": "".join([
        # coiling body: outer then inner edge converging into a fluked tail
        '<path d="M-13.8 4.4C-11.6 -2 -7 -4.4 -4.4 .6C-1.8 -4 2.6 -5 5 -.8C7 -4 9.6 -7.4 12 -10" fill="none" stroke="%s" stroke-width="1.35" stroke-linecap="round"/>' % GOLD,
        '<path d="M-13.8 4.4C-12.2 -.4 -7.8 -2.6 -5 1.8C-2.4 -2.4 1.8 -3.2 4.2 1C6.2 -1.8 9 -5.2 11.2 -8.2" fill="none" stroke="%s" stroke-width="1.05" stroke-linecap="round"/>' % GOLD,
        '<path d="M-13.8 4.4L-16 2.4L-15.8 5.8Z" fill="none" stroke="%s" stroke-width=".9" stroke-linejoin="round"/>' % GOLD,
        # belly scutes across the ribbon
        '<path d="M-12.2 2.6l.8 2.2M-9.4 -.6l.7 2.1M-6.2 -1.8l.7 2.2M-2.6 1.6l.8 2.2M.8 -1l.7 2.2M4 1l.7 2M7.2 -3.4l.6 2.1M10 -7.6l.5 2" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        # dorsal fins on the wave crests
        '<path d="M-9.6 -1.7L-8.5 -5.1L-6.5 -3.2ZM-2.2 -3.5L-1.1 -6.9L.9 -4.9ZM4.5 -3.4L5.7 -6.2L7.4 -4.5Z" fill="none" stroke="%s" stroke-width=".8" stroke-linejoin="round"/>' % GOLD,
        # raised head: open jaws, teeth, forked tongue, eye
        '<path d="M11.4 -9.6C12.6 -11.6 14.4 -13 16.2 -13L16.6 -12.3L13.8 -11.5" fill="none" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>' % GOLD,
        '<path d="M11.2 -8.2C12 -9.4 12.8 -10.4 13.8 -11.5L16.4 -11.9" fill="none" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>' % GOLD,
        '<path d="M15.4 -12.4l.1 .9M14.4 -12l.1 .8" fill="none" stroke="%s" stroke-width=".6" stroke-linecap="round"/>' % GOLD,
        '<path d="M16.5 -12.2l1.9 -.7m-1.9 .7l2 .8" fill="none" stroke="%s" stroke-width=".65" stroke-linecap="round"/>' % GOLD,
        '<circle cx="13.3" cy="-11.9" r=".6" fill="%s"/>' % GOLD,
    ]),
    "dragon": "".join([
        # far wing, near wing, body, legs, neck, head, tail
        '<path d="M4.2 -5C4 -8.2 2.6 -11.4 0 -14.2C.6 -12.2 1 -11 1.6 -10C.6 -9.8 -.2 -9.4 -.8 -8.8C.2 -7.6 1 -6 1.4 -4.6C2.2 -4.6 3.4 -4.7 4.2 -5Z" fill="none" stroke="%s" stroke-width="1" stroke-linejoin="round"/>' % GOLD,
        '<path d="M1.6 -5.2C.4 -8.8 -2 -12.4 -5.4 -15C-4.6 -13 -4 -11.8 -3.4 -10.6C-4.6 -10.6 -5.6 -10.2 -6.4 -9.6C-5 -8.4 -3.8 -6.8 -3 -5C-2.6 -4.4 -2.2 -4 -1.6 -3.6C-.4 -4 .6 -4.6 1.6 -5.2Z" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M.6 -5.4C-1.2 -7.6 -2.6 -9.6 -3.4 -10.6M.2 -5.8C-1.4 -6.6 -2.6 -7.2 -3.6 -7.6" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        '<path d="M-4.4 -1.8C-4.4 -4 -1.6 -5.4 1.8 -5.4C5.2 -5.4 7.6 -4 7.6 -1.8C7.6 .4 5.2 1.8 1.8 1.8C-1.6 1.8 -4.4 .4 -4.4 -1.8Z" fill="none" stroke="%s" stroke-width="1.25"/>' % GOLD,
        '<path d="M-2 -.6q1 .9 .6 2M.4 -1q1 .9 .6 2M2.8 -.8q1 .9 .6 2" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        '<path d="M4.4 1.6C4.6 3.4 4.8 4.8 4.8 6.2L4.4 7.2L6.2 7.2L6.2 6C6.2 4.6 6 3.2 5.6 1.8" fill="none" stroke="%s" stroke-width="1" stroke-linejoin="round"/>' % GOLD,
        '<path d="M5.6 1.4C6.2 3.6 6.4 5.4 6.4 6.8L6 7.9L8 7.9L8 6.6C8 5 7.8 3.2 7.2 1.6" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M-4.4 1.2C-4.2 3 -4 4.4 -4 5.8L-4.4 6.9L-2.6 6.9L-2.6 5.8C-2.6 4.4 -2.8 3 -3.2 1.4" fill="none" stroke="%s" stroke-width="1" stroke-linejoin="round"/>' % GOLD,
        '<path d="M-3.2 1.2C-2.8 3.4 -2.6 5.2 -2.6 6.8L-3 7.9L-1 7.9L-1 6.6C-1 5 -1.2 3.2 -1.6 1.4" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M6.8 -4.2C8 -6.6 9.6 -8.8 11.4 -10.6" fill="none" stroke="%s" stroke-width="1.3" stroke-linecap="round"/>' % GOLD,
        '<path d="M7.5 -2.6C8.6 -4.6 9.8 -6.4 11.4 -7.8" fill="none" stroke="%s" stroke-width="1.1" stroke-linecap="round"/>' % GOLD,
        '<path d="M11.4 -10.6C12.5 -12 14.2 -12.9 15.8 -12.6L16.3 -11.7L13 -10.8" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M11.4 -7.8C12 -9 12.4 -10 13 -10.8L15.9 -11.2" fill="none" stroke="%s" stroke-width="1.1" stroke-linejoin="round"/>' % GOLD,
        '<path d="M15.1 -11.5l.1 .8M14 -11.2l.1 .7" fill="none" stroke="%s" stroke-width=".6" stroke-linecap="round"/>' % GOLD,
        '<path d="M12.6 -12.3C12.2 -13.4 11.6 -14.2 10.8 -14.8M14.2 -12.4C14.2 -13.5 14 -14.3 13.6 -15" fill="none" stroke="%s" stroke-width=".85" stroke-linecap="round"/>' % GOLD,
        '<circle cx="13.2" cy="-11.5" r=".55" fill="%s"/>' % GOLD,
        '<path d="M-4.4 -.6C-7 0 -9.6 1.6 -11.6 4M-4 .8C-6.4 1.6 -8.6 3 -10.4 5.6" fill="none" stroke="%s" stroke-width="1.15" stroke-linecap="round"/>' % GOLD,
        '<path d="M-11.6 4L-14.6 4.8L-10.4 5.6Z" fill="none" stroke="%s" stroke-width="1" stroke-linejoin="round"/>' % GOLD,
    ]),
    "bird": "".join([
        # feathered wings swept up in a V, drawn as blades with feather ribs
        '<path d="M-2.6 -3.6C-6 -6 -9.8 -8.6 -13.4 -10.8C-11.8 -7.6 -8.8 -5 -5.4 -3.8C-4.6 -3.6 -3.4 -3.5 -2.6 -3.6Z" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M-4.2 -4.4C-7 -6.3 -10 -8.4 -12.5 -10.3M-5.6 -4.6C-8 -6.2 -10.4 -8 -12.4 -9.6" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        '<path d="M2.4 -3.8C5.8 -6.2 9.6 -8.8 13.4 -11C11.8 -7.8 8.8 -5.2 5.4 -4C4.6 -3.8 3.4 -3.7 2.4 -3.8Z" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M4 -4.6C6.8 -6.5 9.8 -8.6 12.5 -10.5M5.4 -4.8C7.8 -6.4 10.2 -8.2 12.4 -9.8" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        # body with turned head and hooked beak
        '<path d="M-.8 -4.6C-3 -3 -3.8 .4 -2.8 3.6C-2 6 .4 6.8 2.2 5.2C4.2 3.4 4.4 -.4 3 -3.2C2.2 -4.6 .2 -5.6 -.8 -4.6Z" fill="none" stroke="%s" stroke-width="1.25" stroke-linejoin="round"/>' % GOLD,
        '<path d="M.4 -5C.2 -6.8 1.4 -8.2 3.2 -8.4L6.6 -8.8L5.9 -7.9L5.2 -7.6L5.8 -6.7L3.8 -6.3C2.6 -6 1.4 -5.6 .6 -5Z" fill="none" stroke="%s" stroke-width="1.1" stroke-linejoin="round"/>' % GOLD,
        '<circle cx="3.5" cy="-7.3" r=".55" fill="%s"/>' % GOLD,
        '<path d="M1.6 -8.6C1.2 -9.8 .6 -10.6 -.2 -11.3M2.4 -8.3C2.4 -9.6 2.3 -10.5 2 -11.4" fill="none" stroke="%s" stroke-width=".75" stroke-linecap="round"/>' % GOLD,
        # tail fan and talons
        '<path d="M-2 4.4L-5 10.6L.4 11.2L1.6 5.4Z" fill="none" stroke="%s" stroke-width="1.05" stroke-linejoin="round"/>' % GOLD,
        '<path d="M-.8 5L-2.6 10.8M.4 5.4L-.4 11.1" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        '<path d="M-1.4 5.6l-.6 2l-1.5 .6M.8 6l.5 2l1.6 .5" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
    ]),
    "wolf": "".join([
        # far legs sit behind the body
        '<path d="M-9 -3C-8.8 -.6 -8.7 1.6 -8.7 3.8L-8.9 6.6L-7 6.6L-7.1 4.2C-7.1 2.2 -7.3 .2 -7.6 -1.8" fill="none" stroke="%s" stroke-width="1" stroke-linejoin="round"/>' % GOLD,
        '<path d="M1.5 2.1C1.8 3.8 2 5.2 2 6.6L3.9 6.6L3.8 5.2C3.8 4 3.7 3 3.5 2.1" fill="none" stroke="%s" stroke-width="1" stroke-linejoin="round"/>' % GOLD,
        # body outline: nose, ears, ruff, back, tail, hind leg, belly, front leg, chest, jaw
        '<path d="M13.4 -3.6C13.9 -4.6 13.4 -5.5 12.6 -5.8L10.9 -6.2C9.9 -6.5 9.1 -6.9 8.6 -7.4L8.3 -10.6L7.1 -7.5L5.8 -10.2L5.3 -7.2C4.2 -7 3.2 -6.9 2.2 -7L1.4 -8.3L.7 -6.9L-.5 -7.9L-1 -6.7C-3.4 -6.3 -6 -5.9 -8 -5.2C-9.4 -4.8 -10.2 -4.3 -10.6 -3.7C-12.4 -4.4 -14 -5.8 -14.8 -7.8C-13.6 -7.1 -12.5 -6.6 -11.4 -6.4C-11.5 -5.5 -11.2 -4.6 -10.6 -3.9C-9.2 -3.4 -8.4 -2 -8 -.4C-7.6 2 -7.4 4.6 -7.4 6.6L-7.6 7.8L-5.4 7.8L-5.7 6.4C-5.6 4.6 -5.3 3 -4.8 1.6C-3.6 1.9 -2.4 2.1 -1.2 2.2C0 2.3 1.4 2.3 2.4 2.1C2.9 3.8 3.1 5.4 3.1 6.5L2.9 7.8L5.1 7.8L5.2 6.4C5.2 4.6 5.4 3 5.8 1.6C6.8 .6 7.8 -.8 8.6 -2.2C9.2 -2.9 9.9 -3.4 10.7 -3.7C11.6 -3.9 12.5 -3.9 13.2 -3.8Z" fill="none" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>' % GOLD,
        # snarling mouth with fangs
        '<path d="M12.8 -4.2C11.6 -4.6 10.6 -4.8 9.8 -4.7" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        '<path d="M12.1 -4.5l.1 1.2M11 -4.8l.1 .9" fill="none" stroke="%s" stroke-width=".65" stroke-linecap="round"/>' % GOLD,
        # eye, nostril, inner ears, fur
        '<circle cx="11.2" cy="-5.3" r=".56" fill="%s"/>' % GOLD,
        '<circle cx="13" cy="-4.4" r=".4" fill="%s"/>' % GOLD,
        '<path d="M8.1 -9.6l-1 2M5.7 -9.3l-.9 1.9" fill="none" stroke="%s" stroke-width=".65" stroke-linecap="round"/>' % GOLD,
        '<path d="M3.6 -6.1l-.5 1.4M2.4 -6.5l-.4 1.4M-5.6 -3q1 1.4 .6 3M-4.2 -2.6q1 1.4 .6 2.8M-13.4 -7l1 .6M-12.4 -6.2l1 .5" fill="none" stroke="%s" stroke-width=".65" stroke-linecap="round"/>' % GOLD,
    ]),
    "demon": "".join([
        # horned bust: shoulders, collar, neck
        '<path d="M-8.6 10.6C-7.8 3.4 -4.6 .8 0 .8C4.6 .8 7.8 3.4 8.6 10.6" fill="none" stroke="%s" stroke-width="1.3" stroke-linecap="round"/>' % GOLD,
        '<path d="M-2.4 1L-2.6 -1.6M2.4 1L2.6 -1.6" fill="none" stroke="%s" stroke-width="1.1" stroke-linecap="round"/>' % GOLD,
        '<path d="M-5 4.8C-3.2 4 3.2 4 5 4.8" fill="none" stroke="%s" stroke-width=".75" stroke-linecap="round"/>' % GOLD,
        '<circle cx="0" cy="6.6" r="1.15" fill="none" stroke="%s" stroke-width=".9"/>' % GOLD,
        # swept horns with ridge ticks
        '<path d="M-4.6 -8.8C-6.8 -10.2 -8.3 -12.8 -8.5 -15.2C-6.6 -13.2 -5 -11.6 -3.2 -10.5Z" fill="none" stroke="%s" stroke-width="1.1" stroke-linejoin="round"/>' % GOLD,
        '<path d="M-7.7 -13.6l1.6 .7M-6.6 -12.3l1.5 .6M-5.4 -11.2l1.4 .6" fill="none" stroke="%s" stroke-width=".65" stroke-linecap="round"/>' % GOLD,
        '<path d="M4.6 -8.8C6.8 -10.2 8.3 -12.8 8.5 -15.2C6.6 -13.2 5 -11.6 3.2 -10.5Z" fill="none" stroke="%s" stroke-width="1.1" stroke-linejoin="round"/>' % GOLD,
        '<path d="M7.7 -13.6l-1.6 .7M6.6 -12.3l-1.5 .6M5.4 -11.2l-1.4 .6" fill="none" stroke="%s" stroke-width=".65" stroke-linecap="round"/>' % GOLD,
        # pointed ears
        '<path d="M-6 -4.6L-8.6 -3.8L-6.4 -2.6ZM6 -4.6L8.6 -3.8L6.4 -2.6Z" fill="none" stroke="%s" stroke-width=".9" stroke-linejoin="round"/>' % GOLD,
        # head with heavy brow and fanged snarl
        '<path d="M0 -10.8C3.7 -10.8 6.2 -8.2 6.2 -4.7C6.2 -1.2 3.7 1.4 0 1.4C-3.7 1.4 -6.2 -1.2 -6.2 -4.7C-6.2 -8.2 -3.7 -10.8 0 -10.8Z" fill="none" stroke="%s" stroke-width="1.25"/>' % GOLD,
        '<path d="M-4.3 -6.8L-1.1 -6M4.3 -6.8L1.1 -6" fill="none" stroke="%s" stroke-width=".8" stroke-linecap="round"/>' % GOLD,
        '<path d="M-3.4 -5C-2.7 -5.9 -1.2 -5.9 -.5 -5C-1.2 -4.2 -2.7 -4.2 -3.4 -5ZM3.4 -5C2.7 -5.9 1.2 -5.9 .5 -5C1.2 -4.2 2.7 -4.2 3.4 -5Z" fill="%s"/>' % GOLD,
        '<path d="M0 -3.8L0 -.8" fill="none" stroke="%s" stroke-width=".8" stroke-linecap="round"/>' % GOLD,
        '<path d="M-3 -.2C-2 -.8 -2 -.4 -1.3 .3C-.6 -.4 .6 -.4 1.3 .3C2 -.4 2 -.8 3 -.2" fill="none" stroke="%s" stroke-width=".85" stroke-linecap="round"/>' % GOLD,
        '<path d="M-2 0l.2 1.3M2 0l-.2 1.3" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
        '<path d="M-2.4 -8.8q2.4 -1.2 4.8 0" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
    ]),
    "minotaur": "".join([
        # horns with ridge ticks
        '<path d="M-6.4 -7.6C-10.4 -10.2 -12 -13.6 -10 -15.2C-10.6 -12 -9 -9.6 -5.4 -7.8Z" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M6.4 -7.6C10.4 -10.2 12 -13.6 10 -15.2C10.6 -12 9 -9.6 5.4 -7.8Z" fill="none" stroke="%s" stroke-width="1.15" stroke-linejoin="round"/>' % GOLD,
        '<path d="M-10.6 -13.4l1.7 .8M-9.3 -11.7l1.6 .7M-8 -10.2l1.5 .7M10.6 -13.4l-1.7 .8M9.3 -11.7l-1.6 .7M8 -10.2l-1.5 .7" fill="none" stroke="%s" stroke-width=".65" stroke-linecap="round"/>' % GOLD,
        # skull + muzzle
        '<path d="M-6 -8.2C-6 -3 -3.4 1.6 0 2.2C3.4 1.6 6 -3 6 -8.2C4 -10.2 -4 -10.2 -6 -8.2Z" fill="none" stroke="%s" stroke-width="1.2" stroke-linejoin="round"/>' % GOLD,
        '<path d="M-4.6 -6C-3.4 -6.8 -1.8 -7 -.6 -6.7M4.6 -6C3.4 -6.8 1.8 -7 .6 -6.7" fill="none" stroke="%s" stroke-width=".75" stroke-linecap="round"/>' % GOLD,
        '<path d="M-3.3 -4.6C-2.6 -5.4 -1.2 -5.4 -.6 -4.6C-1.2 -3.9 -2.6 -3.9 -3.3 -4.6ZM3.3 -4.6C2.6 -5.4 1.2 -5.4 .6 -4.6C1.2 -3.9 2.6 -3.9 3.3 -4.6Z" fill="%s"/>' % GOLD,
        '<path d="M-3.8 .2C-3.8 2.4 -2.1 3.9 0 3.9C2.1 3.9 3.8 2.4 3.8 .2" fill="none" stroke="%s" stroke-width="1" stroke-linecap="round"/>' % GOLD,
        '<path d="M-1.8 2.5C-1.3 1.9 -.4 1.9 0 2.5C.4 1.9 1.3 1.9 1.8 2.5" fill="none" stroke="%s" stroke-width=".85" stroke-linecap="round"/>' % GOLD,
        '<path d="M-2.4 4.6C-1.2 5.2 1.2 5.2 2.4 4.6" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
    ]),
    "guardian": "".join([
        # ringed face of the dread guardian
        '<path d="M0 -8.6C5.5 -8.6 8.6 -4.6 8.6 0.4C8.6 6 4.6 9.6 0 9.6C-4.6 9.6 -8.6 6 -8.6 0.4C-8.6 -4.6 -5.5 -8.6 0 -8.6Z" fill="none" stroke="%s" stroke-width="1.2"/>' % GOLD,
        '<path d="M0 -6.6C4.3 -6.6 6.6 -3.5 6.6 .3C6.6 4.5 3.6 7.4 0 7.4C-3.6 7.4 -6.6 4.5 -6.6 .3C-6.6 -3.5 -4.3 -6.6 0 -6.6Z" fill="none" stroke="%s" stroke-width=".7" opacity=".8"/>' % GOLD,
        ('<circle cx="0" cy="-10.4" r="1.85" fill="none" stroke="%s" stroke-width="1"/>' % GOLD) +
        '<circle cx="5.4" cy="-7.6" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="9.2" cy="-3.2" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="9.2" cy="3.2" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="5.4" cy="7.6" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="0" cy="9.4" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="-5.4" cy="7.6" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="-9.2" cy="3.2" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="-9.2" cy="-3.2" r="1.85" fill="none" stroke="%s" stroke-width="1"/><circle cx="-5.4" cy="-7.6" r="1.85" fill="none" stroke="%s" stroke-width="1"/>' % ((GOLD,) * 9),
        '<path d="M-4.6 -3.4l3 1.2m1.6 -1.2l3 1.2" fill="none" stroke="%s" stroke-width=".9" stroke-linecap="round"/>' % GOLD,
        '<path d="M-4.2 -1.4C-3.6 -2.4 -1.7 -2.4 -1.2 -1.4C-1.7 -.5 -3.6 -.5 -4.2 -1.4ZM4.2 -1.4C3.6 -2.4 1.7 -2.4 1.2 -1.4C1.7 -.5 3.6 -.5 4.2 -1.4Z" fill="%s"/>' % GOLD,
        '<path d="M0 -2.4L0 1.6" fill="none" stroke="%s" stroke-width=".8" stroke-linecap="round"/>' % GOLD,
        '<path d="M-3.4 3.6q1.7 1.8 3.4 0q1.7 -1.8 3.4 0" fill="none" stroke="%s" stroke-width=".9" stroke-linecap="round"/>' % GOLD,
        '<path d="M-2.6 5.6q1.3 1.4 2.6 0q1.3 -1.4 2.6 0M-7 1.4q-1 1.6 -.4 3.4M7 1.4q1 1.6 .4 3.4" fill="none" stroke="%s" stroke-width=".7" stroke-linecap="round"/>' % GOLD,
    ]),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nice_km(target_px, px_per_deg, lat_ref):
    km_per_deg = 111.0 * math.cos(math.radians(lat_ref))
    raw = target_px / px_per_deg * km_per_deg
    for cand in (10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000):
        if abs(cand - raw) / raw < 0.45:
            return cand
    return min((10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000),
               key=lambda c: abs(c - raw))


def build(name, spec, lang):
    box = spec["box"]
    pad = 16
    w = spec["w"]
    lonspan, latspan = box[1] - box[0], box[3] - box[2]
    h = int(2 * pad + latspan / lonspan * (w - 2 * pad))
    px = (w - 2 * pad) / lonspan
    lang_title = spec["title"][lang]
    o = []
    A = o.append

    A('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" role="img" aria-label="%s">' % (w, h, esc(lang_title)))
    A('<!-- %s - generated by tools/genmaps.py from Natural Earth 1:110m land (public domain). Dark sea, olive land, gold coast; compass, cartouche and scale bar for the house art direction. No scripts, no external assets. -->' % lang_title)
    A('<style>.lb{font-family:Georgia,"Times New Roman",serif;letter-spacing:.14em;fill:%s}.sea-lb{font-family:Georgia,"Times New Roman",serif;letter-spacing:.14em;fill:%s;font-style:italic}@media (prefers-reduced-motion:reduce){*{animation:none}}</style>' % (GOLD, SEA_TEXT))
    if lang == "fa":
        A('<style>.lb,.sea-lb{font-family:Vazirmatn,"Segoe UI",Tahoma,sans-serif;letter-spacing:0;direction:rtl}</style>')
    A('<defs>')
    A('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (SEA, SEA2))
    A('<linearGradient id="land" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (LAND, LAND2))
    A('<radialGradient id="vign" cx="50%" cy="50%" r="72%"><stop offset="0" stop-color="#04060a" stop-opacity="0"/><stop offset="100%" stop-color="#04060a" stop-opacity=".66"/></radialGradient>')
    A('<pattern id="wav" width="30" height="16" patternUnits="userSpaceOnUse"><path d="M0 9q7.5-9 15 0t15 0" fill="none" stroke="#3d6480" stroke-width="1" opacity=".13"/></pattern>')
    # a gentler coast wobble: the old 3.4-unit displacement at 0.03 frequency
    # chewed up small islands, so the displacement is smaller and its wavelength
    # longer (islands survive, and the coast reads as drawn rather than noisy)
    A('<filter id="rough" x="-4%" y="-4%" width="108%" height="108%"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G"/></filter>')
    # soft dark patch behind a beast, so its gold line art still reads where it
    # crosses olive land instead of drowning in it
    A('<radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#04060a" stop-opacity=".5"/><stop offset="100%" stop-color="#04060a" stop-opacity="0"/></radialGradient>')
    A('<clipPath id="inner"><rect x="%d" y="%d" width="%d" height="%d" rx="4"/></clipPath>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    A('</defs>')

    # sea
    A('<rect width="%d" height="%d" fill="url(#sea)"/>' % (w, h))
    A('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#wav)"/>' % (pad, pad, w - 2 * pad, h - 2 * pad))

    # land
    geo = json.load(open(GEO))
    paths = []
    for feat in geo["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            for ring in poly:
                if max(p[1] for p in ring) < box[2] - 2 or min(p[1] for p in ring) > box[3] + 2:
                    continue
                paths.append(ring_path(ring, box, w, h, pad))
    A('<g clip-path="url(#inner)">')

    # graticule and rhumb lines go UNDER the land: a grid drawn across the coast
    # cuts the outline into segments and turns it into noise, so the grid belongs
    # to the sea; rivers and mountain hatches stay on top of the land below
    g = spec["graticule"]
    lines = []
    lon = math.ceil(box[0] / g) * g
    while lon <= box[1]:
        x, _ = project(lon, box[2], box, w, h, pad)
        lines.append("M%.1f %dV%d" % (x, pad, h - pad))
        lon += g
    lat = math.ceil(box[2] / g) * g
    while lat <= box[3]:
        _, y = project(box[0], lat, box, w, h, pad)
        lines.append("M%d %.1fH%d" % (pad, y, w - pad))
        lat += g
    A('<path d="%s" fill="none" stroke="#41637c" stroke-width=".7" opacity=".28"/>' % "".join(lines))

    # rhumb lines from a wind-rose centre (old charts)
    cx, cy = w - pad - 78, h - pad - 78
    rays = []
    for k in range(16):
        a = k * math.pi / 8
        rays.append("M%d %dl%.0f %.0f" % (cx, cy, math.cos(a) * w, math.sin(a) * w))
    A('<path d="%s" fill="none" stroke="%s" stroke-width=".8" opacity=".16"/>' % ("".join(rays), GOLD))

    # land
    A('<g filter="url(#rough)">')
    A('<path fill="url(#land)" fill-rule="evenodd" stroke="%s" stroke-width="1.2" stroke-linejoin="round" d="%s"/>' % (GOLD, "".join(paths)))
    A('</g>')

    # rivers and mountain hatches sit ON the land
    for riv in spec["rivers"]:
        A('<path d="%s" fill="none" stroke="#41789b" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>' % poly_path(riv, box, w, h, pad))
    for rng in spec["ranges"]:
        A('<path d="%s" fill="none" stroke="#0c120a" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" opacity=".85"/>' % chevrons(rng, box, w, h, pad))
    A('</g>')

    # vignette: it darkens the geography towards the frame, so it must be painted
    # before the labels and beasts — drawn after them it dimmed exactly what the
    # reader is meant to read
    A('<rect width="%d" height="%d" fill="url(#vign)"/>' % (w, h))

    # labels
    for text, lon, lat, size, kind, rot in spec["labels"]:
        label = text if lang == "en" else FA.get(text, text)
        x, y = project(lon, lat, box, w, h, pad)
        cls = "lb" if kind == "r" else "sea-lb"
        r = ' transform="rotate(%d %.0f %.0f)"' % (rot, x, y) if rot else ""
        A('<text class="%s" x="%.0f" y="%.0f" font-size="%d" text-anchor="middle"%s opacity=".92">%s</text>' % (cls, x, y, size, r, esc(label)))

    # mythical creatures ("here be monsters": thin engraved line art). A soft dark
    # halo sits behind each beast so the gold lines still read where the beast
    # crosses olive land, and a dark rim behind its caption does the same for the
    # name; the art runs from about -16..+17 x and -15..+11 y around the origin
    for c in spec.get("creatures", []):
        kind, clon, clat, s, flip = c[:5]
        label = c[5] if len(c) > 5 else None
        x, y = project(clon, clat, box, w, h, pad)
        S = s * 1.28                      # a touch larger for presence
        sx = -S if flip else S
        A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#halo)"/>'
          % (x, y, 19 * S, 15 * S))
        A('<g transform="translate(%.1f %.1f) scale(%.2f %.2f)" opacity=".92">%s</g>'
          % (x, y, sx, S, CREATURE_ART[kind]))
        if label:
            lab = label if lang == "en" else FA.get(label, label)
            A('<text class="lb" x="%.0f" y="%.0f" font-size="12" text-anchor="middle" '
              'stroke="#05070b" stroke-width="3" stroke-opacity=".6" paint-order="stroke" opacity=".95">%s</text>'
              % (x, y + 13 * S + 12, esc(lab)))

    # frame
    A('<rect x="7" y="7" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2" rx="7" opacity=".7"/>' % (w - 14, h - 14, GOLD))
    A('<rect x="13" y="13" width="%d" height="%d" fill="none" stroke="%s" stroke-width=".8" rx="4" opacity=".4"/>' % (w - 26, h - 26, GOLD))
    A('<g stroke="%s" stroke-width="1.3" fill="none" opacity=".55"><path d="M13 34q4-14 18-18"/><path d="M%d 13q14 4 18 18"/><path d="M13 %dq4 14 18 18"/><path d="M%d %d q14-4 18-18"/></g>' % (GOLD, w - 31, h - 31, w - 31, h - 31))

    # title cartouche (top-left). The caption is centred in its box: it used to be
    # anchored "start" at the box's own centre, so a long English title began
    # halfway across and ran out past the right edge of the cartouche
    tw = max(150, int(len(lang_title) * (11 if lang == "fa" else 9.4)) + 34)
    A('<g><rect x="%d" y="%d" width="%d" height="34" rx="7" fill="#070b11" fill-opacity=".82" stroke="%s" stroke-width="1" opacity=".92"/>' % (pad + 14, pad + 14, tw, GOLD))
    A('<text class="lb" x="%d" y="%d" font-size="15" text-anchor="middle" letter-spacing=".1em">%s</text></g>' % (pad + 14 + tw // 2, pad + 36, esc(lang_title)))

    # compass rose (bottom-right)
    A('<g transform="translate(%d %d)"><circle r="24" fill="#070b11" fill-opacity=".8" stroke="%s" stroke-width="1"/>' % (w - pad - 52, h - pad - 52, GOLD))
    A('<g fill="%s" opacity=".9"><path d="M0-20 3.4-6 0-9 -3.4-6Z"/><path d="M0 20 3.4 6 0 9 -3.4 6Z"/><path d="M-20 0-6 3.4-9 0-6-3.4Z"/><path d="M20 0 6 3.4 9 0 6-3.4Z"/></g>' % GOLD)
    A('<circle r="3" fill="none" stroke="%s" stroke-width=".8"/><text class="lb" y="-29" font-size="11" text-anchor="middle">%s</text></g>' % (GOLD, "N" if lang == "en" else "ش"))

    # scale bar (bottom-left)
    ref_lat = (box[2] + box[3]) / 2
    km = nice_km(0.16 * (w - 2 * pad), px, ref_lat)
    bar = km / (111.0 * math.cos(math.radians(ref_lat))) * px
    sx, sy = pad + 24, h - pad - 34
    A('<g transform="translate(%.0f %.0f)" opacity=".8"><rect width="%.0f" height="4" fill="%s"/><rect x="%.0f" width="%.0f" height="4" fill="#070b11" stroke="%s" stroke-width=".6"/>' % (sx, sy, bar / 2, GOLD, bar / 2, bar / 2, GOLD))
    A('<line x1="0" y1="-4" x2="0" y2="6" stroke="%s" stroke-width="1.4"/><line x1="%.0f" y1="-4" x2="%.0f" y2="6" stroke="%s" stroke-width="1.4"/>' % (GOLD, bar, bar, GOLD))
    A('<text class="lb" x="%.0f" y="-9" font-size="11" text-anchor="middle">%s</text></g>' % (bar / 2, "%d km" % km if lang == "en" else "%d کیلومتر" % km))

    A('</svg>')
    svg = "\n".join(o)
    out = os.path.join(OUT, name + ("" if lang == "en" else "-fa") + ".svg")
    with open(out, "w") as f:
        f.write(svg)
    # XML sanity
    import xml.dom.minidom as m
    m.parseString(svg)
    return out, len(svg), (w, h)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, spec in MAPS.items():
        for lang in ("en", "fa"):
            out, size, dim = build(name, spec, lang)
            print("%-28s %6d B  %s" % (os.path.relpath(out, ROOT), size, dim))
    # pin helpers: print % coordinates so content pins can be placed exactly
    print("\nreference pin coordinates (% of map box):")
    pins = {
        "middle-east": [("Uruk", 45.67, 31.32), ("Ur", 46.1, 30.96), ("Babylon", 44.42, 32.54),
                        ("Nineveh", 43.14, 36.36), ("Cedar Forest", 35.6, 34.1)],
        "persia": [("Damavand", 53.06, 35.95), ("Ecbatana", 48.51, 34.8), ("Susa", 48.25, 32.19),
                   ("Persepolis", 52.89, 29.99), ("Balkh", 66.9, 36.76)],
        "india": [("Kailash", 81.25, 31.07), ("Hastinapur", 77.55, 29.02), ("Varanasi", 83.0, 25.32),
                  ("Dwarka", 68.97, 22.24), ("Lanka", 80.4, 8.35)],
        "aegean": [("Olympus", 22.36, 40.09), ("Troy", 26.18, 39.96), ("Delphi", 22.5, 38.48),
                   ("Athens", 23.73, 37.98), ("Knossos", 25.16, 35.3)],
        "scandinavia": [("Uppsala", 17.64, 59.86), ("Birka", 17.64, 59.34), ("Nidaros", 10.4, 63.43),
                        ("Hedeby", 9.42, 54.52), ("Jotunheim", 8.0, 62.0)],
        "world": [("Mesopotamia", 44, 33), ("Persia", 55, 31.5), ("India", 79, 22),
                  ("Greece", 22.5, 39), ("The North", 15, 62)],
    }
    for name, items in pins.items():
        box = MAPS[name]["box"]
        print(" ", name)
        for label, lon, lat in items:
            x, y = pct(lon, lat, box)
            print("    %-14s x=%.1f%% y=%.1f%%" % (label, x, y))
