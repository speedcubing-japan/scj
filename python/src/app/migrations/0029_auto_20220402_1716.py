# Generated by Django 2.2.24 on 2022-04-02 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_auto_20220402_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='competition',
            name='is_registration_only_at_venue',
        ),
        migrations.AddField(
            model_name='competition',
            name='is_registration_at_other',
            field=models.BooleanField(default=False, verbose_name='他で申込みをするか'),
        ),
    ]