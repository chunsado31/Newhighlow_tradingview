# 52주 신고가/신저가 TradingView 스캐너

TradingView Scanner API를 이용해 미국 주식 중 **당일 52주 신고가/신저가**를 기록한 종목을 조회하고, 매일 한국시간 오전 9시에 Gmail로 리포트를 전송하는 자동화 스크립트입니다.

## 파일 구조

| 파일 | 설명 |
|------|------|
| `scanner.py` | TradingView Scanner API로 52주 신고가/신저가 종목 조회 |
| `mailer.py` | Gmail SMTP를 통한 HTML 이메일 전송 |
| `main.py` | 진입점 — scanner와 mailer를 호출 |
| `requirements.txt` | Python 패키지 의존성 |
| `.github/workflows/52w_alert.yml` | GitHub Actions 스케줄 워크플로우 |

## 필터링 조건

- **52주 신고가**: 당일 52주 최고가 갱신 + 거래대금 > $10M
- **52주 신저가**: 당일 52주 최저가 갱신 + 거래대금 > $10M

결과는 거래대금 내림차순으로 정렬됩니다.

---

## Gmail 앱 비밀번호 발급 방법

Gmail SMTP를 사용하려면 **앱 비밀번호**가 필요합니다. 일반 비밀번호로는 인증이 안 됩니다.

### 단계별 안내

1. **2단계 인증 활성화**
   - [Google 계정 보안 페이지](https://myaccount.google.com/security) 접속
   - "Google에 로그인하는 방법" 섹션에서 **2단계 인증** 클릭
   - 안내에 따라 2단계 인증을 활성화

2. **앱 비밀번호 생성**
   - 2단계 인증이 활성화된 상태에서 [앱 비밀번호 페이지](https://myaccount.google.com/apppasswords) 접속
   - 앱 이름에 `TradingView Scanner` 등 원하는 이름 입력
   - **만들기** 클릭
   - 표시되는 **16자리 비밀번호**를 복사 (공백 포함 무관)

3. **비밀번호 보관**
   - 이 비밀번호는 다시 확인할 수 없으므로 안전한 곳에 저장
   - GitHub Secrets에 등록할 때 사용

---

## GitHub Secrets 설정 방법

1. GitHub 리포지토리 페이지에서 **Settings** → **Secrets and variables** → **Actions** 클릭
2. **New repository secret** 클릭 후 아래 2개를 각각 등록:

| Secret Name | 값 |
|---|---|
| `GMAIL_USER` | Gmail 주소 (예: `yourname@gmail.com`) |
| `GMAIL_APP_PASSWORD` | 위에서 발급받은 16자리 앱 비밀번호 |

---

## 로컬 테스트 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
export GMAIL_USER="yourname@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

# 3. 실행
python main.py
```

실행하면 TradingView API를 조회하고 설정된 Gmail로 리포트를 전송합니다.

---

## 스케줄

GitHub Actions가 **UTC 기준 매일 0시 (화~토)** 에 자동 실행됩니다.
- UTC 0시 = 한국시간 오전 9시
- 화~토 실행 = 미국 월~금 장 마감 다음날에 해당

워크플로우를 수동으로 실행하려면 GitHub Actions 탭에서 **Run workflow** 버튼을 클릭하세요.
