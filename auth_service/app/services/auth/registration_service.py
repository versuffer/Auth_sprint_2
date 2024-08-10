from app.exceptions import UserAlreadyExistsError
from app.schemas.api.v1.auth_schemas import CreateUserCredentialsSchema
from app.schemas.services.auth.user_service_schemas import UserCreateSchema, UserSchema
from app.services.auth.user_service import user_service
from app.services.utils.password_service import password_service


class RegistrationService:
    def __init__(self):
        self.password_service = password_service
        self.user_service = user_service

    async def create_user(self, user_credentials: CreateUserCredentialsSchema) -> UserSchema:
        if await self.user_service.get_user_by_credentials(user_credentials=user_credentials):
            raise UserAlreadyExistsError

        hashed_password = self.password_service.hash_password(user_credentials.password)
        return await self.user_service.create(
            UserCreateSchema(**user_credentials.model_dump(), hashed_password=hashed_password)
        )
