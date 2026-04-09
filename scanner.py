# scanner.py — TradingView Scanner API를 이용해 52주 신고가/신저가 종목을 조회하는 모듈

import requests
import pandas as pd

SCANNER_URL = "https://scanner.tradingview.com/america/scan"

COLUMNS = [
    "name",
    "description",
    "market_cap_basic",
    "sector",
    "industry",
    "close",
    "volume",
    "Value.Traded",
]

COLUMN_LABELS = [
    "심볼",
    "종목명",
    "시가총액(B USD)",
    "섹터",
    "산업",
    "현재가",
    "거래량",
    "거래대금(M USD)",
]


def _build_payload(price_filter: dict) -> dict:
    """52주 신고가/신저가 쿼리 페이로드를 생성한다."""
    return {
        "columns": COLUMNS,
        "filter": [
            price_filter,
            {"left": "Value.Traded", "operation": "greater", "right": 10_000_000},
        ],
        "options": {"lang": "en"},
        "sort": {"sortBy": "Value.Traded", "sortOrder": "desc"},
        "range": [0, 500],
    }


def _query(payload: dict) -> pd.DataFrame:
    """TradingView Scanner API에 POST 요청을 보내고 DataFrame을 반환한다."""
    resp = requests.post(SCANNER_URL, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    rows = data.get("data", [])
    if not rows:
        return pd.DataFrame(columns=COLUMN_LABELS)

    records = []
    for row in rows:
        values = row.get("d", [])
        records.append(dict(zip(COLUMNS, values)))

    df = pd.DataFrame(records)

    # 시가총액: 억 달러(B USD) 단위로 포맷
    df["market_cap_basic"] = df["market_cap_basic"].apply(
        lambda x: round(x / 1e9, 2) if pd.notna(x) and x else None
    )
    # 거래대금: M USD 단위로 포맷
    df["Value.Traded"] = df["Value.Traded"].apply(
        lambda x: round(x / 1e6, 2) if pd.notna(x) and x else None
    )

    df.columns = COLUMN_LABELS
    return df


def fetch_52w_high() -> pd.DataFrame:
    """52주 신고가 종목을 조회하여 DataFrame으로 반환한다."""
    # high >= price_52_week_high (오늘 고가가 52주 최고가 이상)
    price_filter = {"left": "high", "operation": "egreater", "right": "price_52_week_high"}
    payload = _build_payload(price_filter)
    return _query(payload)


def fetch_52w_low() -> pd.DataFrame:
    """52주 신저가 종목을 조회하여 DataFrame으로 반환한다."""
    # low <= price_52_week_low (오늘 저가가 52주 최저가 이하)
    price_filter = {"left": "low", "operation": "eless", "right": "price_52_week_low"}
    payload = _build_payload(price_filter)
    return _query(payload)
