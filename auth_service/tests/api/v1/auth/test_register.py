import pytest
from fastapi import status
from httpx import AsyncClient

from app.exceptions import user_already_exists_error
from app.main import app
from app.schemas.api.v1.auth_schemas import (
    RegisterResponseSchema,
    RegisterUserCredentialsSchema,
)
from app.services.repositories.user_repository import user_repository


@pytest.mark.anyio
class TestRegister:
    async def test_register_201(self, async_test_client: AsyncClient):
        # Arrange
        user_data = RegisterUserCredentialsSchema(
            username='random_username', email='random@email.com', password='random_password'
        )
        user_data_json = user_data.model_dump(mode='json')

        # Act
        response = await async_test_client.post(app.url_path_for('api_v1_register'), json=user_data_json)
        response_json = response.json()

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response_json == RegisterResponseSchema(**response_json).model_dump(mode='json')
        assert await user_repository.get(user_id=response_json['id'])

    async def test_register_409_username_duplicate(self, async_test_client: AsyncClient):
        # Arrange
        user_data = RegisterUserCredentialsSchema(
            username='random_username', email='random@email.com', password='random_password'
        )
        user_data_json = user_data.model_dump(mode='json')
        await async_test_client.post(app.url_path_for('api_v1_register'), json=user_data_json)
        user_data_json['email'] = 'another@email.com'

        # Act
        response = await async_test_client.post(app.url_path_for('api_v1_register'), json=user_data_json)
        response_json = response.json()

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response_json == {'detail': user_already_exists_error.detail}

    async def test_register_409_email_duplicate(self, async_test_client: AsyncClient):
        # Arrange
        user_data = RegisterUserCredentialsSchema(
            username='random_username', email='random@email.com', password='random_password'
        )
        user_data_json = user_data.model_dump(mode='json')
        await async_test_client.post(app.url_path_for('api_v1_register'), json=user_data_json)
        user_data_json['username'] = 'another_username'

        # Act
        response = await async_test_client.post(app.url_path_for('api_v1_register'), json=user_data_json)
        response_json = response.json()

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response_json == {'detail': user_already_exists_error.detail}
