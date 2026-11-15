import sys,os,re;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from glist import parse
R=open(os.path.join(os.path.dirname(__file__),'..','work','Dark Law - Meaning of Death (Japan).sfc'),'rb').read()
def w(a): return R[a]|R[a+1]<<8
def refs(lo,hi,bank=4):
    out=[]
    for m in re.finditer(rb'\xa2(..)\x86\x1d',R[bank<<16:(bank+1)<<16],re.S):
        v=w((bank<<16)+m.start()+1)
        if lo<=v<hi: out.append(((bank<<16)+m.start()+1,v))
    return out
def tmpl(a):
    ws=[]
    while w(a)!=0xffff: ws.append(w(a)); a+=2
    return ws
def dec(ws,lst,base):
    o=''
    for x in ws:
        t=x&0x3ff; d=t-base
        if d>=0 and (d&0x10)==0 and d%2==0:
            k=4+(d>>5)*8+((d&0xf)>>1)
            o+=lst[k] if k<len(lst) else '#'
        else: o+='[%03x]'%t
    return o
if __name__=='__main__':
    p=int(sys.argv[1],16); base=int(sys.argv[2],16); lo,hi=int(sys.argv[3],16),int(sys.argv[4],16)
    a=(p>>16)<<16|w(p); lst=parse(R,a)
    for at,v in refs(lo,hi):
        print(hex(at),hex(v),dec(tmpl(0x40000|v),lst,base))
