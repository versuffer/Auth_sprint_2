from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.services.auth.role_service_schemas import RoleSchema


class UserSchema(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_superuser: bool
    roles: list[RoleSchema]

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
