# Generated by Django 5.1 on 2025-01-10 10:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_message_type'),
        ('item', '0011_city_rename_title_sharecircle_district_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='item.item'),
        ),
    ]