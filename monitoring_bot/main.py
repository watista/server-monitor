#!/usr/bin/python3

from config import config
from services.logger import logger
from services.bot import Bot

if __name__ == "__main__":
    logger.info("Starting Server Monitor Bot")
    Bot()
