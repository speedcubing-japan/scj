# Generated by Django 2.2.12 on 2021-05-22 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20210523_0012'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitor',
            name='pay_price',
            field=models.IntegerField(default=0, verbose_name='支払額'),
        ),
    ]