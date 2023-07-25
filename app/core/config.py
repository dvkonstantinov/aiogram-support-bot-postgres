import os
from typing import Optional

from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    GROUP_ID: str
    WEBHOOK_DOMAIN: Optional[str]
    WEBHOOK_PATH: Optional[str]
    APP_HOST: str
    APP_PORT: int
    DATABASE_URL: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str = os.getenv('POSTGRES_USER')
    DB_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
