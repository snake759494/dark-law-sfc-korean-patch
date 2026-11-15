# 빌드

Windows, Python 3.10 이상에서 확인했습니다.

```powershell
pip install -r requirements.txt
python tools/fetch_tools.py        # 갈무리 v2.40.3을 work/fonts/에 받고 해시 대조 (서울한강체 M은 직접 준비)
copy 'Dark Law - Meaning of Death (Japan).sfc' work\
python tools/build.py              # work/Dark Law - Meaning of Death (Korean).sfc 생성
xdelta3 -e -0 -S none -f -s 'work/Dark Law - Meaning of Death (Japan).sfc' 'work/Dark Law - Meaning of Death (Korean).sfc' Dark_Law_SFC_KR.xdelta
```

- `build.py`는 원본 ROM(4,194,304바이트, 헤더 없음)의 SHA-256을 먼저 검사합니다. 글꼴 판이 다르면 결과 ROM도 달라집니다.
- 결과 ROM의 SHA-256이 README의 `output`과 같으면 릴리즈와 동일한 ROM입니다.

## 번역 파일 형식

- `translation/ko_00.txt`~`ko_09.txt`: 대사. `### 0x주소`(원본 문자열 시작) 다음 `KO:` 줄이 한국어입니다. `|`는 줄바꿈, `{FExx}`·`{C7}` 등은 원본 제어 코드입니다.
- `translation/hint_ko.txt`: 술집 힌트. 형식은 대사와 같습니다(주소는 뱅크 안 오프셋).
- `translation/name_ko.txt`·`idesc_ko.txt`·`edesc_ko.txt`·`help_ko.txt`: `주소(16진)<TAB>한국어` 형식의 시나리오 제목, 아이템 설명, 장비 설명, 메뉴 도움말.
- `translation/menu_ko.tsv`: 아이템·마법·직업·몬스터 이름과 메뉴 문자열. 키는 원문의 SHA-1 앞 16자리입니다.
- 타이틀 부제는 `tools/title.py`, 예/아니오 교체는 `tools/yesno.py`에 있습니다.
