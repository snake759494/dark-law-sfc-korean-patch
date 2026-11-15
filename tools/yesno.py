# はい/いいえ -> 예/아니오 : map writers + NMI-time glyph DMA (VRAM 5E30/5EB0)
import menus, hfont
NMI=0xdda00; DAT=0xddb00; J2=0xdd9c0; FLAG=b'\xf0\xff\x7f'
def glyphs():
    top=bytearray(); bot=bytearray()
    for ch in '예아니오':
        g=hfont.glyph(ch)
        top+=hfont.tile(g[0:8,0:8])+hfont.tile(g[0:8,8:16])
        bot+=hfont.tile(g[8:16,0:8])+hfont.tile(g[8:16,8:16])
    return bytes(top+bot)
def patch(rom):
    lo=lambda x:(x&0xffff).to_bytes(2,'little')
    setf=b'\xa9\x5a\x5a\x8f'+FLAG
    # site 1 (bank 4, long STA)
    a=0x4f5a6; e=bytes(rom).find(bytes.fromhex('a9ce218f30a77e'),a)
    assert rom[a:a+3]==bytes.fromhex('a9c621') and 0<e-a<70
    W=[(0xa732,0x21c6),(0xa772,0x21d6),(0xa734,0x2000),(0xa774,0x2000),
       (0xa7b2,0x21c8),(0xa7b4,0x21ca),(0xa7b6,0x21cc),(0xa7f2,0x21d8),(0xa7f4,0x21da),(0xa7f6,0x21dc)]
    c=b''.join(b'\xa9'+lo(v)+b'\x8f'+lo(ad)+b'\x7e' for ad,v in W)+setf+b'\x60'
    na=menus.balloc(4,len(c)); rom[na:na+len(c)]=c
    j=b'\x20'+lo(na)+bytes([0x80,e-(a+5)]); rom[a:a+len(j)]=j
    # site 2 (bank 11, STA abs)
    def rep(old,new):
        o=bytes.fromhex(old); i=bytes(rom).find(o,0x113ec0,0x113f60); assert i>0,old
        rom[i:i+len(o)]=bytes.fromhex(new) if isinstance(new,str) else new
    c2=bytes.fromhex('a9c6218d32a9')+setf+b'\x6b'
    assert set(rom[J2:J2+len(c2)])=={255}; rom[J2:J2+len(c2)]=c2
    rep('a9c6218d32a9',b'\x22'+lo(J2)+b'\xcd\xea\xea')
    rep('a9c8218d36a9','a900008d36a9'); rep('a9d8218d76a9','a900008d76a9')
    rep('a9c8218db4a9','a9ca218db4a9'); rep('a9ca218db6a9','a9cc218db6a9')
    rep('a9d8218df4a9','a9da218df4a9'); rep('a9da218df6a9','a9dc218df6a9')
    # NMI routine (called by JSR from title hook, A 16-bit)
    c=bytearray(bytes.fromhex('af')+FLAG+bytes.fromhex('c95a5a')+b'\xd0\x00'); jo=len(c)-1
    c+=bytes.fromhex('a90000 8f')+FLAG
    c+=bytes.fromhex('ad704348 ad724348 ad744348 ad764348')
    c+=bytes.fromhex('e220 a980 8d1521 c220 a90118 8d7043')
    for va,src in ((0x5e30,DAT),(0x5eb0,DAT+0x80)):
        c+=b'\xa9'+lo(va)+bytes.fromhex('8d1621')+b'\xa9'+lo(src)+bytes.fromhex('8d7243 a98000 8d7543 e220 a9cd 8d7443 a980 8d0b42 c220')
    c+=bytes.fromhex('688d7643 688d7443 688d7243 688d7043')
    c[jo]=len(c)-(jo+1); c+=b'\x60'
    assert set(rom[NMI:NMI+len(c)])=={255}; rom[NMI:NMI+len(c)]=c
    g=glyphs(); rom[DAT:DAT+len(g)]=g
    # field NMI hook (C3:86AC: LDA $4210 / STZ $420C)
    F=0xdd9e0; assert rom[0x386ac:0x386b2]==bytes.fromhex('ad10429c0c42')
    st=bytes.fromhex('ad1042 9c0c42 08 c220 2000da 28 6b')
    assert set(rom[F:F+len(st)])=={255}; rom[F:F+len(st)]=st
    rom[0x386ac:0x386b2]=bytes([0x22])+lo(F)+bytes([0xcd,0xea,0xea])
    # shop-mode NMI (C2:908B) same hook
    assert rom[0x290a2:0x290a8]==bytes.fromhex('ad10429c0c42')
    rom[0x290a2:0x290a8]=bytes([0x22])+lo(F)+bytes([0xcd,0xea,0xea])
    # shop yes/no cursor routine (bank 11): set flag after cursor draw
    S3=0xdd9f0; assert rom[0x112176:0x11217b]==bytes.fromhex('e2209cc70a')
    st=bytes.fromhex('a95a5a 8f')+FLAG+bytes.fromhex('e220 9cc70a 6b')
    assert set(rom[S3:S3+len(st)])=={255}; rom[S3:S3+len(st)]=st
    rom[0x112176:0x11217b]=bytes([0x22])+lo(S3)+bytes([0xcd,0xea])
    # call from title hook: after '08 c220' insert JSR -> need room: hook start
    return NMI
