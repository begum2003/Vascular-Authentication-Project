# Generated by Django 4.0 on 2023-11-24 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0011_h5model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='palm',
            name='accnum',
        ),
        migrations.RemoveField(
            model_name='palm',
            name='acctype',
        ),
    ]
