# Generated by Django 2.2.24 on 2022-03-11 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20211121_1946'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='stripe_customer_id',
        ),
        migrations.AlterField(
            model_name='round',
            name='limit_type',
            field=models.SmallIntegerField(choices=[(1, 'LIMIT'), (2, 'CUMULATIVE')], default=0, verbose_name='制限タイプ'),
        ),
    ]
