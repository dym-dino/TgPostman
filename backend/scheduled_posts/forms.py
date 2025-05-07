"""
Post creation form
Form for creating and scheduling posts with attachments and buttons.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from datetime import timedelta

from django import forms
from django.utils import timezone

from chat_groups.models import ChatGroup
from telegram_accounts.models import TelegramChat

# --------------------------------------------------------------------------------


class MultiFileInput(forms.ClearableFileInput):
    """
    Custom file input widget allowing multiple file selection.

    Returns:
        List of uploaded files.
    """
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)

# --------------------------------------------------------------------------------


class MultiFileField(forms.FileField):
    """
    Custom file field to handle multiple file uploads.

    Args:
        required (bool): Whether the field is required.

    Returns:
        List of cleaned files if valid, raises ValidationError otherwise.
    """
    widget = MultiFileInput

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        if len(files) > 10:
            raise forms.ValidationError("Нельзя прикреплять более 10 файлов.")
        cleaned_files = []
        errors = []
        for f in files:
            try:
                cleaned = super().clean(f, initial)
                cleaned_files.append(cleaned)
            except forms.ValidationError as e:
                errors.extend(e.error_list)
        if errors:
            raise forms.ValidationError(errors)
        return cleaned_files

# --------------------------------------------------------------------------------


class CreatePostForm(forms.Form):
    """
    Form for creating and scheduling a Telegram post.

    Includes content, file attachments, optional inline button,
    target chats/groups, and scheduling options.

    Args:
        user (User): Current authenticated user for filtering chats/groups.

    Returns:
        A configured form instance for post creation.
    """

    content = forms.CharField(
        widget=forms.Textarea,
        label="Сообщение",
        help_text="Можно использовать HTML"
    )
    html = forms.BooleanField(
        required=False,
        initial=True,
        label="Интерпретировать как HTML"
    )
    files = MultiFileField(
        label="Прикрепить файлы",
        help_text="Не более 10 файлов",
        widget=MultiFileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'style': 'max-width: 300px;'
        })
    )
    button_text = forms.CharField(
        label="Текст кнопки",
        required=False,
        help_text="Текст для inline-кнопки"
    )
    button_url = forms.URLField(
        label="Ссылка кнопки",
        required=False,
        help_text="URL для inline-кнопки"
    )
    targets = forms.ModelMultipleChoiceField(
        queryset=TelegramChat.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'multiple': 'multiple'
        }),
        required=False,
        label='Чаты/каналы'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=ChatGroup.objects.none(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'multiple': 'multiple'
        }),
        required=False,
        label='Группы чатов'
    )
    schedule_option = forms.ChoiceField(
        choices=[('delay', 'Задержка'), ('time', 'Точная дата')],
        initial='time',
        widget=forms.RadioSelect(),
        label="Выберите тип планирования"
    )
    delay_seconds = forms.IntegerField(
        label="Задержка (сек)",
        initial=60,
        required=False
    )
    schedule_time = forms.DateTimeField(
        label="Время отправки",
        required=False,
        widget=forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize form fields with user-specific chat and group options.

        Args:
            user (User): Authenticated user passed via kwargs.
        """
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["targets"].queryset = TelegramChat.objects.filter(user=user)
        self.fields["groups"].queryset = ChatGroup.objects.filter(user=user)
        now_local = timezone.localtime(timezone.now())
        default_dt = now_local + timedelta(minutes=10)
        self.fields['schedule_time'].initial = default_dt.strftime('%Y-%m-%dT%H:%M')
