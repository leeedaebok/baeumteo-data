#!/usr/bin/env python3
"""
동네배움터 알리미 - 로컬 강좌 수집 스크립트.

서울시교육청 에버러닝 + 대구 평생학습포털 OpenAPI를 수집해,
앱(Course 모델)이 그대로 파싱하는 표준 필드 스키마 JSON으로 저장한다.
"미래/현재 접수 가능"(접수종료일 >= 오늘)한 강좌만 담아 신선하고 가볍게 유지.

실행:
    LEARNING_API_KEY="<data.go.kr 일반 인증키(Decoding)>" python collect.py
산출물:
    data/courses.json
"""
import os
import sys
import json
import datetime
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

KEY = os.environ.get("LEARNING_API_KEY", "").strip()
if not KEY:
    print("환경변수 LEARNING_API_KEY 가 필요합니다.", file=sys.stderr)
    sys.exit(1)

TODAY = datetime.date.today()
UA = "Mozilla/5.0 (baeumteo-collector)"
TIMEOUT = 40


def fetch_xml(base_url, params):
    """OpenAPI 호출 후 XML 루트 반환(실패 시 None)."""
    qs = urllib.parse.urlencode({**params, "serviceKey": KEY})
    url = f"{base_url}?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode("utf-8", "replace")
    try:
        return ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"  XML 파싱 실패: {e} / 응답 앞부분: {raw[:120]}", file=sys.stderr)
        return None


def norm_date(s):
    """yyyy-MM-dd / yyyyMMdd / yyyy.MM.dd -> yyyy-MM-dd (실패 시 '')."""
    if not s:
        return ""
    d = s.strip().split(" ")[0].split("T")[0].replace(".", "-").replace("/", "-")
    digits = d.replace("-", "")
    if len(digits) == 8 and digits.isdigit():
        return f"{digits[:4]}-{digits[4:6]}-{digits[6:8]}"
    return d


def is_open_or_upcoming(receipt_end):
    """접수종료일이 오늘 이후(포함)면 True. 파싱 실패 시 False로 제외."""
    e = norm_date(receipt_end)
    if not e:
        return False
    try:
        y, m, d = map(int, e.split("-"))
        return datetime.date(y, m, d) >= TODAY
    except Exception:
        return False


def txt(item, tag):
    el = item.find(tag)
    return (el.text or "").strip() if el is not None and el.text else ""


# ── 서울시교육청 에버러닝 ──────────────────────────────────
def collect_seoul():
    base = "https://apis.data.go.kr/7010000/everlearning/getLectureList"
    rows, page, out = 500, 1, []
    while True:
        root = fetch_xml(base, {"pageNo": page, "numOfRows": rows})
        if root is None:
            break
        items = root.findall(".//item")
        if not items:
            break
        for it in items:
            course = {
                "lctreNm": txt(it, "lectureNm"),
                "lctreCo": txt(it, "categoryNm"),
                "edcTrgetType": txt(it, "targetNm"),
                "rceptStartDate": norm_date(txt(it, "applyStartYmd")),
                "rceptEndDate": norm_date(txt(it, "applyEndYmd")),
                "edcStartDay": norm_date(txt(it, "lectureStartYmd")),
                "edcEndDay": norm_date(txt(it, "lectureEndYmd")),
                "psncpa": txt(it, "offApplyNum") or txt(it, "onApplyNum"),
                "lctreCost": txt(it, "lectureCost"),
                "slctnMthType": "",
                "operInstitutionNm": txt(it, "organNm"),
                "edcRdnmadr": " ".join(x for x in ["서울특별시", txt(it, "sigunguNm"), txt(it, "place")] if x),
                "operPhoneNumber": txt(it, "organTelNo"),
                "homepageUrl": "https://everlearning.sen.go.kr/",
                "insttNm": txt(it, "organNm"),
                "referenceDate": TODAY.isoformat(),
            }
            if course["lctreNm"] and is_open_or_upcoming(course["rceptEndDate"]):
                out.append(course)
        total = txt(root, ".//totalCnt") or txt(root, ".//totalCount")
        if len(items) < rows:
            break
        page += 1
        if page > 50:
            break
    return out


# ── 대구 평생학습포털 ─────────────────────────────────────
def collect_daegu():
    base = "https://apis.data.go.kr/6270000/lectureServiceV3/lectureListV3"
    rows, page, out = 500, 1, []
    while True:
        root = fetch_xml(base, {"pageNo": page, "numOfRows": rows})
        if root is None:
            break
        items = root.findall(".//item")
        if not items:
            break
        for it in items:
            course = {
                "lctreNm": txt(it, "lec_title"),
                "lctreCo": txt(it, "lec_abstract"),
                "edcTrgetType": txt(it, "lec_target_name"),
                "rceptStartDate": norm_date(txt(it, "impl_reg_start")),
                "rceptEndDate": norm_date(txt(it, "impl_reg_finish")),
                "edcStartDay": norm_date(txt(it, "impl_start_dt")),
                "edcEndDay": norm_date(txt(it, "impl_finish_dt")),
                "psncpa": txt(it, "lec_fixedcnt"),
                "lctreCost": txt(it, "lec_cost"),
                "slctnMthType": txt(it, "receipt"),
                "operInstitutionNm": txt(it, "ins_name"),
                "edcRdnmadr": " ".join(x for x in ["대구광역시", txt(it, "impl_place")] if x),
                "operPhoneNumber": txt(it, "impl_info_tel"),
                "homepageUrl": txt(it, "lec_refer_url"),
                "insttNm": txt(it, "ins_name"),
                "referenceDate": TODAY.isoformat(),
            }
            if course["lctreNm"] and is_open_or_upcoming(course["rceptEndDate"]):
                out.append(course)
        if len(items) < rows:
            break
        page += 1
        if page > 50:
            break
    return out


def main():
    print(f"[{TODAY}] 수집 시작...")
    seoul = collect_seoul()
    print(f"  서울교육청 에버러닝: {len(seoul)}건 (접수 가능)")
    daegu = collect_daegu()
    print(f"  대구 평생학습포털: {len(daegu)}건 (접수 가능)")

    courses = seoul + daegu
    # 중복 제거 (강좌명|운영기관|접수시작 = 앱 stableId 기준)
    seen, deduped = set(), []
    for c in courses:
        key = f"{c['lctreNm']}|{c['operInstitutionNm']}|{c['rceptStartDate']}"
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    payload = {
        "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
        "count": len(deduped),
        "sources": {"seoul_everlearning": len(seoul), "daegu": len(daegu)},
        "courses": deduped,
    }
    os.makedirs("data", exist_ok=True)
    with open("data/courses.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"저장 완료: data/courses.json  총 {len(deduped)}건 (중복제거 후)")


if __name__ == "__main__":
    main()
