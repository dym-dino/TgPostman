from django.conf import settings
from django.db import models


class TelegramChat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField()
    chat_type = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=255)
    can_post = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat_id')

    def __str__(self):
        return f"{self.title} ({self.chat_id})"
