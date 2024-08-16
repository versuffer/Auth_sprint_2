from yandex_oauth import yao

from .base_provider import BaseProvider
from ...core.config import app_settings
from ...utils.yandex_id.yandex_id import YandexID


class YandexProvider(BaseProvider):
    NAME: str = 'yandex'

    @staticmethod
    def get_auth_url():
        return (
            f'{app_settings.YANDEX_BASE_URL}?'
            f'response_type=code&'
            f'redirect_uri={app_settings.YANDEX_REDIRECT_URI}&'
            f'client_id={app_settings.YANDEX_CLIENT_ID}'
        )

    @staticmethod
    async def get_userdata(code):
        token = yao.get_token_by_code(code, app_settings.YANDEX_CLIENT_ID, app_settings.YANDEX_CLIENT_SECRET)
        social_user = YandexID(token.get('access_token'))
        user_data = social_user.get_user_info_json()

        return user_data
