from fastapi import APIRouter, BackgroundTasks
from app.utils.db_cleanup import backup_and_cleanup_logs
from scripts.feedback_loop import run_feedback_loop

router = APIRouter()


@router.get("/run-cleanup")
def run_cleanup(background_tasks: BackgroundTasks):
    """백업 및 정리를 백그라운드에서 실행"""
    background_tasks.add_task(backup_and_cleanup_logs)
    return {"status": "Cleanup started in background."}


@router.get("/run-feedback-loop")
def run_feedback(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_feedback_loop)
    return {"status": "Feedback loop started in background."}
