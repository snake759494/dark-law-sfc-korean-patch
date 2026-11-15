import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from tbl import T
def sdec(rom,a,nl=(0xc3,)):
    o=[]
    while rom[a]!=0xff:
        c=rom[a]
        if c in nl: o.append('|'); a+=1
        elif 0xfa<=c<=0xfd: o.append(T.get(c<<8|rom[a+1],'〓')); a+=2
        elif c>=0xc0: o.append('{%02X}'%c); a+=1
        else: o.append(T[c]); a+=1
    return ''.join(o)
