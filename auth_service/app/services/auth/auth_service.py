import datetime
import uuid

from app.exceptions import (
    AuthorizationError,
    TokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
    WrongPasswordError,
)
from app.schemas.api.v1.auth_schemas import (
    CredentialsLoginDataSchema,
    HistorySchema,
    HistorySchemaCreate,
    RefreshLoginDataSchema,
    ResetPasswordSchema,
    ResetUsernameSchema,
    SessionDataSchema,
    TokenPairSchema,
    UserTokenDataSchema,
)
from app.schemas.services.auth.user_service_schemas import UserSchema
from app.schemas.services.repositories.user_repository_schemas import UserDBSchema
from app.services.auth.session_service import session_service
from app.services.auth.user_service import user_service
from app.services.utils.password_service import password_service


class AuthenticationService:
    def __init__(self):
        self.password_service = password_service
        self.user_service = user_service
        self.session_service = session_service

    def _verify_user_password(self, user: UserDBSchema, password: str):
        if not self.password_service.verify_password(user.hashed_password, password):
            raise WrongPasswordError

    async def _create_session(self, user: UserDBSchema) -> SessionDataSchema:
        return await self.session_service.create_session(UserTokenDataSchema(login=user.email, roles=user.roles))

    async def _save_user_login_history(
        self, user: UserDBSchema, login_data: CredentialsLoginDataSchema | RefreshLoginDataSchema, session_id: uuid.UUID
    ):
        await self.user_service.save_login_history(
            HistorySchemaCreate(
                user_id=user.id,
                auth_date=datetime.datetime.utcnow(),
                user_agent=login_data.user_agent,
                login_type=login_data.login_type,
                session_id=session_id,
            )
        )  # TODO сделать фоновой таской

    async def authenticate_by_credentials(self, login_data: CredentialsLoginDataSchema) -> TokenPairSchema:
        try:
            user = await self.user_service.get_user(login=login_data.login)
            self._verify_user_password(user=user, password=login_data.password)
            session_data = await self._create_session(user=user)
            await self._save_user_login_history(user=user, login_data=login_data, session_id=session_data.session_id)
            return TokenPairSchema(**session_data.model_dump())
        except (UserNotFoundError, WrongPasswordError) as err:
            raise err

    async def authenticate_by_refresh_token(self, login_data: RefreshLoginDataSchema) -> TokenPairSchema:
        try:
            login = await self.session_service.get_login_from_refresh_token(refresh_token=login_data.refresh_token)
            user = await self.user_service.get_user(login=login)
            session_data = await self._create_session(user=user)
            await self.session_service.delete_session(token=login_data.refresh_token)
            await self._save_user_login_history(user=user, login_data=login_data, session_id=session_data.session_id)
            return TokenPairSchema(**session_data.model_dump())
        except (TokenError, UserNotFoundError) as err:
            raise err

    async def logout(self, token: str) -> None:
        try:
            await self.session_service.delete_session(token)
        except TokenError as err:
            raise err

    async def verify_access_token(self, access_token: str) -> bool:
        try:
            return self.session_service.verify_access_token(access_token)
        except TokenError as err:
            raise err

    async def get_history(self, access_token: str, limit: int, offset: int) -> list[HistorySchema]:
        try:
            login = await self.session_service.get_login_from_access_token(access_token)
            user = await self.user_service.get_user(login)
            return await self.user_service.get_history(user, limit, offset)
        except (TokenError, UserNotFoundError) as err:
            raise err

    async def reset_username(self, reset_schema: ResetUsernameSchema) -> UserSchema:
        try:
            user = await self.user_service.get_user(login=reset_schema.login)
            self._verify_user_password(user=user, password=reset_schema.password)
            return await self.user_service.set_username(user.id, reset_schema.new_username)
        except (UserNotFoundError, WrongPasswordError, UserAlreadyExistsError) as err:
            raise err

    async def reset_password(self, reset_schema: ResetPasswordSchema) -> UserSchema:
        try:
            user = await self.user_service.get_user(login=reset_schema.login)
            self._verify_user_password(user=user, password=reset_schema.password)
            new_hashed_password = self.password_service.hash_password(reset_schema.new_password)
            return await self.user_service.set_password(user.id, new_hashed_password)
        except (UserNotFoundError, WrongPasswordError) as err:
            raise err

    async def authorize_superuser(self, access_token: str) -> None:
        try:
            login = await self.session_service.get_login_from_access_token(access_token=access_token)
            user = await self.user_service.get_user(login=login)
        except (TokenError, UserNotFoundError) as err:
            raise err

        if not user.is_superuser:
            raise AuthorizationError
