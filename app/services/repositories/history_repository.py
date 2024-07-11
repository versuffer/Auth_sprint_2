from app.core.logs import logger
from app.db.postgres.models.users import HistoryModel
from app.schemas.api.v1.auth_schemas import HistorySchemaCreate
from app.schemas.services.repositories.history_repository_schemas import HistoryDBSchema
from app.schemas.services.repositories.user_repository_schemas import UserDBSchema
from app.services.repositories.postgres_repository import (
    PostgresRepository,
    postgres_repository,
)


class HistoryRepository:
    def __init__(self):
        self.db: PostgresRepository = postgres_repository

    async def get(self, user: UserDBSchema, limit: int | None, offset: int | None) -> list[HistoryDBSchema]:
        history = await self.db.get_all_obj(
            HistoryModel, where_value=[(HistoryModel.user_id, user.id)], limit=limit, offset=offset
        )
        return [HistoryDBSchema.model_validate(entry) for entry in history]

    async def create(self, history_data: HistorySchemaCreate) -> None:
        try:
            add_history = HistoryModel(
                user_id=history_data.user_id,
                auth_date=history_data.auth_date,
                user_agent=history_data.user_agent,
                login_type=history_data.login_type,
                session_id=history_data.session_id,
            )
            await self.db.create_obj(add_history)
        except Exception as err:
            logger.error('Oops do not create history %s', err)
            return None


history_repository = HistoryRepository()
