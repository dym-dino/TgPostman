"""
Postman bot entrypoint
Simple Telegram bot that replies with info about the Tg POSTMAN platform.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import time

from decouple import config
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException

# --------------------------------------------------------------------------------
# BOT INITIALIZATION

TOKEN = config('TELEGRAM_BOT_TOKEN')
bot = TeleBot(TOKEN)


# --------------------------------------------------------------------------------
# MESSAGE HANDLER


@bot.message_handler(
    func=lambda m: True,
    content_types=[
        'text', 'photo', 'video', 'audio',
        'document', 'sticker', 'location',
        'voice', 'contact'
    ]
)
def echo_all(message):
    """
    Handle all incoming messages and reply with a preset welcome message.

    Args:
        message (Message): Incoming Telegram message object.

    Returns:
        None
    """
    try:
        bot.send_message(
            message.chat.id,
            "Привет! Я — TG POSTMAN, ваш личный бот-автопостер.\n"
            "Нужно запланировать публикацию в группу или канале? Просто зайдите на "
            "tgpost.ru, задайте текст, время и — готово!\n"
            "Больше не теряйте время — публикуйте с умом и в нужный момент 😊"
        )
    except ApiTelegramException as e:
        print(f"[ERROR] не удалось отправить ответ: {e}")


# --------------------------------------------------------------------------------
# MAIN LOOP


if __name__ == '__main__':
    """
    Start the bot using polling with auto-restart on failure.
    """
    print("🚀 [BOT] Старт polling…")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"[BOT] Polling упал: {e}. Перезапускаем через 5 сек…")
            time.sleep(5)
