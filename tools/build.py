import sys,os,json,subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kotext import *
from tbl import K1
import hfont, font as F
from collections import Counter
W=os.path.join(H,'..','work'); G=W
SRC=os.path.join(G,'Dark Law - Meaning of Death (Japan).sfc')
DST=os.path.join(G,'Dark Law - Meaning of Death (Korean).sfc')
rom=bytearray(open(SRC,'rb').read())
import hashlib
assert hashlib.sha256(rom).hexdigest()=='6c1749b24124f74d3aceefa24297b836b6ee7598fc2094f4d065b3c762c898a4','원본 ROM 해시 불일치'
U=json.load(open(os.path.join(H,'..','data','units.json'),encoding='utf8'))
ko=load_ko()
import menus
# ---------- collect texts
script={}
for s,e in U:
    k=int(s,16)
    if k in ko: script[k]=(int(e,16),norm(ko[k]))
MT=menus.texts()
MP=[]
cnt=Counter()
def count(t):
    for kind,b in toks(t):
        if kind=='c': cnt[b]+=1
for k,(e,t) in script.items(): count(t)
for t,pr in MT: count(t)
PRI=Counter()
for t,pr in MT:
    if pr:
        for kind,b in toks(t):
            if kind=='c': PRI[b]+=1
FIXED={' ':0x00,'?':0x8e,'!':0x8f}
for d in range(10): FIXED[str(d)]=0xa8+d
KANA={c:i for i,c in enumerate(K1) if c not in '□'}
need=[c for c,_ in sorted(cnt.items(),key=lambda x:(-PRI[x[0]],-x[1])) if c not in FIXED and not (c in KANA and not ('가'<=c<='힣'))]
RES=menus.reserved()
G=menus.grid()
S=[]
# ---- small 8x8 font (shop/item lists): item-name chars need 1-byte codes with distinct tiles
SMAP={int(k):v for k,v in json.load(open(os.path.join(H,'..','data','smallmap.json'))).items()}
IC=[]
for i,t in menus.entries():
    if i[:6] in ('fix:65','fix:66','fix:67'):
        k=menus.ko(t)
        if k:
            for c in k:
                if c not in IC and c!=' ' and c not in '?!0123456789 ': IC.append(c)
for c in menus.NAMES+menus.REQ1:
    if c not in S and c not in menus.EXCL1: S.append(c)
for c in IC:
    if len(S)<len(G) and c not in S and '가'<=c<='힣' and c not in menus.EXCL1: S.append(c)
for c,_ in sorted(PRI.items(),key=lambda x:-x[1]):
    if len(S)>=len(G): break
    if '가'<=c<='힣' and c not in S and c not in menus.EXCL1: S.append(c)
assert len(S)<=len(G)
S=sorted(S[:len(G)])
PRE=dict(zip(S,G))
one=[c for c in range(1,0xc0) if c not in (0x8e,0x8f,0x9e,0x9f) and not (0xa8<=c<=0xbf) and c not in RES and c not in G]
two=[x for x in [0xfa00|i for i in list(range(0xa0,0xc0))+list(range(0xc1,0xc8))]+[(p<<8)|i for p in (0xfd,0xfc,0xfb) for i in range(256)]+[0xfa00|i for i in list(range(0x68))+list(range(0xc8,0x100))] if x not in RES]
slots=one+two
need=[c for c in need if c not in PRE]
need=[c for c in IC if c in need and c not in PRE]+[c for c in need if c not in IC or c in PRE]
TOP=[c for c in '새로하기이어터보파일'+''.join(IC) if c in need]
need=TOP+[c for c in need if c not in TOP]
X1=[c for c in need if c in menus.EXCL1]
need=[c for c in need if c not in X1]
need=need[:len(one)]+X1+need[len(one):]
if len(need)>len(slots):
    print('OVERFLOW',len(need),len(slots)); sys.exit(1)
CODE=dict(FIXED); CODE.update(PRE)
need=[c for c in need if c not in PRE]
for c,s in zip(need,slots): CODE[c]=s
print("glyphs",len(need),"/",len(slots),"one",len(one),"IC",len([c for c in IC if c not in PRE]))
def enc(t):
    o=bytearray()
    for kind,b in toks(t):
        if kind=='c':
            if b in CODE: v=CODE[b]
            elif b in KANA: v=KANA[b]
            else: raise ValueError('char %r in %s'%(b,t[:40]))
            o+=bytes([v]) if v<0x100 else bytes([v>>8,v&0xff])
        else: o+=b
    return bytes(o)
# ---------- font
for c,s in CODE.items():
    if c in FIXED and c not in '?!': 
        if c==' ': continue
    g=hfont.glyph(c); a=F.addr(s)
    for t,(y,x) in enumerate(((0,0),(0,8),(8,0),(8,8))):
        off=a+[0,0x10,0x100,0x110][t]
        rom[off:off+16]=hfont.tile(g[y:y+8,x:x+8])
# ---------- small font glyphs
from PIL import Image as _I,ImageFont as _F,ImageDraw as _D
_SF=_F.truetype(os.path.join(H,'..','work','fonts','Galmuri7.ttf'),8)
SB=0x1624b3; ST=0x25ba5
FT={SMAP.get(CODE[c],[0])[0] for c in FIXED}
free=[t for t in range(1,0x90) if t not in FT]
tab={CODE[c]:SMAP.get(CODE[c],[0])[0] for c in FIXED}
for c in IC:
    v=CODE[c]; assert v<0x100,c
    t=free.pop(0); tab[v]=t
    im=_I.new('L',(8,10)); _D.Draw(im).text((0,-1),c,font=_SF,fill=255)
    b=bytearray()
    for y in range(8):
        r=0
        for x in range(8):
            if im.getpixel((x,y))>127: r|=0x80>>x
        b+=bytes([r,0])
    rom[SB+t*16:SB+t*16+16]=b
for k in range(0xc0): rom[ST+2*k:ST+2*k+2]=bytes([tab.get(k,0),0])
print('small glyphs',len(IC))
# ---------- F7 long jump handler at D1:7F80
HND=0x117f80
code=bytes.fromhex(
 'c220ad8d0a29ff00850b0a18650baa'   # x=depth*3
 'bd8f0a851d e220 bd910a851f c220'
 'a00100 b71d 48 e220 c8c8 b71d 9d910a c220 68 9d8f0a e220'
 '4cd93a'.replace(' ',''))
rom[HND:HND+len(code)]=code
rom[0x110422+2*(0xf7-0xc0):0x110422+2*(0xf7-0xc0)+2]=(HND&0xffff|0x8000 if False else 0x7f80).to_bytes(2,'little')
# ---------- free pool
POOL=[(0x1bd240,0x1d0000),(0x1e6850,0x1f0000),(0x29230,0x30000),
(0x199c80,0x1a0000),(0x31a7e0,0x320000),(0xfab60,0x100000),(0x30c320,0x310000),
      (0xbc820,0xc0000),(0x2fd350,0x300000)]
pi=0; cur=POOL[0][0]
def alloc(n):
    global pi,cur
    while cur+n>POOL[pi][1]:
        pi+=1; cur=POOL[pi][0]
    a=cur; cur+=n; return a
def snes(o): return 0xc00000|o
jmp=lambda o: b'\xf7'+snes(o).to_bytes(3,'little')
for k,(e,t) in sorted(script.items()):
    b=enc(t)+jmp(e)
    a=alloc(len(b)); rom[a:a+len(b)]=b
    rom[k:k+4]=jmp(a)
print('script pool used up to',hex(cur),'pool idx',pi)
# ---------- menus
for p in MP:
    if p.get('skip'): continue
    b=enc(p['text'])+p.get('term',b'')
    if len(b)>p['maxlen']: print('MENU LONG',hex(p['off']),p['text'],len(b),p['maxlen']); continue
    b=b+bytes([p.get('pad',0)])*(p['maxlen']-len(b)) if p.get('fill',True) else b
    rom[p['off']:p['off']+len(b)]=b
menus.extra(rom,enc,alloc,CODE,list(slots[len(need):]))
import title; title.patch(rom,menus.ROM0)
import yesno; yesno.patch(rom)
import ptrstr; ptrstr.patch(rom,menus.ROM0,enc)
import edesc; edesc.patch(rom,menus.ROM0,enc)
# checksum
rom[0x40ffdc:0x40ffe0]=b'' if False else rom[0x40ffdc:0x40ffe0]
s=sum(rom)&0xffff
hdr=0xffdc
rom[hdr:hdr+4]=((s^0xffff)&0xffff).to_bytes(2,'little')+s.to_bytes(2,'little')
s=sum(rom)&0xffff
rom[hdr:hdr+4]=((s^0xffff)&0xffff).to_bytes(2,'little')+s.to_bytes(2,'little')
open(DST,'wb').write(rom)
json.dump({c:s for c,s in CODE.items()},open(os.path.join(W,'codes.json'),'w',encoding='utf8'),ensure_ascii=False)
print('wrote',DST)
