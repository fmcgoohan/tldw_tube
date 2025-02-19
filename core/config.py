# tldw_tube/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: str
    proxy_url: Optional[str] = None
    cache_dir: str = './cache'  # Still used for temporary files
    log_level: str = 'INFO'
    rate_limit_count: int = 5
    rate_limit_period: int = 60

    # Database settings
    db_user: str = "user"  # Default values - replace in .env
    db_password: str = "password"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "tldw_tube_db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()
