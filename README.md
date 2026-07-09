# baeumteo-data

「동네배움터 알리미」 앱용 강좌 데이터 저장소.

로컬에서 공공 OpenAPI를 수집해 앱이 그대로 파싱하는 표준 필드 JSON으로 가공하고,
`data/courses.json`으로 커밋한다. 앱은 이 JSON을 jsDelivr CDN으로 받아 로컬 DB에 캐싱한다.

## 데이터 소스
- **서울시교육청 평생학습포털 에버러닝** (data.go.kr 15126482) — 실시간, 미래 접수건 다수
- **대구광역시 평생학습포털** (data.go.kr 15061491) — 실시간

접수종료일이 오늘 이후(접수 가능/예정)인 강좌만 담아 신선하게 유지한다.

## 갱신 방법
```bash
LEARNING_API_KEY="<data.go.kr 일반 인증키(Decoding)>" python collect.py
git add data/courses.json && git commit -m "data: refresh" && git push
```
갱신 주기는 하루 1회면 충분(접수기간이 며칠~몇 달 단위).

## 앱에서 받는 URL (jsDelivr)
```
https://cdn.jsdelivr.net/gh/leeedaebok/baeumteo-data@main/data/courses.json
```

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
필드명은 앱 `Course` 모델의 `@SerializedName`과 일치하므로 앱이 별도 매핑 없이 파싱한다.
