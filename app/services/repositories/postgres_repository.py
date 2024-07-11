from typing import Any, Union

from sqlalchemy import Column, and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.postgres.base import manage_async_session


class PostgresRepository:
    @staticmethod
    def _build_query(
        model,
        action: Union[select, delete, update] = select,
        where_value: list[tuple[Column, Any]] | None = None,
        select_in_load: Column | None = None,
        update_values: dict | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        query = action(model)
        if where_value and len(where_value) == 1:
            _column, _value = where_value[0]
            query = query.where(_column == _value)
        if where_value and len(where_value) > 1:
            query = query.where(and_(_column == _value for _column, _value in where_value))
        if select_in_load:
            query = query.options(*[selectinload(column) for column in select_in_load])
        if action == update:
            query = query.values(**update_values)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        return query

    @manage_async_session
    async def get_one_obj(self, model, *, session: AsyncSession | None = None, limit=None, offset=None, **kwargs):
        query = self._build_query(model, limit=limit, offset=offset, **kwargs)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @manage_async_session
    async def get_all_obj(self, model, *, session: AsyncSession | None = None, **kwargs):
        query = self._build_query(model, **kwargs)
        result = await session.execute(query)
        return result.scalars().all()

    @manage_async_session
    async def create_obj(self, obj, *, session: AsyncSession | None = None) -> None:
        session.add(obj)

    @manage_async_session
    async def update_obj(self, model, *, session: AsyncSession | None = None, **kwargs) -> None:
        query = self._build_query(model, action=update, **kwargs)
        await session.execute(query)

    @manage_async_session
    async def delete_obj(self, model, *, session: AsyncSession | None = None, **kwargs) -> None:
        query = self._build_query(model, action=delete, **kwargs)
        await session.execute(query)


postgres_repository = PostgresRepository()
