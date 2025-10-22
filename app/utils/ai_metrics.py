"""
ai_metrics.py
----------------------------------------
AI 응답 품질 지표 계산 및 Slack 리포트 전송
----------------------------------------
- conversation_evaluation + feedback_log 통합
- 주간 평균 점수 및 개선율 계산
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from app.utils.slack_notifier import send_slack_message

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
engine = create_engine(DATABASE_URL)


def compute_ai_metrics():
    """AI 품질 지표 계산"""
    with engine.begin() as conn:
        df_eval = pd.read_sql(text("""
            SELECT created_at, score
            FROM conversation_evaluation
            WHERE created_at >= DATE('now', '-14 day')
        """), conn)

        df_feed = pd.read_sql(text("""
            SELECT created_at, feedback
            FROM feedback_log
            WHERE created_at >= DATE('now', '-14 day')
        """), conn)

    # 날짜 단위로 집계
    df_eval['date'] = pd.to_datetime(df_eval['created_at']).dt.date
    df_feed['date'] = pd.to_datetime(df_feed['created_at']).dt.date
    df_feed['like'] = df_feed['feedback'].eq('like').astype(int)
    df_feed['dislike'] = df_feed['feedback'].eq('dislike').astype(int)

    df_eval_daily = df_eval.groupby('date')['score'].mean().reset_index(name='avg_score')
    df_feed_daily = df_feed.groupby('date')[['like', 'dislike']].sum().reset_index()
    df = pd.merge(df_eval_daily, df_feed_daily, on='date', how='outer').fillna(0)

    # 지난주 vs 이번주 비교
    df['week'] = pd.to_datetime(df['date']).dt.isocalendar().week
    current_week = df['week'].max()
    prev_week = current_week - 1

    cur_avg = df.loc[df['week'] == current_week, 'avg_score'].mean()
    prev_avg = df.loc[df['week'] == prev_week, 'avg_score'].mean()
    diff = (cur_avg - prev_avg) / prev_avg * 100 if prev_avg else 0

    like_total = df['like'].sum()
    dislike_total = df['dislike'].sum()

    # Slack 메시지 전송
    msg = (
        f"📈 *AI 성능 개선 리포트*\n"
        f"- 이번주 평균 점수: {cur_avg:.2f}\n"
        f"- 지난주 평균 점수: {prev_avg:.2f}\n"
        f"- 변화율: {diff:+.1f}%\n"
        f"- 👍 {like_total} / 👎 {dislike_total}\n"
        f"- 생성시각: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    send_slack_message(msg)
    print("✅ AI Metrics Report 전송 완료")
