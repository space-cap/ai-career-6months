from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENAI_API_KEY: str
    DATABASE_URL: str = "mysql://root:doolman@localhost:3306/ai_career"
    CHROMA_PATH: str = "./chroma_db"

    # Slack 관련 필드 추가
    SLACK_WEBHOOK_URL: str | None = None
    SLACK_BOT_TOKEN: str | None = None
    SLACK_CHANNEL: str | None = None
    SLACK_VERIFICATION_TOKEN: str | None = None  # Slack Slash Command 검증 토큰

    # 로그 보관 기간 (일)
    LOG_RETENTION_DAYS: int = 30

    # 스케줄러 설정
    MONITOR_INTERVAL_MINUTES: int = 30  # 서버 모니터링 주기 (분)
    BACKUP_TIME: str = "00:00"  # 백업 실행 시간 (HH:MM)
    BACKUP_RETENTION_DAYS: int = 7  # 백업 보관 기간 (일)


settings = Settings()
