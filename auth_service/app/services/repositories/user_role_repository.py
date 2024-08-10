from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.core.logs import logger
from app.db.postgres.models.users import UserRoleAssociationModel
from app.exceptions import RoleAlreadyAssignedError, RoleNotAssignedError
from app.services.repositories.postgres_repository import (
    PostgresRepository,
    postgres_repository,
)


class UserRoleRepository:
    def __init__(self):
        self.db: PostgresRepository = postgres_repository

    async def assign_user_role(self, user_id: UUID, role_id: UUID) -> None:
        try:
            user_role = UserRoleAssociationModel(user_id=user_id, role_id=role_id)
            await self.db.create_obj(user_role)
        except IntegrityError as err:
            logger.error('user_id=%s already exist role_id=%s. Error=%s', user_id, role_id, err)
            raise RoleAlreadyAssignedError

    async def revoke_user_role(self, user_id: UUID, role_id: UUID) -> None:
        if not await self.db.get_one_obj(
            UserRoleAssociationModel,
            where_value=[(UserRoleAssociationModel.user_id, user_id), (UserRoleAssociationModel.role_id, role_id)],
        ):
            raise RoleNotAssignedError

        await self.db.delete_obj(
            UserRoleAssociationModel,
            where_value=[(UserRoleAssociationModel.user_id, user_id), (UserRoleAssociationModel.role_id, role_id)],
        )


user_role_repository = UserRoleRepository()
