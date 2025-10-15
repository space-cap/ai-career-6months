import os
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

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
engine = create_engine(DATABASE_URL)

# ✅ reports 폴더 경로 (루트 기준)
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

df = pd.read_sql("SELECT * FROM conversation_log", engine)

# 감정 비율
sentiment_counts = df["sentiment"].value_counts(normalize=True)
plt.figure(figsize=(6, 4))
sentiment_counts.plot(kind="bar", title="Sentiment Ratio")
plt.tight_layout()
plt.savefig(os.path.join(REPORT_DIR, "sentiment_ratio.png"))

# 주제 Top 10
topic_counts = df["topic"].value_counts().head(10)
plt.figure(figsize=(6, 4))
topic_counts.plot(kind="bar", title="Top Topics")
plt.tight_layout()
plt.savefig(os.path.join(REPORT_DIR, "top_topics.png"))

print(f"✅ 분석 리포트가 {REPORT_DIR} 폴더에 저장되었습니다.")
