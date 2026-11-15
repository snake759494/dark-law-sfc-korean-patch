"""title subtitle: Korean text under Dark Law logo via NMI hook"""
import os
from PIL import Image,ImageDraw,ImageFont
import numpy as np
H=os.path.dirname(os.path.abspath(__file__))
TEXT='다크 로 - 죽음의 의미'
NT=12                    # 16x16 tiles, VRAM map row7 col4..11
CODE=0xdd000             # ROM offset (CD:D800)
def render():
    F=ImageFont.truetype(os.path.join(H,'..','work','fonts','SeoulHangangM.ttf'),15)
    im=Image.new('L',(NT*16,16),0); d=ImageDraw.Draw(im)
    w=d.textlength(TEXT,font=F); bb=d.textbbox((0,0),TEXT,font=F)
    d.text(((NT*16-w)/2,(16-(bb[3]-bb[1]))/2-bb[1]),TEXT,font=F,fill=255)
    a=np.asarray(im).astype(float)
    return np.clip(np.round(a/17),0,15).astype(int)
def tile(p):
    b=bytearray(32)
    for y in range(8):
        for x in range(8):
            c=int(p[y,x])
            for k in range(4):
                if c>>k&1: b[(k//2)*16+y*2+(k&1)]|=0x80>>x
    return bytes(b)
def patch(rom,ROM0):
    px=render()
    gfx=bytearray(0x800)          # tiles 0xc0..0xff
    for i in range(NT):
        for q,(dy,dx,t) in enumerate(((0,0,0),(0,8,1),(8,0,16),(8,8,17))):
            n=(i//8)*32+(i%8)*2+t
            gfx[n*32:n*32+32]=tile(px[dy:dy+8,i*16+dx:i*16+dx+8])
    mp=b''.join(((6<<10)|0x2000|(0xc0+(i//8)*32+(i%8)*2)).to_bytes(2,'little') for i in range(NT))
    a=CODE; GFX=a+0x100; MAP=GFX+0x800
    assert set(ROM0[a:MAP+len(mp)])=={255}
    lo=lambda x:(x&0xffff).to_bytes(2,'little')
    c=bytearray()
    c+=bytes.fromhex('9c0c42 ad1042 08 c220 2000da afa2427f c9803c')
    c+=b'\xd0\x00'; j1=len(c)-1
    c+=bytes.fromhex('af00887f c95010')
    c+=b'\xd0\x00'; j2=len(c)-1
    c+=bytes.fromhex('ad704348 ad724348 ad744348 ad764348')
    c+=bytes.fromhex('e220 a980 8d1521 c220 a9002c 8d1621 a90118 8d7043')
    c+=b'\xa9'+lo(GFX)+bytes.fromhex('8d7243 a90008 8d7543 e220 a9cd 8d7443 a980 8d0b42 c220')
    c+=bytes.fromhex('a9e244 8d1621 a20000')
    loop=len(c)
    c+=b'\xbf'+lo(MAP)+b'\xcd'+bytes.fromhex('8d1821 9f60427f e8 e8 e01800')
    c+=b'\xd0'+bytes([(loop-(len(c)+2))&0xff])
    c+=bytes.fromhex('688d7643 688d7443 688d7243 688d7043')
    out=len(c)
    c+=bytes.fromhex('28 6b')
    c[j1]=out-(j1+1); c[j2]=out-(j2+1)
    rom[a:a+len(c)]=c; rom[GFX:GFX+0x800]=gfx; rom[MAP:MAP+len(mp)]=mp
    assert ROM0[0x4a149:0x4a14f]==bytes.fromhex('9c0c42ad1042')
    rom[0x4a149:0x4a14f]=b'\x22'+lo(a)+b'\xcd'+b'\xea\xea'
    Image.fromarray((px*17).astype(np.uint8)).resize((NT*64,64),0).save('title_sub.png')
