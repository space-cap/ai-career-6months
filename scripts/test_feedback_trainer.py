#!/usr/bin/env python3
"""
피드백 학습 루프 테스트 스크립트

Usage:
    python scripts/test_feedback_trainer.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.feedback.feedback_trainer import (
    retrain_from_feedback,
    get_feedback_statistics,
    analyze_negative_feedback_patterns,
)
from app.database import get_db


def test_feedback_statistics():
    """피드백 통계 조회 테스트"""
    print("=" * 80)
    print("[피드백 통계 조회 테스트]")
    print("=" * 80)

    db = next(get_db())
    try:
        stats = get_feedback_statistics(db, days=30)
        print("\n[최근 30일 통계]")
        print(f"  - 전체 피드백: {stats.get('total', 0)}개")
        print(f"  - 긍정 (좋아요): {stats.get('likes', 0)}개")
        print(f"  - 부정 (싫어요): {stats.get('dislikes', 0)}개")
        print(f"  - 만족도: {stats.get('satisfaction_rate', 0):.1%}")
        print(f"  - 기간: {stats.get('period_start', 'N/A')} ~ {stats.get('period_end', 'N/A')}")

        if "error" in stats:
            print(f"  - [경고] 오류: {stats['error']}")

    except Exception as e:
        print(f"[에러] 통계 조회 실패: {e}")
    finally:
        db.close()


def test_negative_feedback_analysis():
    """부정 피드백 패턴 분석 테스트"""
    print("\n" + "=" * 80)
    print("[부정 피드백 패턴 분석 테스트]")
    print("=" * 80)

    db = next(get_db())
    try:
        analysis = analyze_negative_feedback_patterns(db, limit=10)

        print(f"\n[분석 결과]")
        print(f"  - 총 부정 피드백: {analysis.get('total_negative', 0)}개")

        common_issues = analysis.get("common_issues", [])
        if common_issues:
            print(f"\n  [공통 이슈 키워드 Top 5]")
            for issue in common_issues[:5]:
                print(f"    - {issue['keyword']}: {issue['count']}회")
        else:
            print("  - 공통 이슈 키워드: 없음")

        sample_qa = analysis.get("sample_qa_pairs", [])
        if sample_qa:
            print(f"\n  [문제 Q&A 샘플 (최대 2개)]")
            for idx, qa in enumerate(sample_qa[:2], 1):
                print(f"    [{idx}]")
                print(f"      Q: {qa['question'][:80]}...")
                print(f"      A: {qa['answer'][:80]}...")
                print(f"      피드백: {qa['feedback_reason']}")
                print(f"      일시: {qa['created_at']}")
        else:
            print("  - Q&A 샘플: 없음")

        if "error" in analysis:
            print(f"  - [경고] 오류: {analysis['error']}")

    except Exception as e:
        print(f"[에러] 패턴 분석 실패: {e}")
    finally:
        db.close()


def test_full_feedback_loop():
    """전체 피드백 루프 테스트"""
    print("\n" + "=" * 80)
    print("[전체 피드백 학습 루프 테스트]")
    print("=" * 80)

    try:
        print("\n[실행 중...] 피드백 기반 학습 시작")
        result = retrain_from_feedback(days=30, limit=50)

        print("\n[결과]")

        # 통계
        stats = result.get("statistics", {})
        if stats:
            print(f"\n  [통계]")
            print(f"    - 전체 피드백: {stats.get('total', 0)}개")
            print(f"    - 만족도: {stats.get('satisfaction_rate', 0):.1%}")

        # 분석
        analysis = result.get("analysis", {})
        if analysis:
            print(f"\n  [분석]")
            print(f"    - 부정 피드백: {analysis.get('total_negative', 0)}개")
            common = analysis.get("common_issues", [])
            if common:
                print(f"    - 주요 이슈: {', '.join([issue['keyword'] for issue in common[:3]])}")

        # 개선 제안
        suggestions = result.get("suggestions", [])
        if suggestions:
            print(f"\n  [AI 개선 제안 ({len(suggestions)}개)]")
            for idx, suggestion in enumerate(suggestions, 1):
                print(f"    [{idx}] {suggestion.get('category', '일반')}")
                print(f"        {suggestion.get('suggestion', 'N/A')}")
        else:
            print(f"\n  [AI 개선 제안]")
            print("    - 제안 없음 (부정 피드백이 없거나 분석 실패)")

        if "message" in result:
            print(f"\n  [메시지] {result['message']}")

        if "error" in result:
            print(f"\n  [경고] 오류: {result['error']}")

    except Exception as e:
        print(f"[에러] 피드백 루프 실행 실패: {e}")


def main():
    """메인 테스트 실행"""
    print("\n")
    print("###############################################################################")
    print("#                                                                             #")
    print("#              Feedback Trainer Test Suite                                   #")
    print("#                                                                             #")
    print("###############################################################################")
    print("\n")

    # 1. 통계 조회 테스트
    test_feedback_statistics()

    # 2. 부정 피드백 분석 테스트
    test_negative_feedback_analysis()

    # 3. 전체 피드백 루프 테스트
    test_full_feedback_loop()

    print("\n" + "=" * 80)
    print("[테스트 완료]")
    print("=" * 80)
    print("\n")


if __name__ == "__main__":
    main()
