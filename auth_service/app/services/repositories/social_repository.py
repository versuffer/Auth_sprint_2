from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.models.users import SocialAccount
from app.schemas.services.repositories.social_repository_schema import SocialDBSchema
from app.services.repositories.postgres_repository import (
    PostgresRepository,
    postgres_repository,
)


class SocialRepository:
    def __init__(self):
        self.db: PostgresRepository = postgres_repository

    async def create(
        self, social_data: SocialDBSchema, *, session: AsyncSession | None = None
    ) -> SocialDBSchema | None:
        db_social = await self.db.create_obj(
            SocialAccount(**social_data.model_dump()),
            session=session,
        )
        return db_social

    async def get_user_by_psuid(self, psuid: str, *, session: AsyncSession | None = None) -> SocialDBSchema | None:
        db_social = await self.db.get_one_obj(
            SocialAccount,
            where_value=[(SocialAccount.social_id, psuid)],
            # select_in_load=[SocialAccount.user],
            session=session,
        )
        return SocialDBSchema.model_validate(db_social) if db_social else None


social_repository = SocialRepository()
