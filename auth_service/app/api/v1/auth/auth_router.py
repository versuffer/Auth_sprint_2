from fastapi import APIRouter, Depends, Query, Request, status

from app.api.docs.tags import ApiTags
from app.exceptions import (
    TokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
    WrongPasswordError,
    auth_error,
    user_already_exists_error,
)
from app.schemas.api.v1.auth_schemas import (
    CredentialsLoginDataSchema,
    HistoryResponseSchema,
    LoginType,
    RefreshLoginDataSchema,
    RegisterResponseSchema,
    RegisterUserCredentialsSchema,
    ResetPasswordSchema,
    ResetResponseSchema,
    ResetUsernameSchema,
    TokenPairSchema,
    UserCredentialsSchema,
)
from app.services.auth.auth_service import AuthenticationService
from app.services.auth.registration_service import RegistrationService
from app.services.auth.yandex_provider import YandexProvider
from app.services.fastapi.dependencies import get_bearer_token

from auth_service.app.exceptions import ProviderAuthError
from auth_service.app.services.providers.provider_service import ProviderService

auth_router = APIRouter(prefix='/auth')


@auth_router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    summary='Зарегистрировать пользователя',
    response_model=RegisterResponseSchema,
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_register(
    user_credentials: RegisterUserCredentialsSchema,
    service: RegistrationService = Depends(),
):
    try:
        return await service.create_user(user_credentials)
    except UserAlreadyExistsError:
        raise user_already_exists_error


@auth_router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    summary='Аутентифицировать пользователя по логину и паролю',
    response_model=TokenPairSchema,
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_login(
    user_credentials: UserCredentialsSchema,
    request: Request,
    service: AuthenticationService = Depends(),
):
    login_data = CredentialsLoginDataSchema(
        **user_credentials.model_dump(),
        user_agent=request.headers.get('user-agent', 'user agent not defined'),
        login_type=LoginType.CREDENTIALS,
    )
    try:
        return await service.authenticate_by_credentials(login_data=login_data)
    except (WrongPasswordError, UserNotFoundError):
        raise auth_error


@auth_router.post(
    '/refresh',
    status_code=status.HTTP_200_OK,
    summary='Аутентифицировать пользователя по refresh-токену',
    response_model=TokenPairSchema,
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_refresh(
    request: Request,
    refresh_token: str = Depends(get_bearer_token),
    service: AuthenticationService = Depends(),
):
    login_data = RefreshLoginDataSchema(
        refresh_token=refresh_token,
        user_agent=request.headers.get('user-agent', 'user agent not defined'),
        login_type=LoginType.REFRESH,
    )
    try:
        return await service.authenticate_by_refresh_token(login_data=login_data)
    except (TokenError, UserNotFoundError):
        raise auth_error


@auth_router.post(
    '/logout',
    status_code=status.HTTP_200_OK,
    summary='Удалить сессию пользователя по токену',
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_logout(
    token: str = Depends(get_bearer_token),
    service: AuthenticationService = Depends(),
):
    try:
        await service.logout(token)
    except TokenError:
        raise auth_error

    return {'detail': 'Successful logout'}


@auth_router.post(
    '/verify/access_token',
    status_code=status.HTTP_200_OK,
    summary='Проверить access-токен',
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_verify_access_token(
    access_token: str = Depends(get_bearer_token),
    service: AuthenticationService = Depends(),
):
    try:
        await service.verify_access_token(access_token)
    except TokenError:
        raise auth_error

    return {'detail': 'Successful verification'}


@auth_router.post(
    '/reset/username',
    status_code=status.HTTP_200_OK,
    summary='Поменять имя пользователя',
    response_model=ResetResponseSchema,
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_reset_username(
    reset_schema: ResetUsernameSchema,
    service: AuthenticationService = Depends(),
):
    try:
        return await service.reset_username(reset_schema)
    except (WrongPasswordError, UserNotFoundError):
        raise auth_error
    except UserAlreadyExistsError:
        raise user_already_exists_error


@auth_router.post(
    '/reset/password',
    status_code=status.HTTP_200_OK,
    summary='Поменять пароль пользователя',
    response_model=ResetResponseSchema,
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_reset_password(
    reset_schema: ResetPasswordSchema,
    service: AuthenticationService = Depends(),
):
    try:
        return await service.reset_password(reset_schema)
    except (WrongPasswordError, UserNotFoundError):
        raise auth_error


@auth_router.get(
    '/history',
    status_code=status.HTTP_200_OK,
    summary='Получить историю входов пользователя',
    response_model=list[HistoryResponseSchema],
    tags=[ApiTags.V1_AUTH],
)
async def api_v1_get_history(
    access_token: str = Depends(get_bearer_token),
    service: AuthenticationService = Depends(),
    limit: int = Query(10, description="Максимальное количество записей для возврата"),
    offset: int = Query(0, description="Смещение для пагинации"),
):
    try:
        return await service.get_history(access_token, limit, offset)
    except (TokenError, UserNotFoundError):
        raise auth_error


@auth_router.post(
    '/social_auth/{provider_name}',
    status_code=status.HTTP_200_OK,
    summary='Войти с помощью соцсетей',
    response_model=str,
    tags=["Авторизация"],
)
async def social_auth(provider_name: str, provider_service: ProviderService = Depends()) -> str:
    provider = provider_service.get_provider(provider_name)
    return provider.get_auth_url()


@auth_router.get(
    '/login/social/redirect/{provider_name}',
    response_model=TokenPairSchema,
    status_code=status.HTTP_200_OK,
    summary="Войти с помощью редиректа от соцсетей",
    tags=["Авторизация"],
)
async def social_login_redirect(
    code: int,
    provider_name: str,
    request: Request,
    service: AuthenticationService = Depends(),
    provider_service: ProviderService = Depends(),
):
    user_agent = request.headers.get("User-Agent")
    try:
        provider = provider_service.get_provider(provider_name)
        return await service.login_by_provider(code=code, provider=provider, user_agent=user_agent)
    except ProviderAuthError:
        raise auth_error
