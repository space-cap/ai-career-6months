from fastapi import APIRouter, BackgroundTasks
from app.utils.report_utils import generate_and_send_report

router = APIRouter()


@router.get("/run-report")
def run_report(background_tasks: BackgroundTasks):
    """외부 호출 시 즉시 리포트 생성 (백그라운드 실행)"""
    background_tasks.add_task(generate_and_send_report)
    return {"status": "Report generation started in background."}
