from fastapi import Request

from app.exceptions import auth_error


def get_bearer_token(request: Request) -> str:
    if not (token_str := request.headers.get('Authorization')):
        raise auth_error
    try:
        prefix, token = token_str.split(' ')
    except ValueError:
        raise auth_error

    if not prefix == 'Bearer':
        raise auth_error

    return token
