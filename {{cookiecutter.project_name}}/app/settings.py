import functools

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_prefix = ''

    app_version: str = '0.0.1'

    # database configuration
    database_url: str = 'postgresql+asyncpg://admin:admin@localhost/admin'
    db_pool_pre_ping: bool = True
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = True
    debug: bool = False


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()
