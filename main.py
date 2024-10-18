import asyncio
import logging
import sys
import uvicorn
from fastapi_pagination import add_pagination
from loguru import logger
from contextlib import asynccontextmanager
# from log import setup_logger
from typing import AsyncGenerator

import traceback
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from starlette import status
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from const import MIS_TITLE, MIS_VERSION, ENVIRONMENT
from config import CoreSettings
from libs.logs.manager import LogManager
from loaders import (
    init_core,
    init_modules,
    init_eventory,
    init_scheduler,
    init_core_routes,
    init_redis,
    init_migrations,
    pre_init_db,
    pre_init_modules,
    init_db,
    init_admin_user,
    init_mongo,
    init_guardian,
    manifest_init_modules,
    init_modules_root_model,
    generate_schema,
    cleanup_db
)
from loaders import (
    shutdown_modules, shutdown_eventory, shutdown_scheduler, shutdown_db, shutdown_redis, shutdown_mongo)
from core.exceptions import MISError
from core.utils.common import generate_unique_id
from core.utils.schema import MisResponse

LogManager.setup()

settings = CoreSettings()

origins = settings.ALLOW_ORIGINS.split(',')

@asynccontextmanager
async def lifespan(application: FastAPI):
    
    testmode = getattr(app.state, "testing", None)
    
    await init_redis()
    await init_mongo()
    await init_eventory()
    await init_scheduler()
    
    await pre_init_db()
    await manifest_init_modules()
    await pre_init_modules(application)
    await init_db(application, create_db=testmode)
    
    if testmode:
        logger.info('MIS Project API in "testing mode", migrations skipped. Generate schema instead.')
        await generate_schema()
    else:
        await init_migrations()
        
    await init_core()
    await init_admin_user()
    await init_modules_root_model()
    await init_guardian()
    await init_modules()
    await init_core_routes(application)
    add_pagination(app)  # required after init routes

    logger.success('MIS Project API started in test mode!')
    yield

    await shutdown_modules()
    await shutdown_scheduler()
    await shutdown_eventory()
    await shutdown_mongo()
    await shutdown_redis()
    await cleanup_db()
    await shutdown_db()
    
    if testmode:
        logger.info('MIS Project API in "testing mode", removing database.')
        await cleanup_db()


    logger.success('MIS Project API in test mode shutdown complete!')


app = FastAPI(
    title=MIS_TITLE,
    version=MIS_VERSION,
    lifespan=lifespan,
    root_path=settings.ROOT_PATH,
    docs_url=settings.DOCS_URL,
    openapi_url=settings.OPEN_API_URL,
    redoc_url=None,  # disable it completely
    redirect_slashes=False,
    generate_unique_id_function=generate_unique_id,
)


# async def analyze(request: Request, call_next):
#     headers = dict(request.headers)
#     if request.headers.get('user-agent') == 'testclient':
#         for line in json.dumps(headers, indent=4, ensure_ascii=False).splitlines():
#             logger.debug(line)
#
#     return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_name = exc.__class__.__name__
    tb = traceback.format_exc()

    logger.error(f"{request.method} {request.scope['path']}: {exc_name} - {exc.errors()}")
    logger.error(f"Body: {exc.body}")
    logger.error(tb)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=MisResponse[list](
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            msg=exc_name,
            result=[f"{exc['msg']} {exc.get('loc', '')}" for exc in exc.errors()]
        ).model_dump(),
    )


@app.exception_handler(MISError)
async def mis_error_exception_handler(request: Request, exc: MISError):
    exc_name = exc.__class__.__name__

    tb = traceback.format_exc()

    logger.error(f"{request.method} {request.scope['path']}: {exc_name} - {exc.message}")
    logger.error(tb)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=MisResponse[str](
            status_code=exc.status_code,
            msg=exc_name,
            result=exc.message,
        ).model_dump()
    )


async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        exc_name = exc.__class__.__name__

        tb = traceback.format_exc()

        logger.error(f"{request.method} {request.scope['path']}: {exc_name} - {exc}")
        logger.error(tb)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=MisResponse[str](
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                msg=exc_name,
                result="Server error happen. Our devs already fired for that. Anyway see server log for error details."
            ).model_dump(),
        )


app.middleware('http')(catch_exceptions_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(PyInstrumentProfilerMiddleware)
# app.add_middleware(BaseHTTPMiddleware, dispatch=analyze)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.get('/')
async def root():
    return Response(status_code=200)


# for debugging
if __name__ == "__main__":
    if sys.platform == 'win32':
        # https://github.com/saghul/aiodns?tab=readme-ov-file#note-for-windows-users
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT, log_level=settings.SERVER_LOG_LEVEL)
