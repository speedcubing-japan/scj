# Generated by Django 2.2.24 on 2021-07-10 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0012_person_is_event_offerer"),
    ]

    operations = [
        migrations.AddField(
            model_name="competition",
            name="is_enabled",
            field=models.BooleanField(default=False, verbose_name="有効可否"),
        ),
    ]
