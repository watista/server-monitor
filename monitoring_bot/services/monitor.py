#!/usr/bin/python3

import time
import traceback
import asyncio
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from config import config
from services.logger import logger
from services.alerts import alerts
from services.api import Api

class Monitor:

    def __init__(self, functions):

        # Set default values
        self.function = functions
        self.api = Api(self.function)
        self.checks = {
            "ip": config.ip_threshold,
            "disk": config.disk_threshold,
            "apt": {config.apt_threshold, config.apt_security_threshold},
            "load": {config.load_1_threshold, config.load_5_threshold, config.load_15_threshold},
            "memory": {config.ram_threshold, config.swap_threshold},
            "users": config.users_threshold,
            "processes": False
        }

    async def check(self, context: CallbackContext) -> None:
        """ Handles the execution of interval monitor by calling the API """
        logger.info(f"Monitor interval started")
        now = time.time()

        # Check if API is working
        if not await self.api_get("all"):
            return await self.function.send_message(escape_markdown(f"Monitor failed, empty response from API. See the logs for more info.", version=2), config.chat_id, context, None, "MarkdownV2", False)

        # IP
        if not alerts.is_muted("ip"):
            data = await self.api_get("ip")
            if not data:
                return await self.function.send_message(escape_markdown(f"Monitor IP failed, empty response from API. See the logs for more info.", version=2), config.chat_id, context, None, "MarkdownV2", False)
            if not str(data["ip"]) == str(config.ip_threshold):
                await self.function.send_message(f"*❌ IP Check Alert ❌*\n\nMismatch for IP check, current IP is: {escape_markdown(str(data['ip']), version=2)}", config.chat_id, context, None, "MarkdownV2", False)

        # Disk
        if not alerts.is_muted("disk"):
            data = await self.api_get("disk")
            if not data:
                return await self.function.send_message(escape_markdown(f"Monitor Disk failed, empty response from API. See the logs for more info.", version=2), config.chat_id, context, None, "MarkdownV2", False)
            low_disk_messages = [
                f"Disk {name} is almost full, {round(space, 1)}% left on device."
                for name, space in data['disks'].items()
                if float(space) < float(config.disk_threshold)
            ]
            if low_disk_messages:
                alert_msg = "\n".join(low_disk_messages)
                await self.function.send_message(f"*❌ Disk Check Alert ❌*\n\n{(escape_markdown(alert_msg, version=2))}", config.chat_id, context, None, "MarkdownV2", False)

        # Apt
        if not alerts.is_muted("apt"):
            data = await self.api_get("apt")
            if not data:
                return await self.function.send_message(escape_markdown(f"Monitor APT failed, empty response from API. See the logs for more info.", version=2), config.chat_id, context, None, "MarkdownV2", False)
            exceeded = [
                f"{name.replace('_', ' ').capitalize()}: {amount}"
                for name, amount in data.items()
                if (name == "total_updates" and int(amount) > int(config.apt_threshold)) or
                   (name == "critical_updates" and int(amount) > int(config.apt_security_threshold))
            ]
            if exceeded:
                alert_msg = "\n".join(exceeded)
                await self.function.send_message(f"*❌ APT Check Alert ❌*\n\n{(escape_markdown(alert_msg, version=2))}", config.chat_id, context, None, "MarkdownV2", False)

        # Load
        if not alerts.is_muted("load"):
            data = await self.api_get("load")
            if not data:
                return await self.function.send_message(escape_markdown(f"Monitor Load failed, empty response from API. See the logs for more info.", version=2), config.chat_id, context, None, "MarkdownV2", False)
            print(data)


    async def api_get(self, type: str):
        """Make the get request from the API"""

        try:
            status = await self.api.get(type)
            if not status:
                raise ValueError(f"API returned None for {type} command")
            return status

        except Exception as e:
            logger.error(f"Error handling /status_{type} command: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return None

