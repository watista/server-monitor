#!/usr/bin/python3

import os
import colorlog
import logging
import logging.config


def get_logger():

    # Import inside function to break circular dependency
    from config import config

    # Set log vars
    LOG_TYPE = config.log_type.upper()
    LOG_DIR = config.log_dir
    LOG_FILENAME = config.log_filename

    # Create logs directory if not exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Choose handlers based on LOG_TYPE
    active_handlers = ["console"]
    if LOG_TYPE == "DEBUG":
        active_handlers.append("debug_file")
    else:
        active_handlers.append("info_rotating_file")

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            },
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_white,bg_red",
                },
            },
            "extended": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s - [%(pathname)s - %(module)s - %(funcName)s - %(lineno)d]",
            },
        },
        "handlers": {
            "console": {
                "level": LOG_TYPE,
                "formatter": "colored",
                "class": "logging.StreamHandler",
            },
            "debug_file": {
                "level": "DEBUG",
                "formatter": "extended",
                "class": "logging.FileHandler",
                "filename": os.path.join(LOG_DIR, ("debug-" + LOG_FILENAME)),
                "mode": "a",
            },
            "info_rotating_file": {
                "level": "INFO",
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_DIR, LOG_FILENAME),
                "maxBytes": 10485760,
                "backupCount": 31,
            },
        },
        "root": {
            "level": LOG_TYPE,
            "handlers": active_handlers,
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("monitoring_api")
    logger.setLevel(getattr(logging, LOG_TYPE, logging.INFO))
    return logger

logger = get_logger()
