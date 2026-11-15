import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from tbl import T
def parse(rom,a):
    out=[]
    while rom[a]!=0xff:
        c=rom[a]
        if 0xfa<=c<=0xfd: out.append(T.get(c<<8|rom[a+1],'〓')); a+=2
        else: out.append(T.get(c,'?')); a+=1
    return out
if __name__=='__main__':
    rom=open(os.path.join(os.path.dirname(__file__),'..','work','Dark Law - Meaning of Death (Japan).sfc'),'rb').read()
    l=parse(rom,int(sys.argv[1],16)); print(len(l)); print(''.join(l))
    print(' '.join('%d%s'%(i,c) for i,c in enumerate(l)))
