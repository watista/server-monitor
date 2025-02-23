#!/usr/bin/python3

import asyncio
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from services.logger import logger

class Help:

    def __init__(self, functions):

        # Set default values
        self.function = functions

    async def help_command(self, update: Update, context: CallbackContext) -> None:

        # Senf help info
        await self.function.send_message("*🔥Welkom bij de Plex Telegram Download bot🔥*\n\nDeze bot kan voor 3 zaken gebruikt worden:", update, context)
        logger.info(f"*ℹ️ User invoked the /help command ℹ️*\nUsername: {update.effective_user.first_name}\nUser ID: {update.effective_user.id}")
