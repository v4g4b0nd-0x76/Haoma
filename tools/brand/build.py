"""Regenerates the Haoma logo set: emblem, wedge lettering (EN), Nastaliq wordmark (FA), favicon, cover and share-image SVGs, and layouts/partials/logo.html.
Needs: pip install fonttools brotli uharfbuzz. PNG/JPG exports are made separately (see AI.md)."""
import math, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
sys.path.insert(0,HERE)
from fa_word import shaped_path
GOLD='<linearGradient id="@@hg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6cf7a"/><stop offset="1" stop-color="#d9972c"/></linearGradient>'
def P(cx,cy,r,a): return cx+r*math.cos(math.radians(a)), cy+r*math.sin(math.radians(a))
def pts(l): return ' '.join(f'{x:.1f} {y:.1f}' for x,y in l)
# ---------- emblem (100x100) ----------
def mark(ring=True, anim=True):
    c=lambda n: f' class="hm-{n}"' if anim else ''
    r=''
    if ring: r='<circle cx="50" cy="50" r="46.5" fill="none" stroke="url(#@@hg)" stroke-width="1.4"/><circle cx="50" cy="50" r="42" fill="none" stroke="url(#@@hg)" stroke-width="1.8" stroke-dasharray="0.1 3.15" stroke-linecap="round" opacity=".8"/>'
    return (r+'<g transform="translate(6 6) scale(.88)">'+
    '<path d="M26 65H74Q74 84 50 87Q26 84 26 65Z" fill="url(#@@hg)"/><path d="M41 87Q50 90 59 87L58 91H42Z" fill="url(#@@hg)"/><path d="M30 68H70" stroke="#14161a" stroke-width="1" opacity=".35"/>'
    '<g fill="none" stroke="#e8b455" stroke-width="3.2" stroke-linecap="round"><path d="M50 65V33"/><path d="M45 65Q40 51 32 38"/><path d="M55 65Q60 51 68 38"/></g>'
    '<g fill="none" stroke="#e8b455" stroke-width="1.8" stroke-linecap="round"><path d="M46.3 55H53.7M46.8 47H53.2M47.4 40H52.6"/></g>'
    '<g fill="url(#@@hg)"><path transform="translate(32 38) rotate(-34)" d="M0 0Q-3.4-7 0-15Q3.4-7 0 0Z"/><path transform="translate(68 38) rotate(34)" d="M0 0Q-3.4-7 0-15Q3.4-7 0 0Z"/>'
    '<path transform="translate(41.5 52) rotate(-62)" d="M0 0Q-2.2-4.5 0-9.5Q2.2-4.5 0 0Z"/><path transform="translate(58.5 52) rotate(62)" d="M0 0Q-2.2-4.5 0-9.5Q2.2-4.5 0 0Z"/>'
    '<path transform="translate(43.5 45) rotate(-48)" d="M0 0Q-1.8-3.6 0-7.6Q1.8-3.6 0 0Z"/><path transform="translate(56.5 45) rotate(48)" d="M0 0Q-1.8-3.6 0-7.6Q1.8-3.6 0 0Z"/></g>'
    f'<path{c("drop")} d="M50 8C58 18 59 25 50 32C41 25 42 18 50 8Z" fill="url(#@@hg)"/><path d="M50 14C54 20 54 24 50 28C46 24 46 20 50 14Z" fill="#fff4cf" opacity=".55"/>'
    f'<g fill="#f6cf7a"><circle{c("sp")} cx="41" cy="24" r="1"/><circle{c("sp2")} cx="59" cy="22" r="1"/></g></g>')
# ---------- cuneiform-inspired Latin lettering ----------
def wedge(h,t,w0=9,w1=1.3):
    dx,dy=t[0]-h[0],t[1]-h[1];L=math.hypot(dx,dy);nx,ny=-dy/L,dx/L
    return [(h[0]+nx*w0/2,h[1]+ny*w0/2),(h[0]-nx*w0/2,h[1]-ny*w0/2),(t[0]-nx*w1/2,t[1]-ny*w1/2),(t[0]+nx*w1/2,t[1]+ny*w1/2)]
def letter(ch,x0):
    W=[]; w=0
    if ch=='H': W=[wedge((7,0),(7,60)),wedge((37,0),(37,60)),wedge((7,31),(36,31),7)]; w=44
    if ch=='A': W=[wedge((22,0),(3,60)),wedge((22,0),(41,60)),wedge((11,41),(33,41),6)]; w=44
    if ch=='M': W=[wedge((6,0),(6,60)),wedge((50,0),(50,60)),wedge((6,3),(28,43),8),wedge((50,3),(28,43),8)]; w=56
    polys=[[(x+x0,y) for x,y in p] for p in W]
    return polys,w
def word_en(oring=True):
    out=[];x=0;widths={}
    seq='HAOMA'
    for i,ch in enumerate(seq):
        if ch=='O':
            # the O: sun ring holding the haoma drop
            cx=x+26
            out.append(('ring',cx)); x+=52+10; continue
        p,w=letter(ch,x);out+= [('poly',q) for q in p];x+=w+10
    return out,x-10
def en_svg(grp_id='@@hg'):
    items,W=word_en();s=''
    for k,v in items:
        if k=='poly':
            pt=pts(v);s+=f'<polygon points="{pt}" transform="translate(1.3 1.6)" fill="#0b0a0c" opacity=".5"/>'
    for k,v in items:
        if k=='poly': s+=f'<polygon points="{pts(v)}" fill="url(#@@hg)"/>'
        else:
            cx=v;s+=f'<circle cx="{cx+1.3}" cy="31.6" r="24" fill="none" stroke="#0b0a0c" stroke-width="7" opacity=".5"/><circle cx="{cx}" cy="30" r="24" fill="none" stroke="url(#@@hg)" stroke-width="7"/><path d="M{cx} 13C{cx+7} 22 {cx+8} 29 {cx} 38C{cx-8} 29 {cx-7} 22 {cx} 13Z" fill="url(#@@hg)"/><path d="M{cx} 19C{cx+3.5} 24 {cx+3.5} 28 {cx} 32C{cx-3.5} 28 {cx-3.5} 24 {cx} 19Z" fill="#fff4cf" opacity=".5"/>'
    return s,W,60
# ---------- Nastaliq wordmark (outlined) ----------
FONT=os.path.join(HERE,'NotoNastaliqUrdu-Bold.woff2')
FAD,FAB,_=shaped_path(FONT,'هوم')
def fa_svg(height=86):
    x0,y0,x1,y1=FAB;sc=height/(y1-y0);w=(x1-x0)*sc
    tr=f'translate({-x0*sc+1.2:.2f} {-y0*sc+1.5:.2f}) scale({sc:.5f})'
    tr2=f'translate({-x0*sc:.2f} {-y0*sc:.2f}) scale({sc:.5f})'
    return f'<path d="{FAD}" transform="{tr}" fill="#0b0a0c" opacity=".5"/><path d="{FAD}" transform="{tr2}" fill="url(#@@hg)"/>',w,height
STYLE='<style>.hm-drop{animation:hd 6s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:50% 100%}@keyframes hd{to{transform:scale(1.07,1.1);opacity:.85}}.hm-sp,.hm-sp2{animation:hs 5s ease-out infinite;opacity:0}.hm-sp2{animation-delay:-2.5s}@keyframes hs{0%{opacity:0;transform:translateY(0)}25%{opacity:.9}100%{opacity:0;transform:translateY(-16px)}}@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>'
def sub(s,i): return s.replace('@@hg','hg'+i)
def doc(vb,body,bg=None):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{STYLE}<defs>{GOLD}</defs>{bg or ""}{body}</svg>'
# ====================== deliverables ======================
import random, json, os
def build():
    out={}
    en,W,H=en_svg(); fa,fw,fh=fa_svg(78)
    markS=mark(); markN=mark(anim=False)
    out['haoma-mark.svg']=sub(doc('0 0 100 100',markS),'')
    out['haoma-logo.svg']=sub(doc(f'0 0 {116+W+4:.0f} 100',f'<g>{markS}</g><g transform="translate(116 20)">{en}</g>'),'')
    out['haoma-logo-fa.svg']=sub(doc(f'0 0 {fw+16+104:.0f} 100',f'<g transform="translate(0 11)">{fa}</g><g transform="translate({fw+16:.0f} 0)">{markS}</g>'),'')
    # favicon
    out['favicon.svg']=sub(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs>{GOLD}</defs><rect width="64" height="64" rx="13" fill="#14161a"/><g transform="translate(-5 -5) scale(.74)">{mark(ring=False,anim=False)}</g></svg>','f')
    # sky + mountains used by cover and og
    r=random.Random(9)
    def sky(w,h,n,ymax):
        st=''.join(f'<circle cx="{r.randint(10,w-10)}" cy="{r.randint(8,ymax)}" r="{r.choice([1,1.3,1.7,2.2])}" fill="#fff" opacity="{r.choice([.35,.5,.7])}"/>' for _ in range(n));return st
    def ridge(w,h,y0,amp,seed,col):
        rr=random.Random(seed);x=0;d=f'M0 {h} L0 {y0}'
        while x<w:
            x+=rr.randint(w//14,w//8);d+=f' L{min(x,w)} {y0-rr.randint(-amp//3,amp)}'
        return f'<path d="{d} L{w} {h}Z" fill="{col}"/>'
    # ---- cover 1000x1000
    rays=''.join('M%.0f %.0fL%.0f %.0f'%(*P(500,420,260,k*7.5),*P(500,420,430 if k%2==0 else 360,k*7.5)) for k in range(48))
    en2=en.replace('@@hg','@@hg')
    FAC,FWC,_=fa_svg(78)
    cover=(f'<defs>{GOLD}<linearGradient id="cs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#130f26"/><stop offset=".55" stop-color="#3d2336"/><stop offset="1" stop-color="#a8672f"/></linearGradient><radialGradient id="cg"><stop offset="0" stop-color="#ffd27a" stop-opacity=".55"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient></defs>'
     f'<rect width="1000" height="1000" fill="url(#cs)"/>{sky(1000,1000,70,520)}<circle cx="500" cy="420" r="440" fill="url(#cg)"/><g stroke="#f0b650" stroke-width="1.4" opacity=".22"><path d="{rays}"/></g>'
     f'{ridge(1000,1000,700,70,3,"#2b1b2c")}{ridge(1000,1000,790,60,8,"#1b1120")}<rect y="900" width="1000" height="100" fill="#0b0810"/>'
     f'<g transform="translate(320 240) scale(3.6)">{markN}</g>'
     f'<g transform="translate(276 752) scale(1.6)">{en}</g><g transform="translate({500-FWC/2:.0f} 872)">{FAC}</g>'
     '<rect x="22" y="22" width="956" height="956" fill="none" stroke="#e0a03a" stroke-width="2" opacity=".7"/><rect x="34" y="34" width="932" height="932" fill="none" stroke="#e0a03a" stroke-width="4" stroke-dasharray="0.1 11" stroke-linecap="round" opacity=".6"/>')
    for (x,y) in [(22,22),(978,22),(22,978),(978,978)]:
        cover+=f'<polygon transform="translate({x} {y})" points="{pts([P(0,0,13 if k%2==0 else 5,k*22.5-90) for k in range(16)])}" fill="#e0a03a"/>'
    out['haoma-cover.svg']=sub(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">{STYLE}{cover}</svg>','c')
    # ---- og 1200x630
    ogr=''.join('M%.0f %.0fL%.0f %.0f'%(*P(330,300,200,k*9),*P(330,300,300 if k%2==0 else 260,k*9)) for k in range(40))
    og=(f'<defs>{GOLD}<linearGradient id="cs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#130f26"/><stop offset=".6" stop-color="#3d2336"/><stop offset="1" stop-color="#a8672f"/></linearGradient><radialGradient id="cg"><stop offset="0" stop-color="#ffd27a" stop-opacity=".5"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient></defs>'
     f'<rect width="1200" height="630" fill="url(#cs)"/>{sky(1200,630,60,300)}<circle cx="330" cy="300" r="330" fill="url(#cg)"/><g stroke="#f0b650" stroke-width="1.2" opacity=".2"><path d="{ogr}"/></g>'
     f'{ridge(1200,630,500,70,5,"#2b1b2c")}{ridge(1200,630,550,55,12,"#1b1120")}<rect y="590" width="1200" height="40" fill="#0b0810"/>'
     f'<g transform="translate(120 100) scale(4.2)">{markN}</g><g transform="translate(600 190) scale(1.75)">{en}</g><g transform="translate(790 340)">{fa_svg(110)[0]}</g>')
    out['haoma-og.svg']=sub(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">{STYLE}{og}</svg>','o')
    # ---- Hugo inline partial
    def inl(body): return body.replace('@@hg','hg{{ $i }}')
    full_en=f'<svg class="logo logo-full" viewBox="0 0 {116+W+4:.0f} 100" role="img" aria-label="{{{{ site.Title }}}}"><defs>{GOLD}</defs><g>{markS}</g><g transform="translate(116 20)">{en}</g></svg>'
    full_fa=f'<svg class="logo logo-full" viewBox="0 0 {fw+16+104:.0f} 100" role="img" aria-label="{{{{ site.Title }}}}"><defs>{GOLD}</defs><g transform="translate(0 11)">{fa}</g><g transform="translate({fw+16:.0f} 0)">{markS}</g></svg>'
    mk=f'<svg class="logo logo-mark" viewBox="0 0 100 100" role="img" aria-label="{{{{ site.Title }}}}"><defs>{GOLD}</defs>{markS}</svg>'
    part='{{- $i := .id | default "x" -}}\n{{- if eq .v "mark" -}}'+inl(mk)+'{{- else if eq site.Language.Lang "fa" -}}'+inl(full_fa)+'{{- else -}}'+inl(full_en)+'{{- end -}}\n'
    out['_partial_logo.html']=part
    return out
if __name__=='__main__':
    o=build()
    brand=os.path.join(ROOT,'static','img','brand');os.makedirs(brand,exist_ok=True)
    for k,v in o.items():
        if k=='_partial_logo.html': path=os.path.join(ROOT,'layouts','partials','logo.html')
        else: path=os.path.join(brand,k)
        open(path,'w').write(v)
    print('wrote',len(o),'files')
