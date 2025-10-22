"""
admin_dashboard.py
----------------------------------------
AI 운영 관리자 대시보드 (Streamlit)
----------------------------------------
실시간 AI 성능 메트릭, 대화 통계, 피드백 분석 시각화
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Streamlit 페이지 설정
st.set_page_config(page_title="AI Admin Dashboard", layout="wide")

# 데이터베이스 연결
try:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    logger.info(f"데이터베이스 연결 성공: {settings.DATABASE_URL.split('@')[-1]}")
except Exception as e:
    logger.error(f"데이터베이스 연결 실패: {e}")
    st.error(f"[오류] 데이터베이스 연결 실패: {e}")
    st.stop()


def safe_query(query: str, error_message: str = "데이터 조회 중 오류 발생") -> pd.DataFrame:
    """
    안전한 SQL 쿼리 실행 (에러 핸들링 포함)
    """
    try:
        logger.info(f"쿼리 실행: {query[:100]}...")
        df = pd.read_sql(text(query), engine)
        logger.info(f"쿼리 결과: {len(df)}개 행")
        return df
    except SQLAlchemyError as e:
        logger.error(f"{error_message}: {e}")
        st.error(f"[오류] {error_message}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}", exc_info=True)
        st.error(f"[오류] 예상치 못한 오류: {e}")
        return pd.DataFrame()


# 대시보드 헤더
st.title("🧠 AI 운영 관리자 대시보드")
st.markdown("**실시간 AI 챗봇 성능 및 운영 메트릭**")
st.markdown("---")

# 날짜 범위 선택
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input(
        "시작 날짜",
        value=datetime.now() - timedelta(days=30),
        max_value=datetime.now(),
    )
with col2:
    end_date = st.date_input(
        "종료 날짜",
        value=datetime.now(),
        max_value=datetime.now(),
    )

st.markdown("---")

# KPI 카드
st.subheader("📈 주요 지표 (KPI)")

kpi_query = f"""
    SELECT
        COUNT(*) as total_conversations,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(CASE WHEN sentiment IS NOT NULL THEN 1 END) as sentiment_analyzed
    FROM conversation_log
    WHERE created_at >= '{start_date}' AND created_at <= '{end_date} 23:59:59'
"""
kpi_df = safe_query(kpi_query, "KPI 조회 실패")

if not kpi_df.empty:
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(
            label="총 대화 수",
            value=f"{int(kpi_df['total_conversations'].iloc[0]):,}개",
        )
    with kpi2:
        st.metric(
            label="고유 사용자",
            value=f"{int(kpi_df['unique_users'].iloc[0]):,}명",
        )
    with kpi3:
        total = int(kpi_df['total_conversations'].iloc[0])
        analyzed = int(kpi_df['sentiment_analyzed'].iloc[0])
        st.metric(
            label="감정 분석 완료",
            value=f"{analyzed:,}개",
            delta=f"{analyzed/total*100:.1f}%" if total > 0 else "0%",
        )
else:
    st.warning("KPI 데이터가 없습니다.")

st.markdown("---")

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 대화 추이", "💬 감정 분석", "👍 피드백 통계", "🏷️ 주제 분석"]
)

# Tab 1: 대화 추이
with tab1:
    st.subheader("일별 대화 수 추이")

    conv_query = f"""
        SELECT
            created_at::date as date,
            COUNT(*) as conversation_count,
            COUNT(DISTINCT user_id) as user_count
        FROM conversation_log
        WHERE created_at >= '{start_date}' AND created_at <= '{end_date} 23:59:59'
        GROUP BY created_at::date
        ORDER BY date
    """
    conv_df = safe_query(conv_query, "대화 추이 조회 실패")

    if not conv_df.empty:
        st.line_chart(conv_df.set_index("date")["conversation_count"])
        st.caption(f"기간: {start_date} ~ {end_date}")

        # 상세 테이블
        with st.expander("상세 데이터 보기"):
            st.dataframe(conv_df, use_container_width=True)
    else:
        st.info("해당 기간에 대화 데이터가 없습니다.")

# Tab 2: 감정 분석
with tab2:
    st.subheader("감정 분석 결과 분포")

    sentiment_query = f"""
        SELECT
            sentiment,
            COUNT(*) as count
        FROM conversation_log
        WHERE created_at >= '{start_date}' AND created_at <= '{end_date} 23:59:59'
            AND sentiment IS NOT NULL
        GROUP BY sentiment
        ORDER BY count DESC
    """
    sentiment_df = safe_query(sentiment_query, "감정 분석 조회 실패")

    if not sentiment_df.empty:
        st.bar_chart(sentiment_df.set_index("sentiment"))

        # 감정별 비율
        total = sentiment_df['count'].sum()
        sentiment_df['percentage'] = (sentiment_df['count'] / total * 100).round(2)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "가장 많은 감정",
                sentiment_df.iloc[0]['sentiment'],
                f"{sentiment_df.iloc[0]['percentage']}%"
            )
        with col2:
            st.dataframe(sentiment_df, use_container_width=True)
    else:
        st.info("해당 기간에 감정 분석 데이터가 없습니다.")

# Tab 3: 피드백 통계
with tab3:
    st.subheader("좋아요 / 싫어요 추이")

    feedback_query = f"""
        SELECT
            fl.created_at::date as date,
            SUM(CASE WHEN fl.feedback = 'like' THEN 1 ELSE 0 END) AS likes,
            SUM(CASE WHEN fl.feedback = 'dislike' THEN 1 ELSE 0 END) AS dislikes
        FROM feedback_log fl
        JOIN conversation_log cl ON fl.conversation_id = cl.id
        WHERE fl.created_at >= '{start_date}' AND fl.created_at <= '{end_date} 23:59:59'
        GROUP BY fl.created_at::date
        ORDER BY date
    """
    feedback_df = safe_query(feedback_query, "피드백 조회 실패")

    if not feedback_df.empty:
        st.bar_chart(feedback_df.set_index("date")[["likes", "dislikes"]])

        # 전체 피드백 통계
        total_likes = feedback_df['likes'].sum()
        total_dislikes = feedback_df['dislikes'].sum()
        total_feedback = total_likes + total_dislikes

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 피드백", f"{int(total_feedback):,}개")
        with col2:
            st.metric("👍 좋아요", f"{int(total_likes):,}개")
        with col3:
            st.metric("👎 싫어요", f"{int(total_dislikes):,}개")

        if total_feedback > 0:
            satisfaction_rate = (total_likes / total_feedback * 100)
            st.metric("만족도", f"{satisfaction_rate:.1f}%")

        # 상세 테이블
        with st.expander("상세 데이터 보기"):
            st.dataframe(feedback_df, use_container_width=True)
    else:
        st.info("해당 기간에 피드백 데이터가 없습니다.")

# Tab 4: 주제 분석
with tab4:
    st.subheader("주제 분석 결과")

    topic_query = f"""
        SELECT
            topic,
            COUNT(*) as count
        FROM conversation_log
        WHERE created_at >= '{start_date}' AND created_at <= '{end_date} 23:59:59'
            AND topic IS NOT NULL
            AND topic != ''
        GROUP BY topic
        ORDER BY count DESC
        LIMIT 20
    """
    topic_df = safe_query(topic_query, "주제 분석 조회 실패")

    if not topic_df.empty:
        st.bar_chart(topic_df.set_index("topic"))

        # 주제별 통계
        total = topic_df['count'].sum()
        topic_df['percentage'] = (topic_df['count'] / total * 100).round(2)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "가장 많은 주제",
                topic_df.iloc[0]['topic'][:50] + "..." if len(topic_df.iloc[0]['topic']) > 50 else topic_df.iloc[0]['topic'],
                f"{topic_df.iloc[0]['percentage']}%"
            )
        with col2:
            st.metric("분석된 주제 종류", f"{len(topic_df):,}개")

        # 상세 테이블
        with st.expander("상세 데이터 보기 (상위 20개)"):
            st.dataframe(topic_df, use_container_width=True)
    else:
        st.info("해당 기간에 주제 분석 데이터가 없습니다.")

# 푸터
st.markdown("---")
st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("데이터베이스: PostgreSQL | 프레임워크: Streamlit")
