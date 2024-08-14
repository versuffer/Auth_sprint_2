import datetime
from pprint import pformat

import redis
import uvicorn
from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api.api_router import api_router
from app.core.config import app_settings
from app.core.logs import logger
from app.utils.jaeger import configure_tracer

if app_settings.JAEGER_ENABLE:
    configure_tracer(app_settings.JAEGER_HOST, app_settings.JAEGER_PORT)

app = FastAPI(
    title=app_settings.APP_TITLE,
    description=app_settings.APP_DESCRIPTION,
    version='1.0.0',
    debug=app_settings.DEBUG,
    docs_url='/',
)

app.include_router(api_router)

redis_conn = redis.Redis(host='localhost', port=6379, decode_responses=True)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Ограничение запросов от одного пользователя."""

    client_ip = request.headers.get("X-Forwarded-For", 'client ip not defined')
    request_id = request.headers.get('X-Request-Id', 'request id not defined')

    if not client_ip:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Missing Access Identifier"}
        )

    pipe = redis_conn.pipeline()
    now = datetime.datetime.now()
    key = f'{client_ip}:{now.minute}'

    pipe.incr(key, 1)
    pipe.expire(key, 59)
    result = pipe.execute()

    request_number = result[0]
    if request_number > app_settings.REQUEST_LIMIT_PER_MINUTE:
        return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Too Many Requests"})

    response = await call_next(request)

    if not request_id:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'}
        )

    return response


if __name__ == '__main__':
    logger.info("Start with configuration: \n%s", pformat(app_settings.model_dump()))
    uvicorn.run(app, host='localhost', port=10000)
