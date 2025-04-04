"""
Telegram chat info

This file contains logic for interacting with the Telegram bot API to retrieve chat information.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from decouple import config
from telebot import TeleBot

# --------------------------------------------------------------------------------
# BOT INITIALIZATION

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
bot = TeleBot(token=BOT_TOKEN)

# --------------------------------------------------------------------------------
# FUNCTION DEFINITION

def get_chat_info(chat_id: int) -> dict:
    """
    Retrieve information about a Telegram chat, such as title, posting permissions, and chat type.

    :param chat_id: The ID of the chat to retrieve information about
    :return: A dictionary containing the chat's title, post permission, and type
    :raises ValueError: If the chat info cannot be fetched
    """
    try:
        chat = bot.get_chat(chat_id)
        return {
            "title": chat.title or chat.username,
            "can_post": chat.type in ("group", "supergroup", "channel"),
            "chat_type": chat.type,
        }
    except Exception as e:
        raise ValueError(f"Telegram error: {e}")
