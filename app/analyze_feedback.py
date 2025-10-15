import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
engine = create_engine(DATABASE_URL)

# 1️⃣ 대화 로그 로드
df = pd.read_sql("SELECT * FROM conversation_log", engine)

# 2️⃣ 감정 비율 계산
sentiment_counts = df["sentiment"].value_counts(normalize=True)

# 3️⃣ 주제별 분포
topic_counts = df["topic"].value_counts().head(10)

# 4️⃣ 시각화
plt.figure(figsize=(8, 4))
sentiment_counts.plot(kind="bar", title="Sentiment Ratio")
plt.tight_layout()
plt.savefig("reports/sentiment_ratio.png")

plt.figure(figsize=(8, 4))
topic_counts.plot(kind="bar", title="Top Topics")
plt.tight_layout()
plt.savefig("reports/top_topics.png")

print("✅ 분석 리포트가 reports/ 폴더에 저장되었습니다.")
