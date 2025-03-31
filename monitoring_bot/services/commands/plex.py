#!/usr/bin/python3

import traceback
from typing import Dict, Any
from telegram import Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from services.logger import logger
from services.api import Api
from config import config


class Plex:
    """
    Class responsible for the Plex status command.
    """

    def __init__(self, functions: object) -> None:
        """
        Initializes the Privacy class.
        :param functions: Functions for interacting with the Telegram bot.
        """
        self.function = functions
        self.api = Api(self.function)

    async def plex(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /plex command """
        logger.info("Plex command invoked")

        try:
            status = await self.api.get("plex")
            if not status:
                raise ValueError(f"API returned None for plex command")

            formatted_msg = await self.create_status_message(status)
            await self.function.send_message(formatted_msg, context)

        except Exception as e:
            logger.error(f"Error handling /status_plex command: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            await self.function.send_message(escape_markdown(f"Retrieving data from API for plex status failed, see the logs for more information.", version=2), context)


    async def create_status_message(self, json: Dict[str, Any]) -> str:
        """ Generates a formatted Telegram message with server status. """
        json = json["plex"]
        intro_message = f"📺 *Plex Stream Status* 📺\n"

        if json['response']['data']['stream_count'] == "0":
            return f"{intro_message}\nNo current streams\."

        message = f"Active Streams: {json['response']['data']['stream_count']}\n"
        message += f"Total bandwidth: {json['response']['data']['total_bandwidth']}\n\n"

        for session in json["response"]["data"]["sessions"]:
            message += f"{session.get('username', 'Unknown User')} ({session.get('friendly_name', 'Unknown Device')})\n"
            if session.get("library_name", "") == "TV Shows":
                message += f"{session.get('full_title', 'Unknown Title')} (S{int(session.get('parent_media_index', '0')):02}E{int(session.get('media_index', '0')):02}) ({session.get('progress_percent', '0')}%)\n"
            else:
                message += f"{session.get('full_title', 'Unknown Title')}\n"
            message += f"{session.get('platform', 'Unknown Platform')} ({session.get('device', 'Unknown Device')} - {session.get('ip_address_public', 'Unknown IP Address')})\n"
            message += f"Bandwidth: {session.get('bandwidth', 'Unknown Bandwidth')}\n"
            message += f"Quality: {session.get('quality_profile', 'Unknown Quality Profile')} - {session.get('stream_video_resolution', 'Unknown Resolution')}p\n"
            message += f"State: {session.get('state', 'Unknown State')}\n\n"

        return intro_message + escape_markdown(message, version=2)

