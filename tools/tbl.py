import json,os
H=os.path.dirname(os.path.abspath(__file__))
K1=(' あいうえおかきくけこさしすせそ'
    'たちつてとなにぬねのはひふへほま'
    'みむめもやゆよらりるれろわをんー'
    'がぎぐげござじずぜぞだぢづでどば'
    '□アイウエオカキクケコサシスセソ'
    'タチツテトナニヌネノハヒフヘホマ'
    'ミムメモヤユヨラリルレロワヲンヴ'
    'ガギグゲゴザジズゼゾダヂヅデドバ'
    'びぶべぼぱぴぷぺぽぁぃぅぇぉ？！'
    'ビブベボパピプペポァィゥェォ・。'
    'っゃゅょッャュョ０１２３４５６７'
    '８９゛／＋－＆＊◀▶Ｍ□□□□□')
assert len(K1)==192,len(K1)
T={i:c for i,c in enumerate(K1)}
fix_path=os.path.join(H,'..','data','kanji_fix.json')
ocr=json.load(open(os.path.join(H,'..','data','ocr.json'),encoding='utf8'))
for k,v in ocr.items(): T[int(k,16)]=v[0][0]
if os.path.exists(fix_path):
    for k,v in json.load(open(fix_path,encoding='utf8')).items(): T[int(k,16)]=v
def dec(b,i=0,end=None,stop_ff=True):
    out=[]
    while i<len(b) and (end is None or i<end):
        c=b[i]
        if c<0xc0: out.append(T[c]); i+=1
        elif c>=0xfa and c<=0xfd: out.append(T.get(c<<8|b[i+1],'〓')); i+=2
        elif c==0xff:
            out.append('{FF}'); i+=1
            if stop_ff: break
        else: out.append('{%02X %02X}'%(c,b[i+1])); i+=2
    return ''.join(out),i
