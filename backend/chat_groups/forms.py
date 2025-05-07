"""
Chat group forms
Forms for managing chat groups and members.
"""

# --------------------------------------------------------------------------------

from django import forms

from telegram_accounts.models import TelegramChat
from .models import ChatGroup, ChatGroupMember

# --------------------------------------------------------------------------------


class ChatGroupForm(forms.ModelForm):
    """
    Form for creating or editing a chat group.

    Meta:
        model (ChatGroup): Model used for the form.
        fields (list): Fields included in the form.
        labels (dict): Labels for form fields.
        widgets (dict): Widget customization for fields.
    """

    class Meta:
        model = ChatGroup
        fields = ['name']
        labels = {'name': 'Название группы'}
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя группы'
            })
        }

# --------------------------------------------------------------------------------


class ChatGroupMemberForm(forms.ModelForm):
    """
    Form for adding a chat to a group.

    Args:
        user (User): The user whose chats are shown.
        group (ChatGroup): The group to filter out existing chats from.

    Returns:
        Form instance with customized chat and language choices.
    """

    chat_id = forms.ChoiceField(
        label='Чат/канал',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = ChatGroupMember
        fields = ['chat_id', 'language']
        labels = {'language': 'Язык чата'}
        widgets = {
            'language': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, user=None, group=None, **kwargs):
        """
        Initialize the form with filtered chat choices and modified language choices.

        Args:
            *args: Positional arguments for the form.
            user (User): User whose Telegram chats are fetched.
            group (ChatGroup): Group used to exclude existing members.
            **kwargs: Keyword arguments for the form.
        """
        super().__init__(*args, **kwargs)

        chats = TelegramChat.objects.filter(user=user)
        if group is not None:
            existing = group.members.values_list('chat_id', flat=True)
            chats = chats.exclude(chat_id__in=existing)

        choices = []
        for chat in chats:
            name = chat.title or str(chat.chat_id)
            username = ''
            if chat.url:
                username = '@' + chat.url.replace('https://t.me/', '')
            display = f"{name} ({chat.chat_id}{' ' + username if username else ''})"
            choices.append((str(chat.chat_id), display))

        choices.insert(0, ('', '— выберите чат —'))
        self.fields['chat_id'].choices = choices

        lang_choices = list(self.fields['language'].choices)
        lang_choices.insert(0, ('', '— выберите язык —'))
        self.fields['language'].choices = lang_choices
