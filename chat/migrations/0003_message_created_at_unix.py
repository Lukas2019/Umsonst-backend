# Generated by Django 5.0.6 on 2024-07-15 17:29

import time
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0002_message"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="created_at_unix",
            field=models.IntegerField(default=time.time),
        ),
    ]
