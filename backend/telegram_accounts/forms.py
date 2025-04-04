from django import forms

from .models import TelegramChat
from .telegram_api import get_chat_info


class AddChatForm(forms.Form):
    chat_id = forms.CharField(label="Chat/Channel ID", help_text="Введите ID канала или чата")

    def clean_chat_id(self):
        try:
            return int(self.cleaned_data["chat_id"])
        except ValueError:
            raise forms.ValidationError("ID должен быть числом.")


class TelegramChatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = TelegramChat
        fields = ['chat_id']
        widgets = {
            'chat_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chat or Channel ID'}),
        }

    def clean_chat_id(self):
        chat_id = self.cleaned_data['chat_id']
        if TelegramChat.objects.filter(user=self.user, chat_id=chat_id).exists():
            raise forms.ValidationError("Чат с таким ID уже добавлен.")
        try:
            chat_info = get_chat_info(chat_id)
            self.cleaned_data['title'] = chat_info['title']
            self.cleaned_data['chat_type'] = chat_info['chat_type']
        except Exception as e:
            raise forms.ValidationError(f"Не удалось получить данные чата: {e}")
        return chat_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        instance.title = self.cleaned_data.get('title')
        instance.chat_type = self.cleaned_data.get('chat_type')
        if commit:
            instance.save()
        return instance
