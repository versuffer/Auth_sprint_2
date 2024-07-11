import datetime
import uuid
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.services.auth.role_service_schemas import RoleSchemaBase
from app.schemas.services.auth.user_service_schemas import UserSchema


class LoginType(StrEnum):
    CREDENTIALS = 'credentials'
    REFRESH = 'refresh'


class UserCredentialsSchema(BaseModel):
    login: str
    password: str


class CreateUserCredentialsSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class RegisterUserCredentialsSchema(CreateUserCredentialsSchema):
    pass


class BaseLoginDataSchema(BaseModel):
    user_agent: str
    login_type: LoginType


class CredentialsLoginDataSchema(BaseLoginDataSchema, UserCredentialsSchema):
    pass


class RefreshLoginDataSchema(BaseLoginDataSchema):
    refresh_token: str


class UserTokenDataSchema(BaseModel):
    login: str
    roles: list[RoleSchemaBase]


class TokenPairSchema(BaseModel):
    access_token: str
    refresh_token: str


class SessionDataSchema(TokenPairSchema):
    session_id: uuid.UUID


class ResetUsernameSchema(UserCredentialsSchema):
    new_username: str


class ResetResponseSchema(UserSchema):
    pass


class ResetPasswordSchema(UserCredentialsSchema):
    new_password: str


class RegisterResponseSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr


class HistorySchemaCreate(BaseModel):
    user_id: uuid.UUID
    auth_date: datetime.datetime
    user_agent: str
    login_type: LoginType
    session_id: uuid.UUID


class HistorySchema(BaseModel):
    id: uuid.UUID
    auth_date: datetime.datetime
    user_agent: str

    model_config = ConfigDict(from_attributes=True)


class HistoryResponseSchema(HistorySchema):
    pass
