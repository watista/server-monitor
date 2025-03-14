#!/usr/bin/python3

import re
from services.logger import logger
from telegram.error import RetryAfter


class Functions:

    # Send standard text message
    async def send_message(self, text: str, update, context, reply_markup=None, parse_mode='MarkdownV2', regular=True) -> None:

        # Check if the user_id is regular or special
        chat_id = update.effective_user.id if regular else update
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text[:1024],
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await context.bot.send_message(
                chat_id=chat_id,
                text=text[:1024],
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

        # Debug log
        logger.debug(text)
