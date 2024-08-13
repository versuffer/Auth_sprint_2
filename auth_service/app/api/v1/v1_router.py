from fastapi import APIRouter

from app.api.v1.auth.auth_router import auth_router
from app.api.v1.roles.roles_router import roles_router
from app.api.v1.users.users_router import users_router

v1_router = APIRouter(prefix='/v1')

v1_router.include_router(auth_router)
v1_router.include_router(roles_router)
v1_router.include_router(users_router)
