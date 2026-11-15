import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mtab import FIX,PT,fld,entries,rom as ROM0,w
from sdec import sdec
H=os.path.dirname(os.path.abspath(__file__))
import hashlib
def _h(s): return hashlib.sha1(s.encode('utf8')).hexdigest()[:16]
KO={}
for ln in open(os.path.join(H,'..','translation','menu_ko.tsv'),encoding='utf8'):
    ln=ln.rstrip('\n')
    if '\t' in ln:
        a,b=ln.split('\t'); KO[a]=b
B3=[0x3fc30,0x40000]
BANKFREE={0x04:[0x4f650,0x50000],0x0d:[0xd7140,0xdd000],0x0e:[0xe8550,0xf0000],0x06:[0x6ad80,0x70000]}
def balloc(bank,n):
    a=BANKFREE[bank][0]; BANKFREE[bank][0]+=n
    assert BANKFREE[bank][0]<=BANKFREE[bank][1]; return a
def L(s):
    d={}
    for tok in s.split(','):
        i,c=tok.split(':'); d[int(i)]=c
    return d
GLISTS=[
 (0xd606c, L('19:새,20:로,21:하,22:기,23:이,24:어,25:터,26:보,27:파,28:일,29: ,30: ,31: ,32: ,33: ,34: ,35: ')),
 (0x43f95, L('1: ,3:까,4:지,16:상,17:태,18:장,19:비,20:도,21:구,22:마,23:법,24:휴,25:식,26:설,27:정,28: ,29:힘,30:회,31:피,32:지,33:능,34:솜,35:씨,36:민,37:첩,38:생,39:명,40:행,41:운,42: ,43:직,44:업,45:경,46:험,47:치,48:공,49:격,50:방,51:어,52:기,53:능,54: ,60:남,61:여')),
 (0x440ef, L('4:감,5:정,6:해,7:주')),
 (0x440ed, {}),
 (0x440e7, {}),
 (0x440e9, {}),
 (0x440eb, {}),
 (0xd6070, L('36:예,37:아,38:니')),
 (0xe27fa, L('38:결,39:정,40:전,41:환')),
 (0xe27fe, L('38:결,39:정,40:전,41:환')),
 (0xe27f6, L('5: ,7:까,8:지,20:상,21:태,22:장,23:비,24:도,25:구,26:마,27:법,28:휴,29:식,30:설,31:정,32: ,33:힘,34:회,35:피,36:지,37:능,38:솜,39:씨,40:민,41:첩,42:생,43:명,44:행,45:운,46: ,47:직,48:업,49:경,50:험,51:치,52:공,53:격,54:방,55:어,56:기,57:능,64:남,65:여')),
]
def setk():
  k=set()
  for p in (0x440ed,0xd6070):
    i=(p>>16)<<16|w(p)
    while ROM0[i]!=0xff:
        n=2 if 0xfa<=ROM0[i]<=0xfd else 1
        if n==1: k.add(ROM0[i])
        i+=n
  return k
def reserved():
    r={0x2f,0x9e}
    global CURP
    for p,d in GLISTS:
        CURP=p
        a=(p>>16)<<16|w(p); i=a; k=0
        while ROM0[i]!=0xff:
            n=2 if 0xfa<=ROM0[i]<=0xfd else 1
            c=ROM0[i] if n==1 else ROM0[i]<<8|ROM0[i+1]
            if k>=4 and k not in d and c!=0: r.add(c)
            i+=n; k+=1
    return r
def grid():
    a=0xe295b; g=[]; i=a
    while ROM0[i]!=0xff:
        c=ROM0[i]; i+=1
        if c in (0,0x2f,0x9e) or c>=0xa8: continue
        if c not in g: g.append(c)
    return g[:148]
NAMES='가나다라마바사아자차카타파하거너더러머버서어저커터고노도로모보소오조코토포호구두루무부수우주쿠그드르브스츠크트프니디리미비시이지티히민준현영진수연희윤성훈석은경호한명'
def ko(s):
    k=s.strip()
    return KO.get(_h(k))
def texts():
    out=[]
    for p,d in GLISTS:
        for c in d.values(): out.append((c,0))
    for i,s in entries():
        t=ko(s)
        if t: out.append((t,1 if i.startswith('fix') else 0))
    import mlabel
    return out+town_texts()+hint_texts()+help_texts()+mlabel.texts()+__import__('rawmod').texts()+[('독주',0)]+[(t,0) for t in load_names().values()]+[(t,0) for t in load_desc().values()]
def center(t,width=12):
    n=len(t); return ' '*max(0,(width-n)//2)+t
import font as FNT
KCOPY={}
LIM=0
def kcopy(rom,c,SPARE):
    key=c
    if key not in KCOPY:
        if not SPARE: print("KCOPY short",hex(c),hex(KP)); return bytes([c])
        s=SPARE.pop(0); KCOPY[key]=s
        src=FNT.addr(c); dst=FNT.addr(s)
        for o in (0,0x10,0x100,0x110): rom[dst+o:dst+o+16]=ROM0[src+o:src+o+16]
    s=KCOPY[key]; return bytes([s]) if s<0x100 else bytes([s>>8,s&0xff])
def extra(rom,enc,alloc,CODE,SPARE=None):
    global USED
    USED=set(CODE.values())
    err=0
    global KP
    for p,d in GLISTS:
        KP=p
        bank=p>>16; a=bank<<16|int.from_bytes(rom[p:p+2],'little')
        ents=[]; i=a
        while rom[i]!=0xff:
            n=2 if 0xfa<=rom[i]<=0xfd else 1
            ents.append(bytes(rom[i:i+n])); i+=n
        import mlabel
        if p in mlabel.SCREENS or p in mlabel.ENT: d=mlabel.plan(p)[0]
        for k,c in d.items(): ents[k]=enc(c)
        for k,e in enumerate(ents):
            if p not in (0xe27fa,0xe27fe,0xe27f6) and k>=4 and k not in d and len(e)==1 and 0<e[0]<0xa8 and e[0] in USED:
                ents[k]=kcopy(rom,e[0],SPARE)
        b=b''.join(ents)+bytes([255])
        olen=i-a+1
        if p in (0x440ed,0x43f95):
            j=i+1; t=[]
            while rom[j]!=0xff:
                n=2 if 0xfa<=rom[j]<=0xfd else 1
                e=bytes(rom[j:j+n]); j+=n
                if p==0x43f95 and len(t)<2: e=enc('독주'[len(t)])
                elif len(t)>=4 and n==1 and 0<e[0]<0xa8 and e[0] in USED and e[0] not in (0x2f,0x9e): e=kcopy(rom,e[0],SPARE)
                t.append(e)
            b+=b''.join(t)+bytes([255]); olen=j-a+1
        if len(b)<=olen: na=a
        else: na=balloc(bank,len(b))
        if p==0xd606c: print('title list',len(b),olen)
        rom[na:na+len(b)]=b
        rom[p:p+2]=(na&0xffff).to_bytes(2,'little')
    import mlabel; mlabel.write(rom)
    import rawmod; rawmod.patch(rom,enc,alloc)
    # fixed fields
    for name,a0,st,n,mx,pad,term in FIX:
        for k in range(n):
            a=a0+k*st; s=fld(a,mx); t=ko(s)
            if not t: continue
            b=enc(t)
            if len(b)>mx: print('LONG',name,t,len(b)); err+=1; continue
            if pad is not None: b=b+bytes([pad])*(mx-len(b))
            else:
                b=b+b'\xff'
                b=b+b'\x00'*(mx+1-len(b))
            rom[a:a+len(b)]=b
    # pointer tables
    for name,t,n,_,_ in PT:
        bank=t>>16; old={}
        ps=[w(t+2*k) for k in range(n)]
        uniq=sorted(set(ps))
        if name in ('sdesc','skdesc'):
            lo=(bank<<16)|min(uniq); hi=max((bank<<16)|p for p in uniq)
            while ROM0[hi]!=0xff: hi+=1
            cur=[lo,hi+1]
        newp={}
        for p in uniq:
            a=(bank<<16)|p; s=sdec(ROM0,a); t2=ko(s)
            if t2 is None:
                if name in ('sdesc','skdesc'):
                    e=a
                    while ROM0[e]!=0xff: e+=1
                    b=ROM0[a:e+1]
                else: newp[p]=p; continue
            else:
                if name=='idesc': t2=center(t2)
                b=enc(t2)+b'\xff'
            if name in ('sdesc','skdesc'):
                if cur[0]+len(b)>cur[1]: cur=B3
                na=cur[0]; cur[0]+=len(b)
                if cur[0]>cur[1]: print('SDESC overflow'); err+=1
            else: na=balloc(bank,len(b))
            rom[na:na+len(b)]=b; newp[p]=na&0xffff
        for k in range(n):
            rom[t+2*k:t+2*k+2]=newp[ps[k]].to_bytes(2,'little')
    town_patch(rom,enc)
    hint_patch(rom,enc)
    help_patch(rom,enc,alloc)
    name_patch(rom,enc)
    desc_patch(rom,enc)
    print('menus done, errors',err)
TOWN={0:('레이나드 왕궁','국왕을 알현한다'),1:('세이비어 사원','상태 치유와 저주 해제'),
2:('택스 노동조합','직업 소개와 전직'),3:('샤노아 타운으로','성 아래 시가지로 이동'),
4:('락덕 정','파티 편성. 휴식'),5:('그레고르 무기점','무기.방어구 매매'),
6:('세리스 도구점','약.액세서리 매매'),7:('센트리아 공원','마을 중심. 정보 게시'),
8:('로사솔 마법조합','마법을 탐구한다'),9:('크리즈의 여관','휴식을 취한다'),
10:('레이나드 성으로','레이나드 성으로 이동'),11:('레이폴 정문','모험을 떠난다'),
12:('봉인의 동굴로','옛 수수께끼 동굴로 이동'),13:('모험 목적지로','현재 목적지가 없습니다'),
15:('모험 목적지로','소피아 신전 성지로 이동'),16:('모험 목적지로','트러스 포레스트로 이동'),
17:('모험 목적지로','사우스크리크로 이동'),18:('모험 목적지로','샤노아 타운으로 이동'),
20:('모험 목적지로','훈기 포레스트로 이동'),22:('모험 목적지로','드라크 산 광산터로 이동'),
27:('모험 목적지로','마사키 헤드로 이동'),29:('모험 목적지로','의사 헤이퍼 집으로 이동'),
30:('모험 목적지로','모롤 산 깊은 곳으로 이동')}
TOWN[14]=TOWN[3]; TOWN[19]=TOWN[15]; TOWN[21]=TOWN[16]
for i in (23,24,25,26): TOWN[i]=TOWN[22]
TOWN[28]=TOWN[27]
GL2=[((0x450cb,0x450e0),L('10:시,11:나,12:리,13:오,14:를,15: ,16:중,17:단,18: ,19: ,20:기,21:록,22:이,23: ,24:없,25:습,26:니,27:다')),
     ((0xd1638,0xd164d,0xd174a,0xd175f),L('10:기,11:록,12:이,13: ,14:없,15:습,16:니,17:다'))]
REQ1='시나리오를중단이없습니다'
EXCL1='기록'
err_gl2=[]
def town_texts():
    o=[]
    for n,d in TOWN.values(): o+= [(n,0),(d,0)]
    for p,d in GL2:
        for c in d.values(): o.append((c,0))
    return o
def town_patch(rom,enc):
    t=0x102b4; ps=[w(t+2*i) for i in range(31)]
    lo=0x10000|min(ps); hi=0x10000|max(ps)
    while ROM0[hi]!=0xff: hi+=1
    cur=lo; done={}
    for i in range(31):
        n,d=TOWN[i]
        key=(n,d)
        if key not in done:
            b=b'\x00'+enc(n.ljust(13))+enc(d.ljust(14))+b'\xff'
            if cur+len(b)>hi+1: raise SystemExit('TOWN overflow')
            rom[cur:cur+len(b)]=b; done[key]=cur; cur+=len(b)
        rom[t+2*i:t+2*i+2]=(done[key]&0xffff).to_bytes(2,'little')
    print('town used',cur-lo,'of',hi+1-lo)
    for pp,d in GL2:
        p=pp[0]; bank=p>>16; a=bank<<16|w(p); ents=[]; i=a
        while ROM0[i]!=0xff:
            n=2 if 0xfa<=ROM0[i]<=0xfd else 1
            ents.append(bytes(ROM0[i:i+n])); i+=n
        oe=[len(e) for e in ents]
        for k,c in d.items(): ents[k]=enc(c)
        for k,e in enumerate(ents):
            if len(e)!=oe[k]: print('GL2 size mismatch',hex(p),k,d.get(k),len(e),oe[k])
        b=b''.join(ents)+bytes([255])
        rom[a:a+len(b)]=b
def load_hints():
    d={};cur=None
    for ln in open(os.path.join(H,'..','translation','hint_ko.txt'),encoding='utf8'):
        ln=ln.rstrip('\n')
        if ln.startswith('### '): cur=int(ln[4:],16)
        elif ln.startswith('KO:') and cur is not None: d[cur]=ln[3:].strip(); cur=None
    return d
def hint_str(t):
    ls=t.split('|')
    return ''.join(l.ljust(14) for l in ls[:-1])+ls[-1]
def hint_texts():
    return [(hint_str(t),0) for t in load_hints().values()]
def hint_patch(rom,enc):
    HK=load_hints(); NB=0x1d0000
    rom[NB|0xce6e:NB|0xf2ac]=ROM0[0x5ce6e:0x5f2ac]
    assert ROM0[0x4500e:0x45010]==bytes([0xa9,0xc5]); rom[0x4500f]=0xdd
    chunks=[]
    for p in sorted(HK):
        a=0x50000|p; e=a
        while ROM0[e]!=0xff: e+=1
        chunks.append([NB|p,NB|(e+1)])
    chunks.append([NB|0xf2b0,NB+0x10000])
    chunks.sort(); m=[]
    for c in chunks:
        if m and c[0]<=m[-1][1]: m[-1][1]=max(m[-1][1],c[1])
        else: m.append(c)
    chunks=m; new={}
    BB={p:enc(hint_str(HK[p]))+bytes([255]) for p in HK}
    for p in sorted(HK,key=lambda p:-len(BB[p])):
        b=BB[p]
        for c in sorted(chunks,key=lambda c:c[1]-c[0]):
            if c[1]-c[0]>=len(b):
                rom[c[0]:c[0]+len(b)]=b; new[p]=c[0]&0xffff; c[0]+=len(b); break
        else: raise SystemExit('HINT overflow %x'%p)
    for a in range(NB|0xcea2,NB|0xcfb2,2):
        v=w(a-NB+0x50000)
        if v in new: rom[a:a+2]=new[v].to_bytes(2,'little')
    print('hints left space',sum(c[1]-c[0] for c in chunks))
def load_help():
    d={}
    for ln in open(os.path.join(H,'..','translation','help_ko.txt'),encoding='utf8'):
        if '\t' in ln:
            a,b=ln.rstrip('\n').split('\t'); d[int(a,16)]=b
    return d
def help_texts(): return [(t,0) for t in load_help().values()]
def help_patch(rom,enc,alloc):
    HK=load_help(); t=0x5f4dd; n=96
    ps=[w(t+2*k) for k in range(n)]
    lo=0x50000|min(ps); hi=0x50000|max(ps)
    while ROM0[hi]!=0xff: hi+=1
    chunks=[[lo,hi+1]]
    for p in (sorted(load_hints()) if 1 else []):
        a=0x50000|p; e=a
        while ROM0[e]!=0xff: e+=1
        chunks.append([a,e+1])
    new={}
    for p in sorted(set(ps)):
        a=0x50000|p
        if a in HK: b=enc(HK[a])+bytes([255])
        else:
            e=a
            while ROM0[e]!=0xff: e+=1
            b=bytes(ROM0[a:e+1])
        for c in chunks:
            if c[1]-c[0]>=len(b):
                rom[c[0]:c[0]+len(b)]=b; new[p]=c[0]&0xffff; c[0]+=len(b); break
        else: raise SystemExit('HELP overflow')
    for k in range(n): rom[t+2*k:t+2*k+2]=new[ps[k]].to_bytes(2,'little')
    global HCH; HCH=chunks
def load_names():
    d={}
    for ln in open(os.path.join(H,'..','translation','name_ko.txt'),encoding='utf8'):
        if chr(9) in ln: a,t=ln.rstrip(chr(10)).split(chr(9)); d[int(a,16)]=t
    return d
def load_desc():
    d={}
    for ln in open(os.path.join(H,'..','translation','idesc_ko.txt'),encoding='utf8'):
        if chr(9) in ln: a,t=ln.rstrip(chr(10)).split(chr(9)); d[int(a,16)]=t
    return d
def desc_patch(rom,enc):
    D=load_desc(); new={}
    for a,t in D.items():
        b=enc(t)+bytes([255])
        for c in sorted(HCH,key=lambda c:c[1]-c[0]):
            if c[1]-c[0]>=len(b):
                rom[c[0]:c[0]+len(b)]=b; new[a&0xffff]=c[0]&0xffff; c[0]+=len(b); break
        else: raise SystemExit('DESC overflow %x'%a)
    n=0
    for a in range(0x5f59d,0x5f757,2):
        v=w(a)
        if v in new: rom[a:a+2]=new[v].to_bytes(2,'little'); n+=1
    print('desc moved',len(new),'ptrs',n,'space left',sum(c[1]-c[0] for c in HCH))
def name_patch(rom,enc):
    N=load_names(); new={}
    for v,t in N.items():
        b=enc(t)+bytes([255]); a=0x50000|v; e=a
        while ROM0[e]!=0xff: e+=1
        if len(b)<=e+1-a: rom[a:a+len(b)]=b; continue
        for c in sorted(HCH,key=lambda c:c[1]-c[0]):
            if c[1]-c[0]>=len(b):
                rom[c[0]:c[0]+len(b)]=b; new[v]=c[0]&0xffff; c[0]+=len(b); break
        else: raise SystemExit('NAME overflow %x'%v)
    for lo,hi in ((0x5cbfa,0x5cc2e),(0x5cc62,0x5ce06),(0x5ce1a,0x5ce6e)):
        for a in range(lo,hi,2):
            v=w(a)
            if v in new: rom[a:a+2]=new[v].to_bytes(2,'little')
    print('names moved',len(new),'help/name space left',sum(c[1]-c[0] for c in HCH))
