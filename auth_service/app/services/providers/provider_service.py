from app.exceptions import ProviderAuthError
from app.services.providers.base_provider import BaseProvider
from app.services.providers.yandex_provider import YandexProvider


class ProviderService:
    PROVIDERS = {
        'yandex': YandexProvider
    }

    def get_provider(self, provider_name: str) -> BaseProvider:
        provider = self.PROVIDERS.get(provider_name)
        if not provider:
            raise ProviderAuthError(f'Вход через {provider_name} невозможен')
        return provider
