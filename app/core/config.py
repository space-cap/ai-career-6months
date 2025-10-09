from pydantic_settings import BaseSettings  # 변경
# from pydantic import BaseSettings  # 기존 (잘못됨)


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    MYSQL_URL: str = "mysql://root:doolman@localhost:3306/ai_career"
    CHROMA_PATH: str = "./chroma_db"

    class Config:
        env_file = ".env"


settings = Settings()
