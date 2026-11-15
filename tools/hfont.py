import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
H=os.path.dirname(os.path.abspath(__file__))
F=ImageFont.truetype(os.path.join(H,'..','work','fonts','Galmuri14.ttf'),15)
def bitmap(ch):
    im=Image.new('1',(32,32),0); d=ImageDraw.Draw(im); d.fontmode='1'
    d.text((8,8),ch,font=F,fill=1)
    return np.array(im).astype(bool)
_r=bitmap('한'); TOP=np.where(_r.any(1))[0][0]; BOT=np.where(_r.any(1))[0][-1]
def glyph(ch):
    m=bitmap(ch); g=np.zeros((16,16),np.uint8)
    xs=np.where(m.any(0))[0]
    if len(xs)==0: return g
    w=xs[-1]-xs[0]+1; x0=(16-w)//2
    hh=BOT-TOP+1; y0=(16-hh)//2
    body=np.zeros((16,16),bool)
    ys,xx=np.nonzero(m)
    for y,x in zip(ys,xx):
        Y=y-TOP+y0; X=x-xs[0]+x0
        if 0<=Y<16 and 0<=X<16: body[Y,X]=True
    out=np.zeros_like(body)
    out[1:]|=body[:-1]; out[:-1]|=body[1:]; out[:,1:]|=body[:,:-1]; out[:,:-1]|=body[:,1:]
    g[out&~body]=3; g[body]=1
    return g
def tile(g):
    o=bytearray()
    for y in range(8):
        p0=p1=0
        for x in range(8):
            v=int(g[y][x]); p0|=(v&1)<<(7-x); p1|=((v>>1)&1)<<(7-x)
        o+=bytes([p0,p1])
    return bytes(o)
if __name__=='__main__':
    import sys
    for ch in sys.argv[1]:
        print('\n'.join(''.join('.1.3'[v] for v in r) for r in glyph(ch)));print()
