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


settings = Settings()
