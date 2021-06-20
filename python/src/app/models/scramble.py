from django.db import models
from app.defines.event import Event


class Scramble(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=Event.choices())
    round_id = models.IntegerField('ラウンドID')
    group_id = models.CharField('グループID', max_length=4)
    scramble = models.CharField('スクランブル', max_length=64)