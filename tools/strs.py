import sys,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from tmpl import R,w,parse
def strings(lo,hi):
    a=lo; out=[]
    while a<hi:
        s=a; ws=[]
        while a<hi and w(a)!=0xffff: ws.append(w(a)); a+=2
        out.append((s,ws)); a+=2
    return out
def dk(x,base):
    t=x&0x3ff; d=t-base
    if x==0: return None
    if d>=0 and d%2==0 and not d&0x10: return 4+(d>>5)*8+((d&0xf)>>1)
    return -1
def dec(ws,lst,base):
    o=''
    for x in ws:
        k=dk(x,base)
        o+=' ' if k is None else ('[%03x]'%(x&0x3ff) if k<0 or k>=len(lst) else lst[k])
    return o
if __name__=='__main__':
    p=int(sys.argv[1],16);base=int(sys.argv[2],16);lo,hi=int(sys.argv[3],16),int(sys.argv[4],16)
    lst=parse(R,(p>>16)<<16|w(p))
    for s,ws in strings(lo,hi):
        if ws: print(hex(s),dec(ws,lst,base))
