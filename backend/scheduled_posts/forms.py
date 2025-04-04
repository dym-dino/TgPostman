"""
Create post form

This file defines the form for creating scheduled posts in the Django admin panel.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django import forms

from telegram_accounts.models import TelegramChat

# --------------------------------------------------------------------------------
# FORM DEFINITION

class CreatePostForm(forms.Form):
    """
    Form for creating a scheduled post, including content, HTML option, file upload,
    target chats, and delay in seconds.
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
    file = forms.FileField(
        required=False,
        label="Прикрепить файл"
    )
    targets = forms.ModelMultipleChoiceField(
        queryset=TelegramChat.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Куда отправить"
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
        Override the initializer to set the queryset for 'targets' based on the current user.
        :param args: Positional arguments passed to the parent constructor
        :param kwargs: Keyword arguments, expects 'user' to be present
        """
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["targets"].queryset = TelegramChat.objects.filter(user=user)
