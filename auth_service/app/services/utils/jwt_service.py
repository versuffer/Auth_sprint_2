from datetime import datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.config import app_settings


class JWTService:
    def __init__(self):
        self.key = app_settings.JWT_SECRET_KEY.get_secret_value()
        self.algorithm = app_settings.JWT_ALGORITHM
        self.access_expire_time = app_settings.JWT_ACCESS_TOKEN_EXPIRE_TIME_SECONDS
        self.refresh_expire_time = app_settings.JWT_REFRESH_TOKEN_EXPIRE_TIME_SECONDS

    def _create_token(self, payload: dict, expire_time: datetime) -> str:
        payload |= {'exp': expire_time}
        return jwt.encode(payload=payload, key=self.key, algorithm=self.algorithm)

    def create_access_token(self, payload: dict, base_expire_time: datetime) -> str:
        return self._create_token(
            payload=payload,
            expire_time=base_expire_time + timedelta(seconds=app_settings.JWT_ACCESS_TOKEN_EXPIRE_TIME_SECONDS),
        )

    def create_refresh_token(self, payload: dict, base_expire_time: datetime) -> str:
        payload |= {'refresh': True}
        return self._create_token(
            payload=payload,
            expire_time=base_expire_time + timedelta(seconds=app_settings.JWT_REFRESH_TOKEN_EXPIRE_TIME_SECONDS),
        )

    def get_token_payload(self, token: str, verify_exp: bool = True) -> dict:
        try:
            return jwt.decode(
                jwt=token,
                key=self.key,
                algorithms=[self.algorithm],
                require=['exp'],
                options={'verify_exp': verify_exp},
            )
        except InvalidTokenError as err:
            raise err


jwt_service = JWTService()
