"""
Информация по модулю содержится в README.md
"""

import asyncio

import typer
from pydantic import EmailStr, validate_email
from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.base import async_engine
from app.db.postgres.models.users import UserModel
from app.exceptions import UserAlreadyExistsError
from app.schemas.api.v1.auth_schemas import CreateUserCredentialsSchema
from app.services.auth.registration_service import RegistrationService
from app.services.repositories.user_repository import user_repository

cli_app = typer.Typer()


def _get_valid_email(value: str) -> EmailStr:
    return validate_email(value)[1]


@cli_app.command()
def list_users():
    asyncio.run(_list_users())


@cli_app.command()
def create_user():
    asyncio.run(_create_user())


async def _list_users():
    async with AsyncSession(bind=async_engine) as session:
        console = Console()
        user_table = Table('', 'id', 'username', 'email', 'is_superuser')
        users = (await session.execute(select(UserModel))).scalars().all()
        for num, user in enumerate(users, start=1):
            user_table.add_row(
                str(num),
                str(user.id),
                user.username,
                user.email,
                str(user.is_superuser),
            )
        console.print(user_table)


async def _create_user():

    registration_service = RegistrationService()
    user_credentials = CreateUserCredentialsSchema(
        username=typer.prompt('username'),
        email=_get_valid_email(typer.prompt('email')),
        password=typer.prompt('password', hide_input=True),
    )
    is_superuser = typer.confirm('is_superuser')
    try:
        user = await registration_service.create_user(user_credentials=user_credentials)
        await user_repository.update(user_id=user.id, data={'is_superuser': is_superuser})
        print(f'User {user.username=}, {user.email=}, {is_superuser=} successfully created.')
    except UserAlreadyExistsError:
        print('User already exists.')


if __name__ == '__main__':
    cli_app()
