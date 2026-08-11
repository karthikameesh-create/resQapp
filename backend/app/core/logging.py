import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from app.core.request_context import get_request_id


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True


def setup_logging():
    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "[%(request_id)s] | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDFilter())

    app_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    app_handler.setFormatter(formatter)
    app_handler.addFilter(RequestIDFilter())

    error_handler = RotatingFileHandler(
        "logs/error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(RequestIDFilter())

    access_handler = RotatingFileHandler(
        "logs/access.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    access_handler.setFormatter(formatter)
    access_handler.addFilter(RequestIDFilter())

    root_logger = logging.getLogger()

    root_logger.handlers.clear()

    root_logger.setLevel(logging.INFO)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(access_handler)