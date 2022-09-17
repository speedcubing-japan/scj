from django.db import models
from app.defines.event import Event
from app.defines.competition import RoundType


class Scramble(models.Model):

    competition_id = models.IntegerField("大会ID")
    event_id = models.SmallIntegerField("イベントID", choices=Event.choices())
    round_type = models.SmallIntegerField(
        "ラウンドタイプ", choices=RoundType.choices(), default=0
    )
    group_id = models.CharField("グループID", max_length=4)
    scramble = models.TextField("スクランブル")
