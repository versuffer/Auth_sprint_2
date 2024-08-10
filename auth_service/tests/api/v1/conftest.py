import pytest

from app.schemas.api.v1.auth_schemas import CreateUserCredentialsSchema
from app.schemas.services.auth.user_service_schemas import UserSchema
from app.services.auth.registration_service import RegistrationService


@pytest.fixture
async def test_user_data() -> dict:
    return {'username': 'test_user', 'email': 'test@mail.ru', 'password': 'random_password', 'is_superuser': False}


@pytest.fixture
async def registered_user(test_user_data: dict) -> UserSchema:
    test_user_credentials = CreateUserCredentialsSchema(**test_user_data)
    return await RegistrationService().create_user(test_user_credentials)
