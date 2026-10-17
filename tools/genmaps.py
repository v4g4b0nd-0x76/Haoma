#!/usr/bin/env python3
"""Generate the stylised map artwork in static/img/maps/.

    python3 tools/fetch_geo.py     # once: downloads Natural Earth data into tools/geo/
    python3 tools/genmaps.py       # all maps
    python3 tools/genmaps.py persia world     # only some

Geography is Natural Earth (public domain): 1:110m land for the world sheet and, when
present in tools/geo/, 1:50m land + rivers + lakes for the regional sheets (the script falls
back to 110m land and hand-placed rivers if those files are missing).

House style, in the spirit of the hand-inked Middle-earth charts but on a dark sheet:
dark sea with shore ripples, olive land with grain, gold ink coasts, engraved mountain /
forest / hill / desert / marsh glyphs, tapering rivers, curved spaced-capital lettering with
a halo, a ladder border with degree ticks, ribbon title, compass rose, scale bar, ships on
the water and engraved monsters ("here be dragons"). Art lives in tools/mapart.py.

Outputs, per map: <name>.svg (English) and <name>-fa.svg (Farsi):
    world  middle-east  persia  india  aegean  scandinavia
Pin positions are percentages of the map box and are printed at the end; they do not change
when the art changes. Set COSINE_ASPECT = False to keep the old (stretched) proportions.
"""
import json
import math
import os
import random
import re
import sys
import xml.dom.minidom as minidom

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapart as A  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = os.environ.get("GENMAPS_GEO") or os.path.join(ROOT, "tools", "geo")
OUT = os.path.join(ROOT, "static", "img", "maps")
COSINE_ASPECT = True

GOLD = "#d9bd76"
GOLD_DIM = "#a88f56"
LAND_A, LAND_B = "#3d5131", "#243219"
SEA_A, SEA_B = "#122638", "#070e17"
SEA_TEXT = "#93b9d1"
TEXT = "#e2cf98"
INKC = "#05080b"
FONT = 'Cinzel,"Cormorant Garamond",Georgia,"Times New Roman",serif'
FONT_FA = 'Vazirmatn,"Segoe UI",Tahoma,sans-serif'

# ------------------------------------------------------------------- type sizes
# A label tuple's `size` is a *rank* — how big that name should read next to its
# neighbours on the same sheet (ASIA outranks CHINA). These factors turn the rank
# into points at the reference sheet width (1300); nothing else sets label type.
#
#   'r'  realms, countries, regions, deserts   gold
#   's'  seas, oceans, gulfs                   pale blue, italic
#
# Realms and countries are declared separately from the seas so each can be tuned
# on its own. Farsi runs slightly larger: Persian glyphs are shorter than Cinzel
# capitals at the same point size. Kept modest so labels stay light and neat.
TYPE_SIZE = {
    'r': {'en': 1.05, 'fa': 1.05 * 1.08},
    's': {'en': 1.00, 'fa': 1.00 * 1.08},
}
WORLD_SCALE = 0.78    # the world sheet is wider than a culture sheet, so type drops a shade

# --------------------------------------------------------------------------- data
MAPS = {
    "world": dict(
        box=(-135, 225, -58, 84), w=1800, res="110", cos=False, graticule=30,
        title={"en": "The World", "fa": "جهان"},
        labels=[
            # Academic atlas anchors (lon, lat). Sources noted in comments:
            #   ARABIA   — peninsula centre ~22.8°N 47.5°E (Peakbagger / classical
            #              Arabia Felix bounds; never Horn of Africa)
            #   PERSIA   — Iranian plateau ~53.5°E 32.5°N (east of Mesopotamia,
            #              north of the Gulf; Persepolis 52.9°E 29.9°N is the pin)
            #   INDIA    — Vedic Āryāvarta / Madhyadeśa ~77°E 27°N (Witzel et al.)
            #   SCYTHIA  — Saka steppe north of the Caspian ~50°E 48°N (Iranica:
            #              Saka Tigraxauda; classical Pontic Scythia is farther west)
            #   AFRICA   — Sahara / Sahel band, west of the Red Sea
            ("NORTH AMERICA", -100, 45, 18, "r"),
            ("SOUTH AMERICA", -58, -14, 18, "r"),
            ("EUROPA", 8, 50, 15, "r"),
            ("AFRICA", 18, 10, 20, "r"),
            ("ASIA", 100, 48, 22, "r"),
            ("ARABIA", 47.5, 21, 12, "r"),
            ("PERSIA", 54, 35, 13, "r"),
            ("INDIA", 77, 27, 14, "r"),
            ("CHINA", 110, 35, 14, "r"),
            ("SCYTHIA", 50, 48, 11, "r"),
            ("SIBERIA", 105, 64, 15, "r"),
            ("AUSTRALIA", 134, -25, 14, "r"),
            ("GREENLAND", -42, 73, 12, "r"),
            ("ATLANTIC OCEAN", -34, 22, 14, "s"),
            ("INDIAN OCEAN", 78, -18, 14, "s"),
            ("PACIFIC OCEAN", 160, 6, 14, "s"),
            ("ARCTIC OCEAN", 100, 78, 12, "s"),
            ("MEDITERRANEAN SEA", 18, 35, 10, "s"),
            ("AMAZONIA", -62, -4, 11, "r"),
        ],
        ranges=[
            [(-123, 57), (-116, 50), (-110, 43), (-107, 37), (-106, 32)],
            [(-72, 9), (-76, 2), (-78, -8), (-72, -18), (-70, -30), (-72, -42), (-73, -52)],
            [(6, 45.6), (10, 46.6), (15, 47.2)], [(60, 68), (59, 61), (58, 55)],
            [(73, 35), (78, 32), (84, 28.6), (92, 27.6), (98, 28.4)], [(38, 44), (44, 42.6), (48, 41)],
            [(84, 50), (90, 49), (97, 49.4)], [(-8, 31.6), (-3, 34), (6, 35.6)],
            [(6, 60), (12, 65), (18, 68)], [(45, 36), (48, 33), (52, 29)], [(70, 42), (78, 42.4), (86, 43)],
            [(36, 6), (38, 10), (38, 13)],
        ],
        forests=[(105, 60, 36, 5.5, "pine"), (-100, 56, 22, 5, "pine"), (22, 63, 8, 4, "pine"),
                 (-62, -4, 9, 6, "round"), (22, 0, 8, 5, "round"), (111, 15, 5, 6, "round"), (-120, 47, 3, 6, "pine")],
        deserts=[(5, 24, 16, 5), (47, 24, 7, 4.5), (104, 42, 9, 3.4), (131, -26, 9, 5), (22, -23, 5, 3.4), (-112, 36, 6, 3)],
        rivers=[
            [(31, 30.5), (31.5, 27), (32.5, 23), (33.5, 18), (34, 13), (33, 8), (32, 2), (30, -1)],
            [(-73, -4), (-68, -4), (-64, -5), (-60, -4), (-56, -3), (-52, -2), (-50, 0)],
            [(28, -6), (24, -4), (20, -3), (17, -4), (15, -6), (13, -6), (12, -6)],
            [(-95, 47), (-96, 43), (-95, 38), (-92, 34), (-91, 31), (-89, 29)],
            [(9, 48), (14, 47), (18, 46), (21, 45), (25, 45), (29, 45)], [(9, 47), (8, 45), (7, 43), (6, 41)],
            [(37, 57), (40, 55), (44, 52), (47, 48), (48, 46), (48, 45)], [(78, 30), (81, 26), (85, 25), (88, 24), (90, 23)],
            [(73, 34), (71, 31), (69, 27), (67, 24)], [(97, 32), (102, 29), (106, 29), (110, 30), (114, 31), (119, 32), (122, 31)],
            [(96, 35), (101, 36), (106, 35), (110, 35), (114, 37), (118, 38), (119, 37)], [(75, 52), (73, 57), (70, 62), (68, 66), (69, 70)],
            [(92, 52), (88, 57), (85, 62), (83, 68), (82, 72)], [(108, 53), (112, 58), (116, 63), (122, 68), (127, 72)],
            [(-50, -18), (-53, -22), (-56, -27), (-58, -31), (-59, -34)], [(147, -36), (144, -34), (141, -33), (139, -34), (137, -35)]],   # fallback only: used when the Natural Earth river data is not in tools/geo
        creatures=[("serpent", -40, 8, 1.55, 0, None), ("wyrm", 82, 60.5, 1.4, 1, None), ("bird", 80, -11, 1.5, 0, None),
                   ("makara", 150, -40, 1.2, 1, None)],
        ships=[("longship", -28, 54, 1.1, 0), ("dhow", 64, 13, 1.0, 0), ("trireme", 15, 36.4, .8, 0),
               ("dhow", 123, 6, .9, 1), ("longship", 214, 4, 1.0, 1)],
    ),
    "middle-east": dict(
        box=(26, 60, 23, 41), w=1300, res="50", cos=True, graticule=5,
        title={"en": "Mesopotamia and the Levant", "fa": "بین‌النهرین و شام"},
        labels=[
            ("ANATOLIA", 33, 39.2, 18, "r"), ("LEVANT", 36.4, 33.7, 13, "r"), ("MESOPOTAMIA", 43.2, 34.6, 18, "r"),
            ("ARABIA", 44, 27, 20, "r"), ("PERSIA", 54.6, 33.4, 17, "r"), ("MEDITERRANEAN SEA", 31, 34.1, 13, "s"),
            ("BLACK SEA", 35.5, 41.3, 12, "s"), ("CASPIAN SEA", 51, 40.3, 12, "s"), ("RED SEA", 36.6, 25.4, 12, "s"),
            ("PERSIAN GULF", 51.2, 27.5, 12, "s"), ("AEGEAN", 26, 38, 10, "s"),
        ],
        ranges=[[(29, 37.4), (33, 37.6), (37, 37)], [(44.5, 37.5), (46.5, 33.5), (49, 31), (53, 28), (56, 27)],
                [(49, 36.6), (52, 36.4), (55.5, 36.6)], [(35.9, 34.6), (36.4, 33.6)], [(40, 41), (44, 40), (47, 38.6)]],
        forests=[(36, 36.5, 1.3, .8, "pine"), (50.8, 36.9, 2.2, .45, "round"), (31, 37.3, 3, .5, "pine"), (41, 38.4, 2.4, .5, "pine")],
        deserts=[(42, 30, 7, 3.2), (52, 23.6, 3.4, 1.6), (38, 32.8, 2.2, 1.4), (57, 33, 2.4, 1.6)],
        marshes=[(47.2, 31.2, 1.3, .9)],
        rivers=[
            [(38.6, 37.5), (40.5, 36.6), (42.5, 35), (44, 33.2), (45.4, 31.6), (47, 30.6), (48, 30.1)],
            [(38.2, 38.4), (40.5, 37.4), (42.6, 36.2), (43.5, 34.6), (44.6, 33), (45.6, 31.6), (47.4, 30.7)],
            [(31.2, 30.6), (31.6, 28.5), (32.6, 26), (33.6, 24), (34.4, 23)], [(35.7, 32.7), (35.6, 31.7), (35.5, 31.2)],
            [(47, 32.5), (48.5, 31.6), (49.5, 30.5)]],   # fallback only: used when the Natural Earth river data is not in tools/geo
        creatures=[("guardian", 36.4, 37.0, 1.3, 0, "HUMBABA"), ("wyrm", 44.6, 33.4, 1.25, 0, "MUSHUSSU"),
                   ("anzu", 47.9, 30.6, 1.2, 0, "ANZU")],
        ships=[("trireme", 30.5, 33.2, .8, 0), ("dhow", 51.4, 26.6, .8, 0), ("dhow", 38.6, 21.6, .8, 1),
               ("trireme", 38.8, 41.4, .7, 1)],
    ),
    "persia": dict(
        box=(42, 72, 24, 40), w=1300, res="50", cos=True, graticule=5,
        title={"en": "The Iranian Plateau", "fa": "فلات ایران"},
        labels=[
            ("MEDIA", 47.6, 35.8, 14, "r"), ("PERSIA", 53.4, 31.2, 19, "r"), ("PARTHIA", 58.8, 37.4, 13, "r"),
            ("ARIA", 63.4, 33.8, 14, "r"), ("KAVIR DESERT", 55.4, 34.5, 11, "r"), ("CASPIAN SEA", 51, 38.9, 12, "s"),
            ("PERSIAN GULF", 51.4, 28.2, 12, "s"), ("GULF OF OMAN", 58.5, 25.2, 12, "s"), ("ARABIAN SEA", 66.5, 25.0, 12, "s"),
            ("TRANSOXIANA", 66, 38.6, 13, "r"),
        ],
        ranges=[[(48.8, 36.4), (52, 36.2), (55.5, 36.5)], [(45, 36.5), (46.8, 33), (49.5, 30.5), (53, 28), (56, 26.8)],
                [(58, 38.4), (61.5, 37.4)], [(64, 35.5), (68, 35.2), (71, 35.5)], [(60, 28), (62, 26.6)]],
        forests=[(51.6, 36.8, 2.4, .5, "round"), (46, 35, 1.2, 1.4, "pine")],
        deserts=[(55, 34.4, 3.2, 1.4), (58.6, 30.8, 2, 2.2), (60, 39.2, 3.2, 1.0), (65, 30.6, 1.6, 1.6), (52, 29.6, 1.6, .8)],
        marshes=[(61.2, 31.3, .7, .5)],
        rivers=[
            [(54, 37.4), (56, 38), (58, 38.2)], [(65, 33.6), (63, 31.4), (61.4, 29.6), (60.6, 28.4)],
            [(46.6, 33.4), (48, 32.4), (49.4, 30.6)], [(72, 34.4), (71.4, 33), (71, 31.6)], [(49.6, 33.4), (51.6, 32.4), (53, 32.2)]],   # fallback only: used when the Natural Earth river data is not in tools/geo
        creatures=[("bird", 52.4, 37.0, 1.35, 0, "SIMORGH"), ("dragon3", 46.4, 33.8, 1.2, 1, "DAHAKA"),
                   ("demon", 63.4, 30.6, 1.2, 1, "DAEVA")],
        ships=[("dhow", 52.6, 27.2, .8, 0), ("dhow", 62, 24.8, .8, 1), ("trireme", 51, 38.6, .65, 0)],
    ),
    "india": dict(
        box=(64, 104, 5, 34), w=1300, res="50", cos=True, graticule=5,
        title={"en": "India and the Indus", "fa": "هند و سند"},
        labels=[
            ("INDIA", 78.4, 21.4, 22, "r"), ("HIMALAYA", 83, 30.8, 14, "r"), ("THAR DESERT", 71.4, 27.6, 10, "r"),
            ("DECCAN", 77, 16.6, 13, "r"), ("BENGAL", 89.4, 23.6, 11, "r"), ("ARABIAN SEA", 68.6, 13, 13, "s"),
            ("BAY OF BENGAL", 89, 13.4, 13, "s"), ("INDIAN OCEAN", 80, 6.4, 13, "s"),
        ],
        ranges=[[(72, 33.4), (76, 32.4), (80, 30.4), (84, 28.4), (88, 27), (92, 27.6), (97, 28)], [(74, 27), (75.6, 24.4), (76.6, 22.6)],
                [(73.4, 20), (75, 15), (76.4, 11)], [(79.4, 19.4), (82, 17.6), (84.4, 17)], [(80.5, 30.2), (82, 30.8)]],
        forests=[(82, 27.6, 6, .7, "pine"), (75.6, 13.6, .8, 5, "round"), (81, 20.4, 4, 2, "round"), (94, 26, 2.5, 1.5, "round"),
                 (89.2, 22, 1.2, .6, "round"), (98, 22, 3, 3, "round")],
        deserts=[(71.4, 26.4, 2.6, 2.4)],
        hills=[(77, 17.4, 3, 1.6), (86, 20.6, 1.6, 1.2)],
        rivers=[
            [(72.4, 34), (71.4, 31), (70, 28), (68.4, 25.4), (67.4, 24)], [(78.4, 30), (81, 26.4), (84.6, 25.4), (87.6, 24.4), (90, 23)],
            [(77.6, 30.4), (78.6, 27.4), (81, 26.4)], [(82, 29.4), (87, 27.4), (91, 27), (94.4, 27.4), (95.4, 25.4), (96, 24.4)],
            [(78.4, 19.6), (81.4, 17.6), (84, 16.6), (87, 16.6)], [(74.4, 17), (77.6, 16.4), (80.6, 15.6), (83.4, 15.6)]],   # fallback only: used when the Natural Earth river data is not in tools/geo
        creatures=[("garuda", 80.4, 28.6, 1.3, 0, "GARUDA"), ("naga", 87.6, 23.8, 1.2, 0, "NAGA"), ("makara", 73.6, 8.6, 1.2, 1, "MAKARA")],
        ships=[("dhow", 67.6, 17, .9, 0), ("dhow", 87.4, 11.4, .9, 1), ("dhow", 78, 7.2, .8, 0)],
    ),
    "aegean": dict(
        box=(15, 39, 33.5, 45.5), w=1300, res="50", cos=True, graticule=5,
        title={"en": "The Aegean", "fa": "دریای اژه"},
        labels=[
            ("GREECE", 21.2, 40.4, 17, "r"), ("ANATOLIA", 32.6, 38.9, 17, "r"), ("THRACE", 25.8, 42.1, 12, "r"),
            ("CRETE", 24.8, 35.1, 10, "r"), ("CYPRUS", 33.2, 35.1, 10, "r"), ("AEGEAN SEA", 25.6, 38.5, 13, "s"),
            ("IONIAN SEA", 18, 38, 12, "s"), ("MEDITERRANEAN SEA", 25, 34.0, 12, "s"), ("BLACK SEA", 33.6, 43.6, 12, "s"),
            ("SEA OF MARMARA", 28.4, 40.8, 9, "s"),
        ],
        ranges=[[(20.8, 40.4), (21.8, 39), (22.4, 38)], [(29.6, 37.6), (33, 37.4), (36, 36.6)], [(24.6, 41.6), (27, 41.4)],
                [(17.6, 43.6), (19.4, 42.6), (20.6, 41.6)], [(22.5, 38.6), (23.2, 38.3)]],
        forests=[(21, 40.2, 1.1, 1.4, "pine"), (25.5, 42.3, 1.7, .6, "pine"), (33, 37.4, 3, .5, "pine"), (35.4, 36.6, 1, .6, "pine"), (19, 42, 1.6, 1.4, "pine")],
        hills=[(22, 38.4, 1.4, .9), (27.8, 38.2, 1.4, .9), (23, 36.8, .8, .6)],
        rivers=[
            [(21, 44.8), (23, 45), (25, 45.2), (27.4, 45), (29, 45.2)], [(27.6, 38.4), (29, 37.6), (30.4, 37.4)], [(21.6, 42.6), (21.4, 41.4), (21.6, 40.6)]],   # fallback only: used when the Natural Earth river data is not in tools/geo
        creatures=[("scylla", 16.6, 38.5, 1.0, 0, "SCYLLA"), ("serpent", 22.2, 39.0, .9, 1, "PYTHON"),
                   ("minotaur", 25.6, 35.4, 1.0, 0, "MINOTAUR"), ("dragon", 29.8, 36.9, 1.0, 1, "CHIMERA")],
        ships=[("trireme", 25.2, 37.6, .75, 0), ("trireme", 27.4, 39.4, .65, 1), ("trireme", 20, 36.6, .7, 0), ("trireme", 31, 34.2, .7, 1)],
    ),
    "scandinavia": dict(
        box=(-24, 30, 51, 71), w=1300, res="50", cos=True, graticule=5,
        title={"en": "The North", "fa": "سرزمین شمال"},
        labels=[
            ("SCANDINAVIA", 16, 62.8, 20, "r"), ("FINLAND", 26, 63.2, 14, "r"), ("ICELAND", -18.8, 65, 13, "r"),
            ("DENMARK", 9.6, 55.9, 10, "r"), ("BRITAIN", -3.6, 54.2, 14, "r"), ("GALLIA", 3.6, 51.9, 12, "r"),
            ("BALTIC SEA", 19.6, 58.1, 11, "s"), ("NORTH SEA", 2.4, 57.5, 13, "s"), ("NORWEGIAN SEA", -3, 67.6, 13, "s"),
            ("KARELIA", 29.2, 65.4, 11, "r"),
        ],
        ranges=[[(5.6, 59.4), (7.6, 61.4), (11, 64), (14.6, 66.4), (17, 68.6)], [(-20, 64.6), (-17.6, 65.6)], [(-4.6, 56.6), (-3, 54.6)],
                [(-6, 57), (-4.6, 58)]],
        forests=[(17, 61.6, 6, 4.6, "pine"), (25, 64, 4, 3.4, "pine"), (11, 61, 2, 1.6, "pine"), (-1.6, 52.6, 2, .8, "round"), (2.6, 51.6, 2, .4, "round")],
        hills=[(-4.4, 56.6, 1.4, .9), (-1.6, 54.2, .8, 1)],
        rivers=[
            [(10.4, 59.6), (11, 60.6), (11.6, 61.4)], [(24.4, 67.6), (24.8, 66), (25.4, 65.4)], [(17.6, 51), (18.6, 52.6), (19, 54)], [(30, 60.6), (28.6, 60.4), (27.4, 60.4)]],   # fallback only: used when the Natural Earth river data is not in tools/geo
        creatures=[("serpent", 2.6, 58.6, 1.4, 0, "JORMUNGANDR"), ("wolf", 14.6, 60.2, 1.3, 1, "FENRIR"), ("dragon", 22.4, 66.6, 1.3, 0, "NIDHOGG")],
        ships=[("longship", -9, 60.6, 1.0, 0), ("longship", 21.6, 57.0, .85, 1), ("longship", 7.4, 54.2, .8, 0)],
    ),
}

PINS = {
    "middle-east": [("Uruk", 45.67, 31.32), ("Ur", 46.1, 30.96), ("Babylon", 44.42, 32.54), ("Nineveh", 43.14, 36.36), ("Cedar Forest", 35.6, 34.1)],
    "persia": [("Damavand", 53.06, 35.95), ("Ecbatana", 48.51, 34.8), ("Susa", 48.25, 32.19), ("Persepolis", 52.89, 29.99), ("Balkh", 66.9, 36.76)],
    "india": [("Kailash", 81.25, 31.07), ("Hastinapur", 77.55, 29.02), ("Varanasi", 83.0, 25.32), ("Dwarka", 68.97, 22.24), ("Lanka", 80.4, 8.35)],
    "aegean": [("Olympus", 22.36, 40.09), ("Troy", 26.18, 39.96), ("Delphi", 22.5, 38.48), ("Athens", 23.73, 37.98), ("Knossos", 25.16, 35.3)],
    "scandinavia": [("Uppsala", 17.64, 59.86), ("Birka", 17.64, 59.34), ("Nidaros", 10.4, 63.43), ("Hedeby", 9.42, 54.52), ("Jotunheim", 8.0, 62.0)],
    # Culture pins: Getty Mesopotamia ~44°E 34°N; Iranian plateau (Media–
    # Persis belt, north of Arabia) ~53.5°E 32.5°N; Vedic Madhyadeśa ~77°E 27°N;
    # Olympus 22.4°E 40.1°N; Uppsala 17.6°E 59.9°N.
    "world": [("Mesopotamia", 44, 34), ("Persia", 53.5, 32.5), ("India", 77, 27), ("Greece", 22.4, 40.1), ("The North", 17.6, 59.9)],
}

FA = {
    "NORTH AMERICA": "آمریکای شمالی", "SOUTH AMERICA": "آمریکای جنوبی", "EUROPA": "اروپا", "AFRICA": "آفریقا", "ASIA": "آسیا",
    "ARABIA": "عربستان", "PERSIA": "ایران", "INDIA": "هند", "CHINA": "چین", "SCYTHIA": "سکاها", "SIBERIA": "سیبری",
    "AUSTRALIA": "استرالیا", "GREENLAND": "گرینلند", "ATLANTIC OCEAN": "اقیانوس اطلس", "INDIAN OCEAN": "اقیانوس هند",
    "PACIFIC OCEAN": "اقیانوس آرام", "ARCTIC OCEAN": "اقیانوس منجمد شمالی", "MEDITERRANEAN SEA": "دریای مدیترانه", "AMAZONIA": "آمازونیا",
    "ANATOLIA": "آناتولی", "LEVANT": "شام", "MESOPOTAMIA": "بین‌النهرین", "BLACK SEA": "دریای سیاه", "CASPIAN SEA": "دریای خزر",
    "RED SEA": "دریای سرخ", "PERSIAN GULF": "خلیج فارس", "AEGEAN": "اژه", "MEDIA": "ماد", "PARTHIA": "پارت", "ARIA": "رخج",
    "KAVIR DESERT": "کویر", "TRANSOXIANA": "ماوراءالنهر", "GULF OF OMAN": "دریای عمان", "ARABIAN SEA": "دریای عرب",
    "HIMALAYA": "هیمالیا", "THAR DESERT": "صحرای تار", "DECCAN": "دکن", "BENGAL": "بنگال", "BAY OF BENGAL": "خلیج بنگال",
    "GREECE": "یونان", "THRACE": "تراکیه", "CRETE": "کرت", "CYPRUS": "قبرس", "IONIAN SEA": "دریای یونان", "SEA OF MARMARA": "دریای مرمره",
    "AEGEAN SEA": "دریای اژه", "SCANDINAVIA": "اسکاندیناوی", "FINLAND": "فنلاند", "ICELAND": "ایسلند", "DENMARK": "دانمارک",
    "BRITAIN": "بریتانیا", "GALLIA": "گل", "BALTIC SEA": "دریای بالتیک", "NORTH SEA": "دریای شمال", "NORWEGIAN SEA": "دریای نروژ",
    "KARELIA": "کارلیا",
    "SIMORGH": "سیمرغ", "DAHAKA": "ضحاک", "DAEVA": "دیو", "HUMBABA": "همبابا", "MUSHUSSU": "موشووشو", "ANZU": "آنزو",
    "GARUDA": "گارودا", "NAGA": "ناگا", "MAKARA": "ماکارا", "SCYLLA": "اسکیلا", "PYTHON": "پیتون", "MINOTAUR": "مینوتور",
    "CHIMERA": "کیمرا", "JORMUNGANDR": "یورمونگاندر", "FENRIR": "فنریر", "NIDHOGG": "نیدهوگر",
}


# --------------------------------------------------------------------------- geometry
class Frame:
    def __init__(self, box, w, cos, pad=18):
        self.box, self.w, self.pad = box, w, pad
        lon0, lon1, lat0, lat1 = box
        xs = math.cos(math.radians((lat0 + lat1) / 2)) if (cos and COSINE_ASPECT) else 1.0
        self.h = int(2 * pad + (lat1 - lat0) / ((lon1 - lon0) * xs) * (w - 2 * pad))
        self.pxdeg = (w - 2 * pad) / (lon1 - lon0)

    def xy(self, lon, lat):
        lon0, lon1, lat0, lat1 = self.box
        return (self.pad + (lon - lon0) / (lon1 - lon0) * (self.w - 2 * self.pad),
                self.pad + (lat1 - lat) / (lat1 - lat0) * (self.h - 2 * self.pad))


def pct(lon, lat, box):
    lon0, lon1, lat0, lat1 = box
    return (lon - lon0) / (lon1 - lon0) * 100, (lat1 - lat) / (lat1 - lat0) * 100


def _h(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def vnoise(x, y, seed):
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _h(ix, iy, seed), _h(ix + 1, iy, seed)
    c, d = _h(ix, iy + 1, seed), _h(ix + 1, iy + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def wobble(pts, amp, closed=True, step=9.0):
    """Hand-drawn irregularity: densify long edges, then nudge every vertex with smooth noise."""
    out = []
    n = len(pts)
    for i in range(n if closed else n - 1):
        p, q = pts[i], pts[(i + 1) % n]
        out.append(p)
        seg = math.hypot(q[0] - p[0], q[1] - p[1])
        for k in range(1, int(seg // step) + 1):
            t = k * step / seg
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    if not closed:
        out.append(pts[-1])
    res = []
    for x, y in out:
        dx = (vnoise(x / 41.0, y / 41.0, 11) - .5) * 2 + (vnoise(x / 17.0, y / 17.0, 23) - .5) * .9
        dy = (vnoise(x / 41.0, y / 41.0, 37) - .5) * 2 + (vnoise(x / 17.0, y / 17.0, 53) - .5) * .9
        res.append((x + dx * amp, y + dy * amp))
    return res


def clip_poly(pts, x0, y0, x1, y1):
    def run(pts, inside, inter):
        out = []
        for i, p in enumerate(pts):
            q = pts[i - 1]
            if inside(p):
                if not inside(q):
                    out.append(inter(q, p))
                out.append(p)
            elif inside(q):
                out.append(inter(q, p))
        return out
    def ix(xc):
        return lambda q, p: (xc, q[1] + (p[1] - q[1]) * (xc - q[0]) / ((p[0] - q[0]) or 1e-9))
    def iy(yc):
        return lambda q, p: (q[0] + (p[0] - q[0]) * (yc - q[1]) / ((p[1] - q[1]) or 1e-9), yc)
    for ins, it in ((lambda p: p[0] >= x0, ix(x0)), (lambda p: p[0] <= x1, ix(x1)),
                    (lambda p: p[1] >= y0, iy(y0)), (lambda p: p[1] <= y1, iy(y1))):
        if not pts:
            return []
        pts = run(pts, ins, it)
    return pts


def simplify(pts, tol):
    if len(pts) < 4 or tol <= 0:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        den = math.hypot(dx, dy) or 1e-9
        idx, dmax = -1, 0.0
        for i in range(a + 1, b):
            d = abs(dy * (pts[i][0] - ax) - dx * (pts[i][1] - ay)) / den
            if d > dmax:
                idx, dmax = i, d
        if dmax > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]


def simplify_closed(pts, tol):
    """Douglas-Peucker for a closed ring (split at the point farthest from the start)."""
    if len(pts) < 6 or tol <= 0:
        return pts
    ax, ay = pts[0]
    k = max(range(len(pts)), key=lambda i: (pts[i][0] - ax) ** 2 + (pts[i][1] - ay) ** 2)
    a = simplify(pts[:k + 1], tol)
    b = simplify(pts[k:] + [pts[0]], tol)
    return a[:-1] + b[:-1]


def chaikin(pts, closed=True):
    out = []
    n = len(pts)
    for i in range(n if closed else n - 1):
        p, q = pts[i], pts[(i + 1) % n]
        out += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
    return out


def d_of(pts, close=True):
    return "M" + "L".join("%.1f %.1f" % p for p in pts) + ("Z" if close else "")


def load_geo(name):
    p = os.path.join(GEO, name + ".geojson")
    return json.load(open(p)) if os.path.exists(p) else None


def polygons(geo):
    for f in geo["features"]:
        g = f["geometry"]
        if not g:
            continue
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            yield f.get("properties", {}), poly


def lines(geo):
    for f in geo["features"]:
        g = f["geometry"]
        if not g:
            continue
        for ln in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            yield f.get("properties", {}), ln


def ring_pts(fr, ring, shifts, margin):
    if len(ring) > 1 and ring[0][:2] == ring[-1][:2]:
        ring = ring[:-1]
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    lon0, lon1, lat0, lat1 = fr.box
    if max(lats) < lat0 - 4 or min(lats) > lat1 + 4:
        return
    for sh in shifts:
        if max(lons) + sh < lon0 - 4 or min(lons) + sh > lon1 + 4:
            continue
        pts = [fr.xy(lo + sh, la) for lo, la in ring]
        pts = clip_poly(pts, -margin, -margin, fr.w + margin, fr.h + margin)
        if len(pts) >= 3:
            yield pts


def land_data(fr, spec):
    world = (fr.box[1] - fr.box[0]) > 300
    shifts = (-360, 0, 360) if world else (0,)
    res = spec["res"]
    geo = load_geo("ne_50m_land") if res == "50" else None
    used = "50"
    if geo is None:
        geo, used = load_geo("ne_110m_land"), "110"
    if geo is None:
        sys.exit("missing tools/geo/ne_110m_land.geojson - run tools/fetch_geo.py")
    rings = []
    for _, poly in polygons(geo):
        for ring in poly:
            for pts in ring_pts(fr, ring, shifts, 30):
                pts = simplify_closed(pts, 0.45 if used == "50" else 0.2)
                if used == "110":
                    pts = chaikin(chaikin(pts))
                rings.append(wobble(pts, 1.5 if used == "50" else 2.0))
    return "".join(d_of(r) for r in rings), used, shifts


def lake_paths(fr, used, shifts):
    geo = load_geo("ne_50m_lakes" if used == "50" else "ne_110m_lakes") or load_geo("ne_110m_lakes")
    if not geo:
        return ""
    out = []
    for _, poly in polygons(geo):
        for pts in ring_pts(fr, poly[0], shifts, 10):
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            if (max(xs) - min(xs)) * (max(ys) - min(ys)) < 36:
                continue
            out.append(d_of(wobble(simplify_closed(pts, .5), 1.5 if used == "50" else 2.0)))
    return "".join(out)


def river_paths(fr, used, spec):
    """List of (d, width) - real rivers when the dataset is present, else the hand-placed ones."""
    out = []
    geo = load_geo("ne_50m_rivers_lake_centerlines" if used == "50" else "ne_110m_rivers_lake_centerlines")
    if geo:
        for props, ln in lines(geo):
            sr = props.get("scalerank", 6)
            if used == "50" and sr > (7 if fr.pxdeg > 25 else 4):
                continue
            pts = [fr.xy(*p[:2]) for p in ln]
            runs, cur = [], []
            for p in pts:
                if -20 <= p[0] <= fr.w + 20 and -20 <= p[1] <= fr.h + 20:
                    cur.append(p)
                elif cur:
                    runs.append(cur)
                    cur = []
            if cur:
                runs.append(cur)
            for r in runs:
                if len(r) < 3:
                    continue
                r = wobble(simplify(r, .7), 1.5 if used == "50" else 2.0, closed=False)
                sm = A.catmull(r, 2) if len(r) > 2 else r
                out.append((d_of(sm, False), max(1.0, min(2.7, 1.1 + (8 - sr) * .22))))
        return out
    for riv in spec.get("rivers", []):
        pts = A.catmull([fr.xy(*p) for p in riv], 6)
        out.append((d_of(pts, False), 1.7))
    return out


# --------------------------------------------------------------------------- terrain glyphs
def walk(pts, step):
    """Points + unit tangents every `step` px along a polyline."""
    out, acc, prev = [], 0.0, None
    for p in pts:
        if prev:
            seg = math.hypot(p[0] - prev[0], p[1] - prev[1])
            if seg:
                ux, uy = (p[0] - prev[0]) / seg, (p[1] - prev[1]) / seg
                while acc < seg:
                    out.append((prev[0] + ux * acc, prev[1] + uy * acc, ux, uy))
                    acc += step
                acc -= seg
        prev = p
    return out


def mountains(fr, rng_ll, rnd, s):
    pts = A.catmull([fr.xy(*p) for p in rng_ll], 10)
    peaks = []
    samples = walk(pts, s * 0.8)
    i = 0
    while i < len(samples):
        x, y, ux, uy = samples[i]
        nx, ny = -uy, ux
        swell = .78 + .5 * math.sin(i / 7.0 + len(pts)) ** 2          # ranges rise and fall
        if rnd.random() > .12:                                           # the odd gap between massifs
            peaks.append((x + rnd.uniform(-.3, .3) * s, y + rnd.uniform(-.3, .3) * s, s * rnd.uniform(.8, 1.25) * swell, rnd.uniform(-.25, .25)))
            for side in (-1, 1):
                if rnd.random() < .55:
                    off = rnd.uniform(1.0, 1.9) * s
                    peaks.append((x + nx * off * side + ux * s * rnd.uniform(-.7, .7), y + ny * off * side * .75, s * rnd.uniform(.5, .9) * swell, rnd.uniform(-.3, .3)))
        i += rnd.choice([2, 3, 3, 4, 5])
    peaks.sort(key=lambda p: p[1])
    body, shade, hatch = [], [], []
    for (x, y, sz, lean) in peaks:
        b, sh, h = A.peak(x, y, sz, lean)
        body.append(b)
        shade.append(sh)
        hatch.append(h)
    return "".join(body), "".join(shade), "".join(hatch)


def scatter(fr, region, rnd, spacing, density=1.0):
    lon, lat, rx, ry = region[:4]
    cx, cy = fr.xy(lon, lat)
    prx = rx * fr.pxdeg
    pry = ry * (fr.h - 2 * fr.pad) / (fr.box[3] - fr.box[2])
    n = int(math.pi * prx * pry / (spacing * spacing) * density)
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 14:
        tries += 1
        a, r = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * r * prx, cy + math.sin(a) * r * pry
        if all((x - px) ** 2 + (y - py) ** 2 > spacing * spacing * .62 for px, py in pts):
            pts.append((x, y))
    return pts


# --------------------------------------------------------------------------- text
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_w(text, size, lang, kind):
    """Approximate set width of a label — used only to reserve its collision box."""
    if lang == "fa":
        # Persian: ZWNJ/ZWJ/marks advance nothing. Use a tighter per-glyph factor so
        # collision boxes match the lighter type and labels stay near their anchors.
        n = sum(1 for c in text if c not in "\u200c\u200d\u200e\u200f\u0640")
        return max(size * 1.2, n * size * .42)
    return len(text) * size * (0.88 if kind == "r" else .72)


def nice_km(target_px, px_per_deg, lat_ref):
    km_per_deg = 111.0 * math.cos(math.radians(lat_ref))
    raw = target_px / px_per_deg * km_per_deg
    return min((10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000), key=lambda c: abs(math.log(c / raw)))


class Placer:
    def __init__(self, fr):
        self.fr, self.boxes = fr, []

    def free(self, b):
        pad = self.fr.pad + 10
        if b[0] < pad or b[1] < pad or b[2] > self.fr.w - pad or b[3] > self.fr.h - pad:
            return False
        return not any(not (b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3]) for o in self.boxes)

    def add(self, b):
        self.boxes.append(b)

    def place(self, x, y, w, h, tries=True, near=False):
        """Place a label. near=True only allows small nudges so geographic
        anchors (e.g. Arabia vs Persia) stay in their own realms."""
        offs = [(0, 0)]
        if near:
            for k in (.35, .7, 1.0, 1.4):
                offs += [(0, h * k), (0, -h * k), (w * .35 * k, 0), (-w * .35 * k, 0),
                         (w * .3 * k, h * .7 * k), (-w * .3 * k, h * .7 * k),
                         (w * .3 * k, -h * .7 * k), (-w * .3 * k, -h * .7 * k)]
        elif tries:
            for k in (1, 2, 3, 4):
                offs += [(0, h * 1.15 * k), (0, -h * 1.15 * k), (w * .55 * k, 0), (-w * .55 * k, 0),
                         (w * .4 * k, h * 1.1 * k), (-w * .4 * k, h * 1.1 * k), (w * .4 * k, -h * 1.1 * k), (-w * .4 * k, -h * 1.1 * k)]
        for dx, dy in offs:
            b = (x + dx - w / 2, y + dy - h / 2, x + dx + w / 2, y + dy + h / 2)
            if self.free(b):
                self.add(b)
                return x + dx, y + dy
        self.add((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
        return x, y


# --------------------------------------------------------------------------- build
def build(name, spec, lang):
    rnd = random.Random(sum(map(ord, name)) * 31)
    fr = Frame(spec["box"], spec["w"], spec["cos"])
    w, h, pad = fr.w, fr.h, fr.pad
    title = spec["title"][lang]
    fam = FONT_FA if lang == "fa" else FONT
    world = (fr.box[1] - fr.box[0]) > 300
    s_glyph = (max(4.2, w / 300.0) if not world else 4.6)           # terrain glyph scale
    cs = w / 1300.0                          # creature scale factor
    o = []
    A_ = o.append

    land_d, used, shifts = land_data(fr, spec)
    lakes = lake_paths(fr, used, shifts)
    rivers = river_paths(fr, used, spec)

    A_('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice" role="img" aria-label="%s">' % (w, h, esc(title)))
    A_('<!-- %s - generated by tools/genmaps.py (art: tools/mapart.py) from Natural Earth (public domain). No scripts, no external assets. -->' % esc(title))
    A_('<style>.rl{font-family:%s;font-weight:400;letter-spacing:%s;fill:%s;paint-order:stroke;stroke:%s;stroke-width:2.4px;stroke-linejoin:round;stroke-opacity:.75}'
       '.sl{font-family:%s;font-weight:300;font-style:italic;letter-spacing:%s;fill:%s;paint-order:stroke;stroke:%s;stroke-width:2.2px;stroke-linejoin:round;stroke-opacity:.78}'
       '.cl{font-family:%s;font-weight:400;letter-spacing:.06em;fill:%s;paint-order:stroke;stroke:%s;stroke-width:2.2px;stroke-linejoin:round;stroke-opacity:.78}'
       '@media (prefers-reduced-motion:reduce){*{animation:none}}</style>'
       % (fam, "0" if lang == "fa" else ".12em", TEXT, INKC, fam, "0" if lang == "fa" else ".06em", SEA_TEXT, INKC, fam, GOLD, INKC))
    A_('<defs>')
    A_('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (SEA_A, SEA_B))
    A_('<radialGradient id="seaglow" cx="50%" cy="48%" r="70%"><stop offset="0" stop-color="#2a5a78" stop-opacity=".28"/><stop offset="1" stop-color="#2a5a78" stop-opacity="0"/></radialGradient>')
    A_('<linearGradient id="land" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (LAND_A, LAND_B))
    A_('<radialGradient id="vign" cx="50%" cy="50%" r="74%"><stop offset=".55" stop-color="#03050a" stop-opacity="0"/><stop offset="1" stop-color="#03050a" stop-opacity=".72"/></radialGradient>')
    A_('<pattern id="wav" width="34" height="18" patternUnits="userSpaceOnUse"><path d="M0 10q8.5-9 17 0t17 0" fill="none" stroke="#4a7a98" stroke-width="1" opacity=".14"/></pattern>')
    A_('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.25"/></filter>')
    A_('<path id="landp" d="%s"/>' % land_d)
    A_('<clipPath id="landclip"><use href="#landp" xlink:href="#landp"/></clipPath>')
    A_('<clipPath id="inner"><rect x="%d" y="%d" width="%d" height="%d" rx="3"/></clipPath>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    textpaths = []
    A_('@@TP@@')
    A_('</defs>')

    # ---- sea
    A_('<rect width="%d" height="%d" fill="url(#sea)"/><rect width="%d" height="%d" fill="url(#seaglow)"/>' % (w, h, w, h))
    A_('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#wav)"/>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    A_('<g clip-path="url(#inner)">')
    # graticule + rhumb lines (under the land)
    g = spec["graticule"]
    gl = []
    lon = math.ceil(fr.box[0] / g) * g
    xs_g, ys_g = [], []
    while lon <= fr.box[1]:
        x = fr.xy(lon, fr.box[2])[0]
        xs_g.append(x)
        gl.append("M%.1f %dV%d" % (x, pad, h - pad))
        lon += g
    lat = math.ceil(fr.box[2] / g) * g
    while lat <= fr.box[3]:
        y = fr.xy(fr.box[0], lat)[1]
        ys_g.append(y)
        gl.append("M%d %.1fH%d" % (pad, y, w - pad))
        lat += g
    A_('<path d="%s" fill="none" stroke="#5d8fae" stroke-width=".7" opacity=".24"/>' % "".join(gl))
    cx0, cy0 = w * .62, h * .58
    A_('<path d="%s" fill="none" stroke="%s" stroke-width=".8" opacity=".12"/>' % ("".join("M%.0f %.0fl%.0f %.0f" % (cx0, cy0, math.cos(k * math.pi / 8) * w, math.sin(k * math.pi / 8) * w) for k in range(16)), GOLD))

    # ---- land (everything inside one filter so the hand-drawn wobble is shared)
    A_('<g>')
    for sw_, op in ((30, .05), (21, .08), (13, .12), (6.5, .2)):
        A_('<use href="#landp" xlink:href="#landp" fill="none" stroke="#6aa6c8" stroke-width="%.1f" stroke-linejoin="round" opacity="%.2f"/>' % (sw_, op))
    A_('<use href="#landp" xlink:href="#landp" fill="url(#land)" fill-rule="evenodd"/>')
    A_('<g clip-path="url(#landclip)">')
    A_('<rect width="%d" height="%d" filter="url(#grain)" opacity=".5"/>' % (w, h))
    A_('<use href="#landp" xlink:href="#landp" fill="none" stroke="#05080a" stroke-width="16" opacity=".4"/>')
    # deserts
    dots, dunes = [], []
    for reg in spec.get("deserts", []):
        for (x, y) in scatter(fr, reg, rnd, s_glyph * 1.25, .85):
            dots.append("M%.0f %.0fh0" % (x, y))
            if rnd.random() < .2:
                dunes.append("M%.1f %.1fq%.1f %.1f %.1f 0" % (x - s_glyph * .9, y + 2, s_glyph * .9, -s_glyph * .8, s_glyph * 1.8))
    A_('<path d="%s" fill="none" stroke="#b09a5c" stroke-width="1.5" stroke-linecap="round" opacity=".42"/><path d="%s" fill="none" stroke="#b09a5c" stroke-width=".8" opacity=".4"/>' % ("".join(dots), "".join(dunes)))
    # marshes
    mp = []
    for reg in spec.get("marshes", []):
        for (x, y) in scatter(fr, reg, rnd, s_glyph * 1.7, 1):
            mp.append(A.marsh(x, y, s_glyph * .6))
    A_('<path d="%s" fill="none" stroke="#6fa3bb" stroke-width=".8" opacity=".8"/>' % "".join(mp))
    # hills
    hp, hh = [], []
    for reg in spec.get("hills", []):
        for (x, y) in scatter(fr, reg, rnd, s_glyph * 2.2, .8):
            a_, b_ = A.hill(x, y, s_glyph * 1.3)
            hp.append(a_)
            hh.append(b_)
    A_('<path d="%s" fill="none" stroke="#c8b574" stroke-width=".9" opacity=".75"/><path d="%s" fill="none" stroke="#c8b574" stroke-width=".6" opacity=".6"/>' % ("".join(hp), "".join(hh)))
    # forests
    tb, tt = {"pine": [], "round": []}, []
    for reg in spec.get("forests", []):
        kind = reg[4]
        pts = scatter(fr, reg, rnd, s_glyph * 1.9, 1.0)
        pts.sort(key=lambda p: p[1])
        for (x, y) in pts:
            body, trunk = A.tree(x, y, s_glyph * rnd.uniform(1.1, 1.45), kind)
            tb[kind].append(body)
            tt.append(trunk)
    A_('<path d="%s" fill="#16210f" stroke="#587343" stroke-width=".8" stroke-linejoin="round"/>' % "".join(tb["pine"]))
    A_('<path d="%s" fill="#1e2e16" stroke="#6b8749" stroke-width=".8"/>' % "".join(tb["round"]))
    A_('<path d="%s" fill="none" stroke="#6b5a35" stroke-width=".7"/>' % "".join(tt))
    A_('</g>')                                       # end land clip
    # lakes + rivers
    if lakes:
        A_('<path d="%s" fill="#0f2434" fill-rule="evenodd" stroke="%s" stroke-width="1" opacity=".95"/>' % (lakes, GOLD_DIM))
    for d, wd in rivers:
        A_('<path d="%s" fill="none" stroke="#06101a" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round" opacity=".7"/>' % (d, wd + 1.6))
        A_('<path d="%s" fill="none" stroke="#4f8fb5" stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round"/>' % (d, wd))
    # mountains
    mb, ms, mh = [], [], []
    for rng_ll in spec.get("ranges", []):
        b_, s_, h_ = mountains(fr, rng_ll, rnd, s_glyph * 1.9)
        mb.append(b_)
        ms.append(s_)
        mh.append(h_)
    A_('<path d="%s" fill="#566744" stroke="#e6cf90" stroke-width=".95" stroke-linejoin="round" stroke-linecap="round"/>' % "".join(mb))
    A_('<path d="%s" fill="#141c0e" stroke="none" opacity=".92"/>' % "".join(ms))
    A_('<path d="%s" fill="none" stroke="#e6cf90" stroke-width=".7" opacity=".85"/>' % "".join(mh))
    # inked coastline
    A_('<use href="#landp" xlink:href="#landp" fill="none" stroke="%s" stroke-width="3.4" stroke-linejoin="round" opacity=".9"/>' % INKC)
    A_('<use href="#landp" xlink:href="#landp" fill="none" stroke="%s" stroke-width="1.3" stroke-linejoin="round"/>' % GOLD)
    A_('</g>')                                       # end rough filter group

    # ---- placement bookkeeping
    P = Placer(fr)
    P.add((pad, pad, pad + 14 + max(190, int(len(title) * (13.5 if lang == "fa" else 12.4)) + 64), pad + 64))       # title ribbon
    P.add((w - pad - 130, h - pad - 130, w - pad, h - pad))                                                      # compass
    P.add((pad, h - pad - 70, pad + 330, h - pad))                                                              # scale bar
    for (_, plon, plat) in PINS.get(name, []):
        px, py = fr.xy(plon, plat)
        # Culture-sheet pins are drawn in the SVG; keep a small keep-out so a
        # label does not sit on the dot. World-map pins are HTML overlays — do
        # not reserve boxes for them or Near East names get shoved together.
        if not world:
            P.add((px - 14, py - 22, px + 14, py + 10))
    # ---- ships, then creatures (sea ones sit on the water, land ones on the land)
    deco = []
    for kind, lon, lat, sc, flip in spec.get("ships", []):
        x, y = fr.xy(lon, lat)
        size = sc * cs * (1.55 if not world else 1.05)
        P.add((x - 24 * size, y - 24 * size, x + 24 * size, y + 14 * size))
        deco.append(A.creature(kind, x, y, size, bool(flip)))
        deco.append('<path d="M%.1f %.1fq3-2.2 6 0t6 0t6 0M%.1f %.1fq3-2.2 6 0t6 0" fill="none" stroke="#7fb0cf" stroke-width=".8" opacity=".5"/>' % (x - 15 * size, y + 8 * size, x - 9 * size, y + 11.4 * size))
    for c in spec.get("creatures", []):
        kind, lon, lat, sc, flip = c[:5]
        label = c[5] if len(c) > 5 else None
        x, y = fr.xy(lon, lat)
        size = sc * cs * (1.5 if not world else 1.0)
        P.add((x - 24 * size, y - 24 * size, x + 24 * size, y + 20 * size))
        deco.append(A.creature(kind, x, y, size, bool(flip)))
        if label:
            lab = label if lang == "en" else FA.get(label, label)
            deco.append('<text class="cl" x="%.0f" y="%.0f" font-size="%.0f" text-anchor="middle">%s</text>' % (x, y + 19 * size + 8, max(10, 10.5 * cs * 1.2), esc(lab)))
            P.add((x - 40, y + 19 * size - 2, x + 40, y + 19 * size + 14))
    # ---- labels
    # Near East names stay near their anchors so Arabia/Persia/Scythia never merge.
    STICKY = {"ARABIA", "PERSIA", "SCYTHIA", "INDIA", "MESOPOTAMIA", "EUROPA"}
    labs = sorted(spec["labels"], key=lambda l: -l[3])
    lab_out = []
    for i, (text, lon, lat, size, kind) in enumerate(labs):
        label = text if lang == "en" else FA.get(text, text)
        sz = size * cs * (WORLD_SCALE if world else 1.0) * TYPE_SIZE[kind][lang if lang in TYPE_SIZE[kind] else "en"]
        bw, bh = text_w(label, sz, lang, kind), sz * 1.35
        x0, y0 = fr.xy(lon, lat)
        x, y = P.place(x0, y0, bw, bh, near=(text in STICKY and world))
        L = bw * .62 + 18
        curve = (L * (.11 if kind == "r" else .15)) * (1 if i % 2 == 0 else -1) * (1 if kind == "s" else .8)
        pid = "lp%d" % i
        textpaths.append('<path id="%s" d="M%.1f %.1fQ%.1f %.1f %.1f %.1f"/>' % (pid, x - L, y, x, y - 2 * curve, x + L, y))
        cls = "rl" if kind == "r" else "sl"
        lab_out.append('<text class="%s" font-size="%.1f" text-anchor="middle"><textPath href="#%s" xlink:href="#%s" startOffset="50%%">%s</textPath></text>' % (cls, sz, pid, pid, esc(label)))
    A_("".join(deco))
    A_("".join(lab_out))
    A_('</g>')                                       # end inner clip

    # ---- vignette, ladder border, ticks
    A_('<rect width="%d" height="%d" fill="url(#vign)"/>' % (w, h))
    A_('<rect x="7" y="7" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2" rx="6"/>' % (w - 14, h - 14, GOLD))
    A_('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="%s" stroke-width=".9" rx="3"/>' % (pad - 1, pad - 1, w - 2 * pad + 2, h - 2 * pad + 2, GOLD))
    lad = []
    def ladder(positions, lo, hi, horiz, edge):
        pos = [lo] + [p for p in positions if lo < p < hi] + [hi]
        for i in range(len(pos) - 1):
            if i % 2 == 0:
                a, b = pos[i], pos[i + 1]
                if horiz:
                    lad.append('<rect x="%.1f" y="%d" width="%.1f" height="9"/>' % (a, edge, b - a))
                else:
                    lad.append('<rect x="%d" y="%.1f" width="9" height="%.1f"/>' % (edge, a, b - a))
    ladder(xs_g, pad, w - pad, True, 8)
    ladder(xs_g, pad, w - pad, True, h - 17)
    ladder(ys_g, pad, h - pad, False, 8)
    ladder(ys_g, pad, h - pad, False, w - 17)
    A_('<g fill="%s" opacity=".85">%s</g>' % (GOLD_DIM, "".join(lad)))
    A_('<g stroke="%s" stroke-width="1.3" fill="none" opacity=".6"><path d="M14 40q4-18 22-22"/><path d="M%d 14q18 4 22 22"/><path d="M14 %dq4 18 22 22"/><path d="M%d %dq18-4 22-22"/></g>' % (GOLD, w - 36, h - 36, w - 36, h - 14))

    # ---- title ribbon (top-left)
    tw = max(190, int(len(title) * (13.5 if lang == "fa" else 12.4)) + 64)
    x0, y0 = pad + 12, pad + 10
    A_('<g><path d="M%d %dh%dv34h-%dl-12-17z" fill="#070b11" fill-opacity=".9" stroke="%s" stroke-width="1.2"/>' % (x0, y0 + 6, tw, tw, GOLD))
    A_('<path d="M%d %dl-14 -4v28l14-4z" fill="#0c1218" stroke="%s" stroke-width="1"/><path d="M%d %dl14-4v28l-14-4z" fill="#0c1218" stroke="%s" stroke-width="1"/>' % (x0 + 4, y0 + 10, GOLD, x0 + tw - 4, y0 + 10, GOLD))
    A_('<text x="%d" y="%d" font-family=\'%s\' font-size="%d" font-weight="600" fill="%s" text-anchor="middle" letter-spacing="%s">%s</text></g>' % (x0 + tw // 2, y0 + 29, fam.replace('"', ''), 16 if lang == "en" else 17, TEXT, "0" if lang == "fa" else ".12em", esc(title.upper() if lang == "en" else title)))

    # ---- compass rose (bottom-right)
    cx, cy, R = w - pad - 62, h - pad - 62, 44
    A_('<g transform="translate(%d %d)"><circle r="%d" fill="#070b11" fill-opacity=".72" stroke="%s" stroke-width="1.2"/><circle r="%d" fill="none" stroke="%s" stroke-width=".6" opacity=".7"/>' % (cx, cy, R + 12, GOLD, R + 8, GOLD))
    pts16 = []
    for k in range(16):
        ang = k * math.pi / 8 - math.pi / 2
        ln = R if k % 4 == 0 else (R * .68 if k % 2 == 0 else R * .44)
        wd = .15 if k % 2 == 0 else .12
        tip = (math.cos(ang) * ln, math.sin(ang) * ln)
        l = (math.cos(ang - wd * 2) * R * .22, math.sin(ang - wd * 2) * R * .22)
        r = (math.cos(ang + wd * 2) * R * .22, math.sin(ang + wd * 2) * R * .22)
        A_('<path d="M0 0L%.1f %.1fL%.1f %.1fZ" fill="%s" stroke="%s" stroke-width=".5"/><path d="M0 0L%.1f %.1fL%.1f %.1fZ" fill="#0c1218" stroke="%s" stroke-width=".5"/>' % (l[0], l[1], tip[0], tip[1], GOLD, GOLD, tip[0], tip[1], r[0], r[1], GOLD))
    A_('<circle r="4.2" fill="#070b11" stroke="%s" stroke-width="1"/><path d="M0 %.0fl-5-7q5 3 5 0q0 0 0 0q5 3 5 0z" fill="%s" opacity=".0"/>' % (GOLD, -R - 2, GOLD))
    A_('<path d="M0 %d l-5 -8 q5 3 10 0z" fill="%s"/><text class="cl" y="%d" font-size="14" text-anchor="middle">%s</text></g>' % (-R - 5, GOLD, -R - 16, "N" if lang == "en" else "ش"))

    # ---- scale bar (bottom-left)
    ref_lat = (fr.box[2] + fr.box[3]) / 2
    km = nice_km(0.17 * (w - 2 * pad), fr.pxdeg, ref_lat)
    bar = km / (111.0 * math.cos(math.radians(ref_lat))) * fr.pxdeg
    sx, sy = pad + 26, h - pad - 30
    A_('<g transform="translate(%.0f %.0f)"><rect x="-8" y="-24" width="%.0f" height="44" rx="5" fill="#070b11" fill-opacity=".7"/>' % (sx, sy, bar + 16))
    for i in range(4):
        A_('<rect x="%.1f" width="%.1f" height="5" fill="%s" stroke="%s" stroke-width=".6"/>' % (i * bar / 4, bar / 4, GOLD if i % 2 == 0 else "#070b11", GOLD))
    A_('<text class="cl" x="0" y="-8" font-size="11" text-anchor="start">0</text><text class="cl" x="%.0f" y="-8" font-size="11" text-anchor="end">%s</text></g>' % (bar, ("%d km" % km) if lang == "en" else ("%d کیلومتر" % km)))

    A_('</svg>')
    svg = "\n".join(o).replace("@@TP@@", "".join(textpaths))
    svg = re.sub(r'<path d=""[^>]*/>', "", svg)
    uid = name + ("-fa" if lang == "fa" else "")
    ids = set(re.findall(r' id="([^"]+)"', svg))
    for i_ in sorted(ids, key=len, reverse=True):
        svg = (svg.replace(' id="%s"' % i_, ' id="%s-%s"' % (uid, i_)).replace("url(#%s)" % i_, "url(#%s-%s)" % (uid, i_))
               .replace('href="#%s"' % i_, 'href="#%s-%s"' % (uid, i_)))
    minidom.parseString(svg)
    path = os.path.join(OUT, name + ("" if lang == "en" else "-fa") + ".svg")
    with open(path, "w") as f:
        f.write(svg)
    return path, len(svg), (w, h), used


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    only = [a for a in sys.argv[1:] if a in MAPS] or list(MAPS)
    for nm in only:
        for lg in ("en", "fa"):
            p, size, dim, used = build(nm, MAPS[nm], lg)
            print("%-30s %7.1f KB  %s  land %sm" % (os.path.relpath(p, ROOT), size / 1024, dim, used))
    print("\nreference pin coordinates (% of the map box; unchanged by the art):")
    for nm, items in PINS.items():
        print(" ", nm)
        for label, lon, lat in items:
            x, y = pct(lon, lat, MAPS[nm]["box"])
            print("    %-14s x=%.1f%% y=%.1f%%" % (label, x, y))
