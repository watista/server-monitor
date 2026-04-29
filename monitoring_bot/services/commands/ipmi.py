#!/usr/bin/python3

import subprocess
from subprocess import CalledProcessError
from typing import List

from telegram import Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown

from services.logger import logger


class Ipmi:
    """
    Commands that execute IPMI raw commands via ipmitool.
    """

    def __init__(self, functions: object) -> None:
        self.function = functions

    def _run_ipmitool_raw(self, args: List[str]) -> None:
        subprocess.run(
            ["ipmitool", "raw", *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

    async def stil(self, update: Update, context: CallbackContext) -> None:
        """Handles the /stil command."""
        logger.info("IPMI command invoked: stil")
        try:
            self._run_ipmitool_raw(["0x30", "0x70", "0x66", "0x01", "0x00", "0x16"])
            self._run_ipmitool_raw(["0x30", "0x70", "0x66", "0x01", "0x01", "0x16"])
            await self.function.send_message("`stil` executed successfully\\.", context)
        except CalledProcessError as e:
            logger.error(f"IPMI stil failed (code {e.returncode}):\n{e.stderr}")
            msg = (
                f"`stil` failed with exit code {e.returncode}\\.\n"
                f"Error output:\n```\n{escape_markdown((e.stderr or '').strip(), version=2)}\n```"
            )
            await self.function.send_message(msg, context)

    async def heelstil(self, update: Update, context: CallbackContext) -> None:
        """Handles the /heelstil command."""
        logger.info("IPMI command invoked: heelstil")
        try:
            self._run_ipmitool_raw(["0x30", "0x70", "0x66", "0x01", "0x00", "0x04"])
            self._run_ipmitool_raw(["0x30", "0x70", "0x66", "0x01", "0x01", "0x04"])
            await self.function.send_message("`heelstil` executed successfully\\.", context)
        except CalledProcessError as e:
            logger.error(f"IPMI heelstil failed (code {e.returncode}):\n{e.stderr}")
            msg = (
                f"`heelstil` failed with exit code {e.returncode}\\.\n"
                f"Error output:\n```\n{escape_markdown((e.stderr or '').strip(), version=2)}\n```"
            )
            await self.function.send_message(msg, context)

