"""Engraving-style art for the map generator: monsters, ships and terrain symbols.

Everything is plain SVG paths built from a few helpers (Catmull-Rom splines and
tapered "ribbons"), so creatures stay crisp at any size and weigh a few KB each.
Style: dark inked fill, thin gold outline, a darker halo so they read on both
land and sea.  Local units: a creature spans roughly 40-50 units.
"""
import math

GOLD = "#dcc07a"
INK = "#05080b"
FILL = "#16230f"
FILL2 = "#22331a"
SAIL = "#d9cba0"


def f1(v):
    s = "%.1f" % v
    return s[:-2] if s.endswith(".0") else s


def d_poly(pts, close=True):
    return "M" + "L".join("%s %s" % (f1(x), f1(y)) for x, y in pts) + ("Z" if close else "")


def cr(pts, n=10):
    """Catmull-Rom through pts (open curve) -> dense polyline."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[-2])
    return out


def prof(pairs):
    """Piecewise-linear width profile: [(t, w), ...] -> f(t)."""
    def f(t):
        if t <= pairs[0][0]:
            return pairs[0][1]
        for (t0, w0), (t1, w1) in zip(pairs, pairs[1:]):
            if t <= t1:
                return w0 + (w1 - w0) * (t - t0) / ((t1 - t0) or 1)
        return pairs[-1][1]
    return f


def ribbon(spine, wf):
    n = len(spine)
    L, R = [], []
    for i, (x, y) in enumerate(spine):
        a = spine[max(i - 1, 0)]
        b = spine[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        m = math.hypot(dx, dy) or 1
        nx, ny = -dy / m, dx / m
        w = wf(i / (n - 1)) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L + R[::-1]


def rot(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


class Art:
    def __init__(self):
        self.it = []

    def fill(self, pts, fill=FILL, sw=1.0):
        self.it.append(("f", d_poly(pts), fill, sw))

    def fd(self, d, fill=FILL, sw=1.0):
        self.it.append(("f", d, fill, sw))

    def line(self, pts, sw=1.0, close=False):
        self.it.append(("l", d_poly(pts, close) if not isinstance(pts, str) else pts, None, sw))

    def dot(self, x, y, r=.5):
        self.it.append(("d", (x, y), None, r))

    def ribbon(self, spine, wf, fill=FILL, sw=1.0):
        self.fill(ribbon(spine, wf), fill, sw)

    def merge(self, other, x=0, y=0, ang=0, s=1.0, flip=False):
        """Copy another art in, transforming its points (paths are re-parsed cheaply via a transform group)."""
        self.it.append(("g", other, (x, y, ang, s, flip), 0))

    def _emit(self, halos, mains):
        for kind, a, fill, sw in self.it:
            if kind == "g":
                x, y, ang, s, flip = fill
                hh, mm = [], []
                a._emit(hh, mm)
                tf = 'transform="translate(%s %s) rotate(%s) scale(%s %s)"' % (f1(x), f1(y), f1(math.degrees(ang)), f1(-s if flip else s), f1(s))
                halos.append("<g %s>%s</g>" % (tf, "".join(hh)))
                mains.append("<g %s>%s</g>" % (tf, "".join(mm)))
            elif kind == "f":
                halos.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (a, INK, INK, f1(sw + 2.6)))
                mains.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s"/>' % (a, fill, GOLD, f1(sw)))
            elif kind == "l":
                halos.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (a, INK, f1(sw + 2.4)))
                mains.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (a, GOLD, f1(sw)))
            else:
                halos.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f1(a[0]), f1(a[1]), f1(sw + 1.1), INK))
                mains.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f1(a[0]), f1(a[1]), f1(sw), GOLD))

    def svg(self, x, y, s=1.0, flip=False, ang=0, op=.92):
        halos, mains = [], []
        self._emit(halos, mains)
        tf = "translate(%s %s)" % (f1(x), f1(y))
        if ang:
            tf += " rotate(%s)" % f1(ang)
        tf += " scale(%s %s)" % (f1(-s if flip else s), f1(s))
        return '<g transform="%s" opacity="%s" stroke-linejoin="round" stroke-linecap="round">%s%s</g>' % (tf, op, "".join(halos), "".join(mains))


def xf(pts, x, y, ang, s):
    return [(x + s * rot(p, ang)[0], y + s * rot(p, ang)[1]) for p in pts]


# ------------------------------------------------------------------ heads
def head(a, x, y, ang=0.0, s=1.0, o=.8, horns=True, tongue=True, crest=True, kind="drake"):
    """Reptile head facing +x, drawn into art `a` at (x, y), rotated by ang."""
    P = lambda pts: xf(pts, x, y, ang, s)
    if horns:
        for sp, w in (([(1, -2.8), (-2, -5.2), (-6, -6), (-9, -4.4)], .9), ([(.6, -2.4), (-2.4, -3.6), (-5.6, -3.4)], .6)):
            a.ribbon(P(cr(sp, 6)), prof([(0, 1.5 * w), (1, .12)]), FILL2, .8)
    if crest:
        a.fill(P([(-.6, -2.2), (-2.4, -3.2), (-1.4, -1.2), (-3.2, -1.4), (-1.6, .4), (-.4, .2)]), FILL2, .7)
    # lower jaw rotated open about the hinge
    jaw = [(0.8, .9), (4.2, .2), (8.4, -.1), (9.5, .6), (8.3, 1.6), (4, 2.3), (1, 2.5)]
    ca = math.radians(18 * o)
    jaw = [(.8 + (px - .8) * math.cos(ca) - (py - 1.2) * math.sin(ca), 1.2 + (px - .8) * math.sin(ca) + (py - 1.2) * math.cos(ca)) for px, py in jaw]
    a.fill(P(jaw), FILL2, .9)
    upper = [(-.6, -.8), (0, -2.6), (2.6, -3.5), (6, -3.1), (9.3, -1.7), (10.4, -.5), (7.2, -.1), (4.4, .6), (.9, 1.0)]
    a.fill(P(upper), FILL, 1.0)
    # teeth
    for tx in (4.2, 6.2, 8.2):
        a.line(P([(tx, -.1), (tx + .5, 1.2 + o * .3)]), .6)
    a.line(P([(5.4, 1.2), (5.9, -.4)]), .5)
    a.dot(*P([(3.1, -1.8)])[0], .5)                         # eye
    a.line(P([(1.8, -2.7), (4.6, -2.2)]), .6)                # brow
    a.dot(*P([(9.0, -1.1)])[0], .3)                          # nostril
    if tongue:
        tx, ty = 9.2, .9 + o * 1.2
        a.line(P([(tx, ty), (tx + 3.2, ty + .2), (tx + 5.2, ty - .8)]), .6)
        a.line(P([(tx + 3.2, ty + .2), (tx + 5.0, ty + 1.0)]), .6)


# ------------------------------------------------------------------ monsters
def sea_serpent():
    a = Art()
    # waves at the waterline
    for wx in (-30, -8, 12):
        a.line(cr([(wx, 1.2), (wx + 3, -.6), (wx + 6, 1.2), (wx + 9, -.6), (wx + 12, 1.2)], 4), .6)
    humps = [(-27, -15, 5.2), (-12, 1, 8.4), (4, 17, 6.2)]
    for x0, x1, h in humps:
        sp = [(x0 + (x1 - x0) * t / 20, -h * math.sin(math.pi * t / 20)) for t in range(21)]
        a.ribbon(sp, lambda t: 1.0 + 3.4 * math.sin(math.pi * t) ** .45, FILL, 1.0)
        # scale chevrons along the back
        for t in range(3, 18, 3):
            px, py = sp[t]
            a.line([(px - .9, py + 1.1), (px, py + .1), (px + .9, py + 1.1)], .45)
        # dorsal fin on the crest
        cx, cy = sp[10]
        a.fill([(cx - 1.6, cy - 1.7), (cx - .2, cy - 4.4), (cx + 1.2, cy - 1.7)], FILL2, .7)
    # neck and head
    neck = cr([(17, -1.4), (20.5, -4.5), (22.5, -10), (20.5, -15.5), (22.2, -19.5)], 8)
    a.ribbon(neck, prof([(0, 3.6), (.6, 3.0), (1, 2.6)]), FILL, 1.0)
    for i in range(2, len(neck) - 2, 4):
        a.line([(neck[i][0] - 1.1, neck[i][1] + .2), (neck[i][0] + 1.1, neck[i][1] - .2)], .45)
    for i in range(3, len(neck) - 3, 5):          # dorsal spikes
        px, py = neck[i]
        a.fill([(px - 1.5, py - .6), (px - 3.2, py - 2.0), (px - 1.2, py + .6)], FILL2, .6)
    head(a, 22.2, -19.5, math.radians(-22), 1.35, .9)
    # tail fluke
    a.fill([(-27, -.2), (-31, -3.4), (-29.5, -.2), (-31.6, 2.4)], FILL2, .8)
    return a


def dragon(wings=True, heads=1, flame=False, spikes=True):
    a = Art()
    hind_far = cr([(-8, 3), (-11, 7), (-8.5, 11.5), (-10.5, 13.5)], 6)
    fore_far = cr([(6.5, 3), (9, 7), (12, 10), (11.6, 13.4)], 6)
    a.ribbon(hind_far, prof([(0, 3), (.5, 1.8), (1, 1.2)]), FILL2, .8)
    a.ribbon(fore_far, prof([(0, 2.6), (.5, 1.7), (1, 1.1)]), FILL2, .8)
    for fx, fy in ((-10.5, 13.5), (11.6, 13.4)):
        a.line([(fx - 1.6, fy + 1.2), (fx, fy - .2), (fx + 1.8, fy + 1.0)], .7)
    if wings:
        sh = (2.5, -3.8)
        tips = [(-21, -22), (-5, -33), (12, -28)]
        for tp, k in zip(tips, (-6, -2, 4)):
            pass
        mem = [sh, (-4, -9), (tips[0][0], tips[0][1])]
        mem += cr([tips[0], (-14, -19), (-9, -17), (tips[1][0] - 3, -25), tips[1]], 4)[1:]
        mem += cr([tips[1], (3, -24), (6, -20), (9.6, -23), tips[2]], 4)[1:]
        mem += cr([tips[2], (14, -17), (12, -9), (10.5, -5)], 4)[1:]
        a.fill(mem, "#121c0e", 1.0)
        for tp in tips:
            a.line(cr([sh, ((sh[0] + tp[0]) / 2 - 1, (sh[1] + tp[1]) / 2 + 1.5), tp], 6), .8)
        a.line(cr([(0, -6), (-4, -14), (-3, -18)], 5), .5)
        a.line(cr([(4, -6), (6, -16), (5, -22)], 5), .5)
    spine = cr([(-29, 9), (-23, 11), (-16, 7.5), (-10, 2.8), (-3, .6), (4, -.4), (9, -3.4), (12.4, -8.6), (15.5, -13.4)], 8)
    wf = prof([(0, .3), (.18, 1.4), (.4, 4.6), (.58, 6.2), (.72, 5.0), (.86, 3.0), (1, 2.5)])
    body = ribbon(spine, wf)
    a.fill(body, FILL, 1.1)
    # belly scutes
    for i in range(int(len(spine) * .34), int(len(spine) * .8), 2):
        px, py = spine[i]
        a.line([(px - .6, py + 1.8), (px + .5, py + 3.4)], .45)
    if spikes:
        for i in range(8, len(spine) - 6, 4):
            px, py = spine[i]
            a.fill([(px - 1.3, py - 1.9), (px - .6, py - 4.0), (px + .5, py - 2.1)], FILL2, .6)
    # near legs
    hind = cr([(-9.5, 1.6), (-12.5, 6.5), (-9.8, 11.2), (-12, 13.6)], 6)
    fore = cr([(5.4, 1.8), (7.8, 6.8), (10.6, 10.4), (9.8, 13.8)], 6)
    a.ribbon(hind, prof([(0, 4), (.5, 2.2), (1, 1.3)]), FILL, .9)
    a.ribbon(fore, prof([(0, 3.4), (.5, 2.0), (1, 1.3)]), FILL, .9)
    for fx, fy in ((-12, 13.6), (9.8, 13.8)):
        a.line([(fx - 1.8, fy + 1.4), (fx, fy - .2), (fx + 2.0, fy + 1.1)], .75)
        a.line([(fx - .2, fy + 1.9), (fx, fy - .1)], .5)
    # tail barb
    a.fill([(-29, 9), (-32.5, 6.4), (-31.2, 9.4), (-33, 12)], FILL2, .8)
    # necks and heads
    ends = [(15.5, -13.4, -34, 1.1)]
    if heads == 3:
        ends = [(12, -23, -72, .9), (22.5, -16, -34, .9), (28, -5, 2, .85)]
    for i, (hx, hy, ang, hs) in enumerate(ends):
        if i:
            nk = cr([(9, -3.4), ((9 + hx) / 2 + 2, (-3.4 + hy) / 2 + 1), (hx, hy)], 6)
            a.ribbon(nk, prof([(0, 3.2), (1, 2.2)]), FILL, .9)
        head(a, hx, hy, math.radians(ang), hs, .85, True, True, True)
    if flame:
        hx, hy = 15.5, -13.4
        fl = cr([(hx + 10, hy - 5), (hx + 15, hy - 7), (hx + 18, hy - 5), (hx + 22, hy - 7.5)], 5)
        a.line(fl, .7)
        a.line(cr([(hx + 10, hy - 3), (hx + 14.5, hy - 3.4), (hx + 19, hy - 2)], 5), .6)
    return a


def great_bird(kind="simurgh"):
    a = Art()
    # far wing (smaller, behind)
    for i in range(7):
        ang = math.radians(-100 - i * 9)
        ln = 16 + (3 - abs(i - 3)) * 1.6
        sp = cr([(-1, -2), (-1 + ln * .5 * math.cos(ang) - 1, -2 + ln * .5 * math.sin(ang)), (-1 + ln * math.cos(ang), -2 + ln * math.sin(ang))], 5)
        a.ribbon(sp, prof([(0, 1.6), (.7, 1.9), (1, .2)]), FILL2, .7)
    # tail plumes
    for k, (dy, ln) in enumerate(((0, 26), (4, 30), (8, 23))):
        sp = cr([(-6, 4), (-13, 5 + dy * .4), (-21, 6 + dy * .9), (-ln, 4 + dy * 1.5)], 6)
        a.ribbon(sp, prof([(0, 1.3), (.5, 1.5), (1, .5)]), FILL, .8)
        ex, ey = sp[-1]
        a.fill([(ex - 1.6, ey - 2.2), (ex - 4.2, ey), (ex - 1.6, ey + 2.2), (ex + .8, ey)], FILL2, .6)
        a.dot(ex - 1.6, ey, .55)
    # body and neck
    body = cr([(-8, 4.5), (-2, 2.5), (5, .4), (9, -3.6)], 8)
    a.ribbon(body, prof([(0, .6), (.4, 5.8), (.8, 4.6), (1, 2.6)]), FILL, 1.0)
    # near wing: two rows of feathers
    for i in range(8):
        ang = math.radians(-168 + i * 11)
        ln = 22 + (4 - abs(i - 3.5)) * 1.7
        sp = cr([(1, -2), (1 + ln * .5 * math.cos(ang) + 1.2, -2 + ln * .5 * math.sin(ang)), (1 + ln * math.cos(ang), -2 + ln * math.sin(ang))], 5)
        a.ribbon(sp, prof([(0, 2.1), (.65, 2.6), (1, .25)]), FILL, .8)
    for i in range(7):
        ang = math.radians(-160 + i * 11)
        ln = 11 + (3.5 - abs(i - 3)) * 1.2
        sp = cr([(1, -1), (1 + ln * math.cos(ang), -1 + ln * math.sin(ang))], 3)
        a.ribbon(sp, prof([(0, 2.2), (1, .5)]), FILL2, .6)
    # head
    if kind == "anzu":
        a.fill(xf([(0, -3.6), (2.4, -4.4), (4.6, -3), (5.4, -.6), (3.8, 1.8), (1, 2.4), (-1.4, 1.2), (-2, -1.6)], 10, -6.4, 0, 1.0), FILL, 1.0)
        for k in range(10):
            ang = math.radians(k * 36)
            a.line([(10 + 4.6 * math.cos(ang), -6.4 + 4.6 * math.sin(ang)), (10 + 7.4 * math.cos(ang), -6.4 + 7.4 * math.sin(ang))], .5)
        a.dot(11.4, -7.2, .5)
        a.line([(11, -4.6), (13.6, -4.4)], .6)
    else:
        a.fill([(7.4, -6.4), (9.4, -8.6), (12, -8.2), (13.6, -6.6), (16.2, -5.6), (13.4, -5.0), (12.8, -3.8), (10, -3.4), (8, -4.2)], FILL, 1.0)
        a.dot(11, -7, .5)
        for i, (cx, cy) in enumerate(((8.6, -8.6), (9.6, -9.2), (10.8, -8.8))):    # crest
            a.line(cr([(cx, cy), (cx - 1.4, cy - 3.2), (cx - 4.4 - i, cy - 3.6)], 4), .6)
        if kind == "garuda":
            a.fill([(8.4, -9.4), (9.2, -12), (10.4, -10.2), (11.6, -12.2), (12.2, -9.2)], "#2a2410", .7)
    # legs and talons
    for lx in (-1, 3):
        a.line([(lx, 6.4), (lx - 3.5, 10.2), (lx - 5.6, 11.4)], .8)
        a.line([(lx - 5.6, 11.4), (lx - 7.2, 12.6), (lx - 4.6, 12.8), (lx - 3.4, 12.2)], .6)
    return a


def wolf():
    a = Art()
    for sp in ([(-9, 2), (-10, 7), (-8.4, 11), (-9.2, 12.6)], [(5.4, 2.4), (6.6, 7), (9, 10), (8.4, 12.4)]):
        a.ribbon(cr(sp, 5), prof([(0, 2.8), (.5, 1.6), (1, 1.0)]), FILL2, .8)
    spine = cr([(-14, 0), (-9, -1.6), (-2, -2.4), (5, -2), (9.4, -2.4)], 8)
    a.ribbon(spine, prof([(0, 3.2), (.2, 5.4), (.6, 5.8), (1, 4.2)]), FILL, 1.1)
    for i in range(3, len(spine) - 4, 3):                        # hackles along the back
        px, py = spine[i]
        a.line([(px - .8, py - 2.6), (px - 1.4, py - 4.4)], .6)
        a.line([(px + .4, py - 2.8), (px - .1, py - 4.8)], .6)
    neck = cr([(7.5, -2.8), (11.5, -5), (14.5, -6.6)], 5)
    a.ribbon(neck, prof([(0, 4.4), (1, 3.2)]), FILL, 1.0)
    a.fill(xf([(-.6, -2.4), (2.6, -3.4), (6, -2.4), (9, -1.2), (9.4, .2), (6.6, .6), (3, 1.4), (-.5, 1.6)], 14, -7.4, math.radians(6), 1.0), FILL, 1.0)
    a.fill(xf([(-.4, 1.2), (4, 1.0), (8, 1.6), (7, 2.8), (3.4, 3.1), (0, 2.6)], 14, -7.4, math.radians(6 + 12), 1.0), FILL2, .9)
    for ex in (2.4, 4.4):
        a.line(xf([(ex, 0.2), (ex + .3, 1.6)], 14, -7.4, math.radians(6), 1.0), .5)
    a.fill([(13.2, -10.4), (12.6, -14.2), (15.6, -11.0)], FILL2, .8)
    a.fill([(15.2, -10.0), (16.2, -13.6), (17.6, -9.2)], FILL2, .8)
    a.dot(18.0, -9.4, .5)
    a.line([(19.4, -7.6), (23, -6.6)], .5)
    for sp in ([(-10.6, 2.4), (-12.2, 7.6), (-9.8, 11.6), (-12, 13.2)], [(5.6, 2.8), (7.2, 7.4), (10.4, 10.2), (9.6, 12.8)]):
        a.ribbon(cr(sp, 5), prof([(0, 3.4), (.5, 1.8), (1, 1.1)]), FILL, .9)
        a.line([(sp[-1][0] - 1.6, sp[-1][1] + .4), (sp[-1][0] + 1.4, sp[-1][1] + .4)], .6)
    tail = cr([(-14, 0), (-19, -2), (-24, -7.5), (-27, -10)], 6)
    a.ribbon(tail, prof([(0, 1.0), (.5, 3.0), (1, .3)]), FILL, .9)
    for i in range(4):                                           # fur on tail and chest
        a.line([(-18 - i * 2.2, -2 - i * 1.7), (-19.6 - i * 2.2, -1 - i * 1.5)], .5)
    for i in range(3):
        a.line([(8.4 - i * .8, 2.6 + i * 1.2), (7.8 - i * .8, 4 + i * 1.2)], .5)
    return a


def minotaur():
    a = Art()
    # labrys behind the shoulder
    a.line([(-14, 12), (12, -14)], 1.1)
    a.fd("M9 -17C14 -18 18 -14 17 -10C13 -12 10 -12 9 -17Z", FILL2, .8)
    a.fd("M16 -9C19 -4 17 .5 13 1.5C13 -2 14 -5 16 -9Z", FILL2, .8)
    # shoulders / torso
    a.fd("M-16 16C-16 7 -9 2 0 2C9 2 16 7 16 16Z", FILL, 1.1)
    a.line(cr([(-6, 8), (-3, 11), (0, 9), (3, 11), (6, 8)], 4), .6)
    a.line([(0, 9), (0, 16)], .6)
    a.fill([(-4, 3), (-3.4, -1.4), (3.4, -1.4), (4, 3)], FILL, 1.0)          # neck
    # horns
    a.fill(cr([(-4.4, -9), (-9, -9.6), (-13, -13), (-14, -18), (-12, -16.4), (-9.6, -13.4), (-5.6, -11.6)], 4), FILL2, .9)
    a.fill(cr([(4.4, -9), (9, -9.6), (13, -13), (14, -18), (12, -16.4), (9.6, -13.4), (5.6, -11.6)], 4), FILL2, .9)
    # ears
    a.fill([(-5.2, -7.2), (-9.6, -6.4), (-6, -4.6)], FILL2, .8)
    a.fill([(5.2, -7.2), (9.6, -6.4), (6, -4.6)], FILL2, .8)
    # head
    a.fd("M-5.4 -10C-5.2 -12.4 5.2 -12.4 5.4 -10C5.8 -6 4.6 -2.4 3.6 -.4C2.6 1.8 -2.6 1.8 -3.6 -.4C-4.6 -2.4 -5.8 -6 -5.4 -10Z", FILL, 1.1)
    a.fd("M-3.4 -1.8C-3.4 .8 -1.6 2.4 0 2.4C1.6 2.4 3.4 .8 3.4 -1.8C2 -.8 -2 -.8 -3.4 -1.8Z", FILL2, .8)
    a.dot(-1.4, .7, .38); a.dot(1.4, .7, .38)
    a.line([(-4.4, -7.2), (-1.4, -6.2)], .7); a.line([(4.4, -7.2), (1.4, -6.2)], .7)
    a.dot(-2.4, -5.2, .55); a.dot(2.4, -5.2, .55)
    a.line(cr([(0, 2.4), (0, 4.4), (-1.4, 5.6), (0, 6.6), (1.4, 5.6), (0, 4.4)], 3), .6)      # nose ring
    return a


def humbaba():
    a = Art()
    n = 11
    for k in range(n):                                    # ring of entrail coils
        ang = 2 * math.pi * k / n
        cx, cy = 11.4 * math.cos(ang), 11.4 * math.sin(ang)
        a.fd("M%s %sa3 3 0 1 1 -.1 0Z" % (f1(cx - 3), f1(cy)), FILL2, .8)
        a.line(cr([(cx - 1.4, cy), (cx, cy - 1.4), (cx + 1.4, cy), (cx, cy + 1.2)], 3), .45)
    a.fd("M0 -8.4C5 -8.4 8.4 -4.8 8.4 0C8.4 5.6 4.6 9 0 9C-4.6 9 -8.4 5.6 -8.4 0C-8.4 -4.8 -5 -8.4 0 -8.4Z", FILL, 1.1)
    a.line([(-6, -3.6), (-1.6, -2.4)], .9); a.line([(6, -3.6), (1.6, -2.4)], .9)
    a.fd("M-4.4 -1.2C-3.6 -2.5 -1.6 -2.5 -1 -1.2C-1.6 -.2 -3.6 -.2 -4.4 -1.2ZM4.4 -1.2C3.6 -2.5 1.6 -2.5 1 -1.2C1.6 -.2 3.6 -.2 4.4 -1.2Z", GOLD, .5)
    a.line([(0, -2), (0, 2.6)], .8)
    a.line(cr([(-4.2, 4.6), (-2.2, 6), (0, 4.8), (2.2, 6), (4.2, 4.6)], 3), .9)
    a.line([(-2.4, 5.2), (-2.2, 6.6)], .6); a.line([(2.4, 5.2), (2.2, 6.6)], .6)
    for k in range(-3, 4):
        a.line([(k * 1.2, -8.2), (k * 1.4, -5.6)], .45)
    return a


def div():
    a = Art()
    a.fd("M-17 17C-16 8 -9 4 0 4C9 4 16 8 17 17Z", FILL, 1.1)
    for sx in (-1, 1):                                  # shoulder spikes
        a.fill([(sx * 13, 9), (sx * 18, 3), (sx * 15.4, 11.4)], FILL2, .8)
        a.fill([(sx * 9, 6.6), (sx * 12.4, 1), (sx * 11.6, 8)], FILL2, .8)
    for k, (hx, hy) in enumerate(((-6, -8), (-3, -10.4), (0, -11.4), (3, -10.4), (6, -8))):    # flame hair
        a.fill([(hx - 1.5, hy + 2), (hx - 1.6 + k * .3, hy - 5.4 - (2 - abs(k - 2)) * 1.4), (hx + 1.5, hy + 2)], FILL2, .7)
    # ram horns spiralling out
    for sx in (-1, 1):
        sp = cr([(sx * 5, -7), (sx * 10, -8.4), (sx * 14, -4.6), (sx * 12.4, -.2), (sx * 9, -1.4), (sx * 9.6, -4.4)], 5)
        a.ribbon(sp, prof([(0, 3), (.7, 1.8), (1, .3)]), FILL2, .9)
    a.fd("M0 -9.4C4.4 -9.4 7 -6.4 7 -2.4C7 2 4 5.4 0 5.4C-4 5.4 -7 2 -7 -2.4C-7 -6.4 -4.4 -9.4 0 -9.4Z", FILL, 1.1)
    a.fill([(-6.6, -4.6), (-1.4, -2.4), (-1.4, -3.6), (-6.2, -6.2)], GOLD, .4)
    a.fill([(6.6, -4.6), (1.4, -2.4), (1.4, -3.6), (6.2, -6.2)], GOLD, .4)
    a.dot(-3.1, -3.6, .55); a.dot(3.1, -3.6, .55)
    a.line([(0, -3), (0, .4)], .7)
    a.line(cr([(-4, 2.4), (-2, 3.4), (0, 2.6), (2, 3.4), (4, 2.4)], 3), .8)
    a.fill([(-3.2, 2.8), (-3.8, 6.8), (-1.8, 3.4)], SAIL, .5); a.fill([(3.2, 2.8), (3.8, 6.8), (1.8, 3.4)], SAIL, .5)
    return a


def naga():
    a = Art()
    coil = cr([(-14, 14), (-8, 10), (2, 12), (9, 9), (15, 12.6), (9, 16), (-2, 16), (-10, 18)], 6)
    a.ribbon(coil, prof([(0, 1.4), (.5, 4.6), (1, 1.2)]), FILL, 1.0)
    for i in range(2, len(coil) - 2, 4):
        a.line([(coil[i][0] - .4, coil[i][1] - 1.6), (coil[i][0] + .4, coil[i][1] + 1.6)], .45)
    neck = cr([(-2, 12), (-4, 6), (0, 0), (-1, -6)], 7)
    a.ribbon(neck, prof([(0, 5), (.6, 3.6), (1, 3)]), FILL, 1.0)
    # seven hoods in a fan
    for k in range(7):
        ang = math.radians(-90 + (k - 3) * 25)
        cx, cy = -1 + 12.5 * math.cos(ang), -7 + 12.5 * math.sin(ang)
        base = -1 + 4 * math.cos(ang), -7 + 4 * math.sin(ang)
        a.ribbon(cr([base, ((base[0] + cx) / 2, (base[1] + cy) / 2), (cx, cy)], 3), prof([(0, 2.6), (1, 1.6)]), FILL, .7)
        sc = 1.15 - .08 * abs(k - 3)
        a.fd("M%s %sc-%s -%s %s -%s %s 0c0 %s -%s %s -%s %s Z" % (f1(cx - 3.6 * sc), f1(cy - 1.4 * sc), f1(.2 * sc), f1(3 * sc), f1(7.2 * sc), f1(3 * sc), f1(7.2 * sc), f1(4 * sc), f1(1.8 * sc), f1(5.4 * sc), f1(3.6 * sc), f1(5.4 * sc)), FILL2, .6)
        a.fd("M%s %sa%s %s 0 1 0 %s 0Z" % (f1(cx - 1.6 * sc), f1(cy - 4.6 * sc), f1(1.6 * sc), f1(1.5 * sc), f1(3.2 * sc)), FILL, .7)
        a.dot(cx, cy - 4.6 * sc, .35)
    a.fd("M-4.8 -6.6C-3 -4.6 -1.2 -4.6 -.4 -6.6C-1.4 -7.8 -4 -7.8 -4.8 -6.6Z", FILL2, .6)
    return a


def scylla():
    a = Art()
    a.fd("M-15 15C-11 6 -4 5 0 5C4 5 11 6 15 15Z", FILL, 1.1)
    for k in range(3):
        a.line(cr([(-12 + k * 12, 13), (-10 + k * 12, 10), (-8.4 + k * 12, 13)], 3), .5)
    cfg = ((-10, 6, -19, -8), (-4, 5, -9, -19), (4, 5, 9, -19), (10, 6, 19, -8))
    for bx, by, ex, ey in cfg:
        sp = cr([(bx, by), (bx + (ex - bx) * .2, by - 9), (ex, ey)], 6)
        a.ribbon(sp, prof([(0, 4), (.6, 2.6), (1, 2.3)]), FILL, .9)
        ang = math.atan2(sp[-1][1] - sp[-3][1], sp[-1][0] - sp[-3][0])
        head(a, ex, ey, ang, .8, .9, False, False, False)
    return a


def makara():
    a = Art()
    body = cr([(-26, 6), (-20, 1), (-12, 2), (-4, 4), (4, 2), (11, -2), (15, -6)], 7)
    a.ribbon(body, prof([(0, .5), (.2, 3.2), (.55, 6.4), (.85, 4.6), (1, 3.4)]), FILL, 1.1)
    for i in range(3, len(body) - 4, 3):
        px, py = body[i]
        a.line([(px - 1.2, py + 1), (px, py - .2), (px + 1.2, py + 1)], .45)
        a.line([(px - 1.2, py + 2.8), (px, py + 1.6), (px + 1.2, py + 2.8)], .45)
    # crocodile snout with curled trunk
    a.fill([(14, -9), (18, -10.4), (23, -9), (26, -6.6), (22, -5), (17, -4.4), (13.4, -4.8)], FILL, 1.0)
    a.line(cr([(25, -7), (29, -6), (30.4, -2), (27.8, -.6), (26.6, -2.6)], 4), 1.0)
    a.fill([(17.4, -4.4), (21.4, -4.6), (22.8, -3), (19, -2.4)], FILL2, .8)
    a.line([(18, -4.4), (18.6, -3)], .5); a.line([(20, -4.6), (20.6, -3.2)], .5)
    a.dot(17.6, -8.2, .55)
    a.fill([(14.6, -10.4), (13.4, -14.4), (16.4, -11.2)], FILL2, .7)
    a.fill([(-26, 6), (-33, 1), (-30, 6), (-33, 12)], FILL2, .9)                # fish tail
    a.line(cr([(-26, 6), (-30, 3), (-31.6, 1.6)], 3), .5); a.line(cr([(-26, 6), (-30, 9), (-31.6, 10.4)], 3), .5)
    a.fill([(-6, 2.6), (-8, -3), (-1.4, 1.4)], FILL2, .8)                       # dorsal fin
    a.fill([(2, 8.2), (-1, 13), (5, 9.6)], FILL2, .8)                           # pectoral
    for wx in (-22, 0, 20):
        a.line(cr([(wx, 12), (wx + 3, 10.6), (wx + 6, 12), (wx + 9, 10.6), (wx + 12, 12)], 4), .5)
    return a


# ------------------------------------------------------------------ ships
def longship():
    a = Art()
    for wx in (-26, -4, 16):
        a.line(cr([(wx, 9), (wx + 3, 7.6), (wx + 6, 9), (wx + 9, 7.6), (wx + 12, 9)], 4), .5)
    hull = [(-22, -2), (-16, 3.6), (0, 5.8), (14, 3.8), (21, -3)]
    outer = cr([(-23, -9), (-24, -3), (-20, 3), (-10, 6), (4, 6.4), (16, 4.4), (22, -1), (23.4, -9.6)], 6)
    a.fill(outer + [(20, -3), (6, 0), (-10, -.4), (-20, -3)][::-1][:0] + cr([(22, -3), (8, -1.4), (-8, -1.6), (-21, -3.6)], 4), FILL, 1.1)
    a.line(cr([(-22, -1.4), (-8, 3.2), (8, 3.4), (21, -.6)], 6), .6)
    for k in range(9):                                      # shields along the gunwale
        sx = -16 + k * 4.2
        a.fd("M%s -1.8a1.6 1.6 0 1 0 .1 0Z" % f1(sx - 1.6), FILL2, .6)
    for k in range(9):
        sx = -16 + k * 4.2
        a.line([(sx, 2.4), (sx - 3, 8)], .45)               # oars
    a.line([(-23, -9), (-26, -14), (-23, -17), (-20.6, -15.4)], 1.1)           # stern curl
    # dragon prow
    a.fd("M23.4 -9.6C25 -13 26 -17 30 -18.4L29 -16.4L32 -16.4L29.4 -14.4C27.4 -13.6 26.6 -11.6 26 -9.4Z", FILL, 1.0)
    a.dot(28.4, -16.6, .4)
    a.line([(0, -1), (0, -26)], 1.1)                                          # mast
    a.fill([(-11, -25), (11, -25), (13, -8), (-13, -8)], SAIL, .9)
    for sx in (-8.6, -4.3, 0, 4.3, 8.6):
        a.fill([(sx - 2.1, -24.4), (sx + 2.1, -24.4), (sx + 2.3, -8.6), (sx - 2.3, -8.6)], "#7a2a22" if int((sx + 9) / 4.3) % 2 == 0 else SAIL, .0)
    a.line([(-11, -25), (11, -25), (13, -8), (-13, -8)], .9, True)
    a.line([(0, -26), (-23, -9)], .5); a.line([(0, -26), (23, -9)], .5)        # stays
    return a


def dhow():
    a = Art()
    for wx in (-26, -4, 16):
        a.line(cr([(wx, 9), (wx + 3, 7.6), (wx + 6, 9), (wx + 9, 7.6), (wx + 12, 9)], 4), .5)
    a.fill(cr([(-22, -4), (-19, 3), (-6, 6), (8, 5.4), (18, 2), (26, -6), (20, -1.6), (4, 0), (-12, -.4), (-20, -2.4)], 5), FILL, 1.1)
    a.fill([(-22, -4), (-24, -8), (-18, -8), (-17, -3)], FILL2, .8)            # high stern
    a.line([(-5, -1), (-5, -10)], .7)
    # lateen sail on a slanting yard
    a.line([(-14, -3), (-1, -24), (20, -4)], 1.0)
    a.fill(cr([(-14, -3), (-1, -24), (6, -14), (20, -4)], 4)[:] + [(-14, -3)][:0], SAIL, .9)
    a.line([(-1, -24), (-1, -3)], .45); a.line([(6, -14), (2, -3)], .4); a.line([(-7, -13), (-8, -3)], .4)
    a.line([(-23, -8), (-17, -9)], .6)
    a.dot(18, 0, .4)
    return a


def trireme():
    a = Art()
    for wx in (-28, -6, 14):
        a.line(cr([(wx, 10), (wx + 3, 8.6), (wx + 6, 10), (wx + 9, 8.6), (wx + 12, 10)], 4), .5)
    a.fill(cr([(-24, -6), (-22, 2), (-8, 5.4), (10, 5), (22, 1.4), (27, -3.6), (22, -1.4), (6, 0), (-10, -.4), (-22, -2)], 5), FILL, 1.1)
    a.fill([(27, -3.6), (33, 0), (28, 1.8), (24, .8)], FILL2, .9)                   # bronze ram
    a.line(cr([(-24, -6), (-27, -12), (-25, -16)], 4), 1.0)                          # raised stern
    for k in range(10):
        ox = -16 + k * 3.8
        a.line([(ox, 2.2), (ox - 4.4, 10)], .5)
    a.dot(21, -.6, .8)                                                              # painted eye
    a.line([(1, -1), (1, -22)], 1.0)
    a.fill([(-8, -20), (10, -20), (11, -7), (-9, -7)], SAIL, .9)
    a.line([(1, -20), (1, -7)], .5)
    return a


CREATURES = {
    "serpent": sea_serpent, "sea-serpent": sea_serpent,
    "dragon": dragon, "wyrm": lambda: dragon(False),
    "mushussu": lambda: dragon(False, 1, False, True),
    "dahaka": lambda: dragon(False, 3),
    "bird": great_bird, "simurgh": lambda: great_bird("simurgh"), "garuda": lambda: great_bird("garuda"),
    "anzu": lambda: great_bird("anzu"),
    "wolf": wolf, "minotaur": minotaur, "guardian": humbaba, "humbaba": humbaba,
    "demon": div, "div": div, "naga": naga, "scylla": scylla, "makara": makara,
    "longship": longship, "dhow": dhow, "trireme": trireme,
}
_CACHE = {}


def creature(kind, x, y, s=1.0, flip=False, op=.92):
    if kind not in _CACHE:
        _CACHE[kind] = CREATURES[kind]()
    return _CACHE[kind].svg(x, y, s, flip, 0, op)


# ------------------------------------------------------------------ terrain symbols
PEAK, SHADE, LINE, HATCH = "#4f5f3d", "#16200e", "#d3c186", "#0c1208"
FOREST, FORLINE, SAND, MARSH = "#1d2e18", "#8fb064", "#9a8650", "#74a893"


def glyph_defs():
    """<defs> content: reusable symbols, anchored at their base centre, ~12 units wide."""
    g = []
    def sym(i, body):
        g.append('<g id="%s">%s</g>' % (i, body))
    pk = lambda d: '<path d="%s" fill="%s" stroke="%s" stroke-width=".7"/>' % (d, PEAK, LINE)
    sh = lambda d: '<path d="%s" fill="%s"/>' % (d, SHADE)
    ha = lambda d: '<path d="%s" fill="none" stroke="%s" stroke-width=".6"/>' % (d, HATCH)
    sn = lambda d: '<path d="%s" fill="none" stroke="%s" stroke-width=".6" opacity=".9"/>' % (d, LINE)
    sym("m1", pk("M-6 0L-2.6 -6.6L0 -10.6L3 -6.6L6 0Z") + sh("M0 -10.6L3 -6.6L6 0L1.4 0Z") + ha("M1.6 -6.4L3.6 -2.4M2.8 -8L5 -2.6M.8 -3.4L1.8 -.4") + sn("M-1.8 -8.2L0 -6.8L1.4 -8.4"))
    sym("m2", pk("M-9.5 0L-6.5 -5.4L-4.4 -7.6L-2 -3.8L0 -6.4L3.2 -11.8L6.6 -5.8L9.5 0Z") + sh("M3.2 -11.8L6.6 -5.8L9.5 0L3.6 0ZM-4.4 -7.6L-2 -3.8L-1.2 0L-4.2 0Z")
        + ha("M4.2 -7.6L6.4 -2.4M5.4 -8.6L8 -2.8M1.4 -5L2.4 -.6M-3.6 -5.4L-2.8 -1.2") + sn("M1.4 -8.6L3.2 -7L4.8 -8.8"))
    sym("m3", pk("M-12 0L-8.6 -6L-6.4 -8.6L-4 -4.6L-1.6 -9.4L1 -13L4 -8L6.6 -9.4L8.8 -5.2L12 0Z") + sh("M1 -13L4 -8L6.6 -9.4L8.8 -5.2L12 0L2.6 0ZM-6.4 -8.6L-4 -4.6L-3.4 0L-7 0Z")
        + ha("M2.4 -8.6L4.6 -2.6M4 -6.4L6 -1.6M7.2 -6L9.4 -1.8M-5.2 -5.4L-4.6 -1.2") + sn("M-.6 -10.4L1 -8.8L2.8 -10.6"))
    sym("m4", pk("M-9 0C-8 -4 -5 -7 -1 -7.6C3 -8 7 -5 9 0Z") + sh("M-1 -7.6C3 -8 7 -5 9 0L2 0C2 -3 1 -6 -1 -7.6Z") + ha("M2 -5.4L3.4 -1.6M4 -4.8L5.6 -1.4"))
    sym("hl", '<path d="M-6 0C-5 -3.6 -2.4 -5 0 -5C2.6 -5 5 -3.6 6 0" fill="%s" stroke="%s" stroke-width=".7"/><path d="M1 -4.9C3.6 -4.4 5.2 -2.6 6 0L2.6 0Z" fill="%s"/>' % (PEAK, LINE, SHADE))
    sym("tp", '<path d="M0 -12L-3 -7.6H3ZM0 -9L-3.8 -4H3.8ZM0 -6L-4.6 0H4.6Z" fill="%s" stroke="%s" stroke-width=".6" stroke-linejoin="round"/><path d="M0 0V1.6" stroke="%s" stroke-width=".8"/>' % (FOREST, FORLINE, FORLINE))
    sym("tr", '<circle cx="0" cy="-5.2" r="3.7" fill="%s" stroke="%s" stroke-width=".6"/><circle cx="-1.8" cy="-6.2" r="1.7" fill="none" stroke="%s" stroke-width=".4"/><path d="M0 -1.5V1.6" stroke="%s" stroke-width=".8"/>' % (FOREST, FORLINE, FORLINE, FORLINE))
    sym("dn", '<path d="M-5.4 0Q-2.6 -4 0 -.6Q2.8 -4 5.4 0" fill="none" stroke="%s" stroke-width=".7"/>' % SAND)
    sym("ms", '<path d="M-2.8 0V-4M0 0V-5.4M2.8 0V-3.6" stroke="%s" stroke-width=".7"/><path d="M-5.4 1.2Q-2.7 -.2 0 1.2T5.4 1.2" fill="none" stroke="%s" stroke-width=".6"/>' % (MARSH, MARSH))
    return "".join(g)
