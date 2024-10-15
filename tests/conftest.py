import os
from functools import partial

import pytest
from fastapi.testclient import TestClient

from main import app
from libs.tortoise_manager import TortoiseManager
from tortoise import Tortoise, ConfigurationError, connections
from tortoise.contrib import test
from tortoise.contrib.test import finalizer, initializer

from tests.config import log
from tests.tortoise_test_overwrite import init_db, get_db_config


@pytest.fixture(scope="session")
def get_mis_client():
    try:
        from tortoise.backends.psycopg import PsycopgClient

        PsycopgClient.default_timeout = float(os.environ.get("TORTOISE_POSTGRES_TIMEOUT", "15"))
    except ImportError:
        pass
    
    init_db_with_migration = partial(init_db, migration_paths=TortoiseManager._migrations_to_apply.values())
    test._init_db = init_db_with_migration
    test.getDBConfig = get_db_config
    initializer(
        modules=TortoiseManager._modules['core'],
        db_url=TortoiseManager._db_url,
        app_label='core',
    )
    
    log.info("Create app client")
    # maybe rework on full lifespan support for tests?
    # https://github.com/adriangb/misc/tree/starlette-state-lifespan
    with TestClient(app) as client:
        yield client
    
    finalizer()


# async def drop_databases():
#     try:
#         await Tortoise._drop_databases()
#     except ConfigurationError:
#         log.warning("[TortoiseManager] Database not initialized")


#@pytest.fixture(scope="session")
#async def init_database():
#    log.info("Init Tortoise to cleanup before tests")
    # Call init() directly to init without create_db flag
    #await Tortoise.init(
    #    db_url=TortoiseManager._db_url,
    #    modules=TortoiseManager._modules,
    #)
    # await Tortoise.init(config=TortoiseManager._tortiose_orm)
    #await drop_databases()
    #await connections.close_all()

    #yield

    #log.info("Cleanup Tortoise after tests")
    #await drop_databases()


# @pytest.fixture(scope="session")
# def initialize_tests(request):
#     try:
#         from tortoise.backends.psycopg import PsycopgClient
# 
#         PsycopgClient.default_timeout = float(os.environ.get("TORTOISE_POSTGRES_TIMEOUT", "15"))
#     except ImportError:
#         pass
# 
#     init_db_with_migration = partial(init_db, migration_paths=TortoiseManager._migrations_to_apply.values())
#     test._init_db = init_db_with_migration
#     test.getDBConfig = get_db_config
#     log.warning(TortoiseManager._db_url)
#     initializer(
#         modules=TortoiseManager._modules['core'],
#         db_url=TortoiseManager._db_url,
#         app_label='core',
#     )
#     
#     request.addfinalizer(finalizer)
