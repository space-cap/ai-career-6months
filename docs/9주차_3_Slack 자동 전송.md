좋아요 😎
이제 9주차 자동화의 **최종 진화형 — “AI 리포트 자동 생성 + Slack 자동 전송 버전”**을 만들어드릴게요.

이건 Render(또는 로컬) 환경에서 **매일 리포트를 만들고 → Slack 채널로 자동 발송**하는 완성된 워크플로우입니다.

---

# 🧭 목표

✅ `conversation_log` 분석
✅ 감정/주제 비율 리포트 생성
✅ 리포트 이미지를 Slack 채널에 자동 업로드
✅ 매일 같은 시각 자동 실행 (schedule 모듈 기반)

---

## 📁 **파일명:** `app/scheduler_report_slack.py`

```python
"""
scheduler_report_slack.py
------------------------------------
AI Career 6 Months - 자동 리포트 생성 & Slack 전송 버전

기능:
  ✅ conversation_log DB 분석
  ✅ 감정/주제 비율 그래프 생성
  ✅ Slack 채널로 이미지 자동 전송
  ✅ 매일 오전 9시 자동 실행 (schedule)
------------------------------------
"""

import os
import io
import time
import schedule
import pandas as pd
import matplotlib.pyplot as plt
import requests
from sqlalchemy import create_engine

# -----------------------------------
# 1️⃣ 환경 변수 및 설정
# -----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # 🔑 Slack Incoming Webhook
engine = create_engine(DATABASE_URL)

REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# -----------------------------------
# 2️⃣ 리포트 생성 함수
# -----------------------------------
def generate_report():
    print("📊 [REPORT] Generating AI feedback report...")
    df = pd.read_sql("SELECT * FROM conversation_log", engine)

    if df.empty:
        print("⚠️ No conversation data found.")
        return None

    # 감정 비율 계산
    sentiment_counts = df["sentiment"].value_counts(normalize=True)
    topic_counts = df["topic"].value_counts().head(10)

    # 감정 그래프
    plt.figure(figsize=(6, 4))
    sentiment_counts.plot(kind="bar", title="Sentiment Ratio", color="skyblue")
    plt.tight_layout()
    sentiment_path = os.path.join(REPORT_DIR, "sentiment_ratio.png")
    plt.savefig(sentiment_path)
    plt.close()

    # 주제 그래프
    plt.figure(figsize=(6, 4))
    topic_counts.plot(kind="bar", title="Top Topics", color="lightgreen")
    plt.tight_layout()
    topic_path = os.path.join(REPORT_DIR, "top_topics.png")
    plt.savefig(topic_path)
    plt.close()

    print(f"✅ Report images saved to {REPORT_DIR}")
    return [sentiment_path, topic_path]


# -----------------------------------
# 3️⃣ Slack 전송 함수
# -----------------------------------
def send_to_slack(files, message="📊 AI Feedback Report Generated!"):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ SLACK_WEBHOOK_URL is not set. Skipping Slack upload.")
        return

    for file_path in files:
        if not os.path.exists(file_path):
            continue

        # Slack의 file upload API 사용
        response = requests.post(
            url="https://slack.com/api/files.upload",
            headers={"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"},
            data={"channels": os.getenv("SLACK_CHANNEL", "#general"), "initial_comment": message},
            files={"file": open(file_path, "rb")}
        )

        if response.status_code == 200:
            print(f"✅ Uploaded {os.path.basename(file_path)} to Slack.")
        else:
            print(f"❌ Failed to upload {file_path}: {response.text}")


# -----------------------------------
# 4️⃣ 전체 실행 함수
# -----------------------------------
def generate_and_send_report():
    print("🚀 Running daily scheduled report...")
    files = generate_report()
    if files:
        send_to_slack(files, "📈 Daily AI Feedback Report 📅")
    print("🧾 Report task complete.")


# -----------------------------------
# 5️⃣ 스케줄 설정
# -----------------------------------
schedule.every().day.at("09:00").do(generate_and_send_report)
# schedule.every(6).hours.do(generate_and_send_report)  # 테스트용 (6시간마다)

# 첫 실행 즉시 1회 실행
generate_and_send_report()

print("⏰ Scheduler started! Waiting for next run...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## ⚙️ **환경 변수 설정 (.env.prod or Render Environment)**

| 변수명                 | 설명                                         |
| ------------------- | ------------------------------------------ |
| `DATABASE_URL`      | Neon PostgreSQL 연결 URL                     |
| `SLACK_WEBHOOK_URL` | Slack Webhook URL *(Incoming Webhook 방식)*  |
| `SLACK_BOT_TOKEN`   | Slack Bot OAuth Token (파일 업로드용, xoxb-로 시작) |
| `SLACK_CHANNEL`     | 리포트 전송할 채널명 (예: `#ai-reports`)             |

---

## 🧰 **Slack 설정 방법**

1️⃣ **Slack에서 앱 생성**

* [https://api.slack.com/apps](https://api.slack.com/apps) → "Create New App"
* "From scratch" 선택

2️⃣ **OAuth & Permissions** 메뉴에서
`files:write`, `chat:write`, `incoming-webhook` 권한 추가

3️⃣ **Install to Workspace** → Token 복사 (예: `xoxb-1234...`)

4️⃣ **Incoming Webhooks** → “Activate” → Webhook URL 생성
(이걸 `SLACK_WEBHOOK_URL`로 설정)

5️⃣ 환경 변수 등록

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxx/xxxx
SLACK_BOT_TOKEN=xoxb-1234-your-token
SLACK_CHANNEL=#ai-reports
```

---

## 🧩 **Render에서 자동 실행하기**

1️⃣ Render → “New +” → “Background Worker” 선택
2️⃣ GitHub 저장소 연결
3️⃣ **Start Command** 입력 👇

```bash
poetry run python -m app.scheduler_report_slack
```

4️⃣ 환경 변수 추가 (`DATABASE_URL`, `SLACK_WEBHOOK_URL`, `SLACK_BOT_TOKEN`, `SLACK_CHANNEL`)
5️⃣ 배포 후 자동 실행 🎉

Render가 24시간 이 스크립트를 돌리면서,
매일 오전 9시에 리포트를 Slack 채널에 자동 전송합니다.

---

## 🧾 **예상 Slack 메시지 예시**

```
📈 Daily AI Feedback Report 📅
✅ Sentiment & Topic analysis complete!
```

🖼️ 첨부:

* `sentiment_ratio.png`
* `top_topics.png`

---

## 🧠 **요약**

| 구성 요소                        | 역할             |
| ---------------------------- | -------------- |
| `schedule`                   | 실행 타이머 관리      |
| `generate_report()`          | DB 분석 및 그래프 생성 |
| `send_to_slack()`            | Slack 파일 업로드   |
| `generate_and_send_report()` | 통합 실행 함수       |
| Render Background Worker     | 항상 실행 상태 유지    |
| Slack Webhook                | 자동 리포트 수신 채널   |

---

원하신다면 ✨
이 Slack 자동 전송 버전을 **이메일(SMTP)** 또는 **Discord Webhook**으로
병렬 전송하도록 확장한 “멀티 채널 알림 버전”도 만들어드릴까요?
→ 리포트가 Slack + Discord + Email 모두로 동시에 전송됩니다.
