#!/usr/bin/python3

from telegram import Update
from telegram.ext import CallbackContext
from config import config
from services.logger import logger

class Monitor:

    def __init__(self, functions):

        # Set default values
        self.function = functions

    async def check(self, context: CallbackContext) -> None:
        """ Handles the execution of interval monitor by calling the API """
        logger.info(f"Monitor interval started")

        try:
            all_status = self.api.get(type)
            if not all_status:
                raise ValueError("API returned None for {type} command")

            formatted_msg = await self.create_status_message(json.loads(all_status.text), type)
            await self.function.send_message(formatted_msg, update, context)

        except Exception as e:
            logger.error(f"Error handling /status_{type} command: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            await self.function.send_message(escape_markdown(f"Retrieving data from API for {type} monitor(s) failed, see the logs for more information.", version=2), update, context)
