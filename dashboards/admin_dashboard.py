import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///./local.db"
engine = create_engine(DATABASE_URL)

st.set_page_config(page_title="AI Admin Dashboard", layout="wide")

st.title("🧠 AI 운영 관리자 대시보드")
st.markdown("---")

tab1, tab2 = st.tabs(["📊 AI Performance", "🧾 Feedback Summary"])

with tab1:
    st.subheader("AI 평균 점수 추이")
    df = pd.read_sql(text("SELECT DATE(created_at) as date, AVG(score) as avg_score FROM conversation_evaluation GROUP BY DATE(created_at)"), engine)
    st.line_chart(df, x="date", y="avg_score")

with tab2:
    st.subheader("좋아요 / 싫어요 추이")
    fb = pd.read_sql(text("""
        SELECT DATE(created_at) as date,
               SUM(CASE WHEN feedback='like' THEN 1 ELSE 0 END) AS likes,
               SUM(CASE WHEN feedback='dislike' THEN 1 ELSE 0 END) AS dislikes
        FROM feedback_log
        GROUP BY DATE(created_at)
    """), engine)
    st.bar_chart(fb.set_index("date"))
