# main.py — 52주 신고가/신저가 스캐너 진입점. scanner와 mailer를 호출하여 이메일을 전송한다.

import os
import sys
import traceback
from datetime import datetime

import pytz

from scanner import fetch_52w_high, fetch_52w_low
from mailer import send_email, build_html_body, build_error_html


def main():
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_app_password:
        print("오류: GMAIL_USER, GMAIL_APP_PASSWORD 환경변수를 설정하세요.")
        sys.exit(1)

    et_now = datetime.now(pytz.timezone("US/Eastern"))
    date_str = et_now.strftime("%Y-%m-%d")
    subject = f"[52W 신고가/신저가] {date_str} (ET 기준)"

    try:
        print("52주 신고가 조회 중...")
        high_df = fetch_52w_high()
        print(f"  → {len(high_df)}종목")

        print("52주 신저가 조회 중...")
        low_df = fetch_52w_low()
        print(f"  → {len(low_df)}종목")

        html_body = build_html_body(high_df, low_df)

    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"스캔 중 오류 발생:\n{error_msg}")
        html_body = build_error_html(error_msg)
        subject = f"[52W 오류] {date_str} (ET 기준)"

    try:
        print("이메일 전송 중...")
        send_email(gmail_user, gmail_app_password, subject, html_body)
        print("이메일 전송 완료!")

    except Exception as e:
        print(f"이메일 전송 실패: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
