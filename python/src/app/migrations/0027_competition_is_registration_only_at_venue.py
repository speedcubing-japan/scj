# Generated by Django 2.2.24 on 2022-04-02 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20220331_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='is_registration_only_at_venue',
            field=models.BooleanField(default=False, verbose_name='現地申込みフラグ'),
        ),
    ]