#!/usr/bin/python3

import asyncio
import subprocess
from subprocess import CalledProcessError
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from telegram.helpers import escape_markdown
from services.logger import logger
from states import UPDATE_CHOICE


class Apt:
    """
    Class responsible for unmuting alerts.
    """

    def __init__(self, functions) -> None:
        """
        Initializes the Update class.
        :param functions: Functions for interacting with the Telegram bot.
        """
        self.function = functions

    async def start_update(self, update: Update, context: CallbackContext) -> Optional[int]:
        """
        Returns a sorted list of upgradeable packages,
        excluding any that are held back.
        """

        logger.info("Update process started")

        # Run all commands up front
        # 1) apt update
        subprocess.run(
            ["sudo", "apt", "update"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, check=True
        )

        # 2) apt list --upgradeable
        upgrade = subprocess.run(
            ["apt", "list", "--upgradeable"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, check=True
        ).stdout.splitlines()

        # 3) apt-mark showhold
        hold = subprocess.run(
            ["apt-mark", "showhold"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, check=True
        ).stdout.splitlines()

        # Parse into sets
        upgradeable = {
            line.split("/", 1)[0]
            for line in upgrade
            if line and not line.startswith("Listing")
        }
        held = {pkg.strip() for pkg in hold if pkg.strip()}

        # Compute difference and sort
        to_upgrade = sorted(upgradeable - held)

        # If nothing to upgrade, finish script
        if not to_upgrade:
            await self.function.send_message("No upgradeable packages\\.", context)
            return ConversationHandler.END

        # Send a messages with the to upgarded packages
        upgrade_string = ", ".join(to_upgrade)
        await self.function.send_message(f"Packages that will be upgraded:\n\n{escape_markdown(upgrade_string, version=2)}", context)
        await asyncio.sleep(1)

        # Provide mute duration options
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Yes", callback_data="yes"),
                InlineKeyboardButton("No", callback_data="no")
            ]
        ])

        # Prompt user to select if the packages should be updated
        await self.function.send_message("Do you want to update these packages?", context, reply_markup)
        return UPDATE_CHOICE

    async def choice_update(self, update: Update, context: CallbackContext) -> None:
        """ Handles the update selection """

        # Save callback query, acknowledge the callback and remove the keyboard
        choice = update.callback_query.data
        await update.callback_query.answer()
        await update.callback_query.edit_message_reply_markup(reply_markup=None)
        logger.info(f"User chose to update packages: {update.callback_query.data}")

        # Upgrade packages if answer was yes
        if choice == "yes":
            try:
                # this will raise CalledProcessError if the command fails
                result = subprocess.run(
                    ["sudo", "apt", "upgrade", "-y"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                # Optionally, log or inspect result.stdout
                logger.info("apt upgrade succeeded:\n" + result.stdout)
                await self.function.send_message(
                    "All packages have been updated successfully\\.", context
                )
            except CalledProcessError as e:
                # e.returncode is the exit status, e.stderr has the error output
                logger.error(f"apt upgrade failed (code {e.returncode}):\n{e.stderr}")
                err_msg = (
                    f"Upgrade failed with exit code {e.returncode}\\.\n"
                    f"Error output:\n```\n{escape_markdown(e.stderr.strip(), version=2)}\n```"
                )
                # Send the error message
                await self.function.send_message(err_msg, context)
        else:
            await self.function.send_message("Ok, no packages have been updated\\.", context)

        return ConversationHandler.END
