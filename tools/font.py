import numpy as np
from PIL import Image
ROM=open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','work','Dark Law - Meaning of Death (Japan).sfc'),'rb').read()
PAGE={0xfd:0x123b78,0xfc:0x127b78,0xfb:0x130000,0xfa:0x134000}
def addr(code):
    if code<0x100:
        c=code; return 0x120129+(c>>4)*0x400+((c>>3)&1)*0x200+(c&7)*0x20
    p,i=code>>8,code&0xff
    return PAGE[p]+(i>>4)*0x400+((i>>3)&1)*0x200+(i&7)*0x20
def tile(b):
    return np.array([[((b[2*y]>>(7-x))&1)|(((b[2*y+1]>>(7-x))&1)<<1) for x in range(8)] for y in range(8)])
def glyph(code,rom=ROM):
    a=addr(code); g=np.zeros((16,16),int)
    g[:8,:8]=tile(rom[a:a+16]); g[:8,8:]=tile(rom[a+16:a+32])
    g[8:,:8]=tile(rom[a+0x100:a+0x110]); g[8:,8:]=tile(rom[a+0x110:a+0x120])
    return g
def sheet(codes,path,cols=16):
    rows=(len(codes)+cols-1)//cols
    im=np.zeros((rows*18,cols*18),np.uint8)+40
    for k,c in enumerate(codes):
        im[(k//cols)*18:(k//cols)*18+16,(k%cols)*18:(k%cols)*18+16]=glyph(c)*80
    Image.fromarray(im).resize((cols*18*2,rows*18*2),0).save(path)
if __name__=='__main__':
    sheet(list(range(0xc0)),'f0.png')
    for p in (0xfd,0xfc,0xfb,0xfa): sheet([p<<8|i for i in range(256)],'f%x.png'%p)
