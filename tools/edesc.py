import os
H=os.path.dirname(os.path.abspath(__file__))
def load():
    d={}
    for ln in open(os.path.join(H,'..','translation','edesc_ko.txt'),encoding='utf8'):
        if '\t' in ln: a,t=ln.rstrip('\n').split('\t'); d[int(a,16)]=t
    return d
def texts(): return [(t,0) for t in load().values()]
def patch(rom,R0,enc):
    D=load(); T0,T1,S0,S1=0x69a12,0x69e12,0x69e12,0x6a2a9
    w=lambda a:R0[a]|R0[a+1]<<8
    ps=sorted(set(w(a) for a in range(T0,T1,2)))
    blob=bytearray(); new={}
    for p in ps:
        a=0x60000|p
        if a in D: t=D[a]; b=enc(' '*max(0,(12-len(t))//2)+t)+bytes([255])
        else:
            e=R0.index(b'\xff',a); b=bytes(R0[a:e+1])
        new[p]=(S0+len(blob))&0xffff; blob+=b
    assert S0+len(blob)<=S1,(len(blob),S1-S0)
    rom[S0:S1]=bytes(blob)+bytes([255])*(S1-S0-len(blob))
    for a in range(T0,T1,2): rom[a:a+2]=new[w(a)].to_bytes(2,'little')
    print('edesc',len(blob),S1-S0)
