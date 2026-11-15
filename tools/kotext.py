import re,os,glob,json
H=os.path.dirname(os.path.abspath(__file__))
TR=os.path.join(H,'..','translation')
def load_ko():
    d={}
    for f in sorted(glob.glob(os.path.join(TR,'ko_*.txt'))):
        cur=None
        for ln in open(f,encoding='utf8'):
            ln=ln.rstrip('\n')
            if ln.startswith('### '): cur=int(ln[4:].strip(),16)
            elif ln.startswith('KO:') and cur is not None:
                d[cur]=ln[3:].strip(); cur=None
    return d
TOK=re.compile(r'\{([0-9A-Fa-f]+)\}|(\|)|(.)',re.S)
def toks(s):
    for m in TOK.finditer(s):
        if m.group(1): yield ('o',bytes.fromhex(m.group(1)))
        elif m.group(2): yield ('n',b'\xc3')
        else: yield ('c',m.group(3))
def tags(s): return [b for k,b in toks(s) if k=='o' and b[0]!=0xe5]
NORM={'“':"'",'”':"'",'‘':"'",'’':"'",'"':"'",'～':'~','！':'!','？':'?','　':' ','・':'.','、':',','。':'.','…':'...','─':'-','—':'-','–':'-','：':':','♪':'~'}
def norm(s):
    return ''.join(NORM.get(c,c) for c in s)
