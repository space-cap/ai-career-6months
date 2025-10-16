"""
벡터스토어 자동 재학습 스크립트
-----------------------------------------
피드백 데이터를 분석하여 부정 피드백 비율이 임계값을 초과하면
벡터스토어를 재학습(re-embedding)합니다.

실행 예시:
    python scripts/retrain_vectorstore.py
    python scripts/retrain_vectorstore.py --threshold 0.4
    python scripts/retrain_vectorstore.py --force

옵션:
    --threshold FLOAT  부정 피드백 임계값 (기본 0.3 = 30%)
    --force            피드백 비율 무시하고 강제로 재학습 실행
    --check-only       재학습 필요 여부만 확인하고 종료
"""

import sys
import os
import shutil
from datetime import datetime
from sqlalchemy import text
from app.database import SessionLocal
from app.utils.vector_retrain import retrain_if_needed
from app.services.vectorstore import get_vectorstore
from app.core.config import settings
from app.utils.slack_notifier import send_slack_message

DOCS_PATH = "docs"
CHROMA_PATH = settings.CHROMA_PATH


def perform_retraining():
    """
    벡터스토어 재학습 실행
    - docs/ 폴더의 모든 .txt 문서를 다시 읽어서 임베딩
    - 기존 Chroma DB는 백업 후 재생성
    """
    print("\n" + "=" * 60)
    print("🔄 벡터스토어 재학습 시작")
    print("=" * 60 + "\n")

    # 1. 기존 Chroma DB 백업
    if os.path.exists(CHROMA_PATH):
        backup_path = f"{CHROMA_PATH}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"📦 기존 벡터스토어 백업: {backup_path}")
        shutil.move(CHROMA_PATH, backup_path)
        print("✅ 백업 완료\n")

    # 2. 문서 목록 확인
    if not os.path.exists(DOCS_PATH):
        print(f"❌ {DOCS_PATH}/ 폴더가 없습니다.")
        return False

    txt_files = [f for f in os.listdir(DOCS_PATH) if f.endswith(".txt") or f.endswith(".md")]
    if not txt_files:
        print(f"⚠️ {DOCS_PATH}/ 폴더에 문서가 없습니다.")
        return False

    print(f"📂 총 {len(txt_files)}개 문서를 재임베딩합니다...\n")

    # 3. 새로운 벡터스토어 생성 및 임베딩
    try:
        store = get_vectorstore()
        success_count = 0
        error_count = 0

        for idx, file_name in enumerate(txt_files, 1):
            file_path = os.path.join(DOCS_PATH, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                print(f"[{idx}/{len(txt_files)}] → 임베딩 중: {file_name}")
                store.add_texts([text], metadatas=[{"source": file_name}])
                success_count += 1

            except Exception as e:
                print(f"⚠️ {file_name} 처리 중 오류: {e}")
                error_count += 1

        # 4. 결과 요약
        print("\n" + "=" * 60)
        print("✅ 벡터스토어 재학습 완료!")
        print("=" * 60)
        print(f"📊 성공: {success_count}개, 실패: {error_count}개")
        print(f"📁 Chroma 경로: {CHROMA_PATH}\n")

        return True

    except Exception as e:
        print(f"\n❌ 재학습 중 오류 발생: {e}")
        return False


def main():
    """메인 실행 함수"""
    # 커맨드 라인 인자 파싱
    args = sys.argv[1:]
    threshold = 0.3
    force_retrain = False
    check_only = False

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--force" in args:
        force_retrain = True
        args.remove("--force")

    if "--check-only" in args:
        check_only = True
        args.remove("--check-only")

    if "--threshold" in args:
        try:
            idx = args.index("--threshold")
            threshold = float(args[idx + 1])
            print(f"📌 부정 피드백 임계값: {threshold:.0%}\n")
        except (IndexError, ValueError):
            print("⚠️ --threshold 옵션 사용법: --threshold 0.3")
            return

    # DB 세션 생성
    db = SessionLocal()
    needs_retrain = False

    try:
        # 1. 피드백 비율 체크
        if force_retrain:
            print("⚡ 강제 재학습 모드 (--force)\n")
            needs_retrain = True
        else:
            needs_retrain = retrain_if_needed(db, threshold=threshold)

        # 2. check-only 모드면 여기서 종료
        if check_only:
            print(f"\n{'🚀 재학습 필요' if needs_retrain else '✅ 재학습 불필요'}")
            return

        # 3. 재학습 실행
        if needs_retrain:
            success = perform_retraining()

            # 4. Slack 알림
            if success:
                message = (
                    f"✅ *벡터스토어 재학습 완료*\n"
                    f"• 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"• 임계값: {threshold:.0%}\n"
                    f"• 상태: 성공"
                )
            else:
                message = (
                    f"❌ *벡터스토어 재학습 실패*\n"
                    f"• 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"• 로그를 확인하세요"
                )

            send_slack_message(message)

        else:
            print("\n🎯 현재 피드백 비율이 정상 범위입니다.")
            print("   재학습을 강제로 실행하려면 --force 옵션을 사용하세요.\n")

    except Exception as e:
        print(f"\n❌ 스크립트 실행 중 오류: {e}")
        send_slack_message(f"❌ 벡터스토어 재학습 스크립트 오류:\n{e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
