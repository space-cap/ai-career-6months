from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    OPENAI_API_KEY: str
    MYSQL_URL: str = "mysql://root:doolman@localhost:3306/ai_career"
    CHROMA_PATH: str = "./chroma_db"


settings = Settings()
