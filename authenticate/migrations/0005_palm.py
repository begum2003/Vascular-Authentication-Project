# Generated by Django 4.0 on 2023-09-18 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0004_rename_accesslevel_users_accnumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='Palm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accnum', models.IntegerField()),
                ('acctype', models.CharField(max_length=150)),
                ('usernames', models.CharField(max_length=150)),
                ('phnumber', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='pics/')),
            ],
        ),
    ]
