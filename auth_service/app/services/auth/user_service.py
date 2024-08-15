import uuid

from app.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.schemas.api.v1.auth_schemas import (
    CreateUserCredentialsSchema,
    HistorySchema,
    HistorySchemaCreate,
)
from app.schemas.services.auth.user_service_schemas import UserCreateSchema, UserSchema
from app.schemas.services.repositories.social_repository_schema import SocialDBSchema
from app.schemas.services.repositories.user_repository_schemas import UserDBSchema
from app.services.repositories.history_repository import history_repository
from app.services.repositories.social_repository import social_repository
from app.services.repositories.user_repository import user_repository
from app.utils.pass_generator import generate_random_string
from app.utils.yandex_id.yandex_id_schema import User as YandexUser


class UserService:
    def __init__(self):
        self.user_repository = user_repository
        self.history_repository = history_repository
        self.social_repository = social_repository

    async def create(self, user_data: UserCreateSchema) -> UserSchema:
        try:
            user = await self.user_repository.create(user_data)
            return UserSchema.model_validate(user)
        except UserAlreadyExistsError as err:
            raise err

    async def get_user(self, login: str) -> UserDBSchema:
        if not (user := await self.user_repository.get_user_by_login(login)):
            raise UserNotFoundError

        return user

    async def get_user_by_credentials(self, user_credentials: CreateUserCredentialsSchema) -> UserDBSchema | None:
        return await self.user_repository.get_user_by_credentials(
            email=user_credentials.email, username=user_credentials.username
        )

    async def save_login_history(self, history_data: HistorySchemaCreate) -> None:
        await self.history_repository.create(history_data)

    async def get_history(self, user: UserDBSchema, limit: int, offset: int) -> list[HistorySchema]:
        return [HistorySchema.model_validate(entry) for entry in await self.history_repository.get(user, limit, offset)]

    async def set_username(self, user_id: uuid.UUID, new_username: str) -> UserSchema:
        if await self.user_repository.get_user_by_login(login=new_username):
            raise UserAlreadyExistsError

        user = await self.user_repository.update(user_id, {'username': new_username})
        return UserSchema.model_validate(user)

    async def set_password(self, user_id: uuid.UUID, new_password: str) -> UserSchema:
        user = await self.user_repository.update(user_id, {'hashed_password': new_password})
        return UserSchema.model_validate(user)

    async def get_or_create_user_by_yandex(self, ya_user: YandexUser) -> UserDBSchema:

        social: SocialDBSchema = await self.social_repository.get_user_by_psuid(
            psuid=ya_user.psuid,
        )

        try:
            user: UserDBSchema = await self.get_user(login=ya_user.default_email)
        except UserNotFoundError:
            user_data: UserCreateSchema = UserCreateSchema(
                username=ya_user.login, email=ya_user.default_email, hashed_password=generate_random_string()
            )
            user = await self.user_repository.create(user_data)

        if social and user:
            return user

        if not social:
            social_data: SocialDBSchema = SocialDBSchema(user_id=user.id, social_id=ya_user.psuid, social_name='yandex')
            await self.social_repository.create(social_data=social_data)

        return user


user_service = UserService()
