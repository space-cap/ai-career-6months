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
import time
import schedule
import pandas as pd
import matplotlib.pyplot as plt
import requests
from sqlalchemy import create_engine
from dotenv import load_dotenv
import platform

# .env 파일에서 환경변수 로드
load_dotenv()

# ✅ 한글 폰트 설정 (matplotlib 한글 깨짐 방지)
if platform.system() == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif platform.system() == "Darwin":  # macOS
    plt.rc("font", family="AppleGothic")
else:  # Linux
    plt.rc("font", family="NanumGothic")

# 마이너스 기호 깨짐 방지
plt.rc("axes", unicode_minus=False)

# -----------------------------------
# 1️⃣ 환경 변수 및 설정
# -----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # 🔑 Slack Bot Token (필수)
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "general")  # 채널 이름 (# 제외)
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
    if not SLACK_BOT_TOKEN:
        print("⚠️ SLACK_BOT_TOKEN is not set. Skipping Slack upload.")
        print("💡 Tip: .env 파일에 SLACK_BOT_TOKEN을 설정하세요.")
        return

    for file_path in files:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found: {file_path}")
            continue

        # Slack의 file upload API 사용
        with open(file_path, "rb") as file:
            response = requests.post(
                url="https://slack.com/api/files.upload",
                headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
                data={"channels": SLACK_CHANNEL, "initial_comment": message},
                files={"file": file}
            )

        # Slack API는 status_code와 ok 필드 모두 확인 필요
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ Uploaded {os.path.basename(file_path)} to Slack #{SLACK_CHANNEL}")
            else:
                print(f"❌ Slack API error: {result.get('error', 'Unknown error')}")
                print(f"   Response: {response.text}")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")


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
