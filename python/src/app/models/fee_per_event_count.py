from django.db import models


class FeePerEventCount(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_count = models.SmallIntegerField('イベント数')
    price = models.IntegerField('料金')