"""raw code strings / headered glyph lists referenced by LDX #a / LDA #bank / STX $1d / STA $1f"""
import re,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from tmpl import R,parse
PATS=(rb'\xa2(..)\xa9(.)\x86\x1d\x85\x1f',rb'\xa9(.)\xa2(..)\x85\x1f\x86\x1d',rb'\xa9(.)\x85\x1f\xa2(..)\x86\x1d',rb'\xa2(..)\x86\x1d\xa9(.)\x85\x1f')
def sites():
    S={}
    for pat in PATS:
        for m in re.finditer(pat,R,re.S):
            if len(m.group(1))==2: ia,ib=m.start(1),m.start(2)
            else: ib,ia=m.start(1),m.start(2)
            bk=R[ib]
            if bk<0xc0: continue
            off=((bk&0x3f)<<16)|R[ia]|R[ia+1]<<8
            S.setdefault(off,[]).append((ia,ib))
    return S
def L(s):
    d={}
    for tok in s.split(','):
        i,c=tok.split(':'); d[int(i)]=c
    return d
# full strings
STR={0x111c25:'기록 없음',0x1119fa:'상승!',0x111a01:'하락!'}
# headered lists: index->char
LST={
 0x22997:L('4:인,5:사,6:사,7:자,8:마,9:도,10:전,11:승,12:여,13:광,14:민,15:상,16:수,17:어,18:직,19:방,20:시,21:도,22:적,23:화,24:정,25:려,26:목,27:학,28:술,29:역,30:병,31:사,32:교,33:기,34:무,35:닌,36:현,37:군,38:주,39:성'),
 0x253d0:L('4:신,5:께,6:감,7:사,8:악,9:의,10:개,11:심,12:부,13:의,14:분,15:배,16:사,17:원,18:수,19:리,20:구,21:제,22:자,23:금'),
 0x26389:L('5:기,6:록,10:기,11:록,15:기,16:록'),
 0x263b2:L('4:크,5:리,6:즈,7: ,9:레,10:피,11:아,12: '),
 0x26a73:L('4:세,5:계,6:의,7:창,8:조,9:태,10:고,11:의,12:대,13:전,14:대,15:전,16:의,17:결,18:말,19:봉,20:인,21:의,22:동,23:굴,24:다,25:르,26:크,27:왕'),
}
SKL=(0x3e5fc,16,'슈트,스크롤,언록,점프,수영,저지먼트,디스펠,트릭가드,소드마스터,히트앤웨이,크로스어택,크리티컬,매직배리어,멘탈배리어,레스토어,디스카운트,슬래시!,오버파워'.split(','))
NPC={0x3f9d4:'옐로',0x3fa1e:'블루',0x3fa68:'그린',0x3fab2:'사이카스',0x3fafc:'메릴',0x3fb46:'로키펠',0x3fb90:'안토니아나',0x3fbda:'맥스터'}
def texts():
    return [(t,0) for t in NPC.values()]+texts0()
def texts0():
    return __import__('ptrstr').texts()+__import__('edesc').texts()+[(t,0) for t in SKL[2]]+[(t,0) for t in STR.values()]+[(''.join(d.values()).replace(' ',''),0) for d in LST.values()]
def patch(rom,enc,alloc):
    S=sites()
    def ents(a):
        e=[]; i=a
        while R[i]!=0xff:
            n=2 if 0xfa<=R[i]<=0xfd else 1
            e.append(bytes(R[i:i+n])); i+=n
        return e,i
    jobs=[(a,enc(t)+b'\xff') for a,t in STR.items()]
    for a,d in LST.items():
        e,_=ents(a)
        for k,c in d.items(): e[k]=enc(c)
        jobs.append((a,b''.join(e)+b'\xff'))
    for a,t in NPC.items():
        e=R.index(bytes([255]),a); b=enc(t)
        if len(b)>e-a: print('NPC long',t,len(b),e-a); continue
        rom[a:e+1]=b+bytes([255])+bytes(e-a-len(b))
    b0,st,nm=SKL
    for i,t in enumerate(nm):
        b=enc(t)+bytes([255]); assert len(b)<=st-1,t
        a=b0+i*st; rom[a:a+st-1]=b+bytes(st-1-len(b))
    for a,b in jobs:
        _,end=ents(a); olen=end+1-a
        assert a in S,hex(a)
        if len(b)<=olen: rom[a:a+len(b)]=b; continue
        na=alloc(len(b)); rom[na:na+len(b)]=b
        for ia,ib in S[a]:
            rom[ia:ia+2]=(na&0xffff).to_bytes(2,'little'); rom[ib]=0xc0|(na>>16)
