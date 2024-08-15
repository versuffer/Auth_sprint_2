from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine


def quote(clause: Any):
    """
    Wrap clause into supported by Postgres quotes.
    """
    return '"' + str(clause) + '"'


async def async_database_exists(url: URL) -> bool:
    """
    Асинхронная версия database_exists из sqlalchemy_utils.
    """
    url = make_url(url)
    database = url.database
    sql = "SELECT 1 FROM pg_database WHERE datname='%s'" % database
    for db in (database, 'postgres', 'template1', 'template0', None):
        url = url._replace(database=db)
        try:
            engine = create_async_engine(url.set(database='postgres'))
            async with engine.connect() as conn:
                # Пробуем, можем ли выполнить запрос к базе.
                # Если не можем, следовательно, базы не существует.
                return bool(await conn.scalar(text(sql)))
        except (ProgrammingError, OperationalError):
            pass
    return False


async def async_create_database(url: URL, encoding: str = 'utf8', template: str = 'template1') -> None:
    """
    Асинхронная версия create_database из sqlalchemy_utils.
    """
    url = make_url(url)
    engine = create_async_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT')
    async with engine.begin() as conn:
        sql = f"CREATE DATABASE {quote(url.database)} ENCODING '{encoding}' TEMPLATE {quote(template)}"
        await conn.execute(text(sql))
    await engine.dispose()


async def async_drop_database(url: URL) -> None:
    """
    Асинхронная версия drop_database из sqlalchemy_utils.
    """
    url = make_url(url)
    engine = create_async_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT')
    async with engine.begin() as conn:
        # Disconnect all users from the database we are dropping.
        version = conn.dialect.server_version_info
        pid_column = 'pid' if (version >= (9, 2)) else 'procpid'
        sql = f'''
            SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{url.database}'
            AND {pid_column} <> pg_backend_pid();
            '''
        await conn.execute(text(sql))

        # Drop the database.
        sql = f'DROP DATABASE {quote(url.database)}'
        await conn.execute(text(sql))
