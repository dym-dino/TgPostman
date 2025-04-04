"""
Post sender

This file contains logic for sending scheduled posts to Telegram chats using the TeleBot library.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from decouple import config
from telebot import TeleBot

from .models import ScheduledPost

# --------------------------------------------------------------------------------
# BOT INITIALIZATION

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
bot = TeleBot(token=BOT_TOKEN)


# --------------------------------------------------------------------------------
# SEND FUNCTION

def send_post(post: ScheduledPost) -> None:
    """
    Send the given ScheduledPost to all its target Telegram chats and delete the file after sending.

    :param post: ScheduledPost instance containing content and target chats
    :raises Exception: If sending fails for any of the target chats
    """
    for chat in post.targets.all():
        try:
            if post.file:
                # Open the file and send it
                with post.file.open("rb") as f:
                    bot.send_document(
                        chat.chat_id,
                        f,
                        caption=None if post.html else post.content,
                        parse_mode="HTML" if post.html else None
                    )

            else:
                bot.send_message(
                    chat.chat_id,
                    text=post.content,
                    parse_mode="HTML" if post.html else None
                )

        except Exception as e:
            raise Exception(f"Failed to send to {chat.chat_id}: {e}")

    # Delete the file after sending
    if post.file:
        post.file.delete()
