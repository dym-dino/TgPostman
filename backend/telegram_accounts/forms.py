"""
Telegram chat forms
Forms for adding and validating Telegram chat/channel data.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django import forms

from .models import TelegramChat
from .telegram_api import get_chat_info

# --------------------------------------------------------------------------------


class AddChatForm(forms.Form):
    """
    Basic form for entering a chat/channel ID manually.

    Fields:
        chat_id (str): Raw input representing the chat/channel ID.

    Returns:
        Cleaned data containing the integer chat ID.
    """

    chat_id = forms.CharField(
        label="Chat/Channel ID",
        help_text="Введите ID канала или чата"
    )

    def clean_chat_id(self):
        """
        Validate that chat_id is a valid integer.

        Returns:
            int: Parsed chat ID.

        Raises:
            ValidationError: If the input is not a valid number.
        """
        try:
            return int(self.cleaned_data["chat_id"])
        except ValueError:
            raise forms.ValidationError("ID должен быть числом.")

# --------------------------------------------------------------------------------


class TelegramChatForm(forms.ModelForm):
    """
    ModelForm for adding a Telegram chat with validation and enrichment.

    Args:
        user (User): The user adding the chat.

    Returns:
        TelegramChat: Saved chat instance linked to the user.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TelegramChat
        fields = ['chat_id']
        widgets = {
            'chat_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chat or Channel ID'
            }),
        }

    def clean_chat_id(self):
        """
        Validate uniqueness and retrieve chat metadata via API.

        Returns:
            int: Validated chat ID.

        Raises:
            ValidationError: If chat already exists or info cannot be retrieved.
        """
        chat_id = self.cleaned_data['chat_id']
        if TelegramChat.objects.filter(user=self.user, chat_id=chat_id).exists():
            raise forms.ValidationError("Чат с таким ID уже добавлен.")
        try:
            chat_info = get_chat_info(chat_id)
            self.cleaned_data['title'] = chat_info['title']
            self.cleaned_data['chat_type'] = chat_info['chat_type']
            self.cleaned_data['url'] = chat_info['url']
        except Exception as e:
            raise forms.ValidationError(f"Не удалось получить данные чата: {e}")
        return chat_id

    def save(self, commit=True):
        """
        Save the chat instance with additional API metadata.

        Args:
            commit (bool): Whether to save to the database immediately.

        Returns:
            TelegramChat: The created or updated instance.
        """
        instance = super().save(commit=False)
        instance.user = self.user
        instance.title = self.cleaned_data.get('title')
        instance.chat_type = self.cleaned_data.get('chat_type')
        instance.url = self.cleaned_data.get('url')
        if commit:
            instance.save()
        return instance
