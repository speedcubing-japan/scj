from django.db import models
from django.utils import timezone
from app.defines.event import Event, Format
from app.defines.competition import RoundType, RoundLimitType


class Round(models.Model):

    id = models.IntegerField('ラウンドID', primary_key=True)
    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=Event.choices())
    event_name = models.CharField('イベント名', max_length=64, default='')
    attempt_count = models.SmallIntegerField('挑戦回数', default=0)
    type = models.SmallIntegerField('ラウンドタイプ', choices=RoundType.choices())
    format_id = models.IntegerField('フォーマットID', choices=Format.choices())
    limit_type = models.SmallIntegerField('制限タイプ', default=0, choices=RoundLimitType.choices())
    limit_time = models.IntegerField('制限時間')
    cutoff_attempt_count = models.SmallIntegerField('カットオフ回数', default=0)
    cutoff_time = models.IntegerField('カットオフ時間')
    proceed_count = models.IntegerField('通過人数')
    room_name = models.CharField('会場名', max_length=64, default='')
    begin_at = models.DateTimeField('開始時刻', default=timezone.now)
    end_at = models.DateTimeField('終了時刻', default=timezone.now)