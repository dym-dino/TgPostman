# Generated by Django 5.1.8 on 2025-04-04 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduled_posts', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledpost',
            name='celery_task_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
