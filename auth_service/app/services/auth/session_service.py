import uuid
from datetime import datetime

from jwt import InvalidTokenError

from app.db.redis.redis_repo import redis_repo
from app.exceptions import (
    AccessTokenValidationError,
    ExpiredSessionError,
    RefreshTokenValidationError,
    TokenDoesNotContainLogin,
    TokenDoesNotContainSessionId,
    TokenError,
    TokenValidationError,
)
from app.schemas.api.v1.auth_schemas import SessionDataSchema, UserTokenDataSchema
from app.services.utils.jwt_service import jwt_service


class SessionService:
    def __init__(self):
        self.jwt_service = jwt_service
        self.redis_repo = redis_repo

    async def create_session(self, user_token_data: UserTokenDataSchema) -> SessionDataSchema:
        user_login = user_token_data.login
        session_id = uuid.uuid4()
        base_expire_time = datetime.utcnow()
        base_token_payload = {'session_id': str(session_id)}

        access_token_payload = user_token_data.model_dump()
        access_token_payload |= base_token_payload
        access_token = self.jwt_service.create_access_token(
            payload=access_token_payload, base_expire_time=base_expire_time
        )

        refresh_token_payload = {'login': user_login}
        refresh_token_payload |= base_token_payload
        refresh_token = self.jwt_service.create_refresh_token(
            payload=refresh_token_payload, base_expire_time=base_expire_time
        )

        await self.redis_repo.save_session(user_login, session_id=session_id)
        return SessionDataSchema(access_token=access_token, refresh_token=refresh_token, session_id=session_id)

    async def get_validated_token_payload(
        self,
        token: str,
        check_expired: bool = True,
        check_access: bool = False,
        check_refresh: bool = False,
        check_session_id: bool = True,
        check_session_expired: bool = False,
        check_login: bool = True,
    ) -> dict:
        try:
            token_payload = self.jwt_service.get_token_payload(token=token, verify_exp=check_expired)
        except InvalidTokenError:
            raise TokenValidationError

        if check_access and 'refresh' in token_payload:
            raise AccessTokenValidationError

        if check_refresh and not token_payload.get('refresh') is True:
            raise RefreshTokenValidationError

        if check_session_id:
            if not (session_id := token_payload.get('session_id')):
                raise TokenDoesNotContainSessionId

            if check_session_expired and not await self.redis_repo.get_session(session_id):
                raise ExpiredSessionError

        if check_login and not token_payload.get('login'):
            raise TokenDoesNotContainLogin

        return token_payload

    async def get_login_from_refresh_token(self, refresh_token: str) -> str:
        try:
            token_payload = await self.get_validated_token_payload(token=refresh_token, check_refresh=True)
            return token_payload['login']
        except TokenError as err:
            raise err

    async def get_login_from_access_token(self, access_token: str) -> str | None:
        try:
            token_payload = await self.get_validated_token_payload(token=access_token, check_access=True)
            return token_payload['login']
        except TokenError as err:
            raise err

    async def verify_access_token(self, access_token: str) -> None:
        try:
            await self.get_validated_token_payload(token=access_token, check_access=True)
        except TokenError as err:
            raise err

    async def delete_session(self, token: str) -> None:
        try:
            token_payload = await self.get_validated_token_payload(
                token=token, check_expired=False, check_session_id=True, check_session_expired=True
            )
        except TokenError as err:
            raise err

        await self.redis_repo.delete_session(token_payload['session_id'])


session_service = SessionService()
