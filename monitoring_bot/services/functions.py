#!/usr/bin/python3

import re
from services.logger import logger


class Functions:

    # Send standard text message
    async def send_message(self, text: str, update, context, reply_markup=None, parse_mode='MarkdownV2') -> None:

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )

        # Debug log
        logger.debug(text)
