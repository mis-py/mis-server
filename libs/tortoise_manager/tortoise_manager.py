from yoyo import get_backend, read_migrations
from tortoise import Tortoise, connections
from tortoise.exceptions import DoesNotExist, IntegrityError
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse
from const import TIMEZONE, BASE_DIR
from .config import TortoiseSettings

settings = TortoiseSettings()


class TortoiseManager:
    _db_url = (
        f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        if all((
            settings.POSTGRES_USER,
            settings.POSTGRES_PASSWORD,
            settings.POSTGRES_HOST,
            settings.POSTGRES_PORT,
            settings.POSTGRES_DB
        )) else
        "sqlite://db.sqlite3"
    )
    _modules = {"core": ["core.db.models", "core.db.mixin", "core.db.guardian"]}
    # _tortiose_orm: dict = {
    #     "connections": {
    #         "default": (
    #             f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    #             f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    #             if all((
    #                 settings.POSTGRES_USER,
    #                 settings.POSTGRES_PASSWORD,
    #                 settings.POSTGRES_HOST,
    #                 settings.POSTGRES_PORT,
    #                 settings.POSTGRES_DB
    #             )) else
    #             "sqlite://db.sqlite3"
    #         )
    #     },
    #     "apps": {
    #         # models is module name
    #         # "core": {
    #         #     "models": ["core.db.models", "core.db.mixin", "core.db.guardian"],
    #         #     "default_connection": "default",
    #         # },
    #         "core": ["core.db.models", "core.db.mixin", "core.db.guardian"],
    #     },
    #     "timezone": TIMEZONE,
    # }
    _migrations_to_apply: dict = {
        "core": str(BASE_DIR / "core" / "migrations"),
    }

    @classmethod
    async def add_models(cls, app: str, models: list[str]):
        # cls._tortiose_orm['apps'][app] = dict(
        #     models=models,
        #     default_connection="default"
        # )
        cls._modules[app] = models

    @classmethod
    async def add_migrations(cls, app_name, path):
        cls._migrations_to_apply[app_name] = path

    @classmethod
    async def pre_init(cls):
        for label, models in cls._modules.items():
            Tortoise.init_models(models, label)

    @classmethod
    async def init(cls, app, add_exception_handlers, create_db=False):
        # await Tortoise.init(config=cls._tortiose_orm, _create_db=settings.POSTGRES_CREATE_DB)
        await Tortoise.init(
            db_url=cls._db_url,
            modules=cls._modules,
            timezone=TIMEZONE,
            _create_db=create_db
        )
        
        if add_exception_handlers:
            async def doesnotexist_exception_handler(request: Request, exc: DoesNotExist):
                return JSONResponse(status_code=404, content={"detail": str(exc)})

            app.add_exception_handler(DoesNotExist, doesnotexist_exception_handler)

            async def integrityerror_exception_handler(request: Request, exc: IntegrityError):
                return JSONResponse(
                    status_code=422,
                    content={"detail": [{"loc": [], "msg": str(exc), "type": "IntegrityError"}]},
                )

            app.add_exception_handler(IntegrityError, integrityerror_exception_handler)

    @classmethod
    async def init_migrations(cls):
        backend = get_backend(cls._db_url)

        for migration in cls._migrations_to_apply.keys():
            migrations = read_migrations(cls._migrations_to_apply[migration])
            try:
                with backend.lock():  
                    logger.debug(f"[TortoiseManager] Applying migration for: {migration} [{migrations}]")
                    backend.apply_migrations(backend.to_apply(migrations))
                    
            except Exception as e:
                e_name = e.__class__.__name__
                logger.error(f"[TortoiseManager] Error during migration: {migration} {e_name} {e}")
                
        # release connections to db
        backend._connection.close()
        del backend._connection
        del backend

    @classmethod
    async def shutdown(cls):
        await connections.close_all()
    
    @classmethod
    async def _generate_schema(cls):
        """
        This must not be used in normal application workflow. All schemas generating is done by migrations.
        """
        await Tortoise.generate_schemas()
    
    @classmethod
    async def _cleanup_db(cls):
        """
        This must not be used in normal application workflow. Only for test purposes.
        """
        await Tortoise._drop_databases()
