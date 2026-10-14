"""Dense engraved bestiary silhouettes for tools/genmaps.py.

Antique atlas language: ink-black fill, thin gold stroke, cross-hatch /
scale / feather texture. Built as many small path elements so beasts read
as etched plates, not thick outline doodles. Keep MAPS creature scales
tiny (~0.5–0.9); these drawings are ~±18 units around the origin.
"""
from __future__ import annotations

GOLD = "#c9a45c"
INK = "#05070a"


def art(kind, gold=GOLD):
    raw = CREATURE_ART.get(kind) or CREATURE_ART["serpent"]
    if gold == GOLD:
        return raw
    return raw.replace(GOLD, gold)


# ---------------------------------------------------------------- builders


class _Engraver:
    """Accumulate filled silhouettes + dense gold hatch texture."""

    __slots__ = ("parts",)

    def __init__(self):
        self.parts: list[str] = []

    def path(self, d, fill=None, stroke=GOLD, sw=0.55, opacity=None):
        bits = [f'd="{d}"']
        bits.append(f'fill="{fill}"' if fill else 'fill="none"')
        if stroke:
            bits.append(f'stroke="{stroke}"')
        bits.append(f'stroke-width="{sw}"')
        bits.append('stroke-linecap="round" stroke-linejoin="round"')
        if opacity is not None:
            bits.append(f'opacity="{opacity}"')
        self.parts.append(f'<path {" ".join(bits)}/>')

    def circle(self, cx, cy, r, fill=GOLD, stroke=None, sw=0.4):
        bits = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
        if stroke:
            bits.append(f'stroke="{stroke}"')
            bits.append(f'stroke-width="{sw}"')
        self.parts.append(f'<circle {" ".join(bits)}/>')

    def hatch_box(self, x0, y0, x1, y1, step=1.6, a=1, b=1, sw=0.32, op=0.78):
        """Cross-hatch a bounding box (diagonal both ways)."""
        w, h = x1 - x0, y1 - y0
        # / direction
        start = -max(w, h)
        end = max(w, h) * 2
        t = start
        while t < end:
            # line through box: y - y0 = (b/a)*(x - x0) shifted by t
            xs, ys = [], []
            # clip parametric line x = x0 + t + s, y = y0 + s (for a=b=1 style)
            # Use two families: NE-SW and NW-SE
            t += step
        # NE-SW (/)
        for k in range(int((w + h) / step) + 3):
            ox = x0 - h + k * step
            self.path(
                f"M{ox:.1f} {y0:.1f}L{ox + h:.1f} {y1:.1f}",
                stroke=GOLD, sw=sw, opacity=op,
            )
        # NW-SE (\)
        for k in range(int((w + h) / step) + 3):
            ox = x0 + k * step
            self.path(
                f"M{ox:.1f} {y0:.1f}L{ox - h:.1f} {y1:.1f}",
                stroke=GOLD, sw=sw * 0.9, opacity=op * 0.85,
            )

    def hatch_body(self, cx, cy, rx, ry, step=1.55, sw=0.3, op=0.72):
        """Oval cross-hatch clipped roughly to body ellipse via short segments."""
        # parallel ribs along major axis
        y = cy - ry + 0.8
        while y < cy + ry:
            # chord width at this y
            dy = (y - cy) / ry
            if abs(dy) < 1:
                hw = rx * (1 - dy * dy) ** 0.5
                self.path(
                    f"M{cx - hw:.1f} {y:.1f}L{cx + hw:.1f} {y:.1f}",
                    stroke=GOLD, sw=sw, opacity=op,
                )
                # short cross ticks
                x = cx - hw + 0.6
                while x < cx + hw:
                    self.path(
                        f"M{x:.1f} {y - 0.7:.1f}L{x + 0.9:.1f} {y + 0.7:.1f}",
                        stroke=GOLD, sw=sw * 0.85, opacity=op * 0.9,
                    )
                    x += step
            y += step

    def scales(self, x0, y0, x1, y1, cols=6, rows=4, r=1.35, sw=0.35):
        """Scale texture: overlapping gold arcs on ink."""
        dx = (x1 - x0) / max(cols - 1, 1)
        dy = (y1 - y0) / max(rows - 1, 1)
        for j in range(rows):
            for i in range(cols):
                cx = x0 + i * dx + (0.55 if j % 2 else 0)
                cy = y0 + j * dy
                self.path(
                    f"M{cx - r:.1f} {cy:.1f}A{r:.1f} {r * 0.7:.1f} 0 0 1 {cx + r:.1f} {cy:.1f}",
                    stroke=GOLD, sw=sw, opacity=0.8,
                )

    def feathers(self, x0, y0, x1, y1, n=8, sw=0.38):
        """Feather ribs from base toward tip."""
        for i in range(n):
            t = i / max(n - 1, 1)
            bx = x0 + (x1 - x0) * 0.15
            by = y0 + (y1 - y0) * t
            tx = x1
            ty = y0 + (y1 - y0) * (t * 0.85 + 0.08)
            self.path(
                f"M{bx:.1f} {by:.1f}L{tx:.1f} {ty:.1f}",
                stroke=GOLD, sw=sw, opacity=0.75,
            )
            # vane ticks
            for k in (0.35, 0.55, 0.75):
                mx = bx + (tx - bx) * k
                my = by + (ty - by) * k
                self.path(
                    f"M{mx:.1f} {my:.1f}l{1.2:.1f} {-0.9 + t * 0.2:.1f}",
                    stroke=GOLD, sw=sw * 0.7, opacity=0.65,
                )

    def horn_ridges(self, pts, sw=0.4):
        """Short ridge marks along a polyline of (x,y)."""
        for i, (x, y) in enumerate(pts):
            self.path(
                f"M{x:.1f} {y:.1f}l{1.1:.1f} {0.6 if i % 2 == 0 else -0.6:.1f}",
                stroke=GOLD, sw=sw, opacity=0.8,
            )

    def teeth(self, x, y, n=4, up=True, sw=0.45):
        for i in range(n):
            tx = x + i * 1.7
            if up:
                self.path(
                    f"M{tx:.1f} {y:.1f}L{tx + 0.7:.1f} {y - 2.2:.1f}L{tx + 1.4:.1f} {y:.1f}Z",
                    fill=INK, stroke=GOLD, sw=sw,
                )
            else:
                self.path(
                    f"M{tx:.1f} {y:.1f}L{tx + 0.7:.1f} {y + 2.2:.1f}L{tx + 1.4:.1f} {y:.1f}Z",
                    fill=INK, stroke=GOLD, sw=sw,
                )

    def done(self):
        return "".join(self.parts)


def _serpent_body(e: _Engraver, coiled=False):
    if coiled:
        e.path(
            "M-18 6C-12-8 -2-14 8-8C16-4 20 2 18 8C16 14 8 16 0 12C-6 9-12 10-18 6Z",
            fill=INK, sw=1.05,
        )
    else:
        e.path(
            "M-26 6C-18-8 -6-14 6-6C14 0 22-2 26-10C28-14 26-16 22-14C14-8 6-2-4-6C-12-9-20-2-26 6Z",
            fill=INK, sw=1.05,
        )


def build_jormungandr():
    e = _Engraver()
    e.path(
        "M-28 4C-22-10 -10-16 2-10C12-6 20-2 24 4C26 8 24 4 22-2C20-8 14-12 6-10C-4-6-14-8-22-2C-26 2-28 6-28 4Z",
        fill=INK, sw=1.1,
    )
    e.scales(-22, -6, 18, 6, cols=10, rows=5, r=1.2)
    e.hatch_body(-4, 0, 18, 8, step=1.7)
    # dorsal plates
    for x, y in [(-16, -4), (-8, -8), (0, -7), (8, -3), (14, 0)]:
        e.path(f"M{x} {y}L{x + 2} {y - 5}L{x + 4} {y + 0.5}Z", fill=INK, stroke=GOLD, sw=0.7)
        e.path(f"M{x + 1.5} {y - 1}L{x + 2} {y - 3.5}", stroke=GOLD, sw=0.35, opacity=0.75)
    # head
    e.path("M22-2C28-8 36-12 42-10L44-6L36-4L32 0C28 3 24 2 22 0Z", fill=INK, sw=1.0)
    e.path("M34-7L42-6L43-2L35-2.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.path("M33-2L41 0L40 3L32 1.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.teeth(34, -5.5, n=4, up=True)
    e.teeth(33.5, -1, n=3, up=False)
    e.circle(30, -6.5, 0.55)
    e.path("M28-10L26-16L30-11Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M32-10.5L33-17L36-11Z", fill=INK, stroke=GOLD, sw=0.7)
    e.horn_ridges([(27, -12), (29, -14), (32, -13.5), (34, -12)])
    e.path("M42-5l5-1.2M42-4l5 2", stroke=GOLD, sw=0.45)
    return e.done()


def build_nidhogg():
    e = _Engraver()
    e.path(
        "M-14 2C-16-8 -8-16 2-16C14-16 20-6 20 2C20 10 12 16 2 16C-8 16-14 10-14 2Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(2, 0, 14, 12, step=1.5)
    e.scales(-8, -8, 14, 8, cols=8, rows=5, r=1.15)
    # wings
    e.path("M6-10C12-20 20-28 30-32C24-22 18-14 12-10C10-9 8-9 6-10Z", fill=INK, sw=0.95)
    e.path("M2-12C6-22 12-32 20-38C14-28 8-20 4-14C3-13 2-12 2-12Z", fill=INK, sw=0.9)
    e.feathers(8, -30, 28, -12, n=7)
    e.feathers(4, -34, 18, -14, n=5)
    # head
    e.path("M12-4C20-12 30-18 38-20L42-16L34-12L28-6C24-2 16 0 12-2Z", fill=INK, sw=1.0)
    e.path("M32-16L40-14L41-10L33-11Z", fill=INK, stroke=GOLD, sw=0.75)
    e.path("M31-11L39-9L38-5L30-6.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.teeth(33, -13.5, n=4)
    e.circle(28, -15, 0.55)
    for hx, hy in [(24, -20), (29, -21), (34, -19)]:
        e.path(f"M{hx} {hy}L{hx - 1} {hy - 8}L{hx + 3} {hy - 1}Z", fill=INK, stroke=GOLD, sw=0.7)
    e.horn_ridges([(25, -24), (28, -26), (32, -25), (35, -22)])
    # legs + claws
    e.path("M-6 12C-8 20-6 26-4 30L0 30L-1 22C-2 18-4 14-4 12Z", fill=INK, sw=0.85)
    e.path("M8 12C10 20 12 26 14 30L18 29L15 22C14 18 11 14 9 12Z", fill=INK, sw=0.85)
    for base in [(-4, 30), (14, 30)]:
        e.path(f"M{base[0]} {base[1]}l-2.5 3.5M{base[0]+2} {base[1]}l0 3.8M{base[0]+4} {base[1]}l2.5 3.2",
               stroke=GOLD, sw=0.5)
    e.path("M-14 4C-22 10-28 18-32 26L-26 26L-22 16C-18 10-15 6-14 4Z", fill=INK, sw=0.85)
    e.path("M-30 24L-36 26L-30 28Z", fill=INK, stroke=GOLD, sw=0.7)
    return e.done()


def build_fenrir():
    e = _Engraver()
    e.path(
        "M-16 0C-16-10 -6-16 4-16C14-16 20-8 20 0C20 8 12 14 2 14C-8 14-16 8-16 0Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(2, -1, 14, 11, step=1.55)
    # fur strokes
    for x, y in [(-10, -6), (-4, -10), (2, -11), (8, -8), (-8, 4), (0, 6), (8, 4)]:
        e.path(f"M{x} {y}l{-1.5 if x < 0 else 1.2} {-2.8}", stroke=GOLD, sw=0.4, opacity=0.8)
        e.path(f"M{x + 1.2} {y + 0.5}l{-1 if x < 0 else 1} {-2.2}", stroke=GOLD, sw=0.32, opacity=0.7)
    # head / snout
    e.path("M12-6C20-12 28-16 36-14L40-8L32-6L26-2C22 2 16 2 12 0Z", fill=INK, sw=1.0)
    e.path("M32-9L40-6L41-2L33-3.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.path("M31-3L39 0L38 4L30 1.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.teeth(33, -6.5, n=4)
    e.teeth(32, -1, n=3, up=False)
    e.circle(27, -9, 0.6)
    e.path("M18-12L16-22L22-14Z", fill=INK, stroke=GOLD, sw=0.75)
    e.path("M24-13L26-24L30-14Z", fill=INK, stroke=GOLD, sw=0.75)
    e.horn_ridges([(17, -16), (19, -18), (25, -18), (27, -16)])
    # fur on neck
    for i in range(6):
        e.path(f"M{6 + i * 1.5} {-8 - i * 0.2}l-1 {-3.5}", stroke=GOLD, sw=0.35, opacity=0.75)
    # legs
    for x in (-10, -2, 8):
        e.path(f"M{x} 10C{x - 1} 18 {x} 24 {x + 1} 28L{x + 5} 28L{x + 3} 20C{x + 2} 16 {x + 1} 12 {x} 10Z",
               fill=INK, sw=0.8)
        e.path(f"M{x + 1} 28l-2 3M{x + 3} 28l0 3.4M{x + 5} 28l2 2.8", stroke=GOLD, sw=0.45)
    e.path("M-16-2C-24-8 -32-10 -38-4C-32 2-26 4-20 4C-18 4-16 2-16-2Z", fill=INK, sw=0.85)
    for i in range(5):
        e.path(f"M{-22 - i * 3} {-4 - i * 0.3}l-1.2 2.8", stroke=GOLD, sw=0.35, opacity=0.75)
    return e.done()


def build_simorgh():
    e = _Engraver()
    # wings
    e.path("M-4-2C-14-10 -26-20 -34-28C-26-16 -16-8 -6-4C-5-3 -4-2 -4-2Z", fill=INK, sw=0.95)
    e.path("M4-2C14-10 26-20 34-28C26-16 16-8 6-4C5-3 4-2 4-2Z", fill=INK, sw=0.95)
    e.feathers(-30, -26, -6, -4, n=9)
    e.feathers(6, -4, 30, -26, n=9)
    # body
    e.path(
        "M-4-4C-8 0 -9 10 -4 16C-1 20 5 20 8 16C12 10 11 0 6-4C3-7 -1-7 -4-4Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(2, 4, 7, 10, step=1.4)
    e.scales(-2, 0, 8, 12, cols=5, rows=4, r=1.0)
    # head
    e.path("M2-4C1-12 4-16 10-18L18-19L15-15L11-14L13-10L8-9C4-8 2-5 2-4Z", fill=INK, sw=0.9)
    e.circle(10, -14, 0.55)
    for hx, hy in [(5, -16), (9, -17), (13, -16)]:
        e.path(f"M{hx} {hy}L{hx - 1} {hy - 9}L{hx + 3} {hy - 1}Z", fill=INK, stroke=GOLD, sw=0.65)
    e.horn_ridges([(6, -20), (8, -22), (11, -22), (14, -20)])
    # peacock tail
    e.path("M-2 14L-10 30L4 32L8 16Z", fill=INK, sw=0.85)
    e.feathers(-8, 16, 6, 30, n=6)
    e.path("M-4 20L-12 26L-2 28Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M6 20L14 27L7 29Z", fill=INK, stroke=GOLD, sw=0.7)
    for i in range(5):
        e.path(f"M{i - 1} 16l{i * 0.3 - 1} 8", stroke=GOLD, sw=0.35, opacity=0.7)
    return e.done()


def build_dahaka():
    e = _Engraver()
    e.path(
        "M-12 2C-14-8 -6-16 2-16C12-16 18-6 18 2C18 10 10 16 0 16C-10 16-14 10-12 2Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(2, 0, 12, 12, step=1.5)
    e.scales(-6, -8, 12, 8, cols=7, rows=5, r=1.1)
    # three heads
    heads = [
        (-8, -10, -24, -26, -30, -24),
        (2, -12, 16, -30, 24, -28),
        (10, -6, 28, -20, 34, -16),
    ]
    for bx, by, mx, my, tipx, tipy in heads:
        e.path(
            f"M{bx} {by}C{bx + 4} {by - 8} {mx} {my} {tipx} {tipy}L{tipx + 4} {tipy + 4}"
            f"L{mx + 2} {my + 6}C{bx + 8} {by + 2} {bx + 2} {by + 2} {bx} {by}Z",
            fill=INK, sw=0.9,
        )
        e.path(
            f"M{tipx - 2} {tipy + 2}L{tipx + 5} {tipy + 3}L{tipx + 4} {tipy + 7}L{tipx - 2} {tipy + 5}Z",
            fill=INK, stroke=GOLD, sw=0.7,
        )
        e.teeth(tipx - 1, tipy + 3.5, n=3)
        e.circle(tipx - 4, tipy + 1, 0.45)
        for k in range(3):
            e.path(
                f"M{tipx - 6 + k * 2} {tipy - 2}L{tipx - 7 + k * 2} {tipy - 8}",
                stroke=GOLD, sw=0.45,
            )
            e.path(
                f"M{tipx - 6 + k * 2} {tipy - 4}L{tipx - 5.5 + k * 2} {tipy - 7}",
                fill=INK, stroke=GOLD, sw=0.55,
            )
    # wing flaps
    e.path("M-4-8C0-18 6-24 14-28C8-18 2-12 0-8Z", fill=INK, sw=0.8)
    e.path("M6-8C12-18 20-24 28-26C20-18 12-12 8-8Z", fill=INK, sw=0.8)
    e.feathers(-2, -24, 12, -10, n=5)
    e.feathers(8, -24, 26, -10, n=5)
    # legs
    e.path("M-12 4C-20 10-26 18-30 26L-24 26L-20 16C-16 10-13 6-12 4Z", fill=INK, sw=0.8)
    e.path("M-4 12C-5 20-4 26-2 30L2 30L1 22C0 18-2 14-2 12Z", fill=INK, sw=0.8)
    e.path("M6 12C8 20 10 26 12 30L16 29L14 22C12 18 9 14 7 12Z", fill=INK, sw=0.8)
    return e.done()


def build_daeva():
    e = _Engraver()
    e.path("M-10 28C-9 12 -6 2 0 2C6 2 9 12 10 28L6 28C5 16 3 10 0 10C-3 10-5 16-6 28Z",
           fill=INK, sw=1.0)
    e.hatch_body(0, 16, 6, 12, step=1.4)
    for y in (12, 16, 20, 24):
        e.path(f"M-5 {y}H5", stroke=GOLD, sw=0.35, opacity=0.75)
        e.path(f"M-3 {y - 1}L3 {y + 1}", stroke=GOLD, sw=0.28, opacity=0.65)
    e.path("M-2 8H2V14H-2Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M0-18C8-18 14-10 14-2C14 6 8 12 0 12C-8 12-14 6-14-2C-14-10-8-18 0-18Z",
           fill=INK, sw=1.1)
    e.hatch_body(0, -4, 10, 12, step=1.45)
    # horns
    e.path("M-8-12C-16-18 -20-28 -18-36C-12-28 -10-20 -6-14Z", fill=INK, sw=0.85)
    e.path("M8-12C16-18 20-28 18-36C12-28 10-20 6-14Z", fill=INK, sw=0.85)
    e.horn_ridges([(-16, -28), (-14, -24), (-12, -20), (-10, -16)])
    e.horn_ridges([(16, -28), (14, -24), (12, -20), (10, -16)])
    for y in range(-32, -14, 3):
        e.path(f"M{-15} {y}l2.2 1", stroke=GOLD, sw=0.35, opacity=0.75)
        e.path(f"M{15} {y}l-2.2 1", stroke=GOLD, sw=0.35, opacity=0.75)
    # face
    e.path("M-12-4L-18-1L-12 3Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M12-4L18-1L12 3Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M-8-6L-2-3M8-6L2-3", stroke=GOLD, sw=0.55)
    e.path("M-7-2C-5-4 -3-4 -1.5-2C-3 0-5 0-7-2Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M7-2C5-4 3-4 1.5-2C3 0 5 0 7-2Z", fill=INK, stroke=GOLD, sw=0.7)
    e.circle(-4.2, -2, 0.35, fill=GOLD)
    e.circle(4.2, -2, 0.35, fill=GOLD)
    e.path("M0-1V5", stroke=GOLD, sw=0.5)
    e.path("M-5 7C-3 4 -2 5 0 8C2 5 3 4 5 7", stroke=GOLD, sw=0.55)
    e.teeth(-3, 8, n=4, up=False)
    e.path("M-5-14q5-3 10 0", stroke=GOLD, sw=0.4, opacity=0.75)
    for i in range(4):
        e.path(f"M{-6 + i * 3} {-12}l0.5 {-2}", stroke=GOLD, sw=0.3, opacity=0.7)
    return e.done()


def build_mushussu():
    e = _Engraver()
    e.path(
        "M-16 2C-16-8 -6-14 4-14C16-14 22-4 22 4C22 12 14 18 4 18C-8 18-16 12-16 2Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(2, 2, 15, 12, step=1.5)
    e.scales(-10, -6, 16, 10, cols=9, rows=5, r=1.25)
    # dragon head
    e.path("M10-4C18-14 28-22 38-26L44-20L36-18L28-10C24-6 16-2 10-4Z", fill=INK, sw=1.0)
    e.path("M34-22L42-19L43-14L35-15.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.path("M33-16L41-13L40-8L32-9.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.teeth(35, -19, n=4)
    e.circle(30, -18, 0.55)
    e.path("M26-26L24-34L28-27Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M32-26L34-35L38-27Z", fill=INK, stroke=GOLD, sw=0.7)
    e.horn_ridges([(27, -28), (30, -30), (34, -29), (36, -27)])
    # scorpion tail
    e.path("M-16 2C-24 0 -30-6 -36-14L-38-8L-30-2C-26 2-20 4-16 4Z", fill=INK, sw=0.85)
    e.scales(-34, -10, -18, 2, cols=5, rows=3, r=1.0)
    e.path("M-36-12L-42-10L-38-4Z", fill=INK, stroke=GOLD, sw=0.7)
    # legs + hind
    e.path("M-6 14C-8 22-6 28-4 32L0 32L-1 24C-2 20-4 16-4 14Z", fill=INK, sw=0.8)
    e.path("M8 14C10 22 12 28 14 32L18 31L15 24C14 20 11 16 9 14Z", fill=INK, sw=0.8)
    for base in [(-4, 32), (14, 32)]:
        e.path(f"M{base[0]} {base[1]}l-2 3M{base[0]+2} {base[1]}l0 3.4M{base[0]+4} {base[1]}l2 2.8",
               stroke=GOLD, sw=0.45)
    # small forewings
    e.path("M0-10C4-20 10-26 18-30C12-22 6-14 2-10Z", fill=INK, sw=0.75)
    e.path("M8-10C14-20 22-26 30-28C22-20 14-14 10-10Z", fill=INK, sw=0.75)
    e.feathers(2, -28, 16, -12, n=5)
    return e.done()


def build_humbaba():
    e = _Engraver()
    e.path(
        "M0-16C12-16 18-6 18 4C18 16 8 22 0 22C-8 22-18 16-18 4C-18-6-12-16 0-16Z",
        fill=INK, sw=1.15,
    )
    e.hatch_body(0, 2, 14, 16, step=1.45)
    # entrails / guts texture (classic Humbaba face)
    for r in (4, 7, 10, 13):
        e.path(
            f"M0 {-r}A{r} {r * 0.85} 0 1 1 0 {r}A{r} {r * 0.85} 0 1 1 0 {-r}",
            stroke=GOLD, sw=0.4, opacity=0.7,
        )
    import math
    for a in range(0, 360, 30):
        rad = math.radians(a)
        cx = round(15.5 * math.cos(rad), 1)
        cy = round(1 + 16.5 * math.sin(rad) * 0.95, 1)
        e.circle(cx, cy, 2.0, fill=INK, stroke=GOLD, sw=0.7)
        e.path(
            f"M{cx - 1.2} {cy}L{cx + 1.2} {cy}M{cx} {cy - 1.2}L{cx} {cy + 1.2}"
            f"M{cx - 0.8} {cy - 0.8}L{cx + 0.8} {cy + 0.8}",
            stroke=GOLD, sw=0.28, opacity=0.75,
        )
    # face
    e.path("M-8-5L-2-1M8-5L2-1", stroke=GOLD, sw=0.7)
    e.path("M-8-1C-6-4 -3-4 -1.5-1C-3 2-6 2-8-1Z", fill=INK, stroke=GOLD, sw=0.75)
    e.path("M8-1C6-4 3-4 1.5-1C3 2 6 2 8-1Z", fill=INK, stroke=GOLD, sw=0.75)
    e.circle(-4.5, -1, 0.45)
    e.circle(4.5, -1, 0.45)
    e.path("M0-4V5", stroke=GOLD, sw=0.55)
    e.path("M-7 8q3.5 5 7 0q3.5-5 7 0", stroke=GOLD, sw=0.65)
    e.path("M-5 11q2.5 3.5 5 0q2.5-3.5 5 0", stroke=GOLD, sw=0.45)
    e.teeth(-4, 10, n=5, up=False)
    # beard / cheek folds
    e.path("M-10 8C-14 14-12 20-8 22L-6 18C-8 14-8 10-8 8Z", fill=INK, sw=0.75)
    e.path("M10 8C14 14 12 20 8 22L6 18C8 14 8 10 8 8Z", fill=INK, sw=0.75)
    for i in range(4):
        e.path(f"M{-9} {10 + i * 2.5}l-2.5 1.5", stroke=GOLD, sw=0.35, opacity=0.75)
        e.path(f"M{9} {10 + i * 2.5}l2.5 1.5", stroke=GOLD, sw=0.35, opacity=0.75)
    return e.done()


def build_anzu():
    e = _Engraver()
    e.path("M-4-2C-14-10 -26-20 -34-28C-26-16 -16-8 -6-4C-5-3 -4-2 -4-2Z", fill=INK, sw=0.9)
    e.path("M4-2C14-10 26-20 34-28C26-16 16-8 6-4C5-3 4-2 4-2Z", fill=INK, sw=0.9)
    e.feathers(-30, -26, -6, -4, n=8)
    e.feathers(6, -4, 30, -26, n=8)
    e.path(
        "M-4-4C-9 0 -10 10 -5 16C-2 20 5 20 8 16C13 10 12 0 7-4C4-7 0-7 -4-4Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(2, 4, 7, 10, step=1.4)
    e.scales(-2, 0, 8, 12, cols=5, rows=4, r=1.0)
    # lion head
    e.path("M1-4C0-12 4-17 10-18L18-19L16-15L12-14L14-10L8-9C4-8 2-5 1-4Z", fill=INK, sw=0.9)
    e.circle(10, -13, 0.55)
    e.path("M6-16L4-25L8-18Z", fill=INK, stroke=GOLD, sw=0.65)
    e.path("M11-16.5L13-26L16-17.5Z", fill=INK, stroke=GOLD, sw=0.65)
    for i in range(5):
        e.path(f"M{-2 + i} {-6}l{-1.5 + i * 0.2} {-4}", stroke=GOLD, sw=0.35, opacity=0.8)
    e.path("M-2 14L-10 28L4 30L8 16Z", fill=INK, sw=0.8)
    e.feathers(-8, 16, 6, 28, n=5)
    e.teeth(10, -11, n=3, up=False)
    return e.done()


def build_garuda():
    e = _Engraver()
    e.path("M-4-1C-16-10 -28-20 -36-28C-28-16 -16-7 -6-3C-5-2 -4-1 -4-1Z", fill=INK, sw=0.95)
    e.path("M4-1C16-10 28-20 36-28C28-16 16-7 6-3C5-2 4-1 4-1Z", fill=INK, sw=0.95)
    e.feathers(-32, -26, -6, -3, n=10)
    e.feathers(6, -3, 32, -26, n=10)
    e.path(
        "M-3-4C-8 0 -9 11 -4 17C-1 21 5 21 8 17C13 11 12 0 7-4C4-7 0-7 -3-4Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(2, 5, 7, 10, step=1.35)
    e.path("M1-4C0-12 4-17 10-18L18-19L15-15L11-14L13-10L8-9C4-8 2-5 1-4Z", fill=INK, sw=0.9)
    e.circle(10, -13, 0.55)
    for hx, hy in [(5, -16), (9, -17.5), (13, -16)]:
        e.path(f"M{hx} {hy}L{hx - 1} {hy - 10}L{hx + 3} {hy - 1}Z", fill=INK, stroke=GOLD, sw=0.65)
    e.horn_ridges([(6, -20), (9, -23), (12, -22), (15, -19)])
    e.path("M-6 4L-16 12M6 4L16 12", stroke=GOLD, sw=0.7)
    e.path("M-2 14L-8 28L4 30L7 16Z", fill=INK, sw=0.8)
    e.feathers(-6, 16, 5, 28, n=5)
    return e.done()


def build_naga():
    e = _Engraver()
    e.path(
        "M-6 18C-16 8 -18-4 -10-14C-2-24 8-26 16-16C24-6 22 6 14 16C8 22 0 24-6 18Z",
        fill=INK, sw=1.1,
    )
    e.scales(-10, -8, 14, 16, cols=8, rows=8, r=1.3)
    e.hatch_body(2, 2, 12, 14, step=1.6)
    # hooded heads
    e.path("M-2-14C-8-24 -2-34 6-36C14-38 20-30 20-20C20-12 12-10 4-10C0-10-2-12-2-14Z",
           fill=INK, sw=0.95)
    e.path("M0-22C-2-30 2-36 8-38C12-39 16-34 16-28C16-22 12-20 8-20Z", fill=INK, sw=0.8)
    e.path("M10-18C14-28 20-32 26-30C28-28 28-22 24-18C20-15 14-15 10-16Z", fill=INK, sw=0.75)
    e.circle(7, -24, 0.5)
    e.circle(18, -22, 0.4)
    for i in range(5):
        e.path(f"M{4 + i * 2} {-30}L{3 + i * 2} {-38}", stroke=GOLD, sw=0.45)
    e.path("M10-16l5 2.5M10-15.5l5-2", stroke=GOLD, sw=0.4)
    e.path("M8 16C2 26 -6 32-16 34L-12 38C0 36 12 26 16 18Z", fill=INK, sw=0.85)
    e.scales(-12, 20, 10, 34, cols=5, rows=3, r=1.1)
    return e.done()


def build_makara():
    e = _Engraver()
    e.path(
        "M-20 2C-14-12 0-18 12-12C24-6 30 2 30 10C30 18 22 24 8 24C-6 24-20 14-20 2Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(4, 4, 18, 12, step=1.5)
    e.scales(-12, -4, 22, 14, cols=10, rows=5, r=1.3)
    # crocodile snout
    e.path("M22 2C30-6 40-10 48-6L50-1L40 1L34 6C30 8 26 6 22 4Z", fill=INK, sw=1.0)
    e.path("M38-3L48-1L49 4L39 2.5Z", fill=INK, stroke=GOLD, sw=0.75)
    e.teeth(39, -1, n=5)
    e.teeth(39, 2.5, n=4, up=False)
    e.circle(32, -2, 0.55)
    e.path("M46-4C50-10 54-6 52 0C50 4 46 2 46-4Z", fill=INK, stroke=GOLD, sw=0.7)
    # trunk curl
    e.path("M-20 4C-28 10-36 18-40 28L-34 28L-30 16C-26 10-22 6-20 4Z", fill=INK, sw=0.85)
    e.path("M-38 26L-46 22L-40 32Z", fill=INK, stroke=GOLD, sw=0.7)
    e.scales(-38, 8, -24, 24, cols=4, rows=4, r=1.0)
    # crest horns
    for x in (-2, 6, 14):
        e.path(f"M{x} -10L{x + 2} {-18}L{x + 4} {-10.5}Z", fill=INK, stroke=GOLD, sw=0.65)
    e.horn_ridges([(-1, -14), (2, -16), (8, -16), (12, -14), (16, -12)])
    # flippers
    e.path("M-4 20C-8 28-4 34 2 36L6 32L2 26C0 23-2 21-2 20Z", fill=INK, sw=0.8)
    e.path("M12 20C16 28 20 34 26 36L30 32L24 26C20 23 16 21 14 20Z", fill=INK, sw=0.8)
    return e.done()


def build_scylla():
    e = _Engraver()
    e.path(
        "M-10 6C-14-4 -6-14 2-14C12-14 18-2 16 6C14 14 4 18-4 18C-10 18-12 12-10 6Z",
        fill=INK, sw=1.05,
    )
    e.hatch_body(2, 2, 10, 12, step=1.45)
    # three dog heads
    for bx, by, hx, hy in [(-8, -8, -26, -28), (0, -10, 14, -32), (10, -4, 30, -20)]:
        e.path(
            f"M{bx} {by}C{bx - 2} {by - 10} {hx + 4} {hy + 4} {hx} {hy}L{hx - 4} {hy + 6}"
            f"L{bx + 4} {by + 2}Z",
            fill=INK, sw=0.85,
        )
        e.path(
            f"M{hx - 2} {hy + 2}L{hx + 6} {hy + 4}L{hx + 5} {hy + 8}L{hx - 2} {hy + 5}Z",
            fill=INK, stroke=GOLD, sw=0.7,
        )
        e.teeth(hx - 1, hy + 3.5, n=3)
        e.circle(hx - 3, hy + 1, 0.4)
        e.path(f"M{hx - 4} {hy - 2}L{hx - 6} {hy - 8}L{hx - 1} {hy - 3}Z", fill=INK, stroke=GOLD, sw=0.6)
    # tentacles
    for i, (sx, ex, ey) in enumerate([(-8, -22, 34), (-2, -4, 38), (6, 14, 36), (10, 26, 30)]):
        e.path(
            f"M{sx} 14C{sx - 4} 22 {ex} {ey - 8} {ex} {ey}L{ex + 4} {ey - 2}"
            f"C{ex + 2} {ey - 10} {sx + 4} 20 {sx + 2} 14Z",
            fill=INK, sw=0.75,
        )
        e.scales(min(sx, ex), 16, max(sx, ex) + 4, ey - 2, cols=3, rows=4, r=0.9)
    return e.done()


def build_python():
    e = _Engraver()
    e.path(
        "M-26 8C-16-10 -2-16 10-6C18 0 26-2 30-12C32-16 28-18 24-14C16-6 6 0-4-4C-12-7-20 0-26 8Z",
        fill=INK, sw=1.1,
    )
    e.scales(-20, -6, 22, 8, cols=12, rows=5, r=1.2)
    e.hatch_body(0, 0, 20, 8, step=1.7)
    for x, y in [(-14, -2), (-4, -6), (6, -2), (16, -6)]:
        e.path(f"M{x} {y}L{x + 2} {y - 5}L{x + 4} {y + 0.5}Z", fill=INK, stroke=GOLD, sw=0.65)
    e.path("M24-10C30-18 40-22 48-18L50-12L40-10L34-6C30-4 26-6 24-10Z", fill=INK, sw=0.95)
    e.path("M40-15L48-13L49-8L41-9Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M39-9L47-7L46-2L38-4Z", fill=INK, stroke=GOLD, sw=0.7)
    e.teeth(41, -12, n=4)
    e.circle(36, -13, 0.55)
    e.path("M48-10l6-1.5M48-9l6 2.2", stroke=GOLD, sw=0.4)
    return e.done()


def build_minotaur():
    e = _Engraver()
    e.path("M-10-10C-20-18 -24-30 -18-38C-22-28 -16-18 -6-12Z", fill=INK, sw=0.9)
    e.path("M10-10C20-18 24-30 18-38C22-28 16-18 6-12Z", fill=INK, sw=0.9)
    e.horn_ridges([(-18, -32), (-16, -28), (-14, -24), (-12, -20), (-10, -16)])
    e.horn_ridges([(18, -32), (16, -28), (14, -24), (12, -20), (10, -16)])
    for y in range(-34, -14, 3):
        e.path(f"M{-17} {y}l2.4 1.1", stroke=GOLD, sw=0.35, opacity=0.75)
        e.path(f"M{17} {y}l-2.4 1.1", stroke=GOLD, sw=0.35, opacity=0.75)
    e.path("M-10-12C-10 0 -6 8 0 10C6 8 10 0 10-12C6-18 -6-18 -10-12Z", fill=INK, sw=1.1)
    e.hatch_body(0, -4, 8, 10, step=1.4)
    e.path("M-7-8C-4-11 0-11 0-8.5M7-8C4-11 0-11 0-8.5", stroke=GOLD, sw=0.45)
    e.path("M-6-4C-4-6 -2-6 -.5-4C-2-2-4-2-6-4Z", fill=INK, stroke=GOLD, sw=0.7)
    e.path("M6-4C4-6 2-6 .5-4C2-2 4-2 6-4Z", fill=INK, stroke=GOLD, sw=0.7)
    e.circle(-3.2, -4, 0.4)
    e.circle(3.2, -4, 0.4)
    e.path("M-6 4C-6 12 -2 16 0 16C2 16 6 12 6 4", stroke=GOLD, sw=0.7)
    e.teeth(-3, 12, n=4, up=False)
    e.path("M-12 10C-10 24 -4 32 0 34C4 32 10 24 12 10C8 14 4 16 0 16C-4 16-8 14-12 10Z",
           fill=INK, sw=0.95)
    e.hatch_body(0, 20, 9, 10, step=1.4)
    for y in (14, 18, 22, 26):
        e.path(f"M-7 {y}H7", stroke=GOLD, sw=0.32, opacity=0.7)
    return e.done()


def build_chimera():
    e = _Engraver()
    e.path(
        "M-14 2C-14-8 -4-14 6-14C16-14 22-4 22 4C22 12 14 18 4 18C-6 18-14 12-14 2Z",
        fill=INK, sw=1.1,
    )
    e.hatch_body(4, 2, 14, 12, step=1.5)
    e.scales(-8, -6, 16, 10, cols=8, rows=5, r=1.15)
    # lion head
    e.path("M10-4C18-14 28-20 38-22L44-16L36-14L28-6C24-2 16 0 10-4Z", fill=INK, sw=0.95)
    e.path("M34-18L42-15L43-10L35-11.5Z", fill=INK, stroke=GOLD, sw=0.7)
    e.teeth(35, -15, n=4)
    e.circle(30, -16, 0.5)
    e.path("M26-22L24-30L28-23Z", fill=INK, stroke=GOLD, sw=0.65)
    e.path("M32-22L34-31L38-23Z", fill=INK, stroke=GOLD, sw=0.65)
    # goat head
    e.path("M0-10C-2-20 4-28 12-30L18-24L12-22L6-14C4-12 2-10 0-10Z", fill=INK, sw=0.85)
    e.circle(10, -24, 0.4)
    e.path("M8-28L6-36L10-30Z", fill=INK, stroke=GOLD, sw=0.6)
    e.path("M12-28L16-36L16-29Z", fill=INK, stroke=GOLD, sw=0.6)
    e.horn_ridges([(8, -32), (10, -34), (14, -33)])
    # serpent tail
    e.path("M-14 4C-22 10-30 18-34 28L-28 28L-24 16C-20 10-16 6-14 4Z", fill=INK, sw=0.85)
    e.path("M-32 26C-38 30-42 26-44 20L-38 20C-37 24-34 28-32 26Z", fill=INK, stroke=GOLD, sw=0.7)
    e.circle(-40, 22, 0.4)
    e.scales(-34, 8, -18, 24, cols=4, rows=4, r=1.0)
    e.path("M-4 14C-6 22-4 28-2 32L2 32L1 24C0 20-2 16-2 14Z", fill=INK, sw=0.8)
    e.path("M8 14C10 22 12 28 14 32L18 31L15 24C14 20 11 16 9 14Z", fill=INK, sw=0.8)
    return e.done()


# ---------------------------------------------------------------- registry

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
