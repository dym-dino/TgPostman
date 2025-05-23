# Generated by Django 5.1.8 on 2025-05-05 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.BigIntegerField()),
                ('chat_type', models.CharField(blank=True, max_length=32)),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True)),
                ('can_post', models.BooleanField(default=False)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
