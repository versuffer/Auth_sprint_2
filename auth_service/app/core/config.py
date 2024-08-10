from pathlib import Path
from typing import Annotated

from pydantic import PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

BASEDIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App
    APP_TITLE: str = 'Auth Sprint 1'
    APP_DESCRIPTION: str = 'Default description'
    DEBUG: bool = False
    LOG_LEVEL: str = 'INFO'

    # Auth
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_TIME_SECONDS: int = 60 * 60  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRE_TIME_SECONDS: int = 86400 * 30  # 30 days

    # Postgres
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_DSN: PostgresDsn | str = ''

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: str
    REDIS_DSN: RedisDsn | str = ''

    model_config = SettingsConfigDict(env_file=BASEDIR / '.env')

    @field_validator('POSTGRES_DSN')
    def build_postgres_dsn(cls, value: PostgresDsn | None, info: ValidationInfo) -> Annotated[str, PostgresDsn]:
        if not value:
            value = PostgresDsn.build(
                scheme='postgresql+asyncpg',
                username=info.data['POSTGRES_USER'],
                password=info.data['POSTGRES_PASSWORD'].get_secret_value(),
                host=info.data['POSTGRES_HOST'],
                port=info.data['POSTGRES_PORT'],
                path=f"{info.data['POSTGRES_DB'] or ''}",
            )
        return str(value)

    @field_validator('REDIS_DSN')
    def build_redis_dsn(cls, value: RedisDsn | None, info: ValidationInfo) -> Annotated[str, RedisDsn]:
        if not value:
            value = RedisDsn.build(
                scheme='redis',
                host=info.data['REDIS_HOST'],
                port=info.data['REDIS_PORT'],
                path=f"{info.data['REDIS_DB'] or ''}",
            )
        return str(value)


app_settings = Settings()
