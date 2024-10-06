import os
from pathlib import Path

MIS_TITLE = 'MIS Project API'
MIS_VERSION = '2.2.0'

DEFAULT_ADMIN_USERNAME = 'admin'

MODULES_DIR_NAME = 'modules'
MODULES_DATA_DIR_NAME = 'modules_data'
LOGS_DIR_NAME = 'logs'
TASKS_DIR_NAME = 'tasks'
# root project dir where main.py exist
BASE_DIR = Path(__file__).parent
# modules sources dir
MODULES_DIR = BASE_DIR / MODULES_DIR_NAME
# modules data dir where they store some files
APPDATA_DIR = BASE_DIR / MODULES_DATA_DIR_NAME
# dir for log storing
LOGS_DIR = BASE_DIR / LOGS_DIR_NAME
# dir for tasklog storing
TASK_LOGS_DIR = LOGS_DIR / TASKS_DIR_NAME

TIMEZONE: str = os.getenv('TIMEZONE', 'Europe/Kyiv')

MODULES_DIR.mkdir(exist_ok=True, mode=775)
APPDATA_DIR.mkdir(exist_ok=True, mode=775)
LOGS_DIR.mkdir(exist_ok=True, mode=775)

DEV_ENVIRONMENT = 'dev'    # for running with containers setup
PROD_ENVIRONMENT = 'prod'  # for production
TEST_ENVIRONMENT = 'test'  # for pytest setup
LOCAL_ENVIRONMENT = 'local'  # for local running without containers

ENVIRONMENT: str = os.getenv('ENVIRONMENT', LOCAL_ENVIRONMENT)

# this is for assign correct local env name to variable
if LOCAL_ENVIRONMENT in ENVIRONMENT:
    LOCAL_ENVIRONMENT = ENVIRONMENT

ENV_FILE = (BASE_DIR / 'envs' / ENVIRONMENT).with_suffix(".env")
