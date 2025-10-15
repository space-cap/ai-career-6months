"""
scheduler_report.py
------------------------------------
AI Career 6 Months - 자동 리포트 스케줄러

기능:
 - conversation_log DB 분석
 - 감정/주제 비율 리포트 생성
 - 일정 간격으로 반복 실행
------------------------------------
"""

import os
import time
import schedule
import pandas as pd
import matplotlib.pyplot as plt
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

# 환경 변수 설정
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
engine = create_engine(DATABASE_URL)

# 리포트 저장 경로 (프로젝트 루트 기준)
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_report():
    """리포트 생성 함수"""
    print("📊 [REPORT] Generating AI feedback report...")

    df = pd.read_sql("SELECT * FROM conversation_log", engine)
    if df.empty:
        print("⚠️ No conversation data yet.")
        return

    # 감정 비율 계산
    sentiment_counts = df["sentiment"].value_counts(normalize=True)
    topic_counts = df["topic"].value_counts().head(10)

    # 감정 그래프
    plt.figure(figsize=(6, 4))
    sentiment_counts.plot(kind="bar", title="Sentiment Ratio")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "sentiment_ratio.png"))
    plt.close()

    # 주제 그래프
    plt.figure(figsize=(6, 4))
    topic_counts.plot(kind="bar", title="Top Topics")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_DIR, "top_topics.png"))
    plt.close()

    print(f"✅ Report generated successfully in {REPORT_DIR}")


# --------------------------------------
# 🔁 스케줄 설정
# --------------------------------------

# 매일 오전 9시에 실행
schedule.every().day.at("09:00").do(generate_report)

# 매시간 테스트용 (원하면 주석 해제)
# schedule.every(1).hours.do(generate_report)

# 첫 실행 즉시 리포트 1회 생성
generate_report()

print("🚀 Scheduler started! Waiting for next run...")

# 무한 루프 실행 (Render Background Worker에서도 사용 가능)
while True:
    schedule.run_pending()
    time.sleep(60)
