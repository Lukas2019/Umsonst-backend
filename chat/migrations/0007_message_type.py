# Generated by Django 5.1 on 2025-01-07 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_message_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='type',
            field=models.CharField(choices=[('text', 'Text'), ('location', 'Location'), ('item', 'Item')], default='text', max_length=100),
        ),
    ]
