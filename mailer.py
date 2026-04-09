# mailer.py — Gmail SMTP를 이용해 52주 신고가/신저가 리포트를 HTML 이메일로 전송하는 모듈

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import pandas as pd
import pytz

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
RECIPIENT = "chunsado31@gmail.com"


def _get_et_now() -> datetime:
    """현재 미국 동부시간(ET)을 반환한다."""
    return datetime.now(pytz.timezone("US/Eastern"))


def _df_to_html_table(df: pd.DataFrame, header_color: str, label: str) -> str:
    """DataFrame을 HTML 표로 변환한다."""
    display_cols = ["심볼", "종목명", "섹터", "산업", "시가총액(B USD)", "거래대금(M USD)"]

    if df.empty:
        return f"""
        <h2 style="color:{header_color};">{label}</h2>
        <p>총 0종목</p>
        <p style="color:#888;">해당 종목 없음</p>
        """

    count = len(df)
    filtered = df[display_cols].copy()

    rows_html = ""
    for i, (_, row) in enumerate(filtered.iterrows()):
        bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        cells = "".join(
            f'<td style="padding:6px 10px;border:1px solid #ddd;">{v if pd.notna(v) else "-"}</td>'
            for v in row
        )
        rows_html += f'<tr style="background:{bg};">{cells}</tr>\n'

    header_cells = "".join(
        f'<th style="padding:8px 10px;border:1px solid #ddd;color:#fff;background:{header_color};">{col}</th>'
        for col in display_cols
    )

    return f"""
    <h2 style="color:{header_color};">{label}</h2>
    <p>총 {count}종목</p>
    <table style="border-collapse:collapse;width:100%;font-size:13px;font-family:Arial,sans-serif;">
      <thead><tr>{header_cells}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """


def build_html_body(high_df: pd.DataFrame, low_df: pd.DataFrame) -> str:
    """52주 신고가/신저가 리포트 HTML 본문을 생성한다."""
    et_now = _get_et_now()
    date_str = et_now.strftime("%Y-%m-%d %H:%M %Z")

    high_table = _df_to_html_table(high_df, "#2e7d32", "📈 52주 신고가")
    low_table = _df_to_html_table(low_df, "#c62828", "📉 52주 신저가")

    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;margin:20px;">
      <h1 style="border-bottom:2px solid #333;padding-bottom:10px;">52주 신고가 / 신저가 리포트</h1>
      <p style="color:#555;">조회 시각: {date_str} (미국 동부시간)</p>
      {high_table}
      <br/>
      {low_table}
      <hr style="margin-top:30px;"/>
      <p style="color:#999;font-size:11px;">TradingView Scanner API 기반 자동 생성 리포트</p>
    </body>
    </html>
    """


def build_error_html(error_msg: str) -> str:
    """에러 발생 시 HTML 본문을 생성한다."""
    et_now = _get_et_now()
    date_str = et_now.strftime("%Y-%m-%d %H:%M %Z")

    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;margin:20px;">
      <h1 style="color:#c62828;">⚠️ 52주 신고가/신저가 스캔 오류</h1>
      <p style="color:#555;">발생 시각: {date_str} (미국 동부시간)</p>
      <pre style="background:#f5f5f5;padding:15px;border-radius:5px;overflow-x:auto;">{error_msg}</pre>
    </body>
    </html>
    """


def send_email(gmail_user: str, gmail_app_password: str, subject: str, html_body: str):
    """Gmail SMTP를 통해 HTML 이메일을 전송한다."""
    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_user
    msg["To"] = RECIPIENT
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, RECIPIENT, msg.as_string())
