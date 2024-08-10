import functools

from app.exceptions import AuthorizationError, TokenError, UserNotFoundError, auth_error


def handle_auth_superuser_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (TokenError, UserNotFoundError, AuthorizationError):
            raise auth_error

    return wrapper
