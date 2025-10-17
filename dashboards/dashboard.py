"""
dashboard.py
---------------------------------
Streamlit 기반 AI 운영 대시보드
---------------------------------
- DB에서 대화 로그, 감정 트렌드, 평가 점수 불러오기
- 그래프 및 통계 표시

실행 방법:
    streamlit run dashboards/dashboard.py

환경 변수:
    - DATABASE_URL: 데이터베이스 연결 문자열 (기본값: sqlite:///./local.db)

요구사항:
    - streamlit >= 1.50.0
    - altair (streamlit에 포함)
    - pandas >= 2.3.3
    - sqlalchemy >= 2.0.30
---------------------------------
"""

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import altair as alt
import os
from dotenv import load_dotenv

# ✅ .env 파일에서 환경변수 로드
load_dotenv()

st.set_page_config(page_title="AI Operations Dashboard", layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
engine = create_engine(DATABASE_URL)

st.title("🤖 AI Operations Dashboard")
st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💬 Sentiment Trends", "🧠 Evaluation Metrics", "🗳️ Feedback Analysis"])

# ------------------------------
# 1️⃣ Overview
# ------------------------------
with tab1:
    st.header("서비스 개요")

    try:
        total_logs = pd.read_sql("SELECT COUNT(*) as cnt FROM conversation_log", engine)["cnt"][0]
        st.metric("총 대화 수", total_logs)

        recent = pd.read_sql(
            "SELECT * FROM conversation_log ORDER BY created_at DESC LIMIT 5",
            engine
        )

        if not recent.empty:
            st.dataframe(recent[["user_id", "question", "sentiment", "topic", "created_at"]])
        else:
            st.info("아직 대화 로그가 없습니다.")

    except SQLAlchemyError as e:
        st.error(f"데이터베이스 조회 중 오류가 발생했습니다: {e}")
    except KeyError as e:
        st.error(f"필수 컬럼이 없습니다: {e}")

# ------------------------------
# 2️⃣ Sentiment Trends
# ------------------------------
with tab2:
    st.header("감정 변화 트렌드")

    try:
        # ✅ 데이터베이스 독립적인 쿼리: pandas에서 날짜 처리
        df = pd.read_sql("""
            SELECT created_at, sentiment
            FROM conversation_log
            WHERE sentiment IS NOT NULL
            ORDER BY created_at
        """, engine)

        if df.empty:
            st.info("아직 감정 분석 데이터가 없습니다.")
        else:
            # ✅ pandas에서 날짜 변환 (DB 종류와 무관)
            df["date"] = pd.to_datetime(df["created_at"]).dt.date

            # 날짜별, 감정별 집계
            df_grouped = df.groupby(["date", "sentiment"]).size().reset_index(name="count")

            # Altair 차트 생성
            chart = alt.Chart(df_grouped).mark_line(point=True).encode(
                x=alt.X("date:T", title="날짜"),
                y=alt.Y("count:Q", title="대화 수"),
                color=alt.Color("sentiment:N", title="감정")
            ).properties(
                width=800,
                height=400,
                title="일별 감정 트렌드"
            )

            st.altair_chart(chart, use_container_width=True)

            # 데이터 테이블도 표시
            st.subheader("📊 상세 데이터")
            st.dataframe(df_grouped)

    except SQLAlchemyError as e:
        st.error(f"데이터베이스 조회 중 오류가 발생했습니다: {e}")
    except Exception as e:
        st.error(f"차트 생성 중 오류가 발생했습니다: {e}")

# ------------------------------
# 3️⃣ Evaluation Metrics
# ------------------------------
with tab3:
    st.header("AI 응답 평가 결과")

    try:
        eval_df = pd.read_sql("SELECT * FROM conversation_evaluation", engine)

        if eval_df.empty:
            st.info("아직 평가 데이터가 없습니다. evaluate_response.py 실행 후 확인하세요.")
        else:
            # ✅ 평가 지표별 평균 계산 (relevance, clarity, emotion)
            cols = ["relevance", "clarity", "emotion"]

            # 컬럼 존재 여부 확인
            available_cols = [col for col in cols if col in eval_df.columns]

            if not available_cols:
                st.warning("평가 지표 컬럼(relevance, clarity, emotion)을 찾을 수 없습니다.")
            else:
                # 전체 평균 점수 계산
                avg_scores = eval_df[available_cols].mean()
                overall_avg = avg_scores.mean()

                st.metric("전체 평균 품질 점수", round(overall_avg, 2))

                # 지표별 평균 점수 표시
                st.subheader("📊 지표별 평균 점수")
                col1, col2, col3 = st.columns(3)

                if "relevance" in available_cols:
                    col1.metric("관련성 (Relevance)", round(avg_scores["relevance"], 2))
                if "clarity" in available_cols:
                    col2.metric("명확성 (Clarity)", round(avg_scores["clarity"], 2))
                if "emotion" in available_cols:
                    col3.metric("감정 적절성 (Emotion)", round(avg_scores["emotion"], 2))

                # 지표별 분포 막대 차트
                st.subheader("📈 지표별 점수 분포")
                chart_data = eval_df[available_cols]
                st.bar_chart(chart_data)

                # 평가 데이터 테이블
                st.subheader("📋 상세 평가 내역")
                display_cols = ["conversation_id"] + available_cols + (["comment"] if "comment" in eval_df.columns else [])
                st.dataframe(eval_df[display_cols])

    except SQLAlchemyError as e:
        st.error(f"데이터베이스 조회 중 오류가 발생했습니다: {e}")
        st.info("💡 Tip: conversation_evaluation 테이블이 존재하는지 확인하세요.")
    except KeyError as e:
        st.error(f"필수 컬럼이 없습니다: {e}")
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")

# ------------------------------
# 4️⃣ Feedback Analysis
# ------------------------------
with tab4:
    st.header("사용자 피드백 분석")

    try:
        feedback_df = pd.read_sql("SELECT * FROM feedback_log", engine)

        if feedback_df.empty:
            st.info("아직 피드백 데이터가 없습니다.")
        else:
            # 피드백 요약 통계
            total_feedback = len(feedback_df)
            likes = len(feedback_df[feedback_df["feedback"] == "like"])
            dislikes = len(feedback_df[feedback_df["feedback"] == "dislike"])
            dislike_ratio = (dislikes / total_feedback * 100) if total_feedback > 0 else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("총 피드백", total_feedback)
            col2.metric("👍 좋아요", likes)
            col3.metric("👎 싫어요", dislikes)
            col4.metric("부정 비율", f"{dislike_ratio:.1f}%")

            # 피드백 분포 차트
            st.subheader("📊 피드백 분포")
            feedback_counts = feedback_df["feedback"].value_counts()
            st.bar_chart(feedback_counts)

            # 최근 피드백 내역
            st.subheader("📋 최근 피드백")
            recent_feedback = feedback_df.sort_values("created_at", ascending=False).head(10)
            display_cols = ["conversation_id", "feedback", "reason", "created_at"]
            available_cols = [col for col in display_cols if col in recent_feedback.columns]
            st.dataframe(recent_feedback[available_cols])

    except SQLAlchemyError as e:
        st.error(f"데이터베이스 조회 중 오류가 발생했습니다: {e}")
        st.info("💡 Tip: feedback_log 테이블이 존재하는지 확인하세요.")
    except Exception as e:
        st.error(f"피드백 분석 중 오류가 발생했습니다: {e}")
