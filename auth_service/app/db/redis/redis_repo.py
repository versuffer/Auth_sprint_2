import uuid

import redis.asyncio as redis

from app.core.config import app_settings


class RedisRepository:
    def __init__(self):
        self.redis = redis.from_url(app_settings.REDIS_DSN)
        self.expire_time: int = max(
            app_settings.JWT_ACCESS_TOKEN_EXPIRE_TIME_SECONDS, app_settings.JWT_REFRESH_TOKEN_EXPIRE_TIME_SECONDS
        )

    @staticmethod
    def _build_session_key(session_id: uuid.UUID) -> str:
        return f'session:{str(session_id)}'

    async def get_session(self, session_id: uuid.UUID) -> str | None:
        session_key = self._build_session_key(session_id)
        return await self.redis.get(session_key)

    async def save_session(self, login: str, session_id: uuid.UUID) -> None:
        session_key = self._build_session_key(session_id)
        await self.redis.set(session_key, login, ex=self.expire_time)

    async def delete_session(self, session_id: uuid.UUID) -> None:
        session_key = self._build_session_key(session_id)
        await self.redis.delete(session_key)


redis_repo = RedisRepository()
