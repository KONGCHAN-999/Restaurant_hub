# Generated by Django 4.2.4 on 2024-04-30 09:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0029_remove_noticemodel_date_remove_noticemodel_detail"),
    ]

    operations = [
        migrations.RenameField(
            model_name="noticemodel",
            old_name="title",
            new_name="subject",
        ),
    ]
