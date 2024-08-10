import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.api.v1.auth_schemas import HistorySchema
from app.schemas.services.auth.role_service_schemas import RoleSchema


class UserDBSchema(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    roles: list[RoleSchema] = []
    history: list[HistorySchema] = []
    id: uuid.UUID
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)
