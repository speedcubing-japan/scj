# Generated by Django 2.2.24 on 2022-12-15 02:09

from django.db import migrations
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0038_auto_20221002_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='twin_competition_id',
        ),
        migrations.AddField(
            model_name='competition',
            name='series_competition_ids',
            field=django_mysql.models.JSONField(default=0, verbose_name='シリーズ大会ID'),
        ),
    ]