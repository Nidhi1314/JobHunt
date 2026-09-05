from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM
    groq_api_key: str = ""

    # Web Search
    tavily_api_key: str = ""

    # Email
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = ""
    alert_to_email: str = ""

    # Scheduler
    pipeline_schedule_hour: int = 8
    pipeline_schedule_minute: int = 0

    # Observability
    langsmith_api_key: str = ""
    langchain_tracing_v2: bool = False
    langchain_project: str = "jobhunt-ai"

    # App
    app_env: str = "development"
    database_url: str = "sqlite:///./jobhunt.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
