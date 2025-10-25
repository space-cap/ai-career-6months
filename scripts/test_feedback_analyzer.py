#!/usr/bin/env python3
"""
피드백 분석기 테스트 스크립트

Usage:
    python scripts/test_feedback_analyzer.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.feedback.feedback_analyzer import analyze_feedback


def test_analyze_feedback():
    """다양한 피드백 텍스트로 감정 분석 테스트"""

    test_cases = [
        "정확하고 자세한 답변이었습니다. 정말 도움이 많이 되었어요!",
        "답변이 너무 불친절하고 이해하기 어려웠습니다.",
        "그냥 그랬어요. 보통입니다.",
        "최고입니다! 완벽한 설명이에요.",
        "전혀 도움이 되지 않았어요. 실망스럽습니다.",
        "괜찮은 것 같아요.",
        "",  # 빈 문자열 테스트 (에러 발생 예상)
    ]

    print("=" * 80)
    print("[피드백 감정 분석 테스트]")
    print("=" * 80)

    for idx, feedback in enumerate(test_cases, 1):
        print(f"\n[테스트 {idx}]")
        print(f"피드백: '{feedback}'")

        try:
            result = analyze_feedback(feedback)
            print(f"결과: {result}")
            print(f"  - 감정: {result['sentiment']} ({result['korean_label']})")
            print(f"  - 점수: {result['score']}")
            if "error" in result:
                print(f"  - [경고] 오류: {result['error']}")

        except ValueError as e:
            print(f"  - [에러] ValueError: {e}")
        except Exception as e:
            print(f"  - [에러] 예외 발생: {e}")

    print("\n" + "=" * 80)
    print("[테스트 완료]")
    print("=" * 80)


if __name__ == "__main__":
    test_analyze_feedback()
