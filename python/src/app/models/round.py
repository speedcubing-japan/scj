from django.db import models
from django.utils import timezone
from app.defines.event import Event, Format
from app.defines.competition import RoundType, RoundLimitType, ProceedType


class Round(models.Model):

    competition_id = models.IntegerField("大会ID")
    event_id = models.SmallIntegerField("イベントID", choices=Event.choices())
    event_name = models.CharField("イベント名", max_length=64, default="")
    attempt_count = models.SmallIntegerField("挑戦回数", default=0)
    type = models.SmallIntegerField("ラウンドタイプ", choices=RoundType.choices())
    format_id = models.IntegerField("フォーマットID", choices=Format.choices())
    limit_type = models.SmallIntegerField(
        "制限タイプ", default=0, choices=RoundLimitType.choices()
    )
    limit_time = models.IntegerField("制限時間")
    cutoff_attempt_count = models.SmallIntegerField("カットオフ回数", default=0)
    cutoff_time = models.IntegerField("カットオフ時間")
    proceed_type = models.SmallIntegerField(
        "進出人数タイプ", default=0, choices=ProceedType.choices()
    )
    proceed_count = models.IntegerField("進出人数")
    proceed_rate = models.IntegerField("進出割合(100分率)", default=0)
    room_name = models.CharField("会場名", max_length=64, default="")
    begin_at = models.DateTimeField("開始時刻", default=timezone.now)
    end_at = models.DateTimeField("終了時刻", default=timezone.now)

    def create(self, round, competition_id):
        self.competition_id = competition_id
        self.event_id = round["event_id"]
        self.event_name = round["event_name"]
        self.attempt_count = round["attempt_count"]
        self.type = round["type"]
        self.format_id = round["format_id"]
        self.limit_type = round["limit_type"]
        self.limit_time = round["limit_time"]
        self.cutoff_attempt_count = round["cutoff_attempt_count"]
        self.cutoff_time = round["cutoff_time"]
        self.proceed_count = round["proceed_count"]
        self.room_name = round["room_name"]
        self.begin_at = round["begin_at"]
        self.end_at = round["end_at"]
        self.save()

    def delete(competition_id):
        Round.objects.filter(competition_id=competition_id).delete()
