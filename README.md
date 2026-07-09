# baeumteo-data

「동네배움터 알리미」 앱용 강좌 데이터 저장소.

로컬에서 공공 OpenAPI를 수집해 앱이 그대로 파싱하는 표준 필드 JSON으로 가공하고,
`data/courses.json`으로 커밋한다. 앱은 이 JSON을 받아 로컬 DB에 캐싱한다.

## 데이터 소스
- **서울시교육청 평생학습포털 에버러닝** (data.go.kr 15126482) — 실시간, 미래 접수건 다수
- **대구광역시 평생학습포털** (data.go.kr 15061491) — 실시간

접수종료일이 오늘 이후(접수 가능/예정)인 강좌만 담아 신선하게 유지한다.

## 갱신 방법

### 원클릭 (권장)
```bat
refresh.bat
```
수집 → 변경이 있으면 자동으로 커밋·push 한다. 인증키는 시스템 환경변수
`LEARNING_API_KEY`(data.go.kr 일반 인증키 Decoding)로 두거나 `refresh.bat` 상단에 입력.

### 수동
```bash
LEARNING_API_KEY="<인증키>" python collect.py
git add data/courses.json && git commit -m "data: refresh" && git push
```

### 자동화 (Windows 작업 스케줄러)
갱신 주기는 하루 1회면 충분(접수기간이 며칠~몇 달 단위).
1. 작업 스케줄러 → 기본 작업 만들기 → 트리거: 매일 (예: 오전 6시)
2. 동작: 프로그램 시작 → `refresh.bat` (시작 위치 = 이 폴더)
3. 시스템 환경변수 `LEARNING_API_KEY` 를 미리 등록해두면 무인 실행됨.

## 앱에서 받는 URL
```
https://raw.githubusercontent.com/leeedaebok/baeumteo-data/master/data/courses.json
```

## 지역/기관 추가 (소스 확장)

`collect.py`는 소스 레지스트리 구조다. 새 지역을 붙이려면:

1. 표준필드 dict의 리스트를 반환하는 수집 함수를 하나 작성한다.
   (기존 `collect_seoul` / `collect_daegu` 를 복사해 필드 매핑만 수정)
   - 지역 필터가 동작하려면 `edcRdnmadr` 를 `"시도 시군구 …"` 형태로 구성할 것.
   - `rceptEndDate`(접수종료일)를 채우고 `is_open_or_upcoming()` 으로 미래건만 담을 것.
2. `SOURCES` 리스트에 `("이름", 함수)` 한 줄 추가.
```python
SOURCES = [
    ("seoul_everlearning", collect_seoul),
    ("daegu", collect_daegu),
    ("busan", collect_busan),   # ← 추가
]
```
앱은 수정할 필요가 없다 — JSON 스키마가 같으면 그대로 반영된다.

### 확장 후보 (조사됨)
- 공식 API: 부산·인천다모아 등은 data.go.kr 활용신청 후 필드 확인 필요
- 크롤링: 인천교육청 평생학습관(ilec.go.kr)은 정적 HTML이라 파싱 가능(단 robots 회색지대, 저빈도 준수)

## JSON 스키마
```jsonc
{
  "generatedAt": "2026-07-09T15:18:24",
  "count": 847,
  "sources": { "seoul_everlearning": 584, "daegu": 264 },
  "courses": [
    {
      "lctreNm": "강좌명", "lctreCo": "분류/설명", "edcTrgetType": "교육대상",
      "rceptStartDate": "YYYY-MM-DD", "rceptEndDate": "YYYY-MM-DD",
      "edcStartDay": "YYYY-MM-DD", "edcEndDay": "YYYY-MM-DD",
      "psncpa": "정원", "lctreCost": "수강료", "slctnMthType": "선정/접수방법",
      "operInstitutionNm": "운영기관", "edcRdnmadr": "시도 시군구 장소",
      "operPhoneNumber": "전화", "homepageUrl": "신청링크", "insttNm": "관리기관",
      "referenceDate": "YYYY-MM-DD"
    }
  ]
}
```
필드명은 앱 `Course` 모델의 `@SerializedName` 과 일치하므로 앱이 별도 매핑 없이 파싱한다.
