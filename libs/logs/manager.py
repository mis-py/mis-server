import datetime
import logging
import sys
from typing import Callable

import pytz
from loguru import logger

from config import CoreSettings
from const import LOGS_DIR, MODULES_DIR, TIMEZONE
from libs.logs.filters import PathLoguruFilter
from libs.logs.formatters import Formatter

settings = CoreSettings()


class LogManager:
    _terminal_handlers: dict[str, int] = {}
    _file_handlers: dict[str, int] = {}

    @classmethod
    def _add_terminal_handler(cls, key: str, handler_id: int) -> None:
        cls._terminal_handlers[key] = handler_id

    @classmethod
    def _remove_terminal_handler(cls, key: str):
        handler_id = cls._terminal_handlers.get(key)
        if handler_id:
            logger.remove(handler_id)

    @classmethod
    def _add_file_handler(cls, key: str, handler_id: int) -> None:
        cls._file_handlers[key] = handler_id

    @classmethod
    def _remove_file_handler(cls, key: str):
        handler_id = cls._file_handlers.get(key)
        if handler_id:
            logger.remove(handler_id)

    @classmethod
    def _setup_logging(cls):
        logging.getLogger('uvicorn').handlers.clear()

    @classmethod
    def _setup_loguru(cls):
        logger.remove()
        logger.configure(patcher=custom_log_timezone)

        # core logs
        exclude_modules_logs_filter = PathLoguruFilter(
            path=MODULES_DIR, exclude_mode=True,
        )
        cls.set_loggers(
            name="core",
            level=settings.LOG_LEVEL,
            format=settings.LOGGER_FORMAT,
            filter=exclude_modules_logs_filter,
            rotation=settings.LOG_ROTATION,
        )

    @classmethod
    def setup(cls):
        cls._setup_logging()
        cls._setup_loguru()

    @classmethod
    def set_terminal_handler(cls, key: str, filter: Callable, level: str, format: str):
        formatter = Formatter(fmt=format, context_key=key)

        # add new terminal logs handler
        handler_id = logger.add(
            sink=sys.stderr,
            level=level,
            format=formatter.format,
            filter=filter,
        )

        # remove old handler if exists
        cls._remove_terminal_handler(key)

        cls._add_terminal_handler(key=key, handler_id=handler_id)
        return handler_id

    @classmethod
    def set_file_handler(
            cls,
            key: str,
            filter: Callable,
            save_path: str,
            level: str,
            format: str,
            rotation: str,
            serialize: bool = True,
    ):
        formatter = Formatter(fmt=format, context_key=key)

        # add new file logs handler
        handler_id = logger.add(
            sink=save_path,
            format=formatter.format,
            rotation=rotation,
            level=level,
            filter=filter,
            serialize=serialize,
        )

        # remove old handler if exists
        cls._remove_file_handler(key)

        cls._add_file_handler(key=key, handler_id=handler_id)

        return handler_id

    @classmethod
    def set_loggers(cls, name: str, level: str, format: str, rotation: str, filter: Callable):
        """Set terminal and file logger handlers"""

        cls.set_terminal_handler(key=name, level=level, filter=filter, format=format)
        logger.debug(f"[{name}] Terminal logger was set")

        #cls.set_file_handler(
        #    key=name,
        #    level=level,
        #    filter=filter,
        #    format=format,
        #    save_path=LOGS_DIR / name / f"{name}.log",
        #    rotation=rotation, serialize=True,
        #)
        #logger.debug(f"[{name}] File logger was set")


def custom_log_timezone(record):
    tz = pytz.timezone(TIMEZONE)
    dt = datetime.datetime.now(tz)
    record["extra"]["datetime"] = dt.strftime('%d-%m-%Y %H:%M:%S.%f')[:-3]
