import uuid

from app.exceptions import (
    RoleAlreadyAssignedError,
    RoleAlreadyExistsError,
    RoleNotAssignedError,
    RoleNotFoundError,
    UserNotFoundError,
)
from app.schemas.services.auth.role_service_schemas import (
    CreateRoleSchema,
    PartialUpdateRoleSchema,
    RoleSchema,
)
from app.services.repositories.role_repository import role_repository
from app.services.repositories.user_repository import user_repository
from app.services.repositories.user_role_repository import user_role_repository


class RoleService:
    def __init__(self):
        self.role_repository = role_repository

    async def get_roles(self) -> list[RoleSchema]:
        return [RoleSchema.validate(role) for role in await self.role_repository.get_all()]

    async def get_role(self, role_id: uuid.UUID) -> RoleSchema:
        if not (role := await self.role_repository.get(role_id)):
            raise RoleNotFoundError

        return role

    async def create_role(self, role_data: CreateRoleSchema) -> RoleSchema:
        if await self.role_repository.get_by_title(role_title=role_data.title):
            raise RoleAlreadyExistsError

        return await self.role_repository.create(role_data)

    async def partially_update_role(self, role_id: uuid.UUID, role_data: PartialUpdateRoleSchema) -> RoleSchema:
        if not await self.role_repository.get(role_id=role_id):
            raise RoleNotFoundError

        if (role := await self.role_repository.get_by_title(role_title=role_data.title)) and role.id != role_id:
            raise RoleAlreadyExistsError

        return await self.role_repository.update(role_id=role_id, data=role_data.model_dump(exclude_unset=True))

    async def delete_role(self, role_id: uuid.UUID) -> bool:
        if not await self.role_repository.get(role_id):
            raise RoleNotFoundError

        return await self.role_repository.delete(role_id)


class UserRoleService:
    def __init__(self):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.user_role_repository = user_role_repository

    async def get_user_roles(self, user_id: uuid.UUID) -> list[RoleSchema]:
        if not (user := await self.user_repository.get(user_id)):
            raise UserNotFoundError
        return [RoleSchema.model_validate(role) for role in user.roles]

    async def assign_user_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        if not await self.user_repository.get(user_id):
            raise UserNotFoundError
        if not await self.role_repository.get(role_id):
            raise RoleNotFoundError

        try:
            await self.user_role_repository.assign_user_role(user_id, role_id)
        except RoleAlreadyAssignedError as err:
            raise err

    async def revoke_user_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        if not await self.user_repository.get(user_id):
            raise UserNotFoundError
        if not await self.role_repository.get(role_id):
            raise RoleNotFoundError

        try:
            await self.user_role_repository.revoke_user_role(user_id, role_id)
        except RoleNotAssignedError as err:
            raise err
