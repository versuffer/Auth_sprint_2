from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from app.db.postgres.models.base import Base, text


class UserModel(Base):
    __tablename__ = 'users'

    username: Mapped[text] = mapped_column(nullable=False, unique=True)
    email: Mapped[text] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[text] = mapped_column(nullable=False)
    is_superuser: Mapped[bool] = mapped_column(nullable=False, server_default=expression.false())

    # one-to-many
    history: Mapped[list['HistoryModel']] = relationship(
        back_populates='user',
        cascade="all, delete",
        passive_deletes=True,
    )

    # many-to-many
    roles: Mapped[list['RoleModel']] = relationship(
        secondary='user_role_associations',
        back_populates='users',
        cascade="all, delete",
    )


class RoleModel(Base):
    __tablename__ = 'roles'

    title: Mapped[text] = mapped_column(nullable=False, unique=True)
    description: Mapped[text | None] = mapped_column(nullable=True)

    # many-to-many
    users: Mapped[list['UserModel']] = relationship(
        secondary='user_role_associations',
        back_populates='roles',
        passive_deletes=True,
    )


class HistoryModel(Base):
    __tablename__ = 'history'

    user_agent: Mapped[text] = mapped_column(nullable=False)
    login_type: Mapped[text] = mapped_column(nullable=False)  # Login by credentials or refresh-token
    session_id: Mapped[UUID] = mapped_column(nullable=False)
    auth_date: Mapped[datetime] = mapped_column(nullable=False)

    # many-to-one
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user: Mapped[UserModel] = relationship(back_populates='history')


class UserRoleAssociationModel(Base):
    __tablename__ = 'user_role_associations'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id: Mapped[UUID] = mapped_column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='user_role_association_unique'),)
