import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sdec import sdec
from tbl import T
rom=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','work','Dark Law - Meaning of Death (Japan).sfc'),'rb').read()
w=lambda a:int.from_bytes(rom[a:a+2],'little')
# fixed fields: (name, first, stride, count, maxbytes, pad, term)
FIX=[('item',0x65a32,0x20,301,8,None,0xff),
     ('icls',0x67a33,0x20,256,8,None,0xff),
     ('spell',0x3ee03,0x20,24+15,8,None,0xff),
     ('class',0x3ea03,0x20,28,6,None,0xff),
     ('mon',0xf1910,0x20,49,8,0x00,None)]
# pointer tables: (name, table, count, region_start, region_end)  strings FF-terminated, newline C3
PT=[('idesc',0x69a12,512,None,None),
    ('sdesc',0x3f5c3,96,None,None),
    ('cgen',0xe2cf7,32,None,None),('skdesc',0x3e7fe,31,None,None)]
def fld(a,n):
    o=[];i=a
    while i<a+n and rom[i]!=0xff:
        c=rom[i]
        if 0xfa<=c<=0xfd: o.append(T.get(c<<8|rom[i+1],'〓')); i+=2
        elif c<0xc0: o.append(T[c]); i+=1
        else: o.append('{%02X}'%c); i+=1
    return ''.join(o)
def entries():
    out=[]
    for name,a,st,n,mx,pad,term in FIX:
        for k in range(n):
            s=fld(a+k*st,mx)
            if s.strip() in ('','？？？','？？'): continue
            out.append(('fix:%x'%(a+k*st),s))
    for name,t,n,_,_ in PT:
        bank=t&0xff0000; seen=set()
        for k in range(n):
            p=bank|w(t+2*k)
            if p in seen: continue
            seen.add(p); s=sdec(rom,p)
            if s.strip() in ('','？？？'): continue
            out.append(('str:%x'%p,s))
    return out
