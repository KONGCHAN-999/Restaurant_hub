# Generated by Django 4.2.4 on 2024-04-29 04:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0026_notice"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Notice",
            new_name="NoticeModel",
        ),
    ]
