# Generated by Django 2.2.24 on 2022-03-31 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20220327_1026'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='stripeprogress',
            index=models.Index(fields=['charge_id'], name='idx_charge_id'),
        ),
    ]
