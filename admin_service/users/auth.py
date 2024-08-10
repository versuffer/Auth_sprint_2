import http
import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

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

        print(payload)
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(response.status_code)
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()
        print(data)

        try:
            user, created = User.objects.get_or_create(email=username)

            print(user)
            print(created)
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
