#!/usr/bin/python3

import traceback

# from states import VERIFY
from config import config
from services.logger import logger
from services.functions import Functions
from services.commands.privacy import Privacy
from services.commands.plex import Plex
from services.commands.status import Status
from services.commands.mute import Mute
from services.commands.unmute import Unmute
from services.monitor import Monitor
from states import MUTE_OPTION, SELECT_DURATION, CUSTOM_DURATION, UNMUTE_OPTION

from telegram import Update, BotCommand
from telegram.ext import (
    CommandHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler,
    Application,
    ConversationHandler
)


class Bot:

    def __init__(self) -> None:

        # Set classes
        self.function = Functions()
        self.privacy = Privacy(self.function)
        self.plex = Plex(self.function)
        self.status = Status(self.function)
        self.mute = Mute(self.function)
        self.unmute = Unmute(self.function)
        self.monitor = Monitor(self.function)
        self.allowed_users = list(map(int, config.allowed_users.split(",")))

        # Create the Application using the new async API
        self.application = Application.builder().token(config.bot_token).concurrent_updates(False).read_timeout(300).build(
        ) if config.env == "live" else Application.builder().token(config.bot_token_dev).concurrent_updates(False).read_timeout(300).build()

        # Add conversation handler with different states
        self.application.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler("mute", self.mute.start_mute,
                               filters.User(self.allowed_users)),
                CommandHandler("unmute", self.unmute.start_unmute,
                               filters.User(self.allowed_users))
            ],
            states={
                MUTE_OPTION: [CallbackQueryHandler(self.mute.option_mute)],
                UNMUTE_OPTION: [CallbackQueryHandler(self.unmute.option_unmute)],
                SELECT_DURATION: [CallbackQueryHandler(self.mute.select_duration)],
                CUSTOM_DURATION: [MessageHandler(filters.ChatType.GROUPS & (filters.TEXT & ~filters.COMMAND), self.mute.custom_duration)]
            },
            fallbacks=[
                CommandHandler("stop", self.stop,
                               filters.User(self.allowed_users))
            ],
            conversation_timeout=86400
        ))

        # Add stand-alone handlers
        self.application.add_handler(CommandHandler(
            "plex", self.plex.plex, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_all", self.status.all_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_ip", self.status.ip_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_disk", self.status.disk_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_apt", self.status.apt_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_load", self.status.load_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_memory", self.status.memory_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_users", self.status.users_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "status_process", self.status.process_command, filters.User(self.allowed_users)))
        self.application.add_handler(CommandHandler(
            "privacy", self.privacy.privacy, filters.User(self.allowed_users)))

        # Add error handler
        self.application.add_error_handler(self.error_handler)

        # Run the publish command function
        self.application.job_queue.run_once(
            lambda _: self.application.create_task(self.publish_command_list()), when=0)

        # Enable the Schedule Job Queue
        self.application.job_queue.run_repeating(
            self.monitor.check, interval=int(config.alert_interval), first=0)

        # Start the bot
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES, poll_interval=1, timeout=5)

    async def publish_command_list(self) -> None:
        """ Create and publish command list """
        command_list = [
            BotCommand("plex", "Get Plex stream status"),
            BotCommand("mute", "Select a alert to mute"),
            BotCommand("unmute", "Select a alert to unmute"),
            BotCommand("status_all", "Get info from all monitors"),
            BotCommand("status_ip", "Get IP monitor info"),
            BotCommand("status_disk", "Get disk monitor info"),
            BotCommand("status_apt", "Get APT monitor info"),
            BotCommand("status_load", "Get server load monitor info"),
            BotCommand("status_memory", "Get RAM/memory monitor info"),
            BotCommand("status_users", "Get logged in users monitor info"),
            BotCommand("status_process",
                       "Get different processes monitor info"),
            BotCommand("privacy", "Display the privacy policy")
        ]
        await self.application.bot.set_my_commands(command_list)

    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        """ Function for unexpected errors """
        error_message = "".join(traceback.format_exception(
            None, context.error, context.error.__traceback__))
        logger.error(f"Error happened with Telegram dispatcher: {error_message}")

    async def stop(self, update: Update, context: CallbackContext) -> None:
        """ Cancel command """
        await self.function.send_message(f"Alright, command has been stopped\\.", context)
        return ConversationHandler.END
