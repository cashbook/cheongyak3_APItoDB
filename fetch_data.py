import httpx
import time
from database import create_table, insert_records

API_BASE = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1"
ENDPOINT = "/getAPTLttotPblancDetail"
SERVICE_KEY = "e7076445bae090b5d44086f596241353727d4d7ff43604faf560bdecf99d37fe"
PER_PAGE = 100  # 한 번에 가져올 건수 (최대값 사용)


def fetch_page(page: int) -> dict:
    url = f"{API_BASE}{ENDPOINT}"
    params = {
        "page": page,
        "perPage": PER_PAGE,
        "serviceKey": SERVICE_KEY,
    }
    resp = httpx.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all():
    create_table()
    print("Table ready.")

    # 첫 페이지로 totalCount 확인
    print("Fetching page 1 ...")
    first = fetch_page(1)
    total_count = first.get("totalCount", 0)
    print(f"Total records available: {total_count}")

    data = first.get("data", [])
    total_inserted = insert_records(data)
    print(f"Page 1: {len(data)} records fetched, {total_inserted} upserted.")

    if total_count == 0:
        print("No data available.")
        return

    total_pages = (total_count + PER_PAGE - 1) // PER_PAGE
    print(f"Total pages to fetch: {total_pages}")

    for page in range(2, total_pages + 1):
        print(f"Fetching page {page}/{total_pages} ...")
        try:
            result = fetch_page(page)
            page_data = result.get("data", [])
            count = insert_records(page_data)
            total_inserted += count
            print(f"  -> {len(page_data)} records fetched, {count} upserted. (Total: {total_inserted})")
        except httpx.HTTPStatusError as e:
            print(f"  -> HTTP error on page {page}: {e.response.status_code}")
        except Exception as e:
            print(f"  -> Error on page {page}: {e}")

        # API 호출 간격 제한 (rate limit 방지)
        time.sleep(0.3)

    print(f"\nDone! Total records upserted: {total_inserted}")


if __name__ == "__main__":
    fetch_all()
