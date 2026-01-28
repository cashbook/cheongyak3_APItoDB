# 프로젝트 브리핑: 청약홈 APT 분양정보 API-to-DB-to-Web

## 1. 프로젝트 개요

공공데이터포털의 **청약홈 분양정보 조회 서비스** API에서 APT 분양 공고 데이터를 **전량 수집**하여 PostgreSQL에 저장하고, 웹 테이블로 조회할 수 있는 시스템입니다.

```
[공공데이터포털 API] → fetch_data.py → [PostgreSQL DB] → main.py → [웹 브라우저]
       (수집)              (저장)           (조회+서빙)        (표시)
```

## 2. 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python 3.11 |
| 웹 프레임워크 | FastAPI + Uvicorn |
| DB | PostgreSQL 16 (localhost:5432) |
| DB 드라이버 | psycopg2 |
| HTTP 클라이언트 | httpx |
| 템플릿 엔진 | Jinja2 |
| CSS | Tailwind CSS (CDN) |
| 배포 예정 | Railway |

## 3. 데이터 소스

- **API**: `https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail`
- **엔드포인트**: `getAPTLttotPblancDetail` (APT 분양 상세 정보) 1개만 사용
- **출력 필드**: 총 **49개** (주택 기본정보, 청약 일정, 순위별 접수일, 사업 속성 등)
- **현재 수집량**: **2,644건**

## 4. 폴더/파일 구성 및 역할

```
cheongyak3_APItoDB/
├── database.py          # DB 계층
├── fetch_data.py        # 데이터 수집 스크립트
├── main.py              # 웹 서버 (진입점)
├── templates/
│   └── index.html       # 웹 UI 템플릿
├── requirements.txt     # 의존성 목록
└── 기술문서_*.pdf        # API 기술문서 (참고용)
```

### database.py — DB 계층

- PostgreSQL 접속 설정 (`host: localhost`, `port: 5432`, `db: cheongyakAPI`, `user/pw: admin`)
- `apt_lttot_pblanc_detail` 테이블 생성 (49개 컬럼 + id PK)
- `UNIQUE(house_manage_no, pblanc_no)` 제약 조건으로 중복 방지
- `insert_records()`: API 응답의 대문자 키 → 소문자 컬럼명 매핑 후 **UPSERT** (ON CONFLICT DO UPDATE)

### fetch_data.py — 데이터 수집

- API에서 페이지 단위(100건/페이지)로 전체 데이터를 순회 수집
- 첫 페이지 응답의 `totalCount`로 전체 페이지 수 계산
- 0.3초 간격으로 호출 (Rate Limit 방지)
- 실행: `python fetch_data.py`

### main.py — FastAPI 웹 서버

- 포트 **8001**에서 실행 (`reload=True`로 개발 모드)
- `GET /` 단일 라우트: DB에서 49개 필드 전체를 조회하여 HTML 테이블로 렌더링
- **검색**: 주택명, 공급지역명, 공급주소 ILIKE 검색
- **페이지네이션**: 기본 50건/페이지, 10~500 범위 조절 가능
- **정렬**: 모집공고일 기준 최신순

### templates/index.html — 웹 UI

- Tailwind CSS로 스타일링된 반응형 테이블
- 가로 스크롤 지원 (49개 컬럼이므로 필수)
- URL 컬럼(홈페이지, 모집공고URL)은 클릭 가능한 링크로 렌더링
- 페이지네이션 UI (처음/이전/번호/다음/마지막)

## 5. DB 스키마 요약

| 테이블 | `apt_lttot_pblanc_detail` |
|--------|--------------------------|
| PK | `id` (SERIAL) |
| UNIQUE | `(house_manage_no, pblanc_no)` |
| 컬럼 수 | 49개 + id = 50개 |

주요 컬럼 그룹:

| 그룹 | 컬럼 예시 | 개수 |
|------|-----------|------|
| 주택 기본정보 | house_nm, house_secd_nm, hssply_adres 등 | 13 |
| 모집/접수 일정 | rcrit_pblanc_de, rcept_bgnde, spsply_rcept_bgnde 등 | 3 |
| 1순위 접수일 | gnrl_rnk1_crsparea_rcptde ~ gnrl_rnk1_etc_area_endde | 6 |
| 2순위 접수일 | gnrl_rnk2_crsparea_rcptde ~ gnrl_rnk2_etc_area_endde | 6 |
| 계약/당첨 | przwner_presnatn_de, cntrct_cncls_bgnde/endde | 3 |
| 사업체 정보 | cnstrct_entrps_nm, bsns_mby_nm, mdhs_telno, hmpg_adres | 4 |
| 사업 속성 플래그 | speclt_rdn_earth_at, parcprc_uls_at, public_house_earth_at 등 | 8 |
| 기타 | mvn_prearnge_ym, nsprc_nm, pblanc_url 등 | 6 |

## 6. 전체 49개 컬럼 목록

| # | DB 컬럼명 | 한글명 |
|---|-----------|--------|
| 1 | house_manage_no | 주택관리번호 |
| 2 | pblanc_no | 공고번호 |
| 3 | house_nm | 주택명 |
| 4 | house_secd | 주택구분코드 |
| 5 | house_secd_nm | 주택구분 |
| 6 | house_dtl_secd | 주택상세구분코드 |
| 7 | house_dtl_secd_nm | 주택상세구분 |
| 8 | rent_secd | 분양구분코드 |
| 9 | rent_secd_nm | 분양구분 |
| 10 | subscrpt_area_code | 공급지역코드 |
| 11 | subscrpt_area_code_nm | 공급지역 |
| 12 | hssply_zip | 공급우편번호 |
| 13 | hssply_adres | 공급위치 |
| 14 | tot_suply_hshldco | 공급규모(세대) |
| 15 | rcrit_pblanc_de | 모집공고일 |
| 16 | nsprc_nm | 분양가격비고 |
| 17 | rcept_bgnde | 청약접수시작일 |
| 18 | rcept_endde | 청약접수종료일 |
| 19 | spsply_rcept_bgnde | 특별공급접수시작 |
| 20 | spsply_rcept_endde | 특별공급접수종료 |
| 21 | gnrl_rnk1_crsparea_rcptde | 1순위해당지역시작 |
| 22 | gnrl_rnk1_crsparea_endde | 1순위해당지역종료 |
| 23 | gnrl_rnk1_etc_gg_rcptde | 1순위경기지역시작 |
| 24 | gnrl_rnk1_etc_gg_endde | 1순위경기지역종료 |
| 25 | gnrl_rnk1_etc_area_rcptde | 1순위기타지역시작 |
| 26 | gnrl_rnk1_etc_area_endde | 1순위기타지역종료 |
| 27 | gnrl_rnk2_crsparea_rcptde | 2순위해당지역시작 |
| 28 | gnrl_rnk2_crsparea_endde | 2순위해당지역종료 |
| 29 | gnrl_rnk2_etc_gg_rcptde | 2순위경기지역시작 |
| 30 | gnrl_rnk2_etc_gg_endde | 2순위경기지역종료 |
| 31 | gnrl_rnk2_etc_area_rcptde | 2순위기타지역시작 |
| 32 | gnrl_rnk2_etc_area_endde | 2순위기타지역종료 |
| 33 | przwner_presnatn_de | 당첨자발표일 |
| 34 | cntrct_cncls_bgnde | 계약시작일 |
| 35 | cntrct_cncls_endde | 계약종료일 |
| 36 | hmpg_adres | 홈페이지 |
| 37 | cnstrct_entrps_nm | 건설업체(시공사) |
| 38 | mdhs_telno | 문의처 |
| 39 | bsns_mby_nm | 사업주체(시행사) |
| 40 | mvn_prearnge_ym | 입주예정월 |
| 41 | speclt_rdn_earth_at | 투기과열지구 |
| 42 | mdat_trget_area_secd | 조정대상지역 |
| 43 | parcprc_uls_at | 분양가상한제 |
| 44 | imprmn_bsns_at | 정비사업 |
| 45 | public_house_earth_at | 공공주택지구 |
| 46 | lrscl_bldlnd_at | 대규모택지개발지구 |
| 47 | npln_prvopr_public_house_at | 수도권내민영공공주택지구 |
| 48 | public_house_spclm_applc_apt | 공공주택특별법적용 |
| 49 | pblanc_url | 모집공고URL |

## 7. 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. DB에 데이터 수집 (최초 1회 또는 갱신 시)
python fetch_data.py

# 3. 웹 서버 실행
python main.py
# → http://localhost:8001 에서 확인
```

## 8. 현재 상태

- DB 수집: 2,644건 저장 완료
- 웹 표시: 49개 필드 전체 표시
- 서버: `http://localhost:8001` 에서 구동 중
