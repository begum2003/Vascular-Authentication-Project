# Generated by Django 4.0 on 2023-09-19 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0007_rename_usernames_palm_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='palm',
            name='username',
        ),
    ]
