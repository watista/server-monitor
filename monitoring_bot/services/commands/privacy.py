#!/usr/bin/python3

import asyncio
from telegram import Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from services.logger import logger
from config import config


class Privacy:
    """
    Class responsible for displaying the privacy policy.
    """

    def __init__(self, functions: object) -> None:
        """
        Initializes the Privacy class.
        :param functions: Functions for interacting with the Telegram bot.
        """
        self.function = functions

    async def privacy(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /privacy command """
        logger.info("Privacy policy command invoked")

        privacy_policy = f"""*Privacy Policy for Server Monitor {escape_markdown(config.server_name.capitalize(), version=2)}*

*1\. Introduction*
This Privacy Policy explains how the *Server Monitor {escape_markdown(config.server_name.capitalize(), version=2)}* bot \(the "Bot"\) operates and handles user data\. By using the Bot, you agree to the terms outlined in this policy\.

*2\. Data Collection*
The Bot collects the following data:
\- Telegram *Chat ID* \(user\(s\) or group\) – to send monitoring alerts
\- *API address, username, and password* – to fetch server status
\- *Server status information* – for monitoring purposes

*3\. Data Usage*
The collected data is only used to:
\- Retrieve server monitoring information
\- Send alerts to the user\(s\) or group

*4\. Data Storage*
\- No user data is permanently stored\.
\- Logs are kept for {config.log_retention} for debugging and monitoring purposes\.

*5\. Data Sharing*
\- No user data is shared with third parties\.
"""

        await self.function.send_message(privacy_policy, context)
        await asyncio.sleep(1)
        privacy_policy = f"""*6\. Data Security*
\- The Bot does not store user data\.
\- API credentials are used only for real\-time queries and are not saved\.

*7\. User Rights*
\- Since no personal data is stored, no deletion requests are necessary or possible\.

*8\. Contact Information*
For any privacy concerns or questions, contact the bot owner: *@{config.bot_owner}* on Telegram\.
"""

        return await self.function.send_message(privacy_policy, context)
