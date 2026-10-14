"""Volumetric engraved bestiary for tools/genmaps.py.

LOCKED: 2D SVG that READS sculpted — gradient body mass, deep shade faces,
lit midtones, gold RIM ONLY on light edges (never full gold outline wireframe).
Soft ground shadow + form hatch/scales. Decorative scale ~0.65–0.9 in MAPS.
"""
from __future__ import annotations

GOLD = "#c9a45c"
INK = "#080604"
BODY = "#4a3a28"       # readable bronze midtone on olive land
SHADE = "#0c0906"      # near-black shade face
HIGH = "#7a6440"       # lit rock/flesh
RIM = "#e0c278"        # bright rim-light (lit edges only)
SNOW = "#e8d9a8"
SCALE = "#b89548"


def art(kind, gold=GOLD):
    raw = CREATURE_ART.get(kind) or CREATURE_ART["serpent"]
    if gold == GOLD:
        return raw
    return raw.replace(GOLD, gold).replace(RIM, gold).replace(SCALE, gold).replace(SNOW, gold)


def _vol_defs(uid: str) -> str:
    """Per-beast gradients + soft blur (unique ids so maps don't collide)."""
    return (
        f'<defs>'
        f'<linearGradient id="{uid}-body" x1="10%" y1="5%" x2="95%" y2="100%">'
        f'<stop offset="0%" stop-color="#c4a060"/>'
        f'<stop offset="28%" stop-color="#7a6040"/>'
        f'<stop offset="62%" stop-color="#2e2418"/>'
        f'<stop offset="100%" stop-color="#050402"/>'
        f'</linearGradient>'
        f'<linearGradient id="{uid}-wing" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#a88850"/>'
        f'<stop offset="40%" stop-color="#4a3824"/>'
        f'<stop offset="100%" stop-color="#060402"/>'
        f'</linearGradient>'
        f'<radialGradient id="{uid}-orb" cx="35%" cy="30%" r="70%">'
        f'<stop offset="0%" stop-color="#d0b070"/>'
        f'<stop offset="40%" stop-color="#6a5238"/>'
        f'<stop offset="100%" stop-color="#050402"/>'
        f'</radialGradient>'
        f'<filter id="{uid}-blur" x="-40%" y="-40%" width="180%" height="180%">'
        f'<feGaussianBlur stdDeviation="1.4"/>'
        f'</filter>'
        f'</defs>'
    )


class _Engraver:
    __slots__ = ("parts", "uid")

    def __init__(self, uid: str):
        self.uid = uid
        self.parts: list[str] = [_vol_defs(uid)]

    def path(self, d, fill=None, stroke=None, sw=0.55, opacity=None, filt=None):
        bits = [f'd="{d}"']
        bits.append(f'fill="{fill}"' if fill else 'fill="none"')
        if stroke:
            bits.append(f'stroke="{stroke}"')
            bits.append(f'stroke-width="{sw}"')
            bits.append('stroke-linecap="round" stroke-linejoin="round"')
        if opacity is not None:
            bits.append(f'opacity="{opacity}"')
        if filt:
            bits.append(f'filter="url(#{filt})"')
        self.parts.append(f'<path {" ".join(bits)}/>')

    def circle(self, cx, cy, r, fill=RIM, stroke=None, sw=0.35, opacity=None):
        bits = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
        if stroke:
            bits.append(f'stroke="{stroke}"')
            bits.append(f'stroke-width="{sw}"')
        if opacity is not None:
            bits.append(f'opacity="{opacity}"')
        self.parts.append(f'<circle {" ".join(bits)}/>')

    def soft_shadow(self, cx, cy, rx, ry, op=0.55):
        self.parts.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" '
            f'opacity="{op}" filter="url(#{self.uid}-blur)"/>'
        )

    def mass(self, d, grad="body"):
        """Gradient-filled volume — NO gold outline (rim is separate lit edges)."""
        self.path(d, fill=f"url(#{self.uid}-{grad})", stroke=SHADE, sw=0.35)

    def shade(self, d, op=0.75):
        self.path(d, fill=SHADE, opacity=op)

    def lit(self, d, op=0.55):
        self.path(d, fill=HIGH, opacity=op)

    def rim(self, d, sw=1.05, op=0.9):
        """Gold only along a lit edge path (open stroke)."""
        self.path(d, stroke=RIM, sw=sw, opacity=op)

    def hatch(self, cx, cy, rx, ry, step=1.5, sw=0.28, op=0.5):
        y = cy - ry + 0.7
        while y < cy + ry:
            dy = (y - cy) / ry
            if abs(dy) < 1:
                hw = rx * (1 - dy * dy) ** 0.5
                # denser on shade (right) side
                self.path(
                    f"M{cx - hw * 0.15:.1f} {y:.1f}L{cx + hw:.1f} {y:.1f}",
                    stroke=SCALE, sw=sw, opacity=op,
                )
                self.path(
                    f"M{cx - hw:.1f} {y:.1f}L{cx - hw * 0.2:.1f} {y:.1f}",
                    stroke=SNOW, sw=sw * 0.7, opacity=op * 0.35,
                )
            y += step

    def scales(self, x0, y0, x1, y1, cols=6, rows=4, r=1.3, sw=0.3):
        dx = (x1 - x0) / max(cols - 1, 1)
        dy = (y1 - y0) / max(rows - 1, 1)
        for j in range(rows):
            for i in range(cols):
                cx = x0 + i * dx + (0.5 if j % 2 else 0)
                cy = y0 + j * dy
                # tiny filled scale plate with lit top
                self.path(
                    f"M{cx - r:.1f} {cy:.1f}A{r:.1f} {r * 0.65:.1f} 0 0 1 {cx + r:.1f} {cy:.1f}"
                    f"L{cx:.1f} {cy + r * 0.4:.1f}Z",
                    fill=SHADE, opacity=0.45,
                )
                self.path(
                    f"M{cx - r:.1f} {cy:.1f}A{r:.1f} {r * 0.65:.1f} 0 0 1 {cx + r:.1f} {cy:.1f}",
                    stroke=SCALE, sw=sw, opacity=0.7,
                )
                # highlight on upper arc
                self.path(
                    f"M{cx - r * 0.6:.1f} {cy - 0.15:.1f}A{r * 0.6:.1f} {r * 0.4:.1f} 0 0 1 {cx + r * 0.2:.1f} {cy - 0.4:.1f}",
                    stroke=SNOW, sw=sw * 0.7, opacity=0.4,
                )

    def feathers(self, x0, y0, x1, y1, n=8, sw=0.32):
        for i in range(n):
            t = i / max(n - 1, 1)
            bx = x0 + (x1 - x0) * 0.1
            by = y0 + (y1 - y0) * t
            tx = x1
            ty = y0 + (y1 - y0) * (t * 0.85 + 0.08)
            self.path(
                f"M{bx:.1f} {by:.1f}L{tx:.1f} {ty:.1f}L{tx - 1.4:.1f} {ty + 1.6:.1f}"
                f"L{bx:.1f} {by + 1.2:.1f}Z",
                fill=f"url(#{self.uid}-wing)", opacity=0.85,
            )
            self.shade(
                f"M{bx + (tx - bx) * 0.4:.1f} {by + (ty - by) * 0.4:.1f}"
                f"L{tx:.1f} {ty:.1f}L{tx - 1.4:.1f} {ty + 1.6:.1f}Z",
                op=0.45,
            )
            self.rim(f"M{bx:.1f} {by:.1f}L{tx:.1f} {ty:.1f}", sw=sw, op=0.65)

    def horns(self, pts, sw=0.36):
        for i, (x, y) in enumerate(pts):
            self.path(
                f"M{x:.1f} {y:.1f}l{1.05:.1f} {0.5 if i % 2 == 0 else -0.5:.1f}",
                stroke=RIM, sw=sw, opacity=0.7,
            )

    def teeth(self, x, y, n=4, up=True):
        for i in range(n):
            tx = x + i * 1.6
            if up:
                self.path(
                    f"M{tx:.1f} {y:.1f}L{tx + 0.6:.1f} {y - 2.0:.1f}L{tx + 1.2:.1f} {y:.1f}Z",
                    fill=SNOW, stroke=RIM, sw=0.35,
                )
            else:
                self.path(
                    f"M{tx:.1f} {y:.1f}L{tx + 0.6:.1f} {y + 2.0:.1f}L{tx + 1.2:.1f} {y:.1f}Z",
                    fill=SNOW, stroke=RIM, sw=0.35,
                )

    def eye(self, cx, cy, r=0.55):
        self.circle(cx, cy, r * 1.7, fill=SHADE, opacity=0.9)
        self.circle(cx, cy, r, fill=RIM)
        self.circle(cx + r * 0.28, cy - r * 0.22, r * 0.38, fill=SNOW)

    def done(self):
        return "".join(self.parts)


# ---------------------------------------------------------------- builders


def build_dahaka():
    """Aži Dahāka — three sculpted dragon heads on a bronze orb torso.

    Same volumetric language that works for Humbaba at map scale: strong
    orb gradient, big shade/lit faces, sparse scales (no gold hatch grid).
    """
    e = _Engraver("dahaka")
    e.soft_shadow(0, 20, 20, 5.5, op=0.62)
    # —— torso: readable bronze sphere (like humbaba's orb) ——
    torso = "M-14 4C-14-10 -6-18 2-18C14-18 20-8 20 4C20 14 12 20 2 20C-10 20-14 12-14 4Z"
    e.mass(torso, grad="orb")
    e.shade("M4-2C14 2 18 10 16 16C8 20-2 16-6 8C-2 2 2-2 4-2Z", op=0.78)
    e.lit("M-14 2C-10-12 0-16 10-12C2-6-6 0-12 4C-16 4-16 4-14 2Z", op=0.62)
    e.rim("M-14 2C-10-12 0-16 10-12", sw=1.35)
    # sparse form scales only (not a gold plate grid)
    e.scales(-4, -6, 10, 10, cols=4, rows=3, r=1.4)
    # —— three thick necks + heads ——
    heads = [
        # base_x, base_y, tip_x, tip_y, snout angle bias
        (-6, -12, -22, -28),
        (4, -16, 8, -34),
        (12, -8, 28, -22),
    ]
    for bx, by, tipx, tipy in heads:
        # thick neck mass
        mx, my = (bx + tipx) / 2 + 2, (by + tipy) / 2 - 2
        neck = (
            f"M{bx - 3:.1f} {by:.1f}"
            f"C{bx - 1:.1f} {by - 8:.1f} {mx - 4:.1f} {my:.1f} {tipx - 3:.1f} {tipy + 2:.1f}"
            f"L{tipx + 5:.1f} {tipy + 4:.1f}"
            f"C{mx + 4:.1f} {my + 4:.1f} {bx + 5:.1f} {by + 2:.1f} {bx + 3:.1f} {by + 2:.1f}Z"
        )
        e.mass(neck, grad="body")
        e.shade(
            f"M{bx:.1f} {by + 1:.1f}C{mx + 2:.1f} {my + 2:.1f} {tipx + 2:.1f} {tipy + 3:.1f}"
            f"L{tipx + 5:.1f} {tipy + 4:.1f}C{mx + 3:.1f} {my + 5:.1f} {bx + 3:.1f} {by + 2:.1f}Z",
            op=0.72,
        )
        e.lit(
            f"M{bx - 3:.1f} {by:.1f}C{mx - 3:.1f} {my - 2:.1f} {tipx - 3:.1f} {tipy + 2:.1f}"
            f"L{tipx:.1f} {tipy + 3:.1f}C{mx - 1:.1f} {my + 1:.1f} {bx:.1f} {by + 1:.1f}Z",
            op=0.55,
        )
        e.rim(
            f"M{bx - 3:.1f} {by:.1f}C{mx - 3:.1f} {my - 2:.1f} {tipx - 3:.1f} {tipy + 2:.1f}",
            sw=1.15,
        )
        # head bulb
        e.mass(
            f"M{tipx - 5:.1f} {tipy:.1f}"
            f"C{tipx - 6:.1f} {tipy - 6:.1f} {tipx + 2:.1f} {tipy - 8:.1f} {tipx + 6:.1f} {tipy - 2:.1f}"
            f"C{tipx + 8:.1f} {tipy + 2:.1f} {tipx + 4:.1f} {tipy + 7:.1f} {tipx - 2:.1f} {tipy + 6:.1f}"
            f"C{tipx - 6:.1f} {tipy + 5:.1f} {tipx - 6:.1f} {tipy + 2:.1f} {tipx - 5:.1f} {tipy:.1f}Z",
            grad="orb",
        )
        e.shade(
            f"M{tipx:.1f} {tipy:.1f}C{tipx + 4:.1f} {tipy + 1:.1f} {tipx + 5:.1f} {tipy + 5:.1f}"
            f"L{tipx - 1:.1f} {tipy + 5:.1f}Z",
            op=0.65,
        )
        e.lit(
            f"M{tipx - 4:.1f} {tipy - 2:.1f}C{tipx - 2:.1f} {tipy - 6:.1f} {tipx + 3:.1f} {tipy - 5:.1f}"
            f"L{tipx:.1f} {tipy:.1f}Z",
            op=0.5,
        )
        e.rim(
            f"M{tipx - 5:.1f} {tipy:.1f}C{tipx - 6:.1f} {tipy - 6:.1f} {tipx + 2:.1f} {tipy - 8:.1f} {tipx + 6:.1f} {tipy - 2:.1f}",
            sw=1.0,
        )
        # jaw
        e.mass(
            f"M{tipx - 2:.1f} {tipy + 2:.1f}L{tipx + 7:.1f} {tipy + 3:.1f}"
            f"L{tipx + 6:.1f} {tipy + 7:.1f}L{tipx - 2:.1f} {tipy + 5:.1f}Z"
        )
        e.shade(
            f"M{tipx + 1:.1f} {tipy + 3:.1f}L{tipx + 7:.1f} {tipy + 3:.1f}"
            f"L{tipx + 6:.1f} {tipy + 7:.1f}Z",
            op=0.6,
        )
        e.teeth(tipx - 1, tipy + 3.2, n=3)
        e.eye(tipx - 1, tipy - 1, r=0.55)
        # two horns
        for k, (ox, oy) in enumerate([(-3, -4), (2, -5)]):
            hx, hy = tipx + ox, tipy + oy
            e.mass(f"M{hx:.1f} {hy:.1f}L{hx - 1.5:.1f} {hy - 8:.1f}L{hx + 2.5:.1f} {hy - 1:.1f}Z")
            e.shade(f"M{hx:.1f} {hy:.1f}L{hx - 1.5:.1f} {hy - 8:.1f}L{hx + 2.5:.1f} {hy - 1:.1f}Z", op=0.4)
            e.rim(f"M{hx:.1f} {hy:.1f}L{hx - 1.5:.1f} {hy - 8:.1f}", sw=0.85)
    # —— wing membranes (filled, not outline) ——
    for d, rim_d in [
        ("M-2-10C2-20 10-28 18-30C12-20 4-12 0-10Z", "M-2-10C2-20 10-28 18-30"),
        ("M8-8C14-18 24-26 32-28C24-18 14-10 10-8Z", "M8-8C14-18 24-26 32-28"),
    ]:
        e.mass(d, grad="wing")
        e.shade(d, op=0.4)
        e.rim(rim_d, sw=1.0)
    e.feathers(0, -26, 16, -12, n=4)
    e.feathers(10, -24, 30, -10, n=4)
    # —— legs ——
    for d, lit_edge in (
        ("M-12 6C-18 12-24 20-28 28L-22 28L-18 16C-15 10-13 7-12 6Z",
         "M-12 6C-18 12-24 20-28 28"),
        ("M-2 14C-3 22-2 28 0 32L4 32L3 22C2 18 0 15-2 14Z",
         "M-2 14C-3 22-2 28 0 32"),
        ("M8 14C10 22 12 28 14 32L18 31L16 22C14 18 11 15 8 14Z",
         "M8 14C10 22 12 28 14 32"),
    ):
        e.mass(d)
        e.shade(d, op=0.42)
        e.rim(lit_edge, sw=0.75, op=0.7)
    return e.done()


def build_humbaba():
    e = _Engraver("humbaba")
    e.soft_shadow(0, 20, 17, 5, op=0.58)
    face = "M0-16C12-16 18-6 18 4C18 16 8 22 0 22C-8 22-18 16-18 4C-18-6-12-16 0-16Z"
    e.mass(face, grad="orb")
    e.shade("M2-4C11 0 15 8 13 16C6 20-1 18-5 12C-3 4 0-2 2-4Z", op=0.72)
    e.lit("M-16 0C-12-11 -3-15 5-13C-1-7-8-2-14 2C-18 2-18 2-16 0Z", op=0.55)
    e.rim("M-16 0C-12-11 -3-15 5-13", sw=1.15)
    e.hatch(0, 2, 13, 15, step=1.35)
    import math
    for r in (4.5, 8, 11.5):
        e.path(
            f"M0 {-r}A{r} {r * 0.85} 0 1 1 0 {r}",
            stroke=SCALE, sw=0.35, opacity=0.45,
        )
        e.path(
            f"M0 {-r}A{r} {r * 0.85} 0 1 0 -.1 {-r}",
            stroke=SNOW, sw=0.25, opacity=0.25,
        )
    for a in range(0, 360, 30):
        rad = math.radians(a)
        cx = round(15.5 * math.cos(rad), 1)
        cy = round(1 + 16.5 * math.sin(rad) * 0.95, 1)
        e.mass(f"M{cx - 2} {cy}A2 2 0 1 1 {cx + 2} {cy}A2 2 0 1 1 {cx - 2} {cy}")
        e.shade(f"M{cx} {cy - 1.6}A1.6 1.6 0 0 1 {cx + 1.6} {cy}L{cx} {cy}Z", op=0.55)
        e.lit(f"M{cx} {cy + 1.6}A1.6 1.6 0 0 1 {cx - 1.6} {cy}L{cx} {cy}Z", op=0.35)
        e.rim(f"M{cx - 1.4} {cy - 0.8}A1.6 1.6 0 0 1 {cx + 0.6} {cy - 1.5}", sw=0.55, op=0.7)
    e.path("M-8-1C-6-4 -3-4 -1.5-1C-3 2-6 2-8-1Z", fill=SHADE)
    e.path("M8-1C6-4 3-4 1.5-1C3 2 6 2 8-1Z", fill=SHADE)
    e.eye(-4.5, -1, r=0.52)
    e.eye(4.5, -1, r=0.52)
    e.path("M0-4V5", stroke=SCALE, sw=0.45, opacity=0.7)
    e.path("M-7 8q3.5 5 7 0q3.5-5 7 0", stroke=RIM, sw=0.55, opacity=0.75)
    e.teeth(-4, 10, n=5, up=False)
    e.mass("M-10 8C-14 14-12 20-8 22L-6 18C-8 14-8 10-8 8Z")
    e.mass("M10 8C14 14 12 20 8 22L6 18C8 14 8 10 8 8Z")
    e.shade("M10 10C13 14 12 18 9 20L7 17Z", op=0.5)
    return e.done()


def build_simorgh():
    e = _Engraver("simorgh")
    e.soft_shadow(0, 18, 18, 4.5, op=0.55)
    e.mass("M-4-2C-14-10 -26-20 -34-28C-26-16 -16-8 -6-4Z", grad="wing")
    e.mass("M4-2C14-10 26-20 34-28C26-16 16-8 6-4Z", grad="wing")
    e.feathers(-30, -26, -6, -4, n=9)
    e.feathers(6, -4, 30, -26, n=9)
    e.rim("M-34-28C-26-16 -16-8 -6-4", sw=1.0)
    e.rim("M34-28C26-16 16-8 6-4", sw=1.0)
    e.mass("M-4-4C-8 0 -9 10 -4 16C-1 20 5 20 8 16C12 10 11 0 6-4C3-7 -1-7 -4-4Z")
    e.shade("M2 0C6 4 8 10 6 16C2 18-2 14 0 6Z", op=0.7)
    e.lit("M-4-2C-6 4 -4 12 0 16C-4 10-6 2Z", op=0.5)
    e.rim("M-4-4C-6 2 -4 12 0 16", sw=0.95)
    e.hatch(2, 4, 7, 10, step=1.35)
    e.scales(-2, 0, 8, 12, cols=5, rows=4, r=1.0)
    e.mass("M2-4C1-12 4-16 10-18L18-19L15-15L11-14L13-10L8-9C4-8 2-5 2-4Z")
    e.eye(10, -14)
    for hx, hy in [(5, -16), (9, -17), (13, -16)]:
        e.mass(f"M{hx} {hy}L{hx - 1} {hy - 9}L{hx + 3} {hy - 1}Z")
        e.rim(f"M{hx} {hy}L{hx - 1} {hy - 9}", sw=0.65)
    e.mass("M-2 14L-10 30L4 32L8 16Z")
    e.shade("M2 16L-2 30L4 32L6 18Z", op=0.55)
    e.feathers(-8, 16, 6, 30, n=6)
    return e.done()


def build_jormungandr():
    e = _Engraver("jorm")
    e.soft_shadow(0, 10, 28, 5, op=0.55)
    body = "M-28 4C-22-10 -10-16 2-10C12-6 20-2 24 4C26 8 24 4 22-2C20-8 14-12 6-10C-4-6-14-8-22-2C-26 2-28 6-28 4Z"
    e.mass(body)
    e.shade("M-8 2C0 8 12 6 22 0C18 6 8 10-2 8Z", op=0.7)
    e.lit("M-26 2C-18-8 -6-12 4-6C-2-2-12 2-22 4Z", op=0.52)
    e.rim("M-26 2C-18-8 -6-12 4-6", sw=1.15)
    e.scales(-22, -6, 18, 6, cols=10, rows=5, r=1.15)
    e.hatch(-4, 0, 18, 8, step=1.65)
    for x, y in [(-16, -4), (-8, -8), (0, -7), (8, -3), (14, 0)]:
        e.mass(f"M{x} {y}L{x + 2} {y - 5}L{x + 4} {y + 0.5}Z")
        e.shade(f"M{x + 2} {y}L{x + 2} {y - 5}L{x + 4} {y + 0.5}Z", op=0.55)
        e.rim(f"M{x} {y}L{x + 2} {y - 5}", sw=0.7)
    e.mass("M22-2C28-8 36-12 42-10L44-6L36-4L32 0C28 3 24 2 22 0Z")
    e.shade("M28-2C34-4 40-6 42-4L40 0L32 1Z", op=0.6)
    e.path("M34-7L42-6L43-2L35-2.5Z", fill=SHADE)
    e.path("M33-2L41 0L40 3L32 1.5Z", fill=SHADE)
    e.teeth(34, -5.5, n=4)
    e.teeth(33.5, -1, n=3, up=False)
    e.eye(30, -6.5)
    e.mass("M28-10L26-16L30-11Z")
    e.mass("M32-10.5L33-17L36-11Z")
    e.horns([(27, -12), (29, -14), (32, -13.5), (34, -12)])
    return e.done()


def build_nidhogg():
    e = _Engraver("nidhogg")
    e.soft_shadow(2, 18, 22, 5, op=0.55)
    e.mass("M-14 2C-16-8 -8-16 2-16C14-16 20-6 20 2C20 10 12 16 2 16C-8 16-14 10-14 2Z")
    e.shade("M2-2C10 0 16 4 18 10C14 14 6 16 0 14Z", op=0.72)
    e.lit("M-12-2C-10-10 -2-14 6-12C2-6-4-2-10 0Z", op=0.52)
    e.rim("M-12-2C-10-10 -2-14 6-12", sw=1.1)
    e.hatch(2, 0, 14, 12, step=1.45)
    e.scales(-8, -8, 14, 8, cols=8, rows=5, r=1.1)
    e.mass("M6-10C12-20 20-28 30-32C24-22 18-14 12-10Z", grad="wing")
    e.mass("M2-12C6-22 12-32 20-38C14-28 8-20 4-14Z", grad="wing")
    e.feathers(8, -30, 28, -12, n=7)
    e.feathers(4, -34, 18, -14, n=5)
    e.mass("M12-4C20-12 30-18 38-20L42-16L34-12L28-6C24-2 16 0 12-2Z")
    e.shade("M22-6C28-10 36-14 40-14L36-10L28-6Z", op=0.6)
    e.path("M32-16L40-14L41-10L33-11Z", fill=SHADE)
    e.teeth(33, -13.5, n=4)
    e.eye(28, -15)
    for hx, hy in [(24, -20), (29, -21), (34, -19)]:
        e.mass(f"M{hx} {hy}L{hx - 1} {hy - 8}L{hx + 3} {hy - 1}Z")
        e.rim(f"M{hx} {hy}L{hx - 1} {hy - 8}", sw=0.65)
    e.mass("M-6 12C-8 20-6 26-4 30L0 30L-1 22C-2 18-4 14-4 12Z")
    e.mass("M8 12C10 20 12 26 14 30L18 29L15 22C14 18 11 14 9 12Z")
    e.mass("M-14 4C-22 10-28 18-32 26L-26 26L-22 16C-18 10-15 6-14 4Z")
    return e.done()


def build_fenrir():
    e = _Engraver("fenrir")
    e.soft_shadow(0, 16, 20, 4.5, op=0.55)
    e.mass("M-16 0C-16-10 -6-16 4-16C14-16 20-8 20 0C20 8 12 14 2 14C-8 14-16 8-16 0Z")
    e.shade("M2-2C10 0 16 4 18 8C12 12 4 14-2 10Z", op=0.7)
    e.lit("M-14-2C-10-10 0-14 8-10C2-6-6-2-12 0Z", op=0.5)
    e.rim("M-14-2C-10-10 0-14 8-10", sw=1.1)
    e.hatch(2, -1, 14, 11, step=1.5)
    for x, y in [(-10, -6), (-4, -10), (2, -11), (8, -8), (-8, 4), (0, 6), (8, 4)]:
        e.path(f"M{x} {y}l{-1.5 if x < 0 else 1.2} {-2.8}", stroke=RIM, sw=0.35, opacity=0.65)
    e.mass("M12-6C20-12 28-16 36-14L40-8L32-6L26-2C22 2 16 2 12 0Z")
    e.shade("M22-4C28-6 34-8 38-6L34-2L26 0Z", op=0.58)
    e.path("M32-9L40-6L41-2L33-3.5Z", fill=SHADE)
    e.teeth(33, -6.5, n=4)
    e.teeth(32, -1, n=3, up=False)
    e.eye(27, -9, r=0.6)
    e.mass("M18-12L16-22L22-14Z")
    e.mass("M24-13L26-24L30-14Z")
    for x in (-10, -2, 8):
        e.mass(f"M{x} 10C{x - 1} 18 {x} 24 {x + 1} 28L{x + 5} 28L{x + 3} 20C{x + 2} 16 {x + 1} 12 {x} 10Z")
    e.mass("M-16-2C-24-8 -32-10 -38-4C-32 2-26 4-20 4C-18 4-16 2-16-2Z")
    return e.done()


def build_daeva():
    e = _Engraver("daeva")
    e.soft_shadow(0, 30, 12, 3.5, op=0.5)
    e.mass("M-10 28C-9 12 -6 2 0 2C6 2 9 12 10 28L6 28C5 16 3 10 0 10C-3 10-5 16-6 28Z")
    e.shade("M2 8C5 14 6 22 5 28L2 28Z", op=0.65)
    e.hatch(0, 16, 6, 12, step=1.35)
    e.mass("M0-18C8-18 14-10 14-2C14 6 8 12 0 12C-8 12-14 6-14-2C-14-10-8-18 0-18Z", grad="orb")
    e.shade("M2-8C8-6 12 0 12 4C8 8 2 10-2 6Z", op=0.68)
    e.lit("M-12-4C-10-12 -4-16 2-16C-2-10-6-4-10-2Z", op=0.5)
    e.rim("M-12-4C-10-12 -4-16 2-16", sw=1.1)
    e.hatch(0, -4, 10, 12, step=1.4)
    e.mass("M-8-12C-16-18 -20-28 -18-36C-12-28 -10-20 -6-14Z")
    e.mass("M8-12C16-18 20-28 18-36C12-28 10-20 6-14Z")
    e.rim("M-8-12C-16-18 -20-28 -18-36", sw=0.85)
    e.rim("M8-12C16-18 20-28 18-36", sw=0.85)
    e.horns([(-16, -28), (-14, -24), (-12, -20), (-10, -16)])
    e.horns([(16, -28), (14, -24), (12, -20), (10, -16)])
    e.path("M-7-2C-5-4 -3-4 -1.5-2C-3 0-5 0-7-2Z", fill=SHADE)
    e.path("M7-2C5-4 3-4 1.5-2C3 0 5 0 7-2Z", fill=SHADE)
    e.eye(-4.2, -2, r=0.42)
    e.eye(4.2, -2, r=0.42)
    e.teeth(-3, 8, n=4, up=False)
    return e.done()


def build_mushussu():
    e = _Engraver("mushussu")
    e.soft_shadow(2, 20, 22, 5, op=0.55)
    e.mass("M-16 2C-16-8 -6-14 4-14C16-14 22-4 22 4C22 12 14 18 4 18C-8 18-16 12-16 2Z")
    e.shade("M4 0C12 2 18 6 20 12C14 16 4 16-2 12Z", op=0.7)
    e.lit("M-14 0C-10-8 0-12 10-8C2-4-6 0-12 2Z", op=0.5)
    e.rim("M-14 0C-10-8 0-12 10-8", sw=1.1)
    e.hatch(2, 2, 15, 12, step=1.45)
    e.scales(-10, -6, 16, 10, cols=9, rows=5, r=1.2)
    e.mass("M10-4C18-14 28-22 38-26L44-20L36-18L28-10C24-6 16-2 10-4Z")
    e.shade("M22-8C30-14 38-18 42-18L38-14L28-10Z", op=0.58)
    e.path("M34-22L42-19L43-14L35-15.5Z", fill=SHADE)
    e.teeth(35, -19, n=4)
    e.eye(30, -18)
    e.mass("M26-26L24-34L28-27Z")
    e.mass("M32-26L34-35L38-27Z")
    e.mass("M-16 2C-24 0 -30-6 -36-14L-38-8L-30-2C-26 2-20 4-16 4Z")
    e.scales(-34, -10, -18, 2, cols=5, rows=3, r=0.95)
    e.mass("M-6 14C-8 22-6 28-4 32L0 32L-1 24C-2 20-4 16-4 14Z")
    e.mass("M8 14C10 22 12 28 14 32L18 31L15 24C14 20 11 16 9 14Z")
    e.mass("M0-10C4-20 10-26 18-30C12-22 6-14 2-10Z", grad="wing")
    e.mass("M8-10C14-20 22-26 30-28C22-20 14-14 10-10Z", grad="wing")
    e.feathers(2, -28, 16, -12, n=5)
    return e.done()


def build_anzu():
    e = _Engraver("anzu")
    e.soft_shadow(0, 16, 16, 4, op=0.52)
    e.mass("M-4-2C-14-10 -26-20 -34-28C-26-16 -16-8 -6-4Z", grad="wing")
    e.mass("M4-2C14-10 26-20 34-28C26-16 16-8 6-4Z", grad="wing")
    e.feathers(-30, -26, -6, -4, n=8)
    e.feathers(6, -4, 30, -26, n=8)
    e.mass("M-4-4C-9 0 -10 10 -5 16C-2 20 5 20 8 16C13 10 12 0 7-4C4-7 0-7 -4-4Z")
    e.shade("M2 0C7 4 10 10 7 16C2 18-2 12 0 4Z", op=0.65)
    e.rim("M-4-4C-7 4 -4 14 0 16", sw=0.95)
    e.hatch(2, 4, 7, 10, step=1.35)
    e.scales(-2, 0, 8, 12, cols=5, rows=4, r=0.95)
    e.mass("M1-4C0-12 4-17 10-18L18-19L16-15L12-14L14-10L8-9C4-8 2-5 1-4Z")
    e.eye(10, -13)
    e.mass("M6-16L4-25L8-18Z")
    e.mass("M11-16.5L13-26L16-17.5Z")
    e.mass("M-2 14L-10 28L4 30L8 16Z")
    e.feathers(-8, 16, 6, 28, n=5)
    e.teeth(10, -11, n=3, up=False)
    return e.done()


def build_garuda():
    e = _Engraver("garuda")
    e.soft_shadow(0, 16, 16, 4, op=0.52)
    e.mass("M-4-1C-16-10 -28-20 -36-28C-28-16 -16-7 -6-3Z", grad="wing")
    e.mass("M4-1C16-10 28-20 36-28C28-16 16-7 6-3Z", grad="wing")
    e.feathers(-32, -26, -6, -3, n=10)
    e.feathers(6, -3, 32, -26, n=10)
    e.mass("M-3-4C-8 0 -9 11 -4 17C-1 21 5 21 8 17C13 11 12 0 7-4C4-7 0-7 -3-4Z")
    e.shade("M2 2C7 6 10 12 6 17C2 18-2 12 0 4Z", op=0.65)
    e.rim("M-3-4C-6 4 -3 14 0 17", sw=0.95)
    e.hatch(2, 5, 7, 10, step=1.3)
    e.mass("M1-4C0-12 4-17 10-18L18-19L15-15L11-14L13-10L8-9C4-8 2-5 1-4Z")
    e.eye(10, -13)
    for hx, hy in [(5, -16), (9, -17.5), (13, -16)]:
        e.mass(f"M{hx} {hy}L{hx - 1} {hy - 10}L{hx + 3} {hy - 1}Z")
        e.rim(f"M{hx} {hy}L{hx - 1} {hy - 10}", sw=0.6)
    e.mass("M-2 14L-8 28L4 30L7 16Z")
    e.feathers(-6, 16, 5, 28, n=5)
    return e.done()


def build_naga():
    e = _Engraver("naga")
    e.soft_shadow(0, 22, 16, 4.5, op=0.55)
    e.mass("M-6 18C-16 8 -18-4 -10-14C-2-24 8-26 16-16C24-6 22 6 14 16C8 22 0 24-6 18Z")
    e.shade("M4 0C12 4 18 10 14 18C6 20 0 16-2 8Z", op=0.68)
    e.lit("M-14 4C-14-6 -6-16 4-20C-2-12-8-4-12 2Z", op=0.48)
    e.rim("M-14 4C-14-6 -6-16 4-20", sw=1.1)
    e.scales(-10, -8, 14, 16, cols=8, rows=8, r=1.25)
    e.hatch(2, 2, 12, 14, step=1.55)
    e.mass("M-2-14C-8-24 -2-34 6-36C14-38 20-30 20-20C20-12 12-10 4-10C0-10-2-12-2-14Z", grad="orb")
    e.shade("M6-20C12-22 16-18 16-14C12-12 6-12 4-14Z", op=0.55)
    e.mass("M0-22C-2-30 2-36 8-38C12-39 16-34 16-28C16-22 12-20 8-20Z")
    e.mass("M10-18C14-28 20-32 26-30C28-28 28-22 24-18C20-15 14-15 10-16Z")
    e.eye(7, -24, r=0.5)
    e.eye(18, -22, r=0.4)
    e.mass("M8 16C2 26 -6 32-16 34L-12 38C0 36 12 26 16 18Z")
    e.scales(-12, 20, 10, 34, cols=5, rows=3, r=1.05)
    return e.done()


def build_makara():
    e = _Engraver("makara")
    e.soft_shadow(4, 18, 24, 5, op=0.55)
    e.mass("M-20 2C-14-12 0-18 12-12C24-6 30 2 30 10C30 18 22 24 8 24C-6 24-20 14-20 2Z")
    e.shade("M8 2C18 4 26 8 28 14C20 20 8 20 0 16Z", op=0.7)
    e.lit("M-18 2C-12-8 0-14 12-8C2-4-8 0-16 4Z", op=0.5)
    e.rim("M-18 2C-12-8 0-14 12-8", sw=1.1)
    e.hatch(4, 4, 18, 12, step=1.45)
    e.scales(-12, -4, 22, 14, cols=10, rows=5, r=1.25)
    e.mass("M22 2C30-6 40-10 48-6L50-1L40 1L34 6C30 8 26 6 22 4Z")
    e.shade("M34 0C40-2 46-4 48-2L46 2L36 4Z", op=0.55)
    e.path("M38-3L48-1L49 4L39 2.5Z", fill=SHADE)
    e.teeth(39, -1, n=5)
    e.teeth(39, 2.5, n=4, up=False)
    e.eye(32, -2)
    e.mass("M-20 4C-28 10-36 18-40 28L-34 28L-30 16C-26 10-22 6-20 4Z")
    e.scales(-38, 8, -24, 24, cols=4, rows=4, r=0.95)
    for x in (-2, 6, 14):
        e.mass(f"M{x} -10L{x + 2} {-18}L{x + 4} {-10.5}Z")
        e.rim(f"M{x} -10L{x + 2} {-18}", sw=0.6)
    e.mass("M-4 20C-8 28-4 34 2 36L6 32L2 26C0 23-2 21-2 20Z")
    e.mass("M12 20C16 28 20 34 26 36L30 32L24 26C20 23 16 21 14 20Z")
    return e.done()


def build_scylla():
    e = _Engraver("scylla")
    e.soft_shadow(0, 22, 18, 5, op=0.55)
    e.mass("M-10 6C-14-4 -6-14 2-14C12-14 18-2 16 6C14 14 4 18-4 18C-10 18-12 12-10 6Z")
    e.shade("M2 0C8 2 14 6 14 12C8 16 0 16-4 10Z", op=0.65)
    e.rim("M-10 4C-12-4 -4-12 4-12", sw=1.0)
    e.hatch(2, 2, 10, 12, step=1.4)
    for bx, by, hx, hy in [(-8, -8, -26, -28), (0, -10, 14, -32), (10, -4, 30, -20)]:
        e.mass(
            f"M{bx} {by}C{bx - 2} {by - 10} {hx + 4} {hy + 4} {hx} {hy}L{hx - 4} {hy + 6}"
            f"L{bx + 4} {by + 2}Z"
        )
        e.shade(
            f"M{bx + 2} {by}C{bx} {by - 6} {hx + 2} {hy + 4} {hx} {hy + 2}"
            f"L{hx - 2} {hy + 6}L{bx + 4} {by + 2}Z",
            op=0.55,
        )
        e.rim(f"M{bx} {by}C{bx - 2} {by - 10} {hx + 4} {hy + 4} {hx} {hy}", sw=0.85)
        e.mass(
            f"M{hx - 2} {hy + 2}L{hx + 6} {hy + 4}L{hx + 5} {hy + 8}L{hx - 2} {hy + 5}Z"
        )
        e.teeth(hx - 1, hy + 3.5, n=3)
        e.eye(hx - 3, hy + 1, r=0.42)
    for sx, ex, ey in [(-8, -22, 34), (-2, -4, 38), (6, 14, 36), (10, 26, 30)]:
        e.mass(
            f"M{sx} 14C{sx - 4} 22 {ex} {ey - 8} {ex} {ey}L{ex + 4} {ey - 2}"
            f"C{ex + 2} {ey - 10} {sx + 4} 20 {sx + 2} 14Z"
        )
        e.scales(min(sx, ex), 16, max(sx, ex) + 4, ey - 2, cols=3, rows=4, r=0.85)
    return e.done()


def build_python():
    e = _Engraver("python")
    e.soft_shadow(0, 10, 26, 4.5, op=0.52)
    e.mass(
        "M-26 8C-16-10 -2-16 10-6C18 0 26-2 30-12C32-16 28-18 24-14C16-6 6 0-4-4C-12-7-20 0-26 8Z"
    )
    e.shade("M-4 2C6 6 16 2 28-8C24-2 12 4 0 4Z", op=0.62)
    e.lit("M-24 6C-16-6 -4-12 6-4C-2 0-12 4-20 6Z", op=0.48)
    e.rim("M-24 6C-16-6 -4-12 6-4", sw=1.1)
    e.scales(-20, -6, 22, 8, cols=12, rows=5, r=1.15)
    e.hatch(0, 0, 20, 8, step=1.65)
    for x, y in [(-14, -2), (-4, -6), (6, -2), (16, -6)]:
        e.mass(f"M{x} {y}L{x + 2} {y - 5}L{x + 4} {y + 0.5}Z")
        e.rim(f"M{x} {y}L{x + 2} {y - 5}", sw=0.6)
    e.mass("M24-10C30-18 40-22 48-18L50-12L40-10L34-6C30-4 26-6 24-10Z")
    e.path("M40-15L48-13L49-8L41-9Z", fill=SHADE)
    e.teeth(41, -12, n=4)
    e.eye(36, -13)
    return e.done()


def build_minotaur():
    e = _Engraver("minotaur")
    e.soft_shadow(0, 28, 12, 3.5, op=0.5)
    e.mass("M-10-10C-20-18 -24-30 -18-38C-22-28 -16-18 -6-12Z")
    e.mass("M10-10C20-18 24-30 18-38C22-28 16-18 6-12Z")
    e.rim("M-10-10C-20-18 -24-30 -18-38", sw=0.9)
    e.rim("M10-10C20-18 24-30 18-38", sw=0.9)
    e.horns([(-18, -32), (-16, -28), (-14, -24), (-12, -20), (-10, -16)])
    e.horns([(18, -32), (16, -28), (14, -24), (12, -20), (10, -16)])
    e.mass("M-10-12C-10 0 -6 8 0 10C6 8 10 0 10-12C6-18 -6-18 -10-12Z", grad="orb")
    e.shade("M2-6C6-4 8 2 6 8C2 10-2 6 0 0Z", op=0.65)
    e.lit("M-8-8C-6-14 0-16 4-14C0-10-4-6-8-6Z", op=0.48)
    e.rim("M-8-8C-6-14 0-16 4-14", sw=1.0)
    e.hatch(0, -4, 8, 10, step=1.35)
    e.path("M-6-4C-4-6 -2-6 -.5-4C-2-2-4-2-6-4Z", fill=SHADE)
    e.path("M6-4C4-6 2-6 .5-4C2-2 4-2 6-4Z", fill=SHADE)
    e.eye(-3.2, -4, r=0.42)
    e.eye(3.2, -4, r=0.42)
    e.teeth(-3, 12, n=4, up=False)
    e.mass("M-12 10C-10 24 -4 32 0 34C4 32 10 24 12 10C8 14 4 16 0 16C-4 16-8 14-12 10Z")
    e.shade("M2 14C6 18 8 26 4 32C0 32-2 24 0 16Z", op=0.55)
    e.hatch(0, 20, 9, 10, step=1.35)
    return e.done()


def build_chimera():
    e = _Engraver("chimera")
    e.soft_shadow(2, 18, 20, 4.5, op=0.55)
    e.mass("M-14 2C-14-8 -4-14 6-14C16-14 22-4 22 4C22 12 14 18 4 18C-6 18-14 12-14 2Z")
    e.shade("M4 0C12 2 18 6 20 12C12 16 2 16-4 10Z", op=0.7)
    e.lit("M-12 0C-8-8 2-12 12-8C4-4-4 0-10 2Z", op=0.5)
    e.rim("M-12 0C-8-8 2-12 12-8", sw=1.1)
    e.hatch(4, 2, 14, 12, step=1.45)
    e.scales(-8, -6, 16, 10, cols=8, rows=5, r=1.1)
    e.mass("M10-4C18-14 28-20 38-22L44-16L36-14L28-6C24-2 16 0 10-4Z")
    e.path("M34-18L42-15L43-10L35-11.5Z", fill=SHADE)
    e.teeth(35, -15, n=4)
    e.eye(30, -16, r=0.5)
    e.mass("M26-22L24-30L28-23Z")
    e.mass("M32-22L34-31L38-23Z")
    e.mass("M0-10C-2-20 4-28 12-30L18-24L12-22L6-14C4-12 2-10 0-10Z")
    e.eye(10, -24, r=0.4)
    e.mass("M8-28L6-36L10-30Z")
    e.mass("M12-28L16-36L16-29Z")
    e.mass("M-14 4C-22 10-30 18-34 28L-28 28L-24 16C-20 10-16 6-14 4Z")
    e.path("M-32 26C-38 30-42 26-44 20L-38 20C-37 24-34 28-32 26Z", fill=BODY)
    e.eye(-40, 22, r=0.4)
    e.scales(-34, 8, -18, 24, cols=4, rows=4, r=0.95)
    e.mass("M-4 14C-6 22-4 28-2 32L2 32L1 24C0 20-2 16-2 14Z")
    e.mass("M8 14C10 22 12 28 14 32L18 31L15 24C14 20 11 16 9 14Z")
    return e.done()


CREATURE_ART = {
    "jormungandr": build_jormungandr(),
    "nidhogg": build_nidhogg(),
    "fenrir": build_fenrir(),
    "wolf": build_fenrir(),
    "simorgh": build_simorgh(),
    "bird": build_simorgh(),
    "dahaka": build_dahaka(),
    "daeva": build_daeva(),
    "demon": build_daeva(),
    "mushussu": build_mushussu(),
    "humbaba": build_humbaba(),
    "guardian": build_humbaba(),
    "anzu": build_anzu(),
    "garuda": build_garuda(),
    "naga": build_naga(),
    "makara": build_makara(),
    "scylla": build_scylla(),
    "python": build_python(),
    "serpent": build_python(),
    "dragon": build_nidhogg(),
    "minotaur": build_minotaur(),
    "chimera": build_chimera(),
}
