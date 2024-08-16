from abc import abstractmethod, ABC


class BaseProvider(ABC):
    NAME: str
    @staticmethod
    @abstractmethod
    def get_auth_url() -> str:
        """Возвращает url для авторизации через соцсети."""

    @staticmethod
    @abstractmethod
    async def get_userdata(code):
        """Возвращает данные пользователя, предоставленные провайдером."""
