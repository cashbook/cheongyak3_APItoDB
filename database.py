import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "cheongyakAPI",
    "user": "admin",
    "password": "admin",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS apt_lttot_pblanc_detail (
            id SERIAL PRIMARY KEY,
            house_manage_no VARCHAR(40),
            pblanc_no VARCHAR(40),
            house_nm VARCHAR(200),
            house_secd VARCHAR(2),
            house_secd_nm VARCHAR(4000),
            house_dtl_secd VARCHAR(2),
            house_dtl_secd_nm VARCHAR(4000),
            rent_secd VARCHAR(1),
            rent_secd_nm VARCHAR(500),
            subscrpt_area_code VARCHAR(3),
            subscrpt_area_code_nm VARCHAR(500),
            hssply_zip VARCHAR(6),
            hssply_adres VARCHAR(256),
            tot_suply_hshldco INTEGER,
            rcrit_pblanc_de VARCHAR(10),
            nsprc_nm VARCHAR(200),
            rcept_bgnde VARCHAR(10),
            rcept_endde VARCHAR(10),
            spsply_rcept_bgnde VARCHAR(10),
            spsply_rcept_endde VARCHAR(10),
            gnrl_rnk1_crsparea_rcptde VARCHAR(21),
            gnrl_rnk1_crsparea_endde VARCHAR(21),
            gnrl_rnk1_etc_gg_rcptde VARCHAR(21),
            gnrl_rnk1_etc_gg_endde VARCHAR(21),
            gnrl_rnk1_etc_area_rcptde VARCHAR(21),
            gnrl_rnk1_etc_area_endde VARCHAR(21),
            gnrl_rnk2_crsparea_rcptde VARCHAR(21),
            gnrl_rnk2_crsparea_endde VARCHAR(21),
            gnrl_rnk2_etc_gg_rcptde VARCHAR(21),
            gnrl_rnk2_etc_gg_endde VARCHAR(21),
            gnrl_rnk2_etc_area_rcptde VARCHAR(21),
            gnrl_rnk2_etc_area_endde VARCHAR(21),
            przwner_presnatn_de VARCHAR(10),
            cntrct_cncls_bgnde VARCHAR(10),
            cntrct_cncls_endde VARCHAR(10),
            hmpg_adres VARCHAR(256),
            cnstrct_entrps_nm VARCHAR(200),
            mdhs_telno VARCHAR(30),
            bsns_mby_nm VARCHAR(200),
            mvn_prearnge_ym VARCHAR(6),
            speclt_rdn_earth_at VARCHAR(1),
            mdat_trget_area_secd VARCHAR(1),
            parcprc_uls_at VARCHAR(1),
            imprmn_bsns_at VARCHAR(1),
            public_house_earth_at VARCHAR(1),
            lrscl_bldlnd_at VARCHAR(1),
            npln_prvopr_public_house_at VARCHAR(1),
            public_house_spclm_applc_apt VARCHAR(1),
            pblanc_url VARCHAR(300),
            UNIQUE(house_manage_no, pblanc_no)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


# API 응답의 대문자 키를 소문자 컬럼명으로 매핑
COLUMN_NAMES = [
    "house_manage_no", "pblanc_no", "house_nm", "house_secd", "house_secd_nm",
    "house_dtl_secd", "house_dtl_secd_nm", "rent_secd", "rent_secd_nm",
    "subscrpt_area_code", "subscrpt_area_code_nm", "hssply_zip", "hssply_adres",
    "tot_suply_hshldco", "rcrit_pblanc_de", "nsprc_nm", "rcept_bgnde", "rcept_endde",
    "spsply_rcept_bgnde", "spsply_rcept_endde",
    "gnrl_rnk1_crsparea_rcptde", "gnrl_rnk1_crsparea_endde",
    "gnrl_rnk1_etc_gg_rcptde", "gnrl_rnk1_etc_gg_endde",
    "gnrl_rnk1_etc_area_rcptde", "gnrl_rnk1_etc_area_endde",
    "gnrl_rnk2_crsparea_rcptde", "gnrl_rnk2_crsparea_endde",
    "gnrl_rnk2_etc_gg_rcptde", "gnrl_rnk2_etc_gg_endde",
    "gnrl_rnk2_etc_area_rcptde", "gnrl_rnk2_etc_area_endde",
    "przwner_presnatn_de", "cntrct_cncls_bgnde", "cntrct_cncls_endde",
    "hmpg_adres", "cnstrct_entrps_nm", "mdhs_telno", "bsns_mby_nm",
    "mvn_prearnge_ym", "speclt_rdn_earth_at", "mdat_trget_area_secd",
    "parcprc_uls_at", "imprmn_bsns_at", "public_house_earth_at",
    "lrscl_bldlnd_at", "npln_prvopr_public_house_at",
    "public_house_spclm_applc_apt", "pblanc_url",
]


def insert_records(records: list[dict]):
    if not records:
        return 0

    conn = get_connection()
    cur = conn.cursor()
    inserted = 0

    for record in records:
        row = {}
        for col in COLUMN_NAMES:
            val = record.get(col.upper())
            if val is not None:
                val = str(val) if not isinstance(val, (int, float)) else val
            row[col] = val

        cols = list(row.keys())
        vals = list(row.values())
        placeholders = ", ".join(["%s"] * len(cols))
        col_names = ", ".join(cols)
        update_set = ", ".join([f"{c} = EXCLUDED.{c}" for c in cols if c not in ("house_manage_no", "pblanc_no")])

        query = f"""
            INSERT INTO apt_lttot_pblanc_detail ({col_names})
            VALUES ({placeholders})
            ON CONFLICT (house_manage_no, pblanc_no)
            DO UPDATE SET {update_set};
        """
        cur.execute(query, vals)
        inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    return inserted


if __name__ == "__main__":
    create_table()
    print("Table created successfully.")
