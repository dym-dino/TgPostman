# Generated by Django 5.1.8 on 2025-04-04 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scheduled_posts', '0001_initial'),
        ('telegram_accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledpost',
            name='targets',
            field=models.ManyToManyField(to='telegram_accounts.telegramchat'),
        ),
    ]
