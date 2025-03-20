#!/usr/bin/python3

import time
import traceback
from typing import Dict, Any, Optional
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from config import config
from services.logger import logger
from services.alerts import alerts
from services.api import Api


class Monitor:
    """
    Class responsible for monitoring various system statuses.
    """

    def __init__(self, functions) -> None:
        """
        Initializes the Monitor class.
        :param functions: Functions for interacting with the Telegram bot.
        """
        self.function = functions
        self.api = Api(self.function)

    async def check(self, context: CallbackContext) -> None:
        """
        Executes monitoring tasks by retrieving data from the API
        and performing relevant checks.
        """
        logger.info(f"Monitor interval started")

        # Check if API is working
        if not await self.get_data("all"):
            # If all alerts are muted, skip further checks
            if all(a['mute_until'] > time.time() for a in alerts.alerts.values()):
                logger.info("All monitors are muted")
                return None

            # Send an alert if the API response is empty
            await self.send_alert("Monitor failed, empty response from API. See the logs for more info.", "Monitor Alert", context)
            for key in alerts.alerts:
                # Mark all alerts as active
                alerts.alerts[key]["active_alert"] = True
            return None

        # Define monitoring checks with associated handlers
        checks = {
            "ip": {"type": "ip", "alert": "IP Check Alert", "handler": self.handle_ip},
            "disk": {"type": "disk", "alert": "Disk Check Alert", "handler": self.handle_disk},
            "apt": {"type": "apt", "alert": "APT Check Alert", "handler": self.handle_apt},
            "load": {"type": "load", "alert": "Load Check Alert", "handler": self.handle_load},
            "memory": {"type": "memory", "alert": "RAM Check Alert", "handler": self.handle_memory},
            "users": {"type": "users", "alert": "Users Check Alert", "handler": self.handle_users},
            "processes": {"type": "processes", "alert": "Process Check Alert", "handler": self.handle_processes},
        }

        # Loop through all checks and execute them if not muted
        for key, check in checks.items():
            if not alerts.is_muted(key):
                # Fetch data from API
                data = await self.get_data(check["type"])
                if data:
                    # Call the appropriate handler
                    await check["handler"](data, check["alert"], context)

    async def handle_ip(self, data: dict, alert_title: str, context: CallbackContext) -> None:
        """Checks if the IP address matches the expected value."""
        try:
            # Generates a formatted message and sets the alert variables accordingly
            if str(data["ip"]) != str(config.ip_threshold):
                await self.send_alert(f"Mismatch for IP check, current IP is: {data['ip']}", alert_title, context)
                alerts.alerts["ip"]["active_alert"] = True
            else:
                alerts.alerts["ip"]["active_alert"] = False
        except KeyError as e:
            logger.error(f"Missing key in IP data: {e}")

    async def handle_disk(self, data: dict, alert_title: str, context: CallbackContext) -> None:
        """Checks available disk space and sends an alert if below threshold."""
        try:
            # Generates a formatted list
            low_disks = [
                f"Disk {name} is almost full, {round(space, 1)}% left."
                for name, space in data['disks'].items()
                if float(space) < float(config.disk_threshold)
            ]

            # Sets the alert variables accordingly
            if low_disks:
                await self.send_alert("\n".join(low_disks), alert_title, context)
                alerts.alerts["disk"]["active_alert"] = True
            else:
                alerts.alerts["disk"]["active_alert"] = False
        except KeyError as e:
            logger.error(f"Missing key in Disk data: {e}")

    async def handle_apt(self, data: dict, alert_title: str, context: CallbackContext) -> None:
        """Checks APT packages to update and sends an alert if above threshold."""
        try:
            # Generates a formatted list
            exceeded = [
                f"{name.replace('_', ' ').capitalize()}: {amount}"
                for name, amount in data.items()
                if (name == "total_updates" and int(amount) > int(config.apt_threshold)) or
                   (name == "critical_updates" and int(amount)
                    > int(config.apt_security_threshold))
            ]

            # Sets the alert variables accordingly
            if exceeded:
                await self.send_alert("\n".join(exceeded), alert_title, context)
                alerts.alerts["apt"]["active_alert"] = True
            else:
                alerts.alerts["apt"]["active_alert"] = False
        except KeyError as e:
            logger.error(f"Missing key in APT data: {e}")

    async def handle_load(self, data: dict, alert_title: str, context: CallbackContext) -> None:
        """Checks server load and sends an alert if above threshold."""
        try:
            # Define threshold types
            thresholds = {
                'load_1m': config.load_1_threshold,
                'load_5m': config.load_5_threshold,
                'load_15m': config.load_15_threshold
            }

            # Generates a formatted list
            exceeded = [
                f"{name.replace('_', ' ').capitalize()}: {value}"
                for name, value in data.items()
                if float(value) > float(thresholds[name])
            ]

            # Sets the alert variables accordingly
            if exceeded:
                await self.send_alert("\n".join(exceeded), alert_title, context)
                alerts.alerts["load"]["active_alert"] = True
            else:
                alerts.alerts["load"]["active_alert"] = False
        except KeyError as e:
            logger.error(f"Missing key in Load data: {e}")

    async def handle_memory(self, data: dict, alert_title: str, context: CallbackContext) -> None:
        """Checks available memory and sends an alert if below threshold."""
        try:
            # Calculates free memory percentage
            ram_free = (data['available_ram'] / data['total_ram']) * 100
            swap_free = (data['available_swap'] / data['total_swap']) * 100

            # Generates a formatted list
            exceeded = []
            if float(ram_free) < float(config.ram_threshold):
                exceeded.append(f"RAM is low: {ram_free:.2f}% available")
            if float(swap_free) < float(config.swap_threshold):
                exceeded.append(f"Swap is low: {swap_free:.2f}% available")

            # Sets the alert variables accordingly
            if exceeded:
                await self.send_alert("\n".join(exceeded), alert_title, context)
                alerts.alerts["memory"]["active_alert"] = True
            else:
                alerts.alerts["memory"]["active_alert"] = False
        except KeyError as e:
            logger.error(f"Missing key in Memory data: {e}")

    async def handle_users(self, data: dict, alert_title: str, context: CallbackContext) -> None:
        """Checks logged in users and sends an alert if above threshold."""
        try:
            # Generates a formatted list and sets the alert variables accordingly
            if int(data['user_count']) > int(config.users_threshold):
                msg = f"Too many users logged in ({data['user_count']}): {', '.join(data['usernames'])}"
                await self.send_alert(msg, alert_title, context)
                alerts.alerts["users"]["active_alert"] = True
            else:
                alerts.alerts["users"]["active_alert"] = False
        except KeyError as e:
            logger.error(f"Missing key in Users data: {e}")

    async def handle_processes(self, data: dict, alert_title: str, context: CallbackContext) -> None:
        """Checks if given processes are running and sends an alert if they are not."""
        try:
            # Checks which processes are failed/false
            failed_processes = [
                name for name, status in data['processes'].items() if not status]

            # Generates a formatted list and sets the alert variables accordingly
            if failed_processes:
                process_list = "\n".join([f"{process}" for process in failed_processes])
                msg = f"The following processes are not running:\n{process_list}"
                await self.send_alert(msg, alert_title, context)
                alerts.alerts["processes"]["active_alert"] = True
            else:
                alerts.alerts["processes"]["active_alert"] = False
        except KeyError as e:
            logger.error(f"Missing key in Processes data: {e}")

    async def get_data(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Fetches data from API and handles errors"""
        try:
            data = await self.api.get(data_type)
            if not data:
                raise ValueError(f"API returned None for {data_type}")
            return data
        except Exception as e:
            logger.error(f"Error fetching {data_type}: {e}")
            logger.debug(traceback.format_exc())
            return None

    async def send_alert(self, message: str, title: str, context: CallbackContext) -> None:
        """Sends a formatted alert message to Telegram."""
        try:
            await self.function.send_message(
                f"*❌ {title} ❌*\n\n{escape_markdown(message, version=2)}\n\nServer: {escape_markdown(config.server_name, version=2)}",
                context, None, "MarkdownV2"
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            logger.debug(traceback.format_exc())
