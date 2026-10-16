"""Engraving-style art for the map generator: monsters, ships and terrain glyphs.

Everything is built from tapered "ribbons" (a spine curve with a width profile) so the
beasts have the swelling, tapering forms of old copper-plate engravings. All art is
defined in local units (a creature is roughly 40 units wide), faces +x and is placed by
genmaps.py. Each piece is drawn twice - a dark halo, then a fine gold line - so it stays
readable on both the dark sea and the olive land.
"""
import math
import random

GOLD = "#e0c47c"
INK = "#05080b"
FILL = "#0e150b"
FILL2 = "#1b2611"


# ------------------------------------------------------------------ geometry
def catmull(pts, n=8, closed=False):
    P = list(pts)
    P = ([P[-1]] + P + [P[0], P[1]]) if closed else ([P[0]] + P + [P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[-2])
    return out


def prof(stops):
    def f(t):
        for (a, wa), (b, wb) in zip(stops, stops[1:]):
            if t <= b:
                return wa + (wb - wa) * ((t - a) / (b - a) if b > a else 0)
        return stops[-1][1]
    return f


def ribbon(spine, width):
    n = len(spine)
    L, R = [], []
    for i, (x, y) in enumerate(spine):
        a, b = spine[max(i - 1, 0)], spine[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (width(i / (n - 1)) if callable(width) else width) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L + R[::-1]


def D(pts, close=True):
    return "M" + "L".join("%.1f %.1f" % p for p in pts) + ("Z" if close else "")


def xf(pts, x=0, y=0, ang=0, s=1.0, fx=1):
    c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    out = []
    for px, py in pts:
        px, py = px * s * fx, py * s
        out.append((x + px * c - py * sn, y + px * sn + py * c))
    return out


def normals(spine):
    n = len(spine)
    out = []
    for i in range(n):
        a, b = spine[max(i - 1, 0)], spine[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        out.append((-dy / d, dx / d, dx / d, dy / d))
    return out


class Art:
    def __init__(self):
        self.items = []

    def shape(self, pts, fill=FILL, sw=1.0):
        self.items.append(("s", D(pts), fill, sw))

    def line(self, pts, sw=0.8, closed=False):
        d = pts if isinstance(pts, str) else D(pts, closed)
        self.items.append(("l", d, None, sw))

    def dot(self, x, y, r=0.5, color=GOLD):
        self.items.append(("o", "%.1f %.1f %.2f" % (x, y, r), color, 0))

    def render(self, x, y, s, fx=1, opacity=0.95):
        halo, main = [], []
        for kind, d, fill, sw in self.items:
            if kind == "s":
                halo.append('<path d="%s" fill="%s" stroke-width="%.2f"/>' % (d, INK, sw + 2.6))
                main.append('<path d="%s" fill="%s" stroke-width="%.2f"/>' % (d, fill, sw))
            elif kind == "l":
                halo.append('<path d="%s" fill="none" stroke-width="%.2f"/>' % (d, sw + 2.6))
                main.append('<path d="%s" fill="none" stroke-width="%.2f"/>' % (d, sw))
            else:
                cx, cy, r = d.split()
                main.append('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="none"/>' % (cx, cy, r, fill))
        return ('<g transform="translate(%.1f %.1f) scale(%.3f %.3f)" opacity="%.2f" stroke-linejoin="round" stroke-linecap="round">'
                '<g stroke="%s" fill="%s">%s</g><g stroke="%s">%s</g></g>'
                % (x, y, s * fx, s, opacity, INK, INK, "".join(halo), GOLD, "".join(main)))


# ------------------------------------------------------------------ shared parts
def head(a, x, y, ang, s=1.0, open_=1.2, horns=True, tongue=True, fangs=True, crest=0):
    """Reptile / serpent head, facing +x, origin at the back of the skull."""
    o = open_
    up = [(0, -2.6), (2.4, -3.5), (5.4, -3.2), (8.2, -2.2), (10.2, -1.2), (10.5, -.2), (7.6, -.5), (4.2, .3), (0, .9)]
    lo = [(.4, 1.2), (3, 1.0), (6.4, 1.3 + o), (9.6, 1.7 + o * 1.5), (9.2, 2.9 + o * 1.5), (5.6, 3.2 + o), (1.6, 2.9)]
    if horns:
        sp = catmull([(1, -3), (-1.2, -5.4), (-4.4, -6.3), (-7.4, -5.6)], 6)
        a.shape(xf(ribbon(sp, prof([(0, 1.3), (1, .2)])), x, y, ang, s), FILL2, .8)
        sp = catmull([(2.2, -3.4), (.8, -6.2), (-1.4, -7.8), (-4.2, -8)], 6)
        a.shape(xf(ribbon(sp, prof([(0, 1.0), (1, .2)])), x, y, ang, s), FILL2, .7)
    for k in range(crest):
        cx = -0.5 - k * 1.6
        a.shape(xf([(cx, -2.6), (cx - 1.2, -5.0 - k * .3), (cx - 2.4, -2.4)], x, y, ang, s), FILL2, .6)
    a.shape(xf(lo, x, y, ang, s), FILL, .9)
    a.shape(xf(up, x, y, ang, s), FILL, 1.0)
    if fangs:
        a.shape(xf([(8.2, -.4), (8.7, 1.3 + o * .6), (9.4, -.5)], x, y, ang, s), GOLD, .4)
        a.shape(xf([(5.8, .1), (6.2, 1.2 + o * .5), (6.8, -.1)], x, y, ang, s), GOLD, .4)
    if tongue and o > .5:
        t = [(8.6, 1.9 + o * .9), (11.6, 1.5 + o), (12.4, .6 + o), (11.6, 1.5 + o), (12.6, 2.4 + o)]
        a.line(xf(t, x, y, ang, s), .6)
    px, py = xf([(3.4, -1.9)], x, y, ang, s)[0]
    a.dot(px, py, .6)
    a.line(xf([(2.2, -2.7), (4.8, -3.1)], x, y, ang, s), .6)
    nx, ny = xf([(9.5, -1.0)], x, y, ang, s)[0]
    a.dot(nx, ny, .3)


def spikes(a, spine, every=3, size=1.8, side=-1, start=0.15, end=0.9, fill=FILL2):
    nrm = normals(spine)
    n = len(spine)
    for i in range(int(n * start), int(n * end), every):
        x, y = spine[i]
        nx, ny, tx, ty = nrm[i]
        h = size * (0.7 + 0.5 * math.sin(i * 1.7) ** 2)
        a.shape([(x - tx * .9, y - ty * .9), (x + nx * side * h - tx * .3, y + ny * side * h - ty * .3), (x + tx * .9, y + ty * .9)], fill, .5)


def hatch_across(a, spine, width, every=3, start=.1, end=.9, sw=.5):
    nrm = normals(spine)
    n = len(spine)
    for i in range(int(n * start), int(n * end), every):
        x, y = spine[i]
        nx, ny = nrm[i][0], nrm[i][1]
        w = (width(i / (n - 1)) if callable(width) else width) / 2 * .8
        a.line([(x - nx * w, y - ny * w), (x + nx * w * .1 + nrm[i][2] * .6, y + ny * w * .1 + nrm[i][3] * .6)], sw)


def limb(a, ctrl, w0, w1, fill=FILL, claw=True, sw=.9):
    sp = catmull(ctrl, 6)
    a.shape(ribbon(sp, prof([(0, w0), (.55, (w0 + w1) / 2), (1, w1)])), fill, sw)
    if claw:
        x, y = sp[-1]
        px, py = sp[-3]
        dx, dy = x - px, y - py
        d = math.hypot(dx, dy) or 1
        dx, dy = dx / d, dy / d
        for k in (-1, 0, 1):
            a.line([(x, y), (x + dx * 1.6 + -dy * k * 1.1, y + dy * 1.6 + dx * k * 1.1)], .6)


# ------------------------------------------------------------------ creatures
def sea_serpent(heads=1, flame=False):
    a = Art()
    water = []
    for (x0, x1, h) in [(-31, -17, 7.5), (-13, 5, 12)]:
        sp = [(x0 + (x1 - x0) * t / 16, -h * math.sin(math.pi * t / 16)) for t in range(17)]
        a.shape(ribbon(sp, lambda t: .6 + 4.6 * math.sin(math.pi * t) ** .42), FILL, 1.1)
        hatch_across(a, sp, 4.6, 1, .1, .9)
        spikes(a, sp, 2, 2.4, -1, .12, .88)
        water.append((x0, x1))
    a.shape([(-31.5, 0), (-36.5, -5), (-34, -1.2), (-39.5, .4), (-33, 1.6)], FILL2, .9)
    neck = catmull([(6, -1), (11.5, -6), (17, -13), (15.6, -20.5), (19.4, -26)], 8)
    a.shape(ribbon(neck, prof([(0, 4.8), (.5, 4.0), (1, 3.0)])), FILL, 1.1)
    spikes(a, neck, 3, 2.3, -1, .1, .9)
    hatch_across(a, neck, 4.0, 2, .1, .9)
    head(a, 18.6, -26.4, -26, 1.3, 1.6, crest=3)
    for (x0, x1) in water:
        a.line("M%.1f 1.6Q%.1f 3.6 %.1f 1.6" % (x0 - 3, (x0 + x1) / 2, x1 + 3), .6)
    a.line("M-39 4.2q3-2 6 0t6 0M7 3.4q3-2 6 0t6 0M-12 4.8q3-2 6 0t6 0M-26 4.6q3-2 6 0t6 0", .55)
    return a


def dragon(wings=True, heads=1, flame=False, horns=True, spiny=True, crest=2):
    a = Art()
    ctrl = [(-29, 9), (-22, 11), (-15, 6), (-9, 2), (-2, 0), (5, -1), (9.5, -4), (13, -10), (15.5, -15)]
    sp = catmull(ctrl, 9)
    # far legs behind the body
    limb(a, [(-6, 3), (-5.4, 8), (-3, 11.5), (-4.4, 14)], 2.2, 1.0, FILL2)
    limb(a, [(8, 3), (9.5, 8), (12.5, 10.6), (11.6, 13.6)], 2.0, 1.0, FILL2)
    if wings:
        tips = [(-6, -23), (6, -27), (19, -21)]
        sh = (3, -3.5)
        mem = [sh, (-1.5, -9), tips[0], (-3, -15), (0, -17.6), tips[1], (6, -17), (10.5, -19.5), tips[2], (14.5, -13), (11.5, -5.5)]
        a.shape(catmull(mem, 4)[:-1], FILL2, 1.0)
        for tp, bend in zip(tips, (-3, 2, 3)):
            rib = catmull([sh, ((sh[0] + tp[0]) / 2 + bend, (sh[1] + tp[1]) / 2), tp], 6)
            a.shape(ribbon(rib, prof([(0, 1.6), (1, .2)])), FILL, .6)
        a.line("M%.1f %.1fL%.1f %.1f" % (tips[0][0] + 1, tips[0][1] + 4, tips[0][0] - 1.5, tips[0][1] + .5), .5)
    wd = prof([(0, .3), (.12, 2.2), (.35, 5.4), (.55, 6.4), (.7, 4.6), (.85, 3.0), (1, 2.6)])
    body = ribbon(sp, wd)
    a.shape(body, FILL, 1.1)
    if spiny:
        spikes(a, sp, 3, 2.2, -1, .12, .93)
    # belly plates & scale hatching
    nrm = normals(sp)
    for i in range(int(len(sp) * .3), int(len(sp) * .83), 2):
        x, y = sp[i]
        nx, ny, tx, ty = nrm[i]
        w = wd(i / (len(sp) - 1)) / 2
        a.line([(x + nx * w * .55, y + ny * w * .55), (x + nx * w * .95 + tx * .3, y + ny * w * .95 + ty * .3)], .5)
    for (cx, cy) in [(-9, -1.5), (-4, -2.2), (1, -2.2), (-12.5, 1.6)]:
        a.line("M%.1f %.1fq1.2 -1.2 2.4 0M%.1f %.1fq1.2 -1.2 2.4 0" % (cx - 1.2, cy, cx - .1, cy + 1.5), .45)
    # near legs
    limb(a, [(-9, 3.4), (-9.4, 8.2), (-7, 12), (-8.6, 14.6)], 2.6, 1.1)
    limb(a, [(5.5, 3.2), (7.2, 8.2), (10.2, 10.8), (9.4, 13.8)], 2.4, 1.1)
    # necks / heads
    hs = [(16.2, -15.7, -32, 1.1)]
    if heads == 3:
        n2 = catmull([(8, -3), (13, -5), (19.5, -7.5), (23, -10)], 7)
        a.shape(ribbon(n2, prof([(0, 2.8), (1, 2)])), FILL, .9)
        n3 = catmull([(8, -3), (10.5, -9), (11.4, -16), (10.2, -21)], 7)
        a.shape(ribbon(n3, prof([(0, 2.8), (1, 2)])), FILL, .9)
        hs += [(23.0, -10.6, -10, .95), (9.4, -21.5, -78, .95)]
    for (hx, hy, ha, hs_) in hs:
        head(a, hx, hy, ha, hs_, 1.5 if flame else 1.2, horns=horns, crest=crest)
    if flame:
        hx, hy = xf([(10.5, 2.5)], 16.2, -15.7, -32, 1.1)[0]
        for k, L in enumerate((7, 9.5, 6.4)):
            ang = math.radians(-32 + (k - 1) * 13)
            a.line([(hx, hy), (hx + math.cos(ang) * L, hy + math.sin(ang) * L), (hx + math.cos(ang + .3) * L * .65, hy + math.sin(ang + .3) * L * .65)], .5)
    return a


def great_bird(crown=False, lion=False, tail=3, crest=3):
    a = Art()

    def wing(rx, ry, a0, a1, L, n, fill, k=1.0, lift=0):
        for i in range(n):
            ang = math.radians(a0 + (a1 - a0) * i / (n - 1))
            ln = L * (0.62 + 0.38 * math.sin(math.pi * (i / (n - 1)) * .9 + .2)) * k
            tip = (rx + math.cos(ang) * ln, ry + math.sin(ang) * ln + lift)
            mid = ((rx + tip[0]) / 2 + math.sin(ang) * ln * .12, (ry + tip[1]) / 2 - math.cos(ang) * ln * .12)
            sp = catmull([(rx, ry), mid, tip], 6)
            a.shape(ribbon(sp, prof([(0, 1.4), (.55, 3.0 * k), (1, .25)])), fill, .75)
            a.line([sp[1], sp[-2]], .35)
    wing(-2, -2, -170, -75, 24, 8, FILL2, .8, -2)       # far wing
    # tail plumes
    for i in range(tail):
        e = i - (tail - 1) / 2
        ctrl = [(-5, 4), (-13, 6 + e * 2), (-22, 7 + e * 5), (-31 - abs(e) * 1.5, 7 + e * 9)]
        sp = catmull(ctrl, 8)
        a.shape(ribbon(sp, prof([(0, 1.8), (.5, 1.5), (1, 1.1)])), FILL, .8)
        ex, ey = sp[-1]
        a.shape(catmull([(ex - 2.2, ey), (ex, ey - 1.6), (ex + 1.8, ey), (ex, ey + 1.6)], 5, True), FILL2, .6)
        a.dot(ex, ey, .55)
    body = catmull([(7, -4), (3, -3.5), (-3, -.5), (-7, 4)], 8)
    a.shape(ribbon(body, prof([(0, 2.6), (.3, 6), (.65, 5), (1, 1.2)])), FILL, 1.0)
    for k in range(4):
        a.line("M%.1f %.1fq1.1 -1.1 2.2 0" % (-3 + k * 2.2 - 1.1, -1 + k * .8), .45)
    wing(-1, -3.6, -150, -42, 27, 9, FILL, 1.0)          # near wing
    # legs
    for dx in (-1.2, 1.6):
        a.line([(dx, 3), (dx - 1.6, 7.4), (dx - 3.2, 9.6)], .8)
        for k in (-1, 0, 1):
            a.line([(dx - 3.2, 9.6), (dx - 5 + k * 1.2, 10.4 + abs(k) * .4)], .5)
    # neck + head
    nk = catmull([(5, -4.4), (8, -6.2), (10, -9.4)], 6)
    a.shape(ribbon(nk, prof([(0, 4), (1, 2.6)])), FILL, 1.0)
    if lion:
        for k in range(14):
            ang = math.radians(-100 + k * 25)
            a.line([(11 + math.cos(ang) * 3.2, -11.4 + math.sin(ang) * 3.2), (11 + math.cos(ang) * 5.6, -11.4 + math.sin(ang) * 5.6)], .5)
        a.shape(catmull([(8.6, -11.4), (9.4, -14), (12.6, -14.6), (14.4, -12.6), (14.2, -10.4), (12, -9.4), (9.4, -9.8)], 5, True), FILL, .9)
        a.shape([(9.4, -14), (9, -16.2), (11, -14.6)], FILL, .6)
        a.shape([(12.8, -14.4), (13.8, -16.4), (14.4, -13.6)], FILL, .6)
        a.dot(11.6, -12.6, .5)
        a.line([(14.4, -11.6), (15.6, -11.2)], .6)
        a.line("M12.6 -10.6q1 1 2 0", .5)
    else:
        a.shape(catmull([(8.6, -11.6), (9.6, -13.6), (12, -14), (13.6, -12.8), (13.2, -10.6), (10.6, -9.8)], 5, True), FILL, .9)
        a.shape([(13.2, -12.8), (17.4, -11.8), (14.6, -10.2), (13.6, -10.4)], GOLD, .5)
        a.dot(11.6, -12.4, .55)
        for k in range(crest):
            sp = catmull([(9.6, -13.4), (8 - k * 1.5, -17 - k * .6), (5.4 - k * 2.3, -18.4 - k * .4)], 5)
            a.shape(ribbon(sp, prof([(0, .9), (1, .2)])), FILL2, .5)
    if crown:
        a.shape([(9.2, -14.8), (9.6, -17.8), (10.8, -15.6), (12, -18.4), (13, -15.2), (14, -17.6), (14.4, -14.6)], GOLD, .5)
    return a


def wolf(howl=False):
    a = Art()
    limb(a, [(-10, 1.5), (-9.4, 6.5), (-10.6, 12)], 3.2, 1.2, FILL2, False)
    limb(a, [(6, 2), (7.6, 7), (6.4, 12)], 2.8, 1.2, FILL2, False)
    sp = catmull([(-14, -1), (-8, -2.4), (0, -3), (8, -2.4), (11.5, -1.5)], 8)
    wd = prof([(0, 3.4), (.3, 5.2), (.7, 5.6), (1, 4.4)])
    a.shape(ribbon(sp, wd), FILL, 1.1)
    # tail
    tl = catmull([(-13, -2), (-19, -2.4), (-23.4, -6), (-22.6, -11.4)], 7)
    a.shape(ribbon(tl, prof([(0, 1.6), (.5, 3.4), (1, .3)])), FILL, .9)
    limb(a, [(-6, 2.6), (-5, 7.6), (-6.4, 12.6)], 3.2, 1.3, FILL, False)
    limb(a, [(9, 2.4), (11.4, 7.2), (10.6, 12)], 3.0, 1.3, FILL, False)
    for (px, py) in [(-10.6, 12), (-6.4, 12.6), (6.4, 12), (10.6, 12)]:
        a.shape(catmull([(px - 1.6, py), (px + .4, py - 1), (px + 2.4, py + .2), (px + .6, py + 1)], 3, True), FILL, .6)
    # neck + head
    nk = catmull([(9, -1.6), (13, -4.6), (15.8, -8.2)], 6)
    a.shape(ribbon(nk, prof([(0, 5.2), (1, 3.8)])), FILL, 1.0)
    skull = [(0, -3.2), (3, -4), (7, -3), (10.2, -1), (10.5, .1), (7, -.2), (3.5, .9), (0, 1.8)]
    jaw = [(1, 1.8), (4, 1.4), (8.6, 2.2), (9.6, 3.4), (5.6, 3.8), (1.6, 3.2)]
    hx, hy, ha = 15, -9.2, 22
    a.shape(xf(jaw, hx, hy, ha), FILL, .9)
    a.shape(xf(skull, hx, hy, ha), FILL, 1.0)
    a.shape(xf([(.2, -3.2), (1.2, -7.2), (3.4, -3.6)], hx, hy, ha), FILL2, .7)
    a.shape(xf([(-1.2, -2.6), (-1.0, -6.4), (1.2, -3.2)], hx, hy, ha), FILL2, .7)
    a.shape(xf([(8.2, -.2), (8.6, 1.8), (9.4, -.1)], hx, hy, ha), GOLD, .4)
    a.shape(xf([(5.8, .2), (6.2, 1.8), (6.9, .1)], hx, hy, ha), GOLD, .4)
    ex, ey = xf([(3.6, -1.6)], hx, hy, ha)[0]
    a.dot(ex, ey, .6)
    nx_, ny_ = xf([(10.2, -.6)], hx, hy, ha)[0]
    a.dot(nx_, ny_, .75)
    a.line(xf([(2.2, -2.6), (4.6, -2.2)], hx, hy, ha), .6)
    for x in range(-12, 9, 3):
        a.line([(x, -6.2 + (x + 12) * .02), (x - 1.8, -4.6)], .55)
    for k in range(4):
        a.line([(10.6 + k * .5, -2.6 + k * 1.2), (9.4 + k * .5, -1.4 + k * 1.4)], .5)
    return a


def minotaur():
    a = Art()
    # labrys behind the shoulder
    a.line([(11.5, 14), (7.4, -15)], 1.2)
    a.shape([(7.4, -15), (2.2, -18.2), (3.8, -13), (7.4, -12.2)], FILL2, .8)
    a.shape([(7.4, -15), (12.6, -18.2), (11, -13), (7.4, -12.2)], FILL2, .8)
    a.shape([(-15, 13), (-12, 4.6), (-5.6, 1.2), (5.6, 1.2), (12, 4.6), (15, 13)], FILL, 1.1)
    a.line("M-9 6q4 5 9 3q5 2 9-3", .6)
    a.line("M0 3.6V9.4M-4.6 10.4q4.6 2.2 9.2 0", .55)
    a.shape([(-3.6, 1.6), (-3, -4.2), (3, -4.2), (3.6, 1.6)], FILL, .9)
    # bull head
    a.shape([(-4.4, -6), (-3.4, -10.6), (0, -11.8), (3.4, -10.6), (4.4, -6), (3.4, -2.6), (2.8, -.4), (-2.8, -.4), (-3.4, -2.6)], FILL, 1.1)
    for fx in (-1, 1):
        sp = catmull([(fx * 3.6, -9.4), (fx * 8.4, -10.4), (fx * 11.4, -14.6), (fx * 10.6, -19.4)], 7)
        a.shape(ribbon(sp, prof([(0, 2.6), (.6, 1.6), (1, .25)])), FILL2, .9)
        a.shape([(fx * 4.2, -8.6), (fx * 8.2, -9), (fx * 5.4, -6.2)], FILL2, .6)
        a.dot(fx * 1.9, -7.4, .6)
        a.line([(fx * .8, -8.4), (fx * 3.2, -8.8)], .7)
        a.dot(fx * 1.2, -2, .35)
    a.line("M0 -10.6V-8.6", .5)
    a.shape(catmull([(-1, -.6), (-1.2, 1.6), (0, 2.4), (1.2, 1.6), (1, -.6)], 4), FILL, .7)
    return a


def humbaba():
    a = Art()
    n = 13
    for k in range(n):
        ang = 2 * math.pi * k / n - math.pi / 2
        cx, cy = math.cos(ang) * 11.4, math.sin(ang) * 11.4
        a.shape(catmull([(cx - 2.4, cy), (cx, cy - 2.4), (cx + 2.4, cy), (cx, cy + 2.4)], 4, True), FILL, .75)
        a.line([(cx - 1.4, cy), (cx + 1.4, cy)], .4)
    a.shape(catmull([(0, -8.8), (7.8, -4), (7.8, 4), (0, 9.4), (-7.8, 4), (-7.8, -4)], 6, True), FILL, 1.1)
    for fx in (-1, 1):
        a.shape(catmull([(fx * 1.2, -2.6), (fx * 3.4, -3.6), (fx * 5.6, -2.8), (fx * 3.6, -1.6)], 4, True), GOLD, .5)
        a.line([(fx * 1.2, -4.6), (fx * 6, -5.4)], .8)
    a.line("M0 -2.4V1.8M-1.4 2.2q1.4 1 2.8 0", .7)
    a.line("M-3.6 4.6q3.6 3 7.2 0", .8)
    for x in (-2.4, -.8, .8, 2.4):
        a.line([(x, 5.4), (x, 6.6)], .5)
    for k in range(5):
        a.line("M%.1f %.1fq1.2 1.8 0 3.2" % (-3.2 + k * 1.6, 8), .5)
    return a


def div():
    a = Art()
    a.shape([(-13, 14), (-11, 5), (-6, 2.4), (6, 2.4), (11, 5), (13, 14)], FILL, 1.1)
    for fx in (-1, 1):
        a.shape([(fx * 8.6, 4.4), (fx * 14, -.6), (fx * 11.6, 5.4)], FILL2, .7)
        a.shape([(fx * 6.6, 3.2), (fx * 10.6, -3.4), (fx * 9, 3.6)], FILL2, .6)
    a.shape([(-3.4, 2.8), (-3, -3.2), (3, -3.2), (3.4, 2.8)], FILL, .9)
    for k, h in enumerate((5.4, 8.4, 6.6, 9.4, 6.6, 8.4, 5.4)):
        x = -6.6 + k * 2.2
        a.shape([(x - 1.2, -10.6 + abs(k - 3) * .5), (x, -10.6 - h), (x + 1.2, -10.6 + abs(k - 3) * .5)], FILL2, .55)
    for fx in (-1, 1):
        cx, cy = fx * 7.2, -9.6
        sp = [(cx + fx * (8.2 * (1 - t / 30.0) + .2) * math.cos(t / 3.4), cy + (7.6 * (1 - t / 30.0) + .2) * math.sin(t / 3.4) * -1) for t in range(31)]
        a.shape(ribbon(sp, prof([(0, 3.2), (1, .3)])), FILL2, .9)
    a.shape(catmull([(0, -12.6), (6.2, -9.8), (6, -2.8), (3.2, .4), (0, 1), (-3.2, .4), (-6, -2.8), (-6.2, -9.8)], 5, True), FILL, 1.1)
    for fx in (-1, 1):
        a.shape(catmull([(fx * 1.2, -7.4), (fx * 3, -8.4), (fx * 4.6, -7.4), (fx * 3, -6.4)], 3, True), GOLD, .4)
        a.line([(fx * 1, -9.4), (fx * 5, -8.4)], .8)
        a.shape([(fx * 2.4, -.2), (fx * 3.2, -4.4), (fx * 4, -.2)], GOLD, .4)
    a.line("M-2.8 -3q2.8 1.4 5.6 0M0 -6.4V-4", .6)
    return a


def cobra(a, bx, by, h, lean, hood=8.5):
    """A rearing cobra seen from the side: S-curved neck, hood swelling below the head, forked tongue."""
    ctrl = [(bx, by), (bx + lean * .3, by - h * .3), (bx - lean * .2, by - h * .62), (bx + lean * .5, by - h * .88), (bx + lean * .9, by - h)]
    sp = catmull(ctrl, 9)
    wd = prof([(0, 4.6), (.45, 3.2), (.62, 3.0), (.72, hood), (.84, hood * .8), (.92, 3.4), (1, 2.6)])
    a.shape(ribbon(sp, wd), FILL, .95)
    nrm = normals(sp)
    n = len(sp)
    for i in range(int(n * .68), int(n * .9), 2):
        x, y = sp[i]
        nx, ny, tx, ty = nrm[i]
        w = wd(i / (n - 1)) / 2 * .8
        a.line([(x - nx * w, y - ny * w), (x + nx * w, y + ny * w)], .4)
    x, y = sp[-1]
    px, py = sp[-3]
    ang = math.degrees(math.atan2(y - py, x - px)) + 28
    a.shape(xf([(0, -1.6), (4.2, .2), (0, 1.9)], x, y, ang), FILL, .8)
    ex, ey = xf([(1.4, -.4)], x, y, ang)[0]
    a.dot(ex, ey, .45)
    a.line(xf([(4.2, .2), (6.6, .2), (7.6, -.6), (6.6, .2), (7.6, 1.0)], x, y, ang), .4)


def naga():
    a = Art()
    coil = catmull([(-16, 12), (-9, 7.5), (-2, 12), (5, 7), (11, 11.5), (16, 8)], 8)
    a.shape(ribbon(coil, prof([(0, .4), (.3, 5.6), (.8, 5.6), (1, 3.8)])), FILL, 1.0)
    hatch_across(a, coil, 5.4, 2, .15, .9)
    cobra(a, -7, 8, 26, -5, 7.4)
    cobra(a, 7, 8, 28, 6, 7.6)
    cobra(a, 0, 9, 36, 1.5, 9.4)
    return a


def scylla():
    a = Art()
    a.shape([(-14, 14), (-11, 7), (-5, 3), (4, 4), (10, 8), (14, 14)], FILL2, 1.0)
    a.line("M-9 12l3-3M-3 13l3-4M4 13l2-4M-11 9l2-2", .5)
    body = catmull([(0, 6), (0, -2), (-.4, -7)], 6)
    a.shape(ribbon(body, prof([(0, 8), (1, 4.6)])), FILL, 1.0)
    for k, (ex, ey, ang) in enumerate([(-13, -14, -150), (-6, -19, -115), (6, -19, -65), (13, -14, -30)]):
        sp = catmull([(0, -2), (ex * .35, -2 + (ey + 2) * .35 + (4 if k % 2 else -3)), (ex * .8, ey * .9), (ex, ey)], 6)
        a.shape(ribbon(sp, prof([(0, 3.2), (1, 2.0)])), FILL, .9)
        wolf_head(a, ex, ey, ang)
    return a


def wolf_head(a, x, y, ang):
    skull = [(0, -2.6), (2.6, -3.4), (6, -2.6), (8.6, -.8), (8.8, .1), (6, -.1), (3, .8), (0, 1.5)]
    jaw = [(.8, 1.5), (3.4, 1.2), (7.2, 2.4), (7.8, 3.4), (4.6, 3.6), (1.4, 2.9)]
    a.shape(xf(jaw, x, y, ang), FILL, .8)
    a.shape(xf(skull, x, y, ang), FILL, .9)
    a.shape(xf([(.2, -2.6), (1.0, -5.8), (2.8, -3)], x, y, ang), FILL2, .6)
    ex, ey = xf([(3.0, -1.4)], x, y, ang)[0]
    a.dot(ex, ey, .5)
    a.shape(xf([(6.6, 0), (7.0, 1.6), (7.7, 0)], x, y, ang), GOLD, .4)


def makara():
    a = Art()
    body = catmull([(-26, 6), (-18, 0), (-9, -4), (0, -2), (7, 3), (11, 9)], 9)
    a.shape(ribbon(body, prof([(0, 1.2), (.25, 5), (.6, 8.4), (.85, 6.6), (1, 4.6)])), FILL, 1.1)
    for i in range(6, len(body) - 8, 3):
        x, y = body[i]
        a.line("M%.1f %.1fq1.4 -1.4 2.8 0M%.1f %.1fq1.4 -1.4 2.8 0" % (x - 1.4, y - 1, x - .2, y + 1.6), .45)
    spikes(a, body, 3, 2.2, -1, .2, .85)
    # fish tail
    a.shape([(-26, 6), (-33, -2), (-31, 4), (-35, 9), (-29, 8), (-26.4, 11)], FILL2, .9)
    # head: crocodile jaws with curled elephant trunk
    a.shape(catmull([(9, 5), (12, 1), (19, -1), (24, 2), (25, 5), (19, 6.6), (13, 9)], 5, True), FILL, 1.0)
    trunk = catmull([(23.4, 2), (28, 0), (29.6, -5), (26.4, -7.4), (24.2, -5.8)], 7)
    a.shape(ribbon(trunk, prof([(0, 3.4), (1, 1.2)])), FILL, .9)
    a.shape([(18, 6.2), (19, 9.4), (20.4, 6.6)], GOLD, .4)
    a.shape([(14.4, 7.6), (15.4, 10.2), (16.6, 7.6)], GOLD, .4)
    a.shape(catmull([(10, 1.4), (11.6, -1.8), (14.2, -1.2), (13, 1)], 4, True), FILL2, .7)
    a.dot(15.6, 1.4, .6)
    a.line([(12.6, -3), (14.4, -6), (15.6, -3.2)], .6)
    return a


def ship(kind="longship"):
    a = Art()
    if kind == "longship":
        hull = catmull([(-19, -4), (-15, 4), (-6, 6.4), (7, 6.4), (15, 4), (20, -3)], 6)
        a.shape(ribbon(hull, prof([(0, 1.6), (.5, 3.2), (1, 1.6)])), FILL, 1.0)
        a.shape(catmull([(-19, -4), (-20.6, -9), (-18, -12.4), (-16.4, -10.4), (-17.6, -9.2)], 4), FILL, .9)       # stern
        a.shape(catmull([(20, -3), (22.4, -8.4), (22, -12.8), (24.6, -14), (23.2, -11), (24.4, -9.6), (22.4, -8)], 4, False), FILL, .9)  # dragon prow
        a.dot(23.6, -12.8, .4)
        a.line([(0, 4), (0, -24)], 1.1)
        sail = [(-9, -22), (9, -22), (10, -6), (-10, -6)]
        a.shape(sail, FILL2, .9)
        for k in range(-3, 4):
            a.line([(k * 2.8, -22), (k * 2.8 + (1 if k > 0 else -1 if k < 0 else 0) * .3, -6)], .6)
        a.line([(-14, -2.6), (14, -2.6)], .5)
        for k in range(-5, 6):
            a.shape(catmull([(k * 2.6 - 1, 1.2), (k * 2.6, -.8), (k * 2.6 + 1, 1.2), (k * 2.6, 2.6)], 3, True), GOLD, .3)
        a.line([(-10, -6), (-19, -4)], .5)
        a.line([(10, -6), (20, -3)], .5)
    elif kind == "dhow":
        hull = catmull([(-18, -2), (-13, 5), (-2, 6.8), (10, 5), (17, 0)], 6)
        a.shape(ribbon(hull, prof([(0, 1.6), (.5, 3.4), (1, 1.6)])), FILL, 1.0)
        a.shape([(-18, -2), (-20, -6), (-14, -4)], FILL, .8)
        a.shape([(17, 0), (24, -3), (19, 1.8)], FILL, .8)
        a.line([(-4, 4), (-2, -20)], 1.0)
        a.shape(catmull([(-3, -20), (9, -8), (15, -2), (-3, -3.6)], 6, True), FILL2, 1.0)
        a.line("M-3 -17Q5 -10 12 -4M-3 -13Q3 -9 8 -4.6", .5)
        a.line([(-13, -6), (-4, -19)], .5)
    elif kind == "trireme":
        hull = catmull([(-20, -3), (-15, 3), (-4, 5), (8, 5), (17, 2), (22, -4)], 6)
        a.shape(ribbon(hull, prof([(0, 1.8), (.5, 3), (1, 1.8)])), FILL, 1.0)
        a.shape([(22, -4), (27, -2.4), (23, 1.2), (20.6, 0)], GOLD, .5)
        a.shape(catmull([(-20, -3), (-22, -8), (-20, -11), (-17.6, -9)], 4), FILL, .8)
        a.line([(1, 3), (1, -17)], 1.0)
        a.shape([(-6, -16), (8, -16), (9, -6), (-7, -6)], FILL2, .8)
        a.line("M-6.5 -11H8.5M-5 -16V-6M1 -16V-6M7 -16V-6", .45)
        for k in range(-5, 6):
            a.line([(k * 3, 2.2), (k * 3 - 3, 9)], .6)
        a.dot(16.4, -.6, .8)
    else:   # reed boat (marsh arabs)
        hull = catmull([(-17, -3), (-10, 3), (0, 4.4), (10, 3), (18, -5)], 6)
        a.shape(ribbon(hull, prof([(0, 1.4), (.5, 3), (1, 1.4)])), FILL, 1.0)
        a.shape([(-17, -3), (-20, -9), (-15.6, -6)], FILL2, .8)
        a.shape([(18, -5), (22, -11), (16.4, -7)], FILL2, .8)
        a.line("M-8 1.4l-1-3M-3 2.4l-.6-3.4M3 2.4l.6-3.4M8 1.4l1-3", .5)
        a.line([(4, -2), (14, -14)], .9)
    return a


# ------------------------------------------------------------------ registry
CREATURES = {
    "serpent": lambda **k: sea_serpent(**k),
    "dragon": lambda **k: dragon(**k),
    "dragon3": lambda **k: dragon(heads=3, wings=False, **k),
    "wyrm": lambda **k: dragon(wings=False, **k),
    "bird": lambda **k: great_bird(**k),
    "garuda": lambda **k: great_bird(crown=True, tail=2, **k),
    "anzu": lambda **k: great_bird(lion=True, tail=2, crest=0, **k),
    "wolf": lambda **k: wolf(**k),
    "minotaur": lambda **k: minotaur(**k),
    "guardian": lambda **k: humbaba(**k),
    "demon": lambda **k: div(**k),
    "naga": lambda **k: naga(**k),
    "scylla": lambda **k: scylla(**k),
    "makara": lambda **k: makara(**k),
    "longship": lambda **k: ship("longship"),
    "dhow": lambda **k: ship("dhow"),
    "trireme": lambda **k: ship("trireme"),
    "reedboat": lambda **k: ship("reed"),
}


def creature(kind, x, y, s, flip=False, **opts):
    return CREATURES[kind](**opts).render(x, y, s, -1 if flip else 1)


# ------------------------------------------------------------------ terrain glyphs
def peak(x, y, s, lean=0.0):
    """Hand-inked mountain: lit left face, shaded right face with hatching, small snow notch."""
    ax, ay = x + lean * s, y - 2.1 * s
    lx, rx = x - 1.05 * s, x + 1.1 * s
    body = "M%.1f %.1fL%.1f %.1fL%.1f %.1fZ" % (lx, y, ax, ay, rx, y)
    # shaded face: from the ridge line down to the right base, with a jagged ridge
    mx = ax + .12 * s
    shade = "M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ" % (
        ax, ay, mx + .3 * s, ay + .7 * s, mx + .05 * s, ay + 1.15 * s, mx + .4 * s, y - .5 * s, mx + .2 * s, y, rx, y)
    hatch = "".join("M%.1f %.1fL%.1f %.1f" % (mx + (.3 + k * .22) * s, y - (1.15 - k * .25) * s, mx + (.5 + k * .22) * s, y - .1 * s) for k in range(3))
    snow = "M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1f" % (ax - .42 * s, ay + .75 * s, ax - .12 * s, ay + .5 * s, ax + .1 * s, ay + .82 * s, ax + .22 * s, ay + .6 * s)
    return body, shade, hatch + snow


def tree(x, y, s, kind):
    if kind == "pine":
        return ("M%.1f %.1fL%.1f %.1fL%.1f %.1fZM%.1f %.1fL%.1f %.1fL%.1f %.1fZ" % (
            x - .55 * s, y - .5 * s, x, y - 1.35 * s, x + .55 * s, y - .5 * s,
            x - .75 * s, y, x, y - .95 * s, x + .75 * s, y)), "M%.1f %.1fv%.1f" % (x, y, .35 * s)
    return ("M%.1f %.1fa%.1f %.1f 0 1 1 %.1f 0a%.1f %.1f 0 1 1 %.1f 0Z" % (x - .6 * s, y - .7 * s, .6 * s, .6 * s, 1.2 * s, .6 * s, .6 * s, -1.2 * s)), "M%.1f %.1fv%.1f" % (x, y - .1 * s, .7 * s)


def hill(x, y, s):
    return "M%.1f %.1fQ%.1f %.1f %.1f %.1f" % (x - s, y, x, y - 1.35 * s, x + s, y), "M%.1f %.1fl%.1f %.1fM%.1f %.1fl%.1f %.1f" % (x + .15 * s, y - .85 * s, .35 * s, .55 * s, x + .4 * s, y - .6 * s, .3 * s, .45 * s)


def marsh(x, y, s):
    return "M%.1f %.1fh%.1fM%.1f %.1fv%.1fM%.1f %.1fv%.1fM%.1f %.1fv%.1f" % (x - s, y, 2 * s, x, y, -1.5 * s, x - .55 * s, y, -s, x + .55 * s, y, -s)
