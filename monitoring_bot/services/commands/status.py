#!/usr/bin/python3

import traceback
import json
from typing import Dict, Any
from telegram import Update
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from services.api import Api
from services.logger import logger
from config import config

class Status:

    def __init__(self, functions: Any) -> None:
        """ Initializes the Status class with necessary dependencies """
        self.function = functions
        self.api = Api(self.function)

    async def all_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_all command """
        await self.do_command(update, context, "all")

    async def ip_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_ip command """
        await self.do_command(update, context, "ip")

    async def disk_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_disk command """
        await self.do_command(update, context, "disk")

    async def apt_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_apt command """
        await self.do_command(update, context, "apt")

    async def load_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_load command """
        await self.do_command(update, context, "load")

    async def memory_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_memory command """
        await self.do_command(update, context, "memory")

    async def users_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_users command """
        await self.do_command(update, context, "users")

    async def process_command(self, update: Update, context: CallbackContext) -> None:
        """ Handles the /status_processes command """
        await self.do_command(update, context, "processes")


    async def do_command(self, update: Update, context: CallbackContext, type: str) -> None:
        """ Handles the execution of status commands by calling the API """
        logger.info(f"User invoked the '{type}_command' command. Username: {update.effective_user.first_name} User ID: {update.effective_user.id}")

        try:
            all_status = await self.api.get(type)
            if not all_status:
                raise ValueError(f"API returned None for {type} command")

            formatted_msg = await self.create_status_message(all_status, type)
            await self.function.send_message(formatted_msg, update, context)

        except Exception as e:
            logger.error(f"Error handling /status_{type} command: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            await self.function.send_message(escape_markdown(f"Retrieving data from API for {type} monitor(s) failed, see the logs for more information.", version=2), update, context)


    async def create_status_message(self, json: Dict[str, Any], type: str) -> str:
        """ Generates a formatted Telegram message with server status. """
        message = f"🚀 *Server Status Report*\n\n"

        def get_section_value(json_data, section, key, default=0):
            """ Helper function to fetch values safely. """
            if type == "all":
                return json_data.get(section, {}).get(key, default)
            return json_data.get(key, default)

        # Public IP
        if type in ["all", "ip"]:
            public_ip = get_section_value(json, "public_ip", "ip", {})
            ip_status = "✅" if public_ip == config.ip_threshold else "❌"
            message += f"🌐{ip_status} *Public IP:* `{escape_markdown(public_ip, version=2)}`\n\n"

        # Disk Space
        if type in ["all", "disk"]:
            disks = get_section_value(json, "disk_space", "disks", {})
            message += "💾 *Disk Space:*\n"
            for disk, space in disks.items():
                message += f" \- `{escape_markdown(disk, version=2)}`: {escape_markdown(str(round(space, 2)), version=2)}% free\n"
            message += "\n"

        # APT Updates
        if type in ["all", "apt"]:
            total_updates = get_section_value(json, "apt_updates", "total_updates")
            critical_updates = get_section_value(json, "apt_updates", "critical_updates")
            message += f"📦 *APT Updates:*\n \- Total: `{total_updates}`\n \- Critical: `{critical_updates}`\n\n"

        # Load Average
        if type in ["all", "load"]:
            load_1m = get_section_value(json, "load_status", "load_1m")
            load_5m = get_section_value(json, "load_status", "load_5m")
            load_15m = get_section_value(json, "load_status", "load_15m")
            message += f"⚡ *Load Average:*\n \- 1m: `{load_1m}`\n \- 5m: `{load_5m}`\n \- 15m: `{load_15m}`\n\n"

        # Memory Usage
        if type in ["all", "memory"]:
            available_ram = get_section_value(json, "memory_status", "available_ram") / 1024
            total_ram = get_section_value(json, "memory_status", "total_ram") / 1024
            available_swap = get_section_value(json, "memory_status", "available_swap") / 1024
            total_swap = get_section_value(json, "memory_status", "total_swap") / 1024
            message += f"🧠 *Memory:*\n \- Available RAM: `{round(available_ram)} GB`\n \- Total RAM: `{round(total_ram)} GB`\n"
            message += f" \- Available Swap: `{round(available_swap)} GB`\n \- Total Swap: `{round(total_swap)} GB`\n\n"

        # Logged in Users
        if type in ["all", "users"]:
            user_count = get_section_value(json, "logged_in_user_status", "user_count")
            usernames = get_section_value(json, "logged_in_user_status", "usernames", [])
            message += f"👥 *Logged\-in Users:* `{user_count}`\n"
            if usernames:
                message += " \- Users: " + ", ".join(usernames) + "\n\n"
            else:
                message += " \- No active users\n\n"

        # Process Status
        if type in ["all", "processes"]:
            processes = get_section_value(json, "process_status", "processes", {})
            message += f"⚙️ *Process Status:*\n"
            for process, status in processes.items():
                emoji = "✅" if status else "❌"
                message += f" \- {emoji} `{process}`\n"

        return message
