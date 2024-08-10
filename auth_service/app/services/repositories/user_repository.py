from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.models.users import UserModel
from app.schemas.services.auth.user_service_schemas import UserCreateSchema
from app.schemas.services.repositories.user_repository_schemas import UserDBSchema
from app.services.repositories.postgres_repository import (
    PostgresRepository,
    postgres_repository,
)


class UserRepository:
    def __init__(self):
        self.db: PostgresRepository = postgres_repository

    async def get_user_by_login(self, login: str) -> UserDBSchema | None:
        user = None
        try:
            validate_email(login)
            user = await self._get_user_by_email(login)
        except EmailNotValidError:
            pass

        return user or await self._get_user_by_username(login)

    async def get_user_by_credentials(self, email: EmailStr, username: str) -> UserDBSchema | None:
        if user := await self._get_user_by_email(email=email):
            return user
        if user := await self._get_user_by_username(username=username):
            return user

        return None

    async def _get_user_by_email(self, email: EmailStr, *, session: AsyncSession | None = None) -> UserDBSchema | None:
        db_user = await self.db.get_one_obj(
            UserModel,
            where_value=[(UserModel.email, email)],
            select_in_load=[UserModel.roles, UserModel.history],
            session=session,
        )
        return UserDBSchema.model_validate(db_user) if db_user else None

    async def _get_user_by_username(self, username: str, *, session: AsyncSession | None = None) -> UserDBSchema | None:
        db_user = await self.db.get_one_obj(
            UserModel,
            where_value=[(UserModel.username, username)],
            select_in_load=[UserModel.roles, UserModel.history],
            session=session,
        )
        return UserDBSchema.model_validate(db_user) if db_user else None

    async def get(self, user_id: UUID) -> UserDBSchema | None:
        db_user = await self.db.get_one_obj(
            UserModel,
            where_value=[(UserModel.id, user_id)],
            select_in_load=[UserModel.roles, UserModel.history],
        )
        return UserDBSchema.model_validate(db_user) if db_user else None

    async def create(self, user_data: UserCreateSchema) -> UserDBSchema:
        user_model = UserModel(**user_data.model_dump())
        await self.db.create_obj(user_model)
        return await self.get(user_model.id)

    async def update(self, user_id: UUID, data: dict) -> UserDBSchema | None:
        await self.db.update_obj(UserModel, where_value=[(UserModel.id, user_id)], update_values=data)
        return await self.get(user_id)


user_repository = UserRepository()
