import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from requests import RequestException

from users.exceptions import AuthenticationServiceError

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = f'http://{settings.AUTH_API_BASE_URL}:{settings.AUTH_API_PORT}/api/v1/auth/login'
        http_user_agent = request.META.get('HTTP_USER_AGENT')
        headers = {'user-agent': http_user_agent}
        payload = {'login': username, 'password': password}

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
        except RequestException as e:
            raise AuthenticationServiceError(f"Error during request to {url}: {str(e)}")

        try:
            user, created = User.objects.get_or_create(email=username)
        except Exception as e:
            raise AuthenticationServiceError(f"Error during user creation or retrieval: {str(e)}")

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
