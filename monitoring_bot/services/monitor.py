#!/usr/bin/python3

import time
import traceback
from telegram.ext import CallbackContext
from telegram.helpers import escape_markdown
from config import config
from services.alerts import alerts
from services.logger import logger
from services.api import Api

class Monitor:

    def __init__(self, functions):

        # Set default values
        self.function = functions
        self.api = Api(self.function)

    async def check(self, context: CallbackContext) -> None:
        """ Handles the execution of interval monitor by calling the API """
        logger.info(f"Monitor interval started")
        now = time.time()

        checks = {
            "ip": config.ip_threshold,
            "apt": config.apt_threshold,
            "apt_security": config.apt_security_threshold,
            "disk": config.disk_threshold,
            "load_1": config.load_1_threshold,
            "load_5": config.load_5_threshold,
            "load_15": config.load_15_threshold,
            "ram": config.ram_threshold,
            "swap": config.swap_threshold,
            "users": config.users_threshold,
        }

        for check, threshold in checks.items():
            if alerts.is_muted(check):
                continue
            data = await self.api.get(check)
            if data and data[check] > threshold:
                if now - alerts.alerts[check]["last_alert"] > 300:
                    send_alert(f"Alert: {check} exceeded threshold ({data[check]} > {threshold})")
                    alerts.alerts[check]["last_alert"] = now


        if alerts.alerts_ip.get("muted") == False:
            ip = await self.api_get(context, "ip")
            if ip.get("ip") == config.ip_threshold:
                alerts.alerts_ip["muted"] = True
                print(1)

        print(alerts.alerts_ip.get("muted"))



        # config.ip_threshold
        # config.apt_threshold
        # config.apt_security_threshold
        # config.disk_threshold
        # config.load_1_threshold
        # config.load_5_threshold
        # config.load_15_threshold
        # config.ram_threshold
        # config.swap_threshold
        # config.users_threshold

    async def api_get(self, context: CallbackContext, type: str):
        """Make the get request from the API"""

        try:
            status = await self.api.get(type)
            if not status:
                raise ValueError(f"API returned None for {type} command")
            return status

        except Exception as e:
            logger.error(f"Error handling /status_{type} command: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            # await self.function.send_message(escape_markdown(f"Retrieving data from API for {type} monitor(s) failed, see the logs for more information.", version=2), update, context)
            return None
