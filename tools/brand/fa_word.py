import io, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
def shaped_path(woff, text, lang='fa'):
    f=TTFont(woff); f.flavor=None; bio=io.BytesIO(); f.save(bio); data=bio.getvalue()
    f=TTFont(io.BytesIO(data)); gs=f.getGlyphSet(); order=f.getGlyphOrder()
    face=hb.Face(hb.Blob(data)); font=hb.Font(face)
    buf=hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font,buf,{})
    x=0; d=''; bp=BoundsPen(gs)
    for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
        name=order[info.codepoint]
        pen=SVGPathPen(gs); tp=TransformPen(pen,(1,0,0,-1,x+pos.x_offset,-pos.y_offset)); gs[name].draw(tp); d+=pen.getCommands()
        bp2=BoundsPen(gs); gs[name].draw(TransformPen(bp2,(1,0,0,-1,x+pos.x_offset,-pos.y_offset)))
        if bp2.bounds: 
            b=bp2.bounds; bp.bounds=(min(bp.bounds[0],b[0]),min(bp.bounds[1],b[1]),max(bp.bounds[2],b[2]),max(bp.bounds[3],b[3])) if bp.bounds else b
        x+=pos.x_advance
    return d,bp.bounds,[order[i.codepoint] for i in buf.glyph_infos]
if __name__=='__main__':
    W='/tmp/f/node_modules/@fontsource/noto-nastaliq-urdu/files/noto-nastaliq-urdu-arabic-700-normal.woff2'
    for w in ['هوم']:
        d,b,names=shaped_path(W,w);print(w,names,b)
        x0,y0,x1,y1=b;pad=40
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-pad} {y0-pad} {x1-x0+2*pad} {y1-y0+2*pad}" width="800"><rect x="{x0-pad}" y="{y0-pad}" width="100%" height="100%" fill="#14161a"/><path d="{d}" fill="#e0a03a"/></svg>'
        open('fa_test.svg','w').write(svg)
