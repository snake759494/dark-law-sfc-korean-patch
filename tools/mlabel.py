"""menu label strings (bank6 tile-word strings) relabel"""
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from tmpl import R,w,parse
from strs import dk
# screen: glist ptr -> (base tile, keep entries, {string addr: new text})
#  new text: '@' keep original word, ' ' blank, other = Korean syllable
SCREENS={
 0x440ed:(0x1e0,set(range(41,47)),{
  0x603c2:'@메시지 속도   @@@',
  0x603de:'@전투 메시지 @@@',
  0x603f6:'@사운드 @@@@@@',
  0x6040e:'켬',0x60412:'끔',
  0x60416:'모노  ',0x60420:'스테레오',
  0x6042a:'일반 조작   ',0x6043c:'전투 조작   ',
  0x6044e:'초기@@ 복귀@',
  0x60460:'결 정@',0x6046a:'취 소@',0x60474:'대 화@',0x60488:'취 소@',
  0x604b6:'패턴  @',0x604c2:'타입  @',0x604ce:'음영  @',
  0x60542:'@운 셔플   ',
  0x606a4:' 조작     ',0x606b6:' 윈도우   ',
  0x60792:' 조작      윈도우   ',0x607b2:' 조작      윈도우   ',0x607d2:' 조작      윈도우   ',
 }),
}
# direct entry assignment (strings shared between screens; keep tile layout)
ENT={
 0x440e9:{4:'사',5:'정',6:'돈',7:'버',8:'림',9:'복',10:'삭',11:'용'},
 0x440eb:{4:' ',5:'현',6:'위',7:'치',8:'시',9:'나',10:'리',11:'오',12:'파',13:'티',14:' ',15:' ',
          16:'도',17:'구',18:' ',19:'황',20:'기',21:'록',22:'하',23:'기'},
}
# word patches: addr -> (glist, entry)  (attr kept)
WP={0x6062a:(0x440e9,11),0x60640:(0x440e9,11),0x60656:(0x440e9,11)}
def strlen(a):
    n=0
    while w(a+2*n)!=0xffff: n+=1
    return n
def plan(p):
    if p in ENT: return dict(ENT[p]),{}
    base,keep,S=SCREENS[p]
    lst=parse(R,(p>>16)<<16|w(p))
    chars=[]
    for a,t in S.items():
        assert len(t)==strlen(a),(hex(a),t,strlen(a))
        for c in t:
            if c not in '@ ' and c not in chars: chars.append(c)
    free=[k for k in range(4,len(lst)) if k not in keep]
    assert len(chars)<=len(free),(len(chars),len(free))
    d={k:' ' for k in free}
    K={}
    for c,k in zip(chars,free): d[k]=c; K[c]=k
    return d,K
def texts():
    out=[(''.join(d.values()).replace(' ',''),0) for d in ENT.values()]
    for p,(b,k,S) in SCREENS.items():
        for t in S.values(): out.append((''.join(c for c in t if c not in '@ '),0))
    return out
def tbase(p):
    a=(p>>16)<<16|w(p); return 0x1e0+(w(a)-0x2f00)//8
def write(rom):
    for a,(p,k) in WP.items():
        o=R[a]|R[a+1]<<8; k-=4; v=(o&0xfc00)|(tbase(p)+(k//8)*0x20+(k%8)*2)
        rom[a:a+2]=v.to_bytes(2,'little')
    for p,(base,keep,S) in SCREENS.items():
        d,K=plan(p)
        for a,t in S.items():
            for i,c in enumerate(t):
                if c=='@': continue
                if c==' ': v=0
                else:
                    o=R[a+2*i]|R[a+2*i+1]<<8; at=(o&0xfc00) if o else 0x2000
                    k=K[c]-4; v=at|(base+(k//8)*0x20+(k%8)*2)
                rom[a+2*i:a+2*i+2]=v.to_bytes(2,'little')
