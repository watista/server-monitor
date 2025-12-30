#!/usr/bin/python3

from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from telegram.helpers import escape_markdown
from services.logger import logger
from config import config
from states import RESTART_OPTION


class Restart:
    """
    Class responsible for muting alerts.
    """

    def __init__(self, functions: object) -> None:
        """
        Initializes the Mute class.
        :param functions: Functions for interacting with the Telegram bot.
        """
        self.function = functions

    async def start_restart(self, update: Update, context: CallbackContext) -> int:
        """ Handles the /restart command and displays list of processes to restart """
        logger.info("Restart process started")

        # Check if any processes are given
        if config.processes is None:
            logger.info("No processes are given as env variable")
            await self.function.send_message("There are no processes given in the env variables\\.", context)
            return ConversationHandler.END

        # Get all processes
        process_list = [
            pl.strip() for pl in config.processes.split(",") if pl.strip()]
        logger.info(f"Available processes: {process_list}")

        # Create inline keyboard buttons for restarting each process
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Restart {alert}", callback_data=f"{alert}")]
            for alert in process_list
        ])

        # Prompt user to select which alert to mute
        await self.function.send_message("Which process do you want to restart?", context, reply_markup)
        return RESTART_OPTION

    async def choice_restart(self, update: Update, context: CallbackContext) -> int:
        """ Handles the restart selection """

        # Save callback query, acknowledge the callback and remove the keyboard
        choice = update.callback_query.data
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        logger.info(f"User chose to restart process: {choice}")

        # Restart the given process
        try:
            # this will raise CalledProcessError if the command fails
            result = subprocess.run(
                ["sudo", "systemctl", "restart", choice],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            # Optionally, log or inspect result.stdout
            logger.info(f"Restart of {choice} succesfull:\n" + result.stdout)
            await self.function.send_message(
                f"Service {choice} has been succesfully restarted\\.", context
            )
        except CalledProcessError as e:
            # e.returncode is the exit status, e.stderr has the error output
            logger.error(f"Restarting of {choice} failed. (code {e.returncode}):\n{e.stderr}")
            err_msg = (
                f"Restart of {choice} failed with error code {e.returncode}\\.\n"
                f"Error output:\n```\n{escape_markdown(e.stderr.strip(), version=2)}\n```"
            )
            # Send the error message
            await self.function.send_message(err_msg, context)

        return ConversationHandler.END
