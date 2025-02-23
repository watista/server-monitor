#!/usr/bin/python3

import os
import colorlog
import logging
import logging.config
from typing import Optional


class Logger:
    """Singleton Logger class to manage application-wide logging."""
    _instance: Optional["Logger"] = None

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._configure_logging()
        return cls._instance

    def _configure_logging(self) -> None:

        # Import inside function to break circular dependency
        from config import config

        # Set log vars
        LOG_LEVEL = config.log_level.upper()
        LOG_DIR = config.log_dir
        LOG_FILENAME = config.log_filename

        # Create logs directory if not exists
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        # Choose handlers based on LOG_LEVEL
        active_handlers = ["console"]
        if LOG_LEVEL == "DEBUG":
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
                    "level": LOG_LEVEL,
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
                "level": LOG_LEVEL,
                "handlers": active_handlers,
            },
        }

        logging.config.dictConfig(LOGGING_CONFIG)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("apscheduler").setLevel(logging.WARNING)
        self.logger = logging.getLogger("monitoring_bot")
        self.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger


logger = Logger().get_logger()
