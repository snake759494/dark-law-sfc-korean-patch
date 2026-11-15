"""pointer-referenced FF strings repacked in place (shop command menu, stat labels)"""
SETS=[
 # (bank, start, end(excl), ptr scan range, {old_addr:ko})
 (0x02,0x27364,0x27422,(0x27200,0x27364),{
  0x7364:'무기 구입',0x736f:'무기 판매',0x737a:'무기 감정',0x7387:'정보 듣기',
  0x7392:'도구 구입',0x739d:'도구 판매',0x73a8:'도구 감정',0x73b5:'전직하기',
  0x73bd:'마법 탐구',0x73cd:'마법 구입',0x73da:'신께 기도',0x73e3:'기부하기',
  0x73ec:'게시판 보기',0x73f7:'파티 해산',0x7404:'파티 결성',0x740f:'숙박하기',0x7417:'기록 남기기'}),
 (0x11,0x11198d,0x1119fa,(0x111943,0x11198d),{
  0x198d:'이름',0x1992:'체력',0x1997:'최대체력',0x19a0:'마법력',0x19a7:'최대마법력',
  0x19b2:'성별',0x19b7:'레벨',0x19bb:'칭호',0x19c0:'경험치',0x19c7:'영웅치',
  0x19ce:'힘',0x19d4:'회피',0x19db:'지능',0x19e0:'솜씨',0x19e6:'민첩',0x19ec:'생명',0x19f3:'행운'}),
]
def texts(): return [(t,0) for s in SETS for t in s[4].values()]
def patch(rom,R0,enc):
    for bank,st,en,(p0,p1),d in SETS:
        blob=bytearray(); new={}
        for old in sorted(d):
            new[old]=(st+len(blob))&0xffff; blob+=enc(d[old])+bytes([255])
        assert st+len(blob)<=en,(hex(st),len(blob),en-st)
        rom[st:en]=bytes(blob)+bytes([255])*(en-st-len(blob))
        n=0
        if bank==0x11:
            for a in range(p0,p1,2):
                w=R0[a]|R0[a+1]<<8; rom[a:a+2]=new[w].to_bytes(2,'little'); n+=1
        else:
            a=0x27326
            while a<0x27364:
                c=R0[a]; a+=1
                for k in range(c):
                    w=R0[a]|R0[a+1]<<8
                    if w in new: rom[a:a+2]=new[w].to_bytes(2,'little'); n+=1
                    a+=2
        print('ptrstr',hex(st),len(blob),en-st,'ptrs',n)
