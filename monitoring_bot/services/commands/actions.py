#!/usr/bin/python3

import subprocess
from subprocess import CalledProcessError
from typing import List

from telegram import Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown

from services.logger import logger


class Actions:
    """
    General command collection that executes system actions.
    Add a new command by:
    - adding an async method here
    - registering it in `services/bot.py`
    """

    def __init__(self, functions: object) -> None:
        self.function = functions

    def _run(self, argv: List[str]) -> None:
        subprocess.run(
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

    async def stil(self, update: Update, context: CallbackContext) -> None:
        """Handles the /stil command."""
        logger.info("Action invoked: stil")
        try:
            self._run(["ipmitool", "raw", "0x30", "0x70", "0x66", "0x01", "0x00", "0x16"])
            self._run(["ipmitool", "raw", "0x30", "0x70", "0x66", "0x01", "0x01", "0x16"])
            await self.function.send_message("`stil` executed successfully\\.", context)
        except CalledProcessError as e:
            logger.error(f"stil failed (code {e.returncode}):\n{e.stderr}")
            msg = (
                f"`stil` failed with exit code {e.returncode}\\.\n"
                f"Error output:\n```\n{escape_markdown((e.stderr or '').strip(), version=2)}\n```"
            )
            await self.function.send_message(msg, context)

    async def heelstil(self, update: Update, context: CallbackContext) -> None:
        """Handles the /heelstil command."""
        logger.info("Action invoked: heelstil")
        try:
            self._run(["ipmitool", "raw", "0x30", "0x70", "0x66", "0x01", "0x00", "0x04"])
            self._run(["ipmitool", "raw", "0x30", "0x70", "0x66", "0x01", "0x01", "0x04"])
            await self.function.send_message("`heelstil` executed successfully\\.", context)
        except CalledProcessError as e:
            logger.error(f"heelstil failed (code {e.returncode}):\n{e.stderr}")
            msg = (
                f"`heelstil` failed with exit code {e.returncode}\\.\n"
                f"Error output:\n```\n{escape_markdown((e.stderr or '').strip(), version=2)}\n```"
            )
            await self.function.send_message(msg, context)

    async def shutdown(self, update: Update, context: CallbackContext) -> None:
        """Handles the /shutdown command."""
        logger.info("Action invoked: shutdown")
        try:
            self._run(["shutdown", "now"])
            await self.function.send_message("`shutdown` executed successfully\\.", context)
        except CalledProcessError as e:
            logger.error(f"shutdown failed (code {e.returncode}):\n{e.stderr}")
            msg = (
                f"`shutdown` failed with exit code {e.returncode}\\.\n"
                f"Error output:\n```\n{escape_markdown((e.stderr or '').strip(), version=2)}\n```"
            )
            await self.function.send_message(msg, context)

    async def reboot(self, update: Update, context: CallbackContext) -> None:
        """Handles the /reboot command."""
        logger.info("Action invoked: reboot")
        try:
            self._run(["reboot", "now"])
            await self.function.send_message("`reboot` executed successfully\\.", context)
        except CalledProcessError as e:
            logger.error(f"reboot failed (code {e.returncode}):\n{e.stderr}")
            msg = (
                f"`reboot` failed with exit code {e.returncode}\\.\n"
                f"Error output:\n```\n{escape_markdown((e.stderr or '').strip(), version=2)}\n```"
            )
            await self.function.send_message(msg, context)

