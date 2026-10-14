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
GEO = os.path.join(ROOT, "tools", "geo", "ne_50m_land.geojson")
GEO_LO = os.path.join(ROOT, "tools", "geo", "ne_110m_land.geojson")  # fallback
OUT = os.path.join(ROOT, "static", "img", "maps")

GOLD = "#c9a45c"
LAND = "#1a2416"
LAND2 = "#0c110b"
SEA = "#0a1420"
SEA2 = "#04080e"
TEXT = "#d8c9a8"
SEA_TEXT = "#6a8fa8"

import map_creatures  # noqa: E402 — approved beasts only (empty during redesign)

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


def simplify_ring(ring, tol_deg=0.12):
    """Drop nearly-collinear vertices so 50m coasts stay detailed but SVG-sized."""
    if len(ring) < 8:
        return ring
    out = [ring[0]]
    for i in range(1, len(ring) - 1):
        ax, ay = out[-1]
        bx, by = ring[i]
        cx, cy = ring[i + 1]
        # perpendicular distance of B from AC in degrees
        dx, dy = cx - ax, cy - ay
        L2 = dx * dx + dy * dy or 1.0
        t = max(0.0, min(1.0, ((bx - ax) * dx + (by - ay) * dy) / L2))
        px, py = ax + t * dx, ay + t * dy
        if (bx - px) ** 2 + (by - py) ** 2 > tol_deg * tol_deg:
            out.append(ring[i])
    out.append(ring[-1])
    return out if len(out) >= 4 else ring


def ring_path(ring, box, w, h, pad, copies=(-360, 0, 360), tol_deg=0.12):
    """Path for one ring; drawn 3x so anything crossing the antimeridian stays joined."""
    ring = simplify_ring(ring, tol_deg=tol_deg)
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


ORN_LIT, ORN_MID, ORN_SHADE = "#9a8250", "#5a4830", "#05070c"
ORN_SNOW, ORN_SNOW_SH = "#f6ecc4", "#8a7a58"
ORN_TREE_LIT, ORN_TREE_MID, ORN_TREE_DARK = "#3a5a2c", "#1a2e16", "#0c180b"


def _ornament_defs():
    """Shared gradients/filters for peaks + trees (emitted once per map)."""
    return (
        '<linearGradient id="mt-b" x1="0%" y1="20%" x2="100%" y2="80%">'
        '<stop offset="0%" stop-color="{lit}"/>'
        '<stop offset="38%" stop-color="{mid}"/>'
        '<stop offset="62%" stop-color="{shade}"/>'
        '<stop offset="100%" stop-color="#020204"/>'
        '</linearGradient>'
        '<linearGradient id="mt-s" x1="15%" y1="0%" x2="90%" y2="100%">'
        '<stop offset="0%" stop-color="{snow}"/>'
        '<stop offset="45%" stop-color="#d8c9a0"/>'
        '<stop offset="100%" stop-color="{snow_sh}"/>'
        '</linearGradient>'
        '<radialGradient id="mt-g" cx="35%" cy="30%" r="70%">'
        '<stop offset="0%" stop-color="{lit}"/>'
        '<stop offset="55%" stop-color="{mid}"/>'
        '<stop offset="100%" stop-color="{shade}"/>'
        '</radialGradient>'
        '<linearGradient id="tr-c" x1="0%" y1="20%" x2="100%" y2="85%">'
        '<stop offset="0%" stop-color="{tlit}"/>'
        '<stop offset="45%" stop-color="{tmid}"/>'
        '<stop offset="100%" stop-color="{tdark}"/>'
        '</linearGradient>'
        '<radialGradient id="tr-ball" cx="32%" cy="28%" r="72%">'
        '<stop offset="0%" stop-color="{tlit}"/>'
        '<stop offset="55%" stop-color="{tmid}"/>'
        '<stop offset="100%" stop-color="{tdark}"/>'
        '</radialGradient>'
        '<filter id="mt-f" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="1.6"/>'
        '</filter>'
    ).format(lit=ORN_LIT, mid=ORN_MID, shade=ORN_SHADE, snow=ORN_SNOW, snow_sh=ORN_SNOW_SH,
             tlit=ORN_TREE_LIT, tmid=ORN_TREE_MID, tdark=ORN_TREE_DARK)


def _peak_stack(x, y, s, shade, rock, mid, lit_rock, snow, crest, deep,
                lean=0.0, texture=True):
    """Gradient-shaded cone with SE soft shadow — shared mt-* paints."""
    parts = []
    tip = (x + lean * s * 0.14, y - s * 1.72)
    bl = (x - s * 1.18, y + s * 0.14)
    br = (x + s * 1.28, y + s * 0.26)
    bf = (x + lean * s * 0.1 + s * 0.12, y + s * 0.52)
    parts.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".55" '
        'filter="url(#mt-f)"/>' % (x + s * 0.3, y + s * 0.6, s * 1.35, s * 0.42, deep))
    parts.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#mt-g)" opacity=".95"/>'
        % (x + lean * s * 0.04, y + s * 0.3, s * 1.12, s * 0.34))
    parts.append(
        '<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="url(#mt-b)"/>'
        % (tip[0], tip[1], bl[0], bl[1], br[0], br[1]))
    parts.append(
        '<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="%s" opacity=".55"/>'
        % (bl[0] * 0.4 + tip[0] * 0.6, bl[1] * 0.35 + tip[1] * 0.65,
           br[0] * 0.4 + tip[0] * 0.6, br[1] * 0.35 + tip[1] * 0.65,
           bf[0], bf[1], shade))
    parts.append(
        '<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="%s" opacity=".4"/>'
        % (bl[0] * 0.4 + tip[0] * 0.6, bl[1] * 0.35 + tip[1] * 0.65,
           tip[0], tip[1] + s * 0.55, bf[0] - s * 0.15, bf[1], mid))
    parts.append(
        '<path d="M%.1f %.1fL%.1f %.1f" fill="none" stroke="%s" stroke-width="%.2f" '
        'opacity=".35" stroke-linecap="round"/>'
        % (tip[0], tip[1], bf[0] - s * 0.05, bf[1] - s * 0.1, crest, max(0.7, s * 0.05)))
    snow_tip = (tip[0] - lean * s * 0.02, tip[1] - s * 0.1)
    sl = (tip[0] * 0.45 + bl[0] * 0.55, tip[1] * 0.5 + bl[1] * 0.5)
    sr = (tip[0] * 0.45 + br[0] * 0.55, tip[1] * 0.5 + br[1] * 0.5)
    parts.append(
        '<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="url(#mt-s)"/>'
        % (snow_tip[0], snow_tip[1], sl[0], sl[1], sr[0], sr[1]))
    parts.append(
        '<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="%s" opacity=".85"/>'
        % (snow_tip[0], snow_tip[1],
           snow_tip[0] - s * 0.16, snow_tip[1] + s * 0.28,
           snow_tip[0] + s * 0.02, snow_tip[1] + s * 0.22, "#fff8e0"))
    if texture:
        for k in range(2):
            t = 0.35 + k * 0.25
            ax = tip[0] + (br[0] - tip[0]) * t
            ay = tip[1] + (br[1] - tip[1]) * t
            bx = tip[0] + (br[0] - tip[0]) * (t + 0.1) + (bl[0] - tip[0]) * 0.08
            by = tip[1] + (br[1] - tip[1]) * (t + 0.1) + (bl[1] - tip[1]) * 0.08
            parts.append(
                '<path d="M%.1f %.1fL%.1f %.1f" fill="none" stroke="%s" stroke-width="0.55" '
                'opacity=".25"/>' % (ax, ay, bx, by, "#000"))
    return "".join(parts), tip, s



def mountain_range(points, box, w, h, pad, step=6.2, scale=1.0, rows=1):
    """Volumetric ridge wall — cones with lit/shade + ground shadow, rising screen-up."""
    shade, rock, mid = "#05070c", "#3a2e1e", "#5a4830"
    lit_rock, snow, crest, deep = "#8a7248", "#f2e6b8", "#e0d2a8", "#000000"
    parts = []
    for row in range(rows):
        row_off = row * 5.5 * scale
        acc = 0.0
        prev = None
        peak_i = 0
        for lon, lat in points:
            pt = project(lon, lat, box, w, h, pad)
            if prev:
                seg = math.hypot(pt[0] - prev[0], pt[1] - prev[1])
                dx = (pt[0] - prev[0]) / (seg or 1)
                dy = (pt[1] - prev[1]) / (seg or 1)
                ox, oy = -dy * row_off * 0.12, row_off
                while acc < seg:
                    x = prev[0] + dx * acc + ox
                    y = prev[1] + dy * acc + oy
                    jitter = 0.75 + 0.55 * ((peak_i * 37 + row * 13) % 5) / 4.0
                    s = 10.5 * jitter * scale * (1.0 - row * 0.1)
                    lean = ((peak_i * 19 + row * 7) % 7 - 3) / 3.0
                    frag, tip, ss = _peak_stack(
                        x, y, s, shade, rock, mid, lit_rock, snow, crest, deep,
                        lean=lean, texture=(peak_i % 2 == 0))
                    parts.append(frag)
                    if peak_i % 2 == 0:
                        frag2, *_ = _peak_stack(
                            x + ss * 0.4, y + ss * 0.1, ss * 0.65,
                            shade, rock, mid, lit_rock, snow, crest, deep,
                            lean=-lean * 0.5, texture=False)
                        parts.append(frag2)
                    if scale >= 1.2 and peak_i % 3 == 1:
                        frag3, *_ = _peak_stack(
                            x - ss * 0.35, y + ss * 0.15, ss * 0.5,
                            shade, rock, mid, lit_rock, snow, crest, deep,
                            lean=lean * 0.35, texture=False)
                        parts.append(frag3)
                    acc += step * (0.72 + 0.18 * ((peak_i * 11) % 3) / 2.0) / max(scale * 0.85, 0.75)
                    peak_i += 1
                acc -= seg
            prev = pt
    return "".join(parts)


def sculpted_peak(lon, lat, box, w, h, pad, scale=1.7, label=None, lang="en"):
    """Named summit (Damavand) — oversized gradient cone + shoulders + soft shadow."""
    shade, rock, mid = ORN_SHADE, "#3a2e1e", ORN_MID
    lit_rock, snow, crest, deep = ORN_LIT, ORN_SNOW, "#e8dcb0", "#000000"
    x, y = project(lon, lat, box, w, h, pad)
    s = 30.0 * scale
    parts = []
    parts.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".6" '
        'filter="url(#mt-f)"/>' % (x + s * 0.4, y + s * 0.7, s * 1.85, s * 0.58, deep))
    parts.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#mt-g)" opacity=".98"/>'
        % (x + s * 0.05, y + s * 0.38, s * 1.5, s * 0.48))
    tip_lo = (x + s * 0.05, y - s * 0.35)
    parts.append(
            '<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="url(#mt-b)"/>'
        % (tip_lo[0], tip_lo[1], x - s * 1.45, y + s * 0.35, x + s * 1.55, y + s * 0.45))
    # foothills first (behind), then main cone in front
    parts.append(_peak_stack(x - s * 0.85, y + s * 0.4, s * 0.48, shade, rock, mid, lit_rock, snow, crest, deep,
                             lean=-0.4, texture=True)[0])
    parts.append(_peak_stack(x + s * 0.82, y + s * 0.48, s * 0.44, shade, rock, mid, lit_rock, snow, crest, deep,
                             lean=0.45, texture=False)[0])
    main = _peak_stack(x, y - s * 0.15, s * 0.95, shade, rock, mid, lit_rock, snow, crest, deep,
                       lean=0.06, texture=True)
    parts.append(main[0])
    tip = main[1]
    parts.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".9"/>'
        % (tip[0] + s * 0.01, tip[1] - s * 0.08, s * 0.14, s * 0.05, "#fff8e0"))
    parts.append(
        '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".55"/>'
        % (tip[0] + s * 0.04, tip[1] - s * 0.06, s * 0.08, s * 0.028, shade))
    if label:
        lab = label if lang == "en" else FA.get(label, label)
        parts.append(
            '<text class="lb" x="%.0f" y="%.0f" font-size="13" text-anchor="middle" '
            'stroke="#05070b" stroke-width="3.2" paint-order="stroke" opacity=".96" '
            'letter-spacing=".12em">%s</text>'
            % (x, tip[1] - s * 0.28, esc(lab)))
    return "".join(parts)



def tree_mark(kind="pine"):
    """Forest stamp with gradient volume: soft shadow + lit→shade crowns."""
    rim, trunk, deep = "#6a8a3e", "#1a140c", "#000000"
    mid = ORN_TREE_MID
    parts = []
    if kind == "palm":
        parts.append(
            '<ellipse cx="1.5" cy="7.8" rx="10" ry="2.4" fill="%s" opacity=".5" filter="url(#mt-f)"/>'
            % deep)
        for ox, oy, sc in [(-5.5, 1.2, 0.85), (5.2, 0.8, 0.9), (0, 0, 1.05),
                           (-2.8, 3.5, 0.7), (3.2, 3.2, 0.72)]:
            parts.append(
                '<g transform="translate(%.1f %.1f) scale(%.2f)">'
                '<path d="M-0.9 7L-0.3-1L0.4-1L0.8 7Z" fill="%s"/>'
                '<path d="M-0.9 7L-0.3-1L0.05-1L-0.1 7Z" fill="%s" opacity=".65"/>'
                '<ellipse cx="0" cy="-3.0" rx="5.4" ry="3.6" fill="url(#tr-ball)"/>'
                '<path d="M-5.5-2.2Q-2.2-7.2 0-3.2Q2.2-7.2 5.5-2.2" fill="none" stroke="%s" '
                'stroke-width="1.1" stroke-linecap="round" opacity=".75"/>'
                '</g>' % (ox, oy, sc, trunk, mid, rim)
            )
        return "".join(parts)
    if kind == "deciduous":
        canopy = [
            (-6.5, -1.0, 5.2, 4.0), (6.0, -0.5, 5.0, 3.8), (0, -3.5, 6.2, 4.6),
            (-3.5, 2.0, 4.4, 3.4), (3.8, 2.2, 4.2, 3.2), (-1.5, -6.0, 3.6, 2.8),
            (2.0, -5.5, 3.4, 2.6), (0.5, 4.0, 3.8, 2.8),
        ]
        parts.append(
            '<ellipse cx="1.5" cy="7.2" rx="11" ry="2.8" fill="%s" opacity=".5" filter="url(#mt-f)"/>'
            % deep)
        for cx, cy, rx, ry in canopy:
            parts.append(
                '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#tr-ball)"/>'
                % (cx, cy, rx, ry))
        return "".join(parts)
    clumps = [
        (-6.2, 1.5, 0.82), (6.0, 1.2, 0.85), (-2.5, -1.5, 0.95),
        (2.8, -1.2, 0.92), (0, -4.0, 1.1), (-4.5, 4.0, 0.7),
        (4.2, 4.2, 0.72), (0.5, 3.5, 0.78), (-1.0, 6.0, 0.65),
    ]
    parts.append(
        '<ellipse cx="1.2" cy="8.0" rx="12" ry="2.8" fill="%s" opacity=".48" filter="url(#mt-f)"/>'
        % deep)
    for ox, oy, sc in clumps:
        parts.append(
            '<g transform="translate(%.1f %.1f) scale(%.2f)">'
            '<path d="M-1.1 6.5L-0.6-1.5L0.2-1.5L0.9 6.5Z" fill="%s"/>'
            '<path d="M-1.1 6.5L-0.6-1.5L-0.15-1.5L-0.2 6.5Z" fill="%s" opacity=".65"/>'
            '<path d="M0-8.2L5.4-1.8H-5.4Z" fill="url(#tr-c)"/>'
            '<path d="M0-5.2L6.2 1.6H-6.2Z" fill="url(#tr-c)"/>'
            '<path d="M0-2.2L7.0 5.0H-7.0Z" fill="url(#tr-c)"/>'
            '<path d="M0-8.2L-5.4-1.8" fill="none" stroke="%s" stroke-width=".85" opacity=".65"/>'
            '</g>' % (ox, oy, sc, trunk, mid, rim)
        )
    return "".join(parts)



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
        ranges=[
            # Andes
            [(-74, 8), (-72, 0), (-70, -10), (-70, -20), (-71, -30), (-72, -40)],
            # Rockies
            [(-120, 50), (-118, 45), (-115, 40), (-112, 35), (-110, 32)],
            # Alps / Caucasus / Himalaya sketch
            [(6, 46), (10, 46), (14, 46)],
            [(42, 42), (46, 41), (50, 40)],
            [(72, 34), (78, 30), (84, 28), (90, 28), (95, 28)],
        ],
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
        # world sheet: no beasts (atlas-scale doodles read as continents; culture maps carry the bestiary)
        creatures=[],
        forests=[
            # Amazonia carpet
            (-65, -2, 1.15, "palm"), (-60, -5, 1.1, "palm"), (-55, -1, 1.05, "palm"),
            (-50, 2, 1.1, "palm"), (-62, -8, 1.0, "palm"), (-48, -6, 1.0, "palm"),
            (-58, 2, 1.05, "palm"), (-70, -4, .95, "palm"), (-52, -3, 1.0, "palm"),
            (-67, -6, .95, "palm"), (-45, 0, .9, "palm"),
            # boreal belts
            (-110, 52, 1.05, "pine"), (-100, 55, 1.1, "pine"), (-90, 52, 1.05, "pine"),
            (-85, 48, 1.0, "pine"), (-95, 50, .95, "pine"), (15, 58, 1.05, "pine"),
            (25, 60, 1.1, "pine"), (35, 58, 1.0, "pine"), (45, 56, 1.0, "pine"),
            (80, 56, 1.05, "pine"), (95, 58, 1.0, "pine"), (105, 52, .95, "pine"),
            (20, 55, .95, "pine"), (55, 58, .9, "pine"),
            # monsoon / equatorial
            (78, 18, 1.0, "deciduous"), (82, 22, .95, "deciduous"), (100, 15, 1.05, "palm"),
            (108, 18, 1.0, "palm"), (115, 22, .95, "palm"), (10, 5, .95, "deciduous"),
            (20, 8, .9, "deciduous"), (-5, 45, .95, "deciduous"), (12, 3, .9, "palm"),
            (105, 12, .9, "palm"),
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
        # beasts redesign in progress — none until approved one-by-one
        creatures=[],
        forests=[
            # Levant cedar belt — dense carpet
            (35.5, 33.8, 1.05, "pine"), (35.8, 34.2, 1.1, "pine"), (36.2, 34.6, 1.0, "pine"),
            (36.4, 35.0, .95, "pine"), (36.8, 34.4, 1.0, "pine"), (37.2, 34.6, 1.05, "pine"),
            (37.6, 35.0, .9, "pine"), (35.2, 34.5, .9, "pine"),
            # Zagros foothills / N Mesopotamia
            (46.5, 35.5, .95, "deciduous"), (45.8, 35.8, .9, "deciduous"),
            (47.2, 34.8, .85, "deciduous"), (42.5, 36.2, .9, "deciduous"),
            (43.2, 36.5, .85, "deciduous"), (41.8, 36.0, .8, "pine"),
            (48.5, 34.2, .8, "deciduous"), (33.5, 37.2, .85, "pine"),
        ],
        graticule=5,
    ),
    "persia": dict(
        box=(42, 72, 24, 40), w=1200, center=32,
        title={"en": "The Iranian Plateau", "fa": "فلات ایران"},
        labels=[
            ("MEDIA", 48.2, 35.6, 15, "r", 0),
            ("PERSIA", 54.2, 31.8, 17, "r", 0),
            ("PARTHIA", 58.6, 36.4, 15, "r", 0),
            ("ARIA", 64, 33.4, 14, "r", 0),
            ("KAVIR DESERT", 55.8, 34.8, 11, "r", -10),
            ("CASPIAN SEA", 51, 37.6, 13, "s", 0),
            ("PERSIAN GULF", 49.8, 29.4, 13, "s", -30),
            ("GULF OF OMAN", 58.5, 25.4, 13, "s", 0),
            ("ARABIAN SEA", 65, 25.4, 13, "s", 0),
            ("TRANSOXIANA", 64, 38.4, 13, "r", 0),
        ],
        ranges=[
            # Alborz — denser wall; Damavand summit drawn separately on top
            {"pts": [(48.8, 36.4), (51.2, 36.25), (52.4, 36.1), (54.2, 36.35), (55.5, 36.5)],
             "scale": 1.2, "step": 5.0, "rows": 2},
            {"pts": [(45, 36.5), (46.8, 33), (49.5, 30.5), (53, 28), (56, 26.8)],
             "scale": 1.1, "step": 5.6},
            [(58, 38.4), (61.5, 37.4)],
            [(64, 35.5), (68, 35.2), (71, 35.5)],
        ],
        # named summit mark (artwork; pin overlay still used on content pages)
        peaks=[
            ("DAMAVAND", 53.06, 35.95, 2.55),
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
        creatures=[],
        forests=[
            # Caspian / Alborz forest carpet (keep clear of Damavand ~53.06,35.95)
            (49.0, 36.2, 1.0, "pine"), (49.5, 36.0, 1.05, "pine"), (50.2, 36.1, 1.0, "pine"),
            (51.0, 36.2, .95, "pine"), (51.6, 36.35, 1.0, "pine"),
            (54.6, 36.35, .95, "pine"), (55.2, 36.2, .85, "pine"),
            # Zagros woodlands
            (45.5, 35.5, .9, "pine"), (46.0, 34.5, .95, "deciduous"), (46.8, 34.0, .9, "deciduous"),
            (47.5, 33.5, .9, "deciduous"), (48.2, 34.0, .85, "deciduous"), (48.8, 32.8, .8, "deciduous"),
            (50.0, 33.0, .8, "deciduous"), (45.2, 36.0, .85, "pine"),
            # Hindu Kush foothills
            (65.5, 34.5, .95, "deciduous"), (66.2, 34.8, .9, "deciduous"), (67.0, 35.0, .9, "deciduous"),
            (67.8, 34.6, .85, "deciduous"), (64.8, 35.0, .85, "pine"),
        ],
        graticule=5,
    ),
    "india": dict(
        box=(64, 104, 5, 34), w=1200, center=32,
        title={"en": "India and the Indus", "fa": "هند و سند"},
        labels=[
            ("INDIA", 78, 22.4, 20, "r", 0),
            ("HIMALAYA", 79, 31.6, 16, "r", -6),
            ("THAR DESERT", 71.4, 27, 13, "r", -20),
            ("DECCAN", 77, 17.6, 14, "r", 0),
            ("BENGAL", 89.4, 23, 13, "r", 0),
            ("ARABIAN SEA", 71.4, 15, 14, "s", -12),
            ("BAY OF BENGAL", 87, 15.4, 14, "s", -14),
            ("INDIAN OCEAN", 80, 7, 14, "s", 0),
        ],
        ranges=[
            # Himalaya — great wall: multi-row, heavy scale, tight step
            {"pts": [(72, 33.4), (76, 32.4), (80, 30.4), (84, 28.4), (88, 27), (92, 27)],
             "scale": 1.85, "step": 4.0, "rows": 4},
            {"pts": [(74, 27), (75.6, 24.4), (76.6, 22.6)], "scale": 1.05, "step": 5.8},
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
        creatures=[],
        forests=[
            # Gangetic / Deccan woodlands
            (77, 22, 1.0, "deciduous"), (78.5, 21, .95, "deciduous"), (79, 20, .95, "deciduous"),
            (80.5, 20.5, 1.0, "deciduous"), (82, 21, 1.05, "deciduous"), (84, 20, .95, "deciduous"),
            (81, 23, .9, "deciduous"), (76, 24, .85, "deciduous"), (83, 22, .9, "deciduous"),
            # Bengal / coastal
            (88, 23, 1.0, "palm"), (89, 22.5, .95, "palm"), (90, 22, .95, "palm"),
            (91.5, 21, .9, "palm"), (87, 24, .9, "palm"), (92, 22, .85, "palm"),
            (74, 15, .9, "palm"), (75, 13.5, .85, "palm"), (76, 12, .85, "palm"),
            (85, 18, .95, "deciduous"), (86.5, 19, .9, "deciduous"), (73, 18, .8, "palm"),
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
        creatures=[],
        forests=[
            (21.2, 39.8, .9, "pine"), (21.5, 39.5, .95, "pine"), (22.2, 40.2, .9, "pine"),
            (22.8, 38.2, .85, "deciduous"), (23.2, 39.0, .8, "pine"), (30.5, 37.8, .9, "pine"),
            (31.2, 38.0, .85, "pine"), (29.8, 37.5, .8, "pine"), (27.5, 38.5, .85, "deciduous"),
            (26.8, 39.2, .8, "deciduous"), (18.5, 40.5, .75, "pine"), (33.5, 36.8, .8, "pine"),
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
        creatures=[],
        forests=[
            # Scandinavian taiga carpet
            (10, 61, 1.05, "pine"), (11.5, 62, 1.0, "pine"), (12, 63, 1.0, "pine"),
            (13.5, 64, 1.0, "pine"), (15, 64.5, 1.05, "pine"), (16.5, 65, 1.0, "pine"),
            (14, 62.5, .95, "pine"), (17, 63, .95, "pine"), (18, 62, .95, "pine"),
            (20, 63.5, .95, "pine"), (25, 65, 1.0, "pine"), (26.5, 64, .95, "pine"),
            (27, 63, .95, "pine"), (22, 64, .9, "pine"), (8, 58, .9, "deciduous"),
            (9.5, 59.5, .9, "pine"), (7.5, 60.5, .85, "pine"), (11, 59.5, .85, "pine"),
            (-18, 64.5, .9, "pine"), (-16, 65, .85, "pine"), (-19.5, 64, .85, "pine"),
            (-17, 63.5, .8, "pine"),
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
    "HIMALAYA": "هیمالیا", "DAMAVAND": "دماوند", "THAR DESERT": "صحرای تار", "DECCAN": "دکن",
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
# Approved beasts only — see tools/map_creatures.py (empty until redesign lands).
CREATURE_ART = map_creatures.CREATURE_ART


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
    A('<!-- %s - generated by tools/genmaps.py from Natural Earth 1:50m land (public domain). Dark sea, olive land, gold coast; compass, cartouche and scale bar for the house art direction. No scripts, no external assets. -->' % lang_title)
    A('<style>.lb{font-family:Georgia,"Times New Roman",serif;letter-spacing:.06em;fill:%s}.sea-lb{font-family:Georgia,"Times New Roman",serif;letter-spacing:.05em;fill:%s;font-style:italic}@media (prefers-reduced-motion:reduce){*{animation:none}}</style>' % (GOLD, SEA_TEXT))
    if lang == "fa":
        A('<style>.lb,.sea-lb{font-family:Vazirmatn,"Segoe UI",Tahoma,sans-serif;letter-spacing:0;direction:rtl}</style>')
    A('<defs>')
    A('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (SEA, SEA2))
    A('<linearGradient id="land" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (LAND, LAND2))
    A('<radialGradient id="vign" cx="50%" cy="50%" r="72%"><stop offset="0" stop-color="#02040a" stop-opacity="0"/><stop offset="100%" stop-color="#02040a" stop-opacity=".78"/></radialGradient>')
    A('<pattern id="wav" width="22" height="12" patternUnits="userSpaceOnUse"><path d="M0 7q5.5-6 11 0t11 0" fill="none" stroke="#3a6a88" stroke-width=".9" opacity=".22"/><path d="M0 3q5.5-4 11 0t11 0" fill="none" stroke="#2f5570" stroke-width=".7" opacity=".12"/></pattern>')
    A('<pattern id="swell" width="40" height="24" patternUnits="userSpaceOnUse"><path d="M2 16c4-3 8-3 12 0M18 10c4-3 8-3 12 0M10 20c3-2 6-2 9 0" fill="none" stroke="#4a7a96" stroke-width=".85" opacity=".2"/><path d="M0 8c5-2 10-2 15 0M20 4c5-2 10-2 15 0" fill="none" stroke="#3a6580" stroke-width=".65" opacity=".12"/></pattern>')
    A('<pattern id="surf" width="14" height="10" patternUnits="userSpaceOnUse"><path d="M1 7q3-4 6 0M8 4q2.5-3 5 0" fill="none" stroke="#5a8aa8" stroke-width=".7" opacity=".18"/></pattern>')
    # soft dark patch behind a beast
    A(_ornament_defs())
    A('<radialGradient id="halo" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="55%" stop-color="#000" stop-opacity=".22"/><stop offset="100%" stop-color="#000" stop-opacity="0"/></radialGradient>')
    A('<clipPath id="inner"><rect x="%d" y="%d" width="%d" height="%d" rx="4"/></clipPath>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    A('</defs>')

    # sea
    A('<rect width="%d" height="%d" fill="url(#sea)"/>' % (w, h))
    A('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#wav)"/>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    A('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#swell)"/>' % (pad, pad, w - 2 * pad, h - 2 * pad))
    A('<rect x="%d" y="%d" width="%d" height="%d" fill="url(#surf)" opacity=".7"/>' % (pad, pad, w - 2 * pad, h - 2 * pad))

    # land — world sheet stays on 110m (file size); regional sheets use 50m coasts
    use_hi = (box[1] - box[0]) < 80 and os.path.exists(GEO)
    geo = json.load(open(GEO if use_hi else (GEO_LO if os.path.exists(GEO_LO) else GEO)))
    # tighter simplify on wide sheets
    _span = box[1] - box[0]
    tol = 0.25 if _span >= 80 else (0.1 if _span >= 30 else 0.06)
    paths = []
    for feat in geo["features"]:
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            for ring in poly:
                if max(p[1] for p in ring) < box[2] - 2 or min(p[1] for p in ring) > box[3] + 2:
                    continue
                paths.append(ring_path(ring, box, w, h, pad, tol_deg=tol))
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

    # land + coastal echo (atlas double-coast)
    A('<path fill="url(#land)" fill-rule="evenodd" stroke="%s" stroke-width="1.55" stroke-linejoin="round" d="%s"/>' % (GOLD, "".join(paths)))
    A('<path fill="none" fill-rule="evenodd" stroke="%s" stroke-width=".55" stroke-linejoin="round" opacity=".35" d="%s"/>' % (GOLD, "".join(paths)))

    # rivers and mountain hatches sit ON the land
    for riv in spec["rivers"]:
        A('<path d="%s" fill="none" stroke="#3d7a9c" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>' % poly_path(riv, box, w, h, pad))
    for rng in spec["ranges"]:
        if isinstance(rng, dict):
            pts = rng["pts"]
            A('<g opacity=".96">%s</g>' % mountain_range(
                pts, box, w, h, pad,
                step=rng.get("step", 6.2),
                scale=rng.get("scale", 1.0),
                rows=rng.get("rows", 1)))
        else:
            A('<g opacity=".96">%s</g>' % mountain_range(rng, box, w, h, pad))
    for pk in spec.get("peaks", []):
        plab, plon, plat = pk[0], pk[1], pk[2]
        psc = pk[3] if len(pk) > 3 else 1.7
        A('<g opacity=".98">%s</g>' % sculpted_peak(plon, plat, box, w, h, pad, scale=psc, label=plab, lang=lang))
    # biome forests — canopy carpets (dense overlapping stamps)
    for fr in spec.get("forests", []):
        flon, flat, fs = fr[0], fr[1], fr[2]
        fkind = fr[3] if len(fr) > 3 else "pine"
        fx, fy = project(flon, flat, box, w, h, pad)
        A('<g transform="translate(%.1f %.1f) scale(%.2f)" opacity=".88">%s</g>'
          % (fx, fy, fs * 1.35, tree_mark(fkind)))
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

    # mythical creatures — empty until each beast is approved (see beast-review/)
    for c in spec.get("creatures", []):
        kind, clon, clat, s, flip = c[:5]
        frag = map_creatures.art(kind)
        if not frag:
            continue
        label = c[5] if len(c) > 5 else None
        x, y = project(clon, clat, box, w, h, pad)
        S = s
        sx = -S if flip else S
        A('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="url(#halo)"/>'
          % (x, y, 16 * S, 13 * S))
        A('<g transform="translate(%.1f %.1f) scale(%.2f %.2f)" opacity=".94">%s</g>'
          % (x, y, sx, S, frag))
        if label:
            lab = label if lang == "en" else FA.get(label, label)
            A('<text class="lb" x="%.0f" y="%.0f" font-size="10" text-anchor="middle" '
              'stroke="#05070b" stroke-width="2.5" stroke-opacity=".55" paint-order="stroke" opacity=".92">%s</text>'
              % (x, y + 12 * S + 10, esc(lab)))

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

    # compass rose (bottom-right) — disk with shade rim + lit face so it sits in the scene
    A('<g transform="translate(%d %d)">'
      '<ellipse cx="3" cy="5" rx="26" ry="8" fill="#000" opacity=".4"/>'
      '<circle r="24" fill="#0a1018" fill-opacity=".92" stroke="%s" stroke-width="1.1"/>'
      '<circle r="24" fill="none" stroke="#05070b" stroke-width="3" stroke-dasharray="0 38 38 0" '
      'stroke-linecap="butt" opacity=".55" transform="rotate(35)"/>'
      '<circle r="18" fill="#121820" opacity=".85"/>'
      '<circle cx="-4" cy="-5" r="14" fill="#1a2430" opacity=".45"/>'
      % (w - pad - 52, h - pad - 52, GOLD))
    # points: each needle has lit + shade half
    A('<g opacity=".95">'
      '<path d="M0-20 3.4-6 0-9Z" fill="%s"/><path d="M0-20 -3.4-6 0-9Z" fill="#f0e0b0"/>'
      '<path d="M0 20 3.4 6 0 9Z" fill="#5a4a28"/><path d="M0 20 -3.4 6 0 9Z" fill="%s"/>'
      '<path d="M-20 0-6 3.4-9 0Z" fill="#5a4a28"/><path d="M-20 0-6-3.4-9 0Z" fill="%s"/>'
      '<path d="M20 0 6 3.4 9 0Z" fill="%s"/><path d="M20 0 6-3.4 9 0Z" fill="#5a4a28"/>'
      '</g>' % (GOLD, GOLD, GOLD, GOLD))
    A('<circle r="3.2" fill="#1a140c" stroke="%s" stroke-width=".9"/>'
      '<circle cx="-.8" cy="-1" r="1.4" fill="#e8d9a8" opacity=".7"/>'
      '<text class="lb" y="-29" font-size="11" text-anchor="middle">%s</text></g>'
      % (GOLD, "N" if lang == "en" else "ش"))

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
