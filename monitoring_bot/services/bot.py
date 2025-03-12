#!/usr/bin/python3

import traceback

# from states import VERIFY
from config import config
from services.logger import logger
from services.functions import Functions
from services.commands.help import Help
from services.commands.status import Status
from services.monitor import Monitor

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

    def __init__(self):

        # Set classes
        self.function = Functions()
        self.help = Help(self.function)
        self.status = Status(self.function)
        self.monitor = Monitor(self.function)

        # Create the Application using the new async API
        self.application = Application.builder().token(config.bot_token).concurrent_updates(False).read_timeout(300).build(
        ) if config.env == "live" else Application.builder().token(config.bot_token_dev).concurrent_updates(False).read_timeout(300).build()

        # Add conversation handler with different states
        # self.application.add_handler(ConversationHandler(
        #     entry_points=[CommandHandler("mute", self.start.start_msg)],
        #     states={
        #         VERIFY: [
        #             CallbackQueryHandler(
        #                 self.start.verification, pattern="^(movie_request|serie_request)$"),
        #             CallbackQueryHandler(
        #                 self.start.parse_request, pattern="^account_request$"),
        #             CallbackQueryHandler(
        #                 self.help.help_command_button, pattern='^info$')
        #         ],
        #         VERIFY_PWD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.start.verify_pwd)],
        #         REQUEST_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.account.request_account)],
        #         REQUEST_ACCOUNT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.account.request_account_email)],
        #         REQUEST_ACCOUNT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.account.request_account_phone)],
        #         REQUEST_ACCOUNT_REFER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.account.request_account_refer)],
        #         REQUEST_MOVIE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.movie.request_media)],
        #         REQUEST_SERIE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.serie.request_media)],
        #         MOVIE_OPTION: [CallbackQueryHandler(self.movie.media_option, pattern="^(0|1|2|3|4)$")],
        #         SERIE_OPTION: [CallbackQueryHandler(self.serie.media_option, pattern="^(0|1|2|3|4)$")],
        #         MOVIE_NOTIFY: [CallbackQueryHandler(self.movie.stay_notified, pattern="^(film_notify_yes|film_notify_no)$")],
        #         SERIE_NOTIFY: [CallbackQueryHandler(self.serie.stay_notified, pattern="^(serie_notify_yes|serie_notify_no)$")],
        #         MOVIE_UPGRADE: [CallbackQueryHandler(self.movie.media_upgrade, pattern="^(film_upgrade_yes|film_upgrade_no)$")],
        #         SERIE_UPGRADE: [CallbackQueryHandler(self.serie.media_upgrade, pattern="^(serie_upgrade_yes|serie_upgrade_no)$")],
        #         SERIE_UPGRADE_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.serie.media_upgrade_option)]
        #     },
        #     fallbacks=[CommandHandler("stop", self.stop)],
        #     conversation_timeout=86400
        # )
        # )

        # Add stand-alone handlers
        self.application.add_handler(CommandHandler("help", self.help.help_command))
        self.application.add_handler(CommandHandler("status_all", self.status.all_command))
        self.application.add_handler(CommandHandler("status_ip", self.status.ip_command))
        self.application.add_handler(CommandHandler("status_disk", self.status.disk_command))
        self.application.add_handler(CommandHandler("status_apt", self.status.apt_command))
        self.application.add_handler(CommandHandler("status_load", self.status.load_command))
        self.application.add_handler(CommandHandler("status_memory", self.status.memory_command))
        self.application.add_handler(CommandHandler("status_users", self.status.users_command))
        self.application.add_handler(CommandHandler("status_process", self.status.process_command))

        # Add error handler
        self.application.add_error_handler(self.error_handler)

        # Run the publish command function
        self.application.job_queue.run_once(lambda _: self.application.create_task(self.publish_command_list()), when=0)

        # Enable the Schedule Job Queue
        self.application.job_queue.run_repeating(self.monitor.check, interval=3, first=0)

        # Start the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=1, timeout=5)


    async def publish_command_list(self):
        """ Create and publish command list """
        command_list = [
            BotCommand("help", "See the help info"),
            BotCommand("status_all", "Get info from all monitors"),
            BotCommand("status_ip", "Get IP monitor info"),
            BotCommand("status_disk", "Get disk monitor info"),
            BotCommand("status_apt", "Get APT monitor info"),
            BotCommand("status_load", "Get server load monitor info"),
            BotCommand("status_memory", "Get RAM/memory monitor info"),
            BotCommand("status_users", "Get logged in users monitor info"),
            BotCommand("status_process", "Get different processes monitor info")
        ]
        await self.application.bot.set_my_commands(command_list)


    async def error_handler(self, update: Update, context: CallbackContext) -> None:
        """ Function for unexpted errors """
        error_message = "".join(traceback.format_exception(None, context.error, context.error.__traceback__))
        logger.error(f"Error happened with Telegram dispatcher: {error_message}")


    async def stop(self, update: Update, context: CallbackContext) -> None:
        """ Cancel command """
        await self.function.send_message(f"Alright, command has been stopped.", update, context)
        return ConversationHandler.END
