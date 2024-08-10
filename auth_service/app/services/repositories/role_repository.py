from typing import Sequence
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.logs import logger
from app.db.postgres.models.users import RoleModel, UserRoleAssociationModel
from app.exceptions import RoleAlreadyExistsError
from app.schemas.services.auth.role_service_schemas import CreateRoleSchema, RoleSchema
from app.services.repositories.postgres_repository import (
    PostgresRepository,
    postgres_repository,
)


class RoleRepository:
    def __init__(self):
        self.db: PostgresRepository = postgres_repository

    async def get_all(self) -> Sequence[RoleSchema]:
        db_roles = await self.db.get_all_obj(RoleModel)
        return [RoleSchema.model_validate(db_role) for db_role in db_roles]

    async def get(self, role_id: UUID) -> RoleSchema | None:
        db_role = await self.db.get_one_obj(RoleModel, where_value=[(RoleModel.id, role_id)])
        return RoleSchema.model_validate(db_role) if db_role else None

    async def get_by_title(self, role_title: str) -> RoleSchema | None:
        db_role = await self.db.get_one_obj(RoleModel, where_value=[(RoleModel.title, role_title)])
        return RoleSchema.model_validate(db_role) if db_role else None

    async def create(self, role_data: CreateRoleSchema) -> RoleSchema | None:
        role = RoleModel(title=role_data.title, description=role_data.description)
        await self.db.create_obj(role)
        return await self.get(role.id)

    async def update(self, role_id: UUID, data: dict) -> RoleSchema | None:
        try:
            await self.db.update_obj(RoleModel, where_value=[(RoleModel.id, role_id)], update_values=data)
            return await self.get(role_id)
        except IntegrityError:
            logger.error(RoleAlreadyExistsError('Role already exist'))
            return None

    async def delete(self, role_id: UUID) -> bool:
        try:
            # Удалю связи
            await self.db.delete_obj(
                UserRoleAssociationModel, where_value=[(UserRoleAssociationModel.role_id, role_id)]
            )

            # Удаляю роль
            await self.db.delete_obj(RoleModel, where_value=[(RoleModel.id, role_id)])
            return True
        except Exception as err:
            logger.error('Can not delete role_id=%s error=%s', role_id, err)
            return False


role_repository = RoleRepository()
