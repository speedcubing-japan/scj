# Generated by Django 2.2.24 on 2022-06-10 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20220421_1012'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='proceed_rate',
            field=models.IntegerField(default=0, verbose_name='進出割合(100分率)'),
        ),
        migrations.AddField(
            model_name='round',
            name='proceed_type',
            field=models.SmallIntegerField(choices=[(0, 'NONE'), (1, 'COUNT'), (2, 'RATE')], default=0, verbose_name='進出人数タイプ'),
        ),
        migrations.AlterField(
            model_name='round',
            name='proceed_count',
            field=models.IntegerField(verbose_name='進出人数'),
        ),
    ]