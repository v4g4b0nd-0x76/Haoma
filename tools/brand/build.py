"""Regenerates the Haoma logo set. The identity is pure text, set in real scripts only:

  Old Persian cuneiform  U+103C3 U+103A2 U+103B6  (ha-u-ma = hauma-, first element of Haumavarga, DNa 25 / XPh 26)
  Old Persian word divider U+103D0
  Avestan                U+10B35 U+10B00 U+10B0A U+10B28 U+10B00  (h-a-o-m-a, written right to left)
  Latin                  HAOMA in Cinzel Bold (inscriptional capitals)
  Persian                هوم in Noto Nastaliq Urdu Bold

Every glyph is taken from a font and converted to outlines. Nothing is drawn by hand or imitated.

The wordmark is the name set above a strip of the ancient scripts (the Old Persian
ha-u-ma, the word divider, then the Avestan name), the whole centred. The Latin
wordmark sets that strip at em 30; the Persian one at em 34, a touch larger so the
strip reads at the same weight as the Latin one once both lockups are scaled to a
common height (the Persian name is narrower and taller than HAOMA).

Needs: pip install fonttools brotli uharfbuzz. PNG/JPG exports are made separately (see AI.md 8a).
The cover/share images (haoma-cover.svg, haoma-og.svg, haoma-og.png) are NOT regenerated here."""
import io, math, os, sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
F_OP = os.path.join(HERE, 'NotoSansOldPersian-Regular.woff')
F_AV = os.path.join(HERE, 'NotoSansAvestan-Regular.woff')
F_LA = os.path.join(HERE, 'Cinzel-Bold.woff')
F_FA = os.path.join(HERE, 'NotoNastaliqUrdu-Bold.woff2')

OP_HAUMA = '\U000103C3\U000103A2\U000103B6'       # ha, u, ma
OP_DIV = '\U000103D0'                             # word divider
AV_HAOMA = '\U00010B35\U00010B00\U00010B0A\U00010B28\U00010B00'  # he a o me a
LA_NAME = 'HAOMA'
FA_NAME = 'هوم'

GOLD = '<linearGradient id="@@hg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6cf7a"/><stop offset="1" stop-color="#d9972c"/></linearGradient>'
NIGHT = '#14161a'

# wordmark strip sizes (em). Persian is set a little larger so its strip reads at
# the same weight as the Latin one when both lockups are scaled to a common height.
STRIP_EM = {'en': 30, 'fa': 34}


# ---------------------------------------------------------------- glyph outlines
_cache = {}
def _font(path):
    if path not in _cache:
        f = TTFont(path); f.flavor = None
        bio = io.BytesIO(); f.save(bio); data = bio.getvalue()
        ft = TTFont(io.BytesIO(data))
        _cache[path] = (ft, ft.getGlyphSet(), ft.getGlyphOrder(), hb.Font(hb.Face(hb.Blob(data))), ft['head'].unitsPerEm)
    return _cache[path]

def shape(path, text, track=0):
    """Outline `text` with HarfBuzz. Returns dict(d, b=(x0,y0,x1,y1) ink bounds, upm), y axis down, baseline y=0.
    `track` (font units) adds letter-spacing; only for Latin capitals."""
    ft, gs, order, hbf, upm = _font(path)
    parts = [text] if not track else list(text)
    x = 0; d = ''; bb = None
    for ci, part in enumerate(parts):
        buf = hb.Buffer(); buf.add_str(part); buf.guess_segment_properties(); hb.shape(hbf, buf, {})
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = order[info.codepoint]
            m = (1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)
            pen = SVGPathPen(gs, ntos=lambda v: f'{v:.0f}'); gs[name].draw(TransformPen(pen, m)); d += pen.getCommands()
            bp = BoundsPen(gs); gs[name].draw(TransformPen(bp, m))
            if bp.bounds:
                b = bp.bounds
                bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
            x += pos.x_advance
        if track and ci < len(parts) - 1: x += track
    return dict(d=d, b=bb, upm=upm)

def size(g, em):
    s = em / g['upm']; b = g['b']
    return (b[2] - b[0]) * s, (b[3] - b[1]) * s

def carved(g, em, x, y, anchor='lt'):
    """Gold glyph run with a soft bevel: dark drop, light upper edge, gold fill.
    anchor 'lt' = x,y is the left-top ink corner; 'ct' = centre-top."""
    s = em / g['upm']; b = g['b']; w = (b[2] - b[0]) * s
    left = x - w / 2 if anchor == 'ct' else x
    tx = left - b[0] * s; ty = y - b[1] * s
    o = max(.7, em * .011)
    f = lambda dx, dy: f'transform="translate({tx+dx:.2f} {ty+dy:.2f}) scale({s:.5f})"'
    return (f'<path d="{g["d"]}" {f(o*1.1, o*1.4)} fill="#0b0a0c" opacity=".55"/>'
            f'<path d="{g["d"]}" {f(-o*.4, -o*.4)} fill="#fff4cf" opacity=".3"/>'
            f'<path d="{g["d"]}" {f(0, 0)} fill="url(#@@hg)"/>')

def flat(g, em, x, y, anchor='lt', fill='url(#@@hg)', opacity=1):
    s = em / g['upm']; b = g['b']; w = (b[2] - b[0]) * s
    left = x - w / 2 if anchor == 'ct' else x
    op = '' if opacity == 1 else ' opacity="%s"' % opacity
    return '<path d="%s" transform="translate(%.2f %.2f) scale(%.5f)" fill="%s"%s/>' % (g['d'], left - b[0] * s, y - b[1] * s, s, fill, op)

def taper(x0, x1, y, t=1.6):
    """Hairline that thins toward x1 (a tapering stroke, like the tail of a wedge)."""
    return f'<path d="M{x0:.1f} {y-t/2:.2f}L{x1:.1f} {y-0.2:.2f}L{x1:.1f} {y+0.2:.2f}L{x0:.1f} {y+t/2:.2f}Z" fill="url(#@@hg)" opacity=".8"/>'


# ---------------------------------------------------------------- the lockups
OP = shape(F_OP, OP_HAUMA)
DIV = shape(F_OP, OP_DIV)
AV = shape(F_AV, AV_HAOMA)
FA = shape(F_FA, FA_NAME)
def LA(track=.30): return shape(F_LA, LA_NAME, track=int(track * 1000))

def rule(cx, y, half, em=26, gap=10):
    """Hairline - Old Persian word divider - hairline, centred on cx."""
    dw, dh = size(DIV, em)
    return (taper(cx - gap - dw / 2, cx - half, y) + taper(cx + gap + dw / 2, cx + half, y)
            + carved(DIV, em, cx, y - dh / 2, 'ct'))

def fa_only(h):
    """Minimal Persian lockup: the name alone in Nastaliq."""
    em = h * FA['upm'] / (FA['b'][3] - FA['b'][1]); w = size(FA, em)[0]; pad = 3
    return flat(FA, em, pad, pad), w + 2 * pad, h + 2 * pad

def under(kind):
    """The wordmark: the name centred above a strip of the ancient scripts,
    the whole thing centred. Returns (svg body, width, height)."""
    name = LA() if kind == 'en' else FA
    name_em = 100 if kind == 'en' else 110 * FA['upm'] / (FA['b'][3] - FA['b'][1])
    pad = 10
    nw, nh = size(name, name_em)
    em = STRIP_EM[kind]
    em_div = em * .62
    ow, oh = size(OP, em); dw, dh = size(DIV, em_div); aw, ah = size(AV, em)
    gap = em * .55
    total = ow + gap + dw + gap + aw
    # The name and the strip are centred on one shared axis, and whichever is wider
    # sets the box width. (For Latin, HAOMA is wider than the strip; for Persian the
    # Nastaliq name is narrower, so the strip governs — both must still be centred.)
    W = max(nw, total) + 2 * pad
    cx = W / 2
    strip_top = pad + nh + name_em * .34
    x = cx - total / 2
    base_ty = strip_top - OP['b'][1] * (em / OP['upm'])          # shared baseline for the two word-runs
    def put(g, e, xx):
        s = e / g['upm']; return flat(g, e, xx, base_ty + g['b'][1] * s)
    body = flat(name, name_em, pad, pad)
    body += put(OP, em, x); x += ow + gap
    body += flat(DIV, em_div, x, strip_top + (oh - dh) / 2); x += dw + gap
    body += put(AV, em, x)
    H = strip_top + max(oh, ah) + pad
    return body, W, H

def stack(kind):
    """Stacked lockup for the 'full' lockup. kind: 'en' | 'fa' | 'both'."""
    if kind == 'fa': return fa_only(100)
    pad = 8; opw, oph = size(OP, 100); W = opw + 2 * pad; cx = W / 2
    out = carved(OP, 100, cx, pad, 'ct'); y = pad + oph + 20
    out += rule(cx, y, opw / 2 + 2); y += 20
    la = LA(); lw, lh = size(la, 40)
    out += flat(la, 40, cx, y, 'ct'); y += lh + 15
    aw, ah = size(AV, 40)
    out += flat(AV, 40, cx, y, 'ct', opacity=.92); y += ah + pad
    return out, W, y

def mark(frame=True):
    """Square emblem: the Avestan letter he (first letter of the name in the script of the Avesta) in a double ruled panel, like a carved inscription tablet."""
    out = ''
    if frame:
        out += ('<rect x="3" y="3" width="94" height="94" rx="3" fill="none" stroke="url(#@@hg)" stroke-width="1.6"/>'
                '<rect x="9" y="9" width="82" height="82" rx="1.5" fill="none" stroke="url(#@@hg)" stroke-width=".8" opacity=".75"/>')
    w, h = size(AV_HE, 100)
    em = 100 * (52 / w) if frame else 100 * (66 / w)
    w, h = size(AV_HE, em)
    out += carved(AV_HE, em, 50, 50 - h / 2, 'ct')
    return out
AV_HE = shape(F_AV, '\U00010B35')

def doc(vb, body, extra=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{extra}<defs>{GOLD}</defs>{body}</svg>'
def sub(s, i): return s.replace('@@hg', 'hg' + i)


def build():
    out = {}
    # ---- brand SVG files
    for name, kind in [('haoma-logo.svg', 'en'), ('haoma-logo-fa.svg', 'fa')]:
        body, W, H = under(kind); out[name] = sub(doc(f'0 0 {W:.0f} {H:.0f}', body), '')
    out['haoma-mark.svg'] = sub(doc('0 0 100 100', mark()), '')
    out['favicon.svg'] = sub(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs>{GOLD}</defs><rect width="64" height="64" rx="13" fill="{NIGHT}"/><g transform="scale(.64)">{mark(frame=False)}</g></svg>', 'f')

    # ---- Hugo inline partial (v = word | full | mark)
    def inl(b, vb, cls):
        return (f'<svg class="logo {cls}" viewBox="{vb}" role="img" aria-label="{{{{ site.Title }}}}"><defs>{GOLD}</defs>{b}</svg>').replace('@@hg', 'hg{{ $i }}')
    parts = {}
    for lang in ('en', 'fa'):
        b, W, H = under(lang); parts[('word', lang)] = inl(b, f'0 0 {W:.0f} {H:.0f}', 'logo-word')
        b, W, H = stack(lang); parts[('full', lang)] = inl(b, f'0 0 {W:.0f} {H:.0f}', 'logo-full')
    mk = inl(mark(), '0 0 100 100', 'logo-mark')
    part = ('{{- $i := .id | default "x" -}}\n{{- if eq .v "mark" -}}' + mk +
            '{{- else if eq .v "word" -}}{{- if eq site.Language.Lang "fa" -}}' + parts[('word', 'fa')] + '{{- else -}}' + parts[('word', 'en')] + '{{- end -}}' +
            '{{- else if eq site.Language.Lang "fa" -}}' + parts[('full', 'fa')] + '{{- else -}}' + parts[('full', 'en')] + '{{- end -}}\n')
    out['_partial_logo.html'] = part
    return out


if __name__ == '__main__':
    o = build()
    brand = os.path.join(ROOT, 'static', 'img', 'brand'); os.makedirs(brand, exist_ok=True)
    for k, v in o.items():
        path = os.path.join(ROOT, 'layouts', 'partials', 'logo.html') if k == '_partial_logo.html' else os.path.join(brand, k)
        open(path, 'w').write(v)
    print('wrote', len(o), 'files')
