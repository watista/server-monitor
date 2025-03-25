#!/usr/bin/python3

from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from telegram.helpers import escape_markdown
from services.logger import logger
from services.alerts import alerts
from states import MUTE_OPTION, SELECT_DURATION, CUSTOM_DURATION


class Mute:
    """
    Class responsible for muting alerts.
    """

    def __init__(self, functions: object) -> None:
        """
        Initializes the Mute class.
        :param functions: Functions for interacting with the Telegram bot.
        """
        self.function = functions

    async def start_mute(self, update: Update, context: CallbackContext) -> int:
        """ Handles the /mute command and displays active alerts that can be muted """
        logger.info("Mute process started")

        # Check if there are any active alerts
        if all(not v['active_alert'] for v in alerts.alerts.values()):
            logger.info("No active alerts to mute")
            await self.function.send_message("There are no active alerts, nothing to mute\\.", context)
            return ConversationHandler.END

        # List all active alerts
        active_alerts = [
            key for key, value in alerts.alerts.items() if value['active_alert']]
        logger.info(f"Active alerts: {active_alerts}")

        # Create inline keyboard buttons for muting each active alert
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Mute {alert}", callback_data=f"{alert}")]
            for alert in active_alerts
        ] + [[InlineKeyboardButton("Mute All", callback_data="mute_all")]])

        # Prompt user to select which alert to mute
        await self.function.send_message("Which alert do you want to mute?", context, reply_markup)
        return MUTE_OPTION

    async def option_mute(self, update: Update, context: CallbackContext) -> int:
        """ Handles alert selection for muting """

        # Save callback query, acknowledge the callback and remove the keyboard
        context.user_data["alert_key"] = update.callback_query.data
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        logger.info(f"User selected alert to mute: {update.callback_query.data}")

        # Provide mute duration options
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1 hour", callback_data="1"),
                InlineKeyboardButton("3 hours", callback_data="3")
            ],
            [
                InlineKeyboardButton("6 hours", callback_data="6"),
                InlineKeyboardButton("12 hours", callback_data="12")
            ],
            [
                InlineKeyboardButton("24 hours", callback_data="24"),
                InlineKeyboardButton("Custom", callback_data="custom")
            ]
        ])

        # Prompt user to select which duration to mute the alert
        await self.function.send_message("What should be the mute duration?", context, reply_markup)
        return SELECT_DURATION

    async def select_duration(self, update: Update, context: CallbackContext) -> Optional[int]:
        """ Handles mute duration selection """

        # Save callback query, acknowledge the callback and remove the keyboard
        duration_data = update.callback_query.data
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        logger.info(f"User selected mute duration: {duration_data}")

        # If the user selects 'custom', ask for manual input
        if duration_data == "custom":
            await self.function.send_message("Please enter the custom duration in hours", context)
            return CUSTOM_DURATION
        else:
            duration_hours = int(duration_data)

        # Proceed with muting alerts
        await self._mute_alerts(update, context, duration_hours)
        return ConversationHandler.END

    async def custom_duration(self, update: Update, context: CallbackContext) -> Optional[int]:
        """ Handles custom duration input """
        try:
            # Validate user input
            duration_hours = int(update.message.text)
            if duration_hours <= 0:
                raise ValueError("Invalid number")

            # Proceed with muting alerts
            await self._mute_alerts(update, context, duration_hours)
            return ConversationHandler.END
        except ValueError as e:
            # Request mute duration again incase of unvalidate answer
            logger.error(f"Invalid custom duration input: {update.message.text} - Error: {e}")
            await self.function.send_message("Please enter a valid number of hours:", context)
            return CUSTOM_DURATION

    async def _mute_alerts(self, update: Update, context: CallbackContext, duration_hours: int) -> None:
        """ Mutes a single or all alerts for the specified duration """
        alert_key = context.user_data["alert_key"]

        if alert_key == "mute_all":
            # Mute all alerts
            for key in alerts.alerts.keys():
                alerts.mute_alert(key, duration_hours)
            message = f"All alerts are muted for {duration_hours} hours."
        else:
            # Mute a specific alert
            alerts.mute_alert(alert_key, duration_hours)
            message = f"{alert_key.capitalize()} is muted for {duration_hours} hours."

        logger.info(message)
        await self.function.send_message(escape_markdown(message, version=2), context)
