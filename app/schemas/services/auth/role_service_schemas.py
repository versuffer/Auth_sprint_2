import uuid

from pydantic import BaseModel, ConfigDict, Field


class RoleSchemaBase(BaseModel):
    title: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class CreateRoleSchema(RoleSchemaBase):
    pass


class PartialUpdateRoleSchema(BaseModel):
    title: str = Field(default='')
    description: str | None = Field(default=None)


class RoleSchema(RoleSchemaBase):
    id: uuid.UUID
