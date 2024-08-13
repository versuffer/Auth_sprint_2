from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.config import BASEDIR, app_settings
from app.db.postgres.models.base import Base
from app.main import app as fastapi_app
from tests.utils import (
    async_create_database,
    async_database_exists,
    async_drop_database,
)


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session', autouse=True)
def _check_environment() -> None:
    """
    У нас установлен плагин pytest-env, который подменяет продовые энвы при старте pytest-сессии на тестовые.
    Тестовые энвы прописываются в pyproject.toml [tool.pytest_env]. Этой фикстурой мы проверяем, заменились
    ли продовые переменные на тестовые. Фикстура нужна в качестве перестраховки от прогонки тестов на проде.
    """

    # Проверяем, что база тестовая
    assert 'test_' in app_settings.POSTGRES_DB

    # Проверяем, что это именно нужная тестовая база, а не тестовая база другого проекта
    assert 'auth_database' in app_settings.POSTGRES_DB

    # Проверяем, что выбрана тестовая база Редиса
    assert app_settings.REDIS_DB == '15'


@pytest.fixture(scope='session')
def randomized_postgres_dsn(_check_environment: None) -> str:
    return app_settings.POSTGRES_DSN + '_' + str(uuid4())  # type: ignore


@pytest.fixture(scope='session')
async def _manage_test_database(randomized_postgres_dsn: str) -> AsyncGenerator[None, None]:
    """
    Фикстура создаёт/пересоздаёт тестовую базу при старте сессии пайтеста и удаляет её при окончании сессии.

    Это необходимо для того, чтобы максимально изолировать прогон тестов от реальных данных.
    Прогоняем тесты на тестовой базе, а потом стираем её, чтобы никак не влиять на продовую базу.

    Фикстура запускается один раз.
    """
    url: URL = randomized_postgres_dsn  # type: ignore

    # Setup
    if await async_database_exists(url=url):
        await async_drop_database(url=url)

    await async_create_database(url=url)

    yield

    # Teardown
    await async_drop_database(url=url)


@pytest.fixture(scope='session')
def _manage_migrations(_manage_test_database, randomized_postgres_dsn: str) -> None:
    """
    Фикстура накатывает миграции для теста и откатывает их после его выполнения, чтобы очистить базу.

    Фикстура намеренно сделала синхронной, так как Алембик при запуске команд запускает собственный
    событийный цикл, чего нельзя делать из уже запущенного событийного цикла.
    """
    app_settings.POSTGRES_DSN = randomized_postgres_dsn
    config = Config(BASEDIR / 'alembic.ini')
    command.upgrade(config, 'head')


@pytest.fixture
async def async_test_engine(mocker: MockerFixture, randomized_postgres_dsn: str) -> AsyncGenerator[AsyncEngine, None]:
    # Setup
    test_engine = create_async_engine(
        url=randomized_postgres_dsn,  # type: ignore
        pool_pre_ping=True,
    )
    mocker.patch('app.db.postgres.base.async_engine', test_engine)

    yield test_engine

    # Teardown
    await test_engine.dispose()


@pytest.fixture
async def _manage_tables(_manage_migrations: None, async_test_engine: AsyncEngine) -> Generator[None, None, None]:
    yield
    async with async_test_engine.begin() as conn:
        await conn.execute(
            text(
                'TRUNCATE {} CASCADE;'.format(
                    ', '.join(f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables))
                )
            )
        )


@pytest.fixture
async def async_test_session(
    _manage_tables: None, async_test_engine: AsyncEngine
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=async_test_engine) as session:
        yield session


@pytest.fixture
async def async_test_client(_manage_tables: None) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=fastapi_app, base_url='http://test') as app:
        yield app
