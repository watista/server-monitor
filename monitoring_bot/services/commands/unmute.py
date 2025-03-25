#!/usr/bin/python3

import time
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from telegram.helpers import escape_markdown
from services.logger import logger
from services.alerts import alerts
from states import UNMUTE_OPTION


class Unmute:
    """
    Class responsible for unmuting alerts.
    """

    def __init__(self, functions) -> None:
        """
        Initializes the Unmute class.
        :param functions: Functions for interacting with the Telegram bot.
        """
        self.function = functions

    async def start_unmute(self, update: Update, context: CallbackContext) -> Optional[int]:
        """ Handles the /unmute command """
        logger.info("Unmute process started")

        # Get a list of currently muted alerts
        muted_alerts = [key for key, value in alerts.alerts.items(
        ) if time.time() < value['mute_until']]

        # If there are no muted alerts, inform the user and end the conversation
        if not muted_alerts:
            logger.info("No muted alerts to unmute")
            await self.function.send_message("There are no muted alerts to unmute\\.", context)
            return ConversationHandler.END

        logger.info(f"Muted alerts: {muted_alerts}")

        # Create inline keyboard buttons for each muted alert
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Unmute {alert}", callback_data=f"{alert}")]
            for alert in muted_alerts
        ])

        # Prompt user to select which alert to unmute
        await self.function.send_message("Which alert do you want to unmute?", context, reply_markup)
        return UNMUTE_OPTION

    async def option_unmute(self, update: Update, context: CallbackContext) -> None:
        """ Handles the unmute selection """

        # Save callback query, acknowledge the callback and remove the keyboard
        alert_key = update.callback_query.data
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        logger.info(f"User selected alert to unmute: {update.callback_query.data}")

        # Check if the selected alert exists, then unmute it
        if alert_key in alerts.alerts:
            alerts.unmute_alert(alert_key)
            logger.info(f"Alert '{alert_key}' has been unmuted.")
            await self.function.send_message(
                escape_markdown(f"{alert_key.capitalize()} has been unmuted.", version=2), context
            )
        else:
            logger.error(f"Attempted to unmute non-existent alert: {alert_key}")
            await self.function.send_message("Invalid alert selection\\.", context)

        return ConversationHandler.END
