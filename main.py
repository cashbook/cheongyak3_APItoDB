from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import get_connection, create_table

app = FastAPI(title="청약홈 APT 분양정보 조회")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    create_table()


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=10, le=500),
    search: str = Query("", description="주택명 또는 공급지역명 검색"),
):
    conn = get_connection()
    cur = conn.cursor()

    where_clause = ""
    params: list = []
    if search:
        where_clause = "WHERE house_nm ILIKE %s OR subscrpt_area_code_nm ILIKE %s OR hssply_adres ILIKE %s"
        like = f"%{search}%"
        params = [like, like, like]

    # 전체 건수
    cur.execute(f"SELECT COUNT(*) FROM apt_lttot_pblanc_detail {where_clause}", params)
    total_count = cur.fetchone()[0]

    total_pages = max(1, (total_count + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * per_page

    cur.execute(
        f"""
        SELECT
            house_manage_no, pblanc_no, house_nm, house_secd_nm,
            house_dtl_secd_nm, rent_secd_nm, subscrpt_area_code_nm,
            hssply_adres, tot_suply_hshldco, rcrit_pblanc_de,
            rcept_bgnde, rcept_endde,
            spsply_rcept_bgnde, spsply_rcept_endde,
            gnrl_rnk1_crsparea_rcptde, gnrl_rnk1_crsparea_endde,
            gnrl_rnk1_etc_area_rcptde, gnrl_rnk1_etc_area_endde,
            gnrl_rnk2_crsparea_rcptde, gnrl_rnk2_crsparea_endde,
            gnrl_rnk2_etc_area_rcptde, gnrl_rnk2_etc_area_endde,
            przwner_presnatn_de, cntrct_cncls_bgnde, cntrct_cncls_endde,
            hmpg_adres, cnstrct_entrps_nm, bsns_mby_nm,
            mvn_prearnge_ym, speclt_rdn_earth_at, mdat_trget_area_secd,
            parcprc_uls_at, imprmn_bsns_at, mdhs_telno,
            pblanc_url
        FROM apt_lttot_pblanc_detail
        {where_clause}
        ORDER BY rcrit_pblanc_de DESC NULLS LAST, house_manage_no DESC
        LIMIT %s OFFSET %s
        """,
        params + [per_page, offset],
    )
    rows = cur.fetchall()

    columns = [
        "주택관리번호", "공고번호", "주택명", "주택구분", "주택상세구분",
        "분양구분", "공급지역", "공급위치", "공급규모(세대)", "모집공고일",
        "청약접수시작일", "청약접수종료일",
        "특별공급접수시작", "특별공급접수종료",
        "1순위해당지역시작", "1순위해당지역종료",
        "1순위기타지역시작", "1순위기타지역종료",
        "2순위해당지역시작", "2순위해당지역종료",
        "2순위기타지역시작", "2순위기타지역종료",
        "당첨자발표일", "계약시작일", "계약종료일",
        "홈페이지", "건설업체(시공사)", "사업주체(시행사)",
        "입주예정월", "투기과열지구", "조정대상지역",
        "분양가상한제", "정비사업", "문의처",
        "모집공고URL",
    ]

    cur.close()
    conn.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "rows": rows,
            "columns": columns,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
            "search": search,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
