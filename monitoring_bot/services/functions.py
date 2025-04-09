#!/usr/bin/python3

from config import config
from services.logger import logger
from telegram.error import RetryAfter


class Functions:

    # Send standard text message
    async def send_message(self, text: str, context, reply_markup=None, parse_mode='MarkdownV2') -> None:

        # Split all words on spaces
        words = text.split(' ')
        messages = []
        current_chunk = ""

        # Loop through all words to create chunks
        for word in words:
            if len(current_chunk) + len(word) + 1 > 1024:
                messages.append(current_chunk)
                # Start a new chunk
                current_chunk = word
            else:
                # Append word to current chunk
                current_chunk += (" " if current_chunk else "") + word

        # Add last chunk if not empty
        if current_chunk:
            messages.append(current_chunk)

        for message in messages:
            while True:
                try:
                    await context.bot.send_message(
                        chat_id=config.chat_id,
                        text=message,
                        parse_mode=parse_mode,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True
                    )
                    break
                except RetryAfter as e:
                    await asyncio.sleep(e.retry_after)
                    await context.bot.send_message(
                        chat_id=config.chat_id,
                        text=message,
                        parse_mode=parse_mode,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True
                    )

        # Debug log
        logger.debug(text)
