# Generated by Django 5.0.6 on 2024-07-15 18:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0004_remove_message_created_at_unix"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="chat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="chat.chat",
            ),
        ),
    ]
