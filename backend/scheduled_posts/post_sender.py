"""
Telegram post sender
Functions for preparing and sending scheduled posts via Telegram.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import asyncio
import io
import mimetypes
import os
from typing import Optional

from decouple import config
from googletrans import Translator
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import (
    InputMediaPhoto, InputMediaVideo,
    InputMediaAudio, InputMediaDocument,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from chat_groups.models import ChatGroupMember
from .models import ScheduledPost

# --------------------------------------------------------------------------------
# CONSTANTS

MAX_MEDIA_SIZE = 5 * 1024 * 1024  # 5MB file size limit

IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
VIDEO_EXT = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.mpeg', '.mpg'}
AUDIO_EXT = {'.mp3', '.ogg', '.wav', '.m4a', '.aac', '.flac'}

# --------------------------------------------------------------------------------
# BOT INITIALIZATION

BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
bot = TeleBot(token=BOT_TOKEN)
translator = Translator()

# --------------------------------------------------------------------------------
# HELPER FUNCTIONS


def _translate_text(text: str, dest: str) -> str:
    """
    Translate text into target language using Google Translate.

    Args:
        text (str): Source text.
        dest (str): Target language code.

    Returns:
        str: Translated text.
    """
    result = translator.translate(text, dest=dest)
    if asyncio.iscoroutine(result):
        result = asyncio.get_event_loop().run_until_complete(result)
    return getattr(result, 'text', text)


def _get_mime_type(filename: str, file_field=None) -> str:
    """
    Determine MIME type of a file based on extension and size.

    Args:
        filename (str): File name to examine.
        file_field (File): File object for size check.

    Returns:
        str: Guessed MIME type or fallback.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext in IMAGE_EXT:
        category = 'image'
    elif ext in VIDEO_EXT:
        category = 'video'
    elif ext in AUDIO_EXT:
        category = 'audio'
    else:
        return 'application/octet-stream'

    if file_field:
        try:
            if file_field.size > MAX_MEDIA_SIZE:
                return 'application/octet-stream'
        except Exception:
            pass

    mime_type = mimetypes.guess_type(filename)[0]
    return mime_type or f"{category}/*"


def _choose_send_mode(attachments) -> str:
    """
    Decide how to send the post depending on attachment types.

    Args:
        attachments (list): List of attachments.

    Returns:
        str: Sending mode: 'text', 'media_group', or 'doc_group'.
    """
    if not attachments:
        return 'text'
    mimes = [_get_mime_type(att.original_name, att.file).lower() for att in attachments]
    if all(m.startswith(('image', 'video', 'audio')) for m in mimes):
        return 'media_group'
    return 'doc_group'

# --------------------------------------------------------------------------------


class Recipient:
    """
    Represents a Telegram message recipient with optional button.

    Args:
        chat_id (int): Telegram chat ID.
        message_text (str): Translated message text.
        button_text (str): Translated inline button text.
    """

    def __init__(
        self,
        chat_id: int,
        message_text: Optional[str] = None,
        button_text: Optional[str] = None
    ):
        self.chat_id = chat_id
        self.message_text = message_text
        self.button_text = button_text

# --------------------------------------------------------------------------------


def send_post(post: ScheduledPost) -> None:
    """
    Send a scheduled post to all associated recipients.

    Args:
        post (ScheduledPost): Post instance to send.

    Returns:
        None
    """
    if post.status.lower() != 'pending':
        return

    parse_mode = 'HTML' if post.html else None

    recipients = []
    seen = set()

    # Collect from groups
    for group in post.groups.all():
        for member in ChatGroupMember.objects.filter(group=group):
            if member.chat_id in seen:
                continue
            seen.add(member.chat_id)
            text = _translate_text(post.content, dest=member.language) if post.content else ''
            btn_text = None
            if post.button_url and post.button_text:
                btn_text = _translate_text(post.button_text, dest=member.language)
            recipients.append(Recipient(chat_id=member.chat_id, message_text=text, button_text=btn_text))

    # Collect from individual targets
    for chat in post.targets.all():
        if chat.chat_id in seen:
            continue
        seen.add(chat.chat_id)
        recipients.append(Recipient(
            chat_id=chat.chat_id,
            message_text=post.content or '',
            button_text=post.button_text if post.button_url and post.button_text else None
        ))

    attachments = list(post.attachments.all())
    mode = _choose_send_mode(attachments)

    for rec in recipients:
        markup = None
        if rec.button_text and post.button_url:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text=rec.button_text, url=post.button_url))

        if mode == 'text':
            bot.send_message(
                chat_id=rec.chat_id,
                text=rec.message_text,
                parse_mode=parse_mode,
                reply_markup=markup
            )
            continue

        if len(attachments) == 1:
            att = attachments[0]
            data = att.file.open('rb').read()
            bio = io.BytesIO(data)
            bio.name = att.original_name
            bio.seek(0)
            mime = _get_mime_type(att.original_name, att.file).lower()

            send_kwargs = {'chat_id': rec.chat_id, 'reply_markup': markup}
            if rec.message_text:
                send_kwargs.update({'caption': rec.message_text, 'parse_mode': parse_mode})

            if mime.startswith('image'):
                bot.send_photo(photo=bio, **send_kwargs)
            elif mime.startswith('video'):
                bot.send_video(video=bio, **send_kwargs)
            elif mime.startswith('audio'):
                bot.send_audio(audio=bio, **send_kwargs)
            else:
                bot.send_document(document=bio, **send_kwargs)
            continue

        blobs = []
        for att in attachments:
            data = att.file.open('rb').read()
            bio = io.BytesIO(data)
            bio.name = att.original_name
            bio.seek(0)
            mime = _get_mime_type(att.original_name, att.file).lower()
            if mode == 'media_group':
                if mime.startswith('image'):
                    blobs.append(InputMediaPhoto(media=bio))
                elif mime.startswith('video'):
                    blobs.append(InputMediaVideo(media=bio))
                elif mime.startswith('audio'):
                    blobs.append(InputMediaAudio(media=bio))
            else:
                blobs.append(InputMediaDocument(media=bio))

        if rec.message_text:
            if mode == 'media_group':
                blobs[0].caption = rec.message_text
                blobs[0].parse_mode = parse_mode
            else:
                blobs[-1].caption = rec.message_text
                blobs[-1].parse_mode = parse_mode

        try:
            bot.send_media_group(chat_id=rec.chat_id, media=blobs)
        except ApiTelegramException:
            for idx, att in enumerate(attachments):
                data = att.file.open('rb').read()
                bio = io.BytesIO(data)
                bio.name = att.original_name
                bio.seek(0)
                kwargs = {}
                if idx == len(attachments) - 1 and rec.message_text:
                    kwargs.update({'caption': rec.message_text, 'parse_mode': parse_mode})
                if idx == len(attachments) - 1:
                    kwargs['reply_markup'] = markup
                bot.send_document(chat_id=rec.chat_id, document=bio, **kwargs)
