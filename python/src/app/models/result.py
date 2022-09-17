from django.db import models
from app.defines.event import Event
from app.defines.competition import RoundType


class Result(models.Model):

    competition_id = models.IntegerField("大会ID")
    event_id = models.SmallIntegerField("イベントID", choices=Event.choices())
    person_id = models.IntegerField("競技者ID")
    round_type = models.SmallIntegerField(
        "ラウンドタイプ", choices=RoundType.choices(), default=0
    )
    rank = models.SmallIntegerField("順位")
    best = models.FloatField("Best")
    average = models.FloatField("Average")
    value1 = models.FloatField("値1")
    value2 = models.FloatField("値2")
    value3 = models.FloatField("値3")
    value4 = models.FloatField("値4")
    value5 = models.FloatField("値5")

    round_name = ""
    format_values = []

    class Meta:
        indexes = [models.Index(name="idx_competition_id", fields=["competition_id"])]

    def set_round_name(self, round_name):
        self.round_name = round_name

    def __str__(self):
        return (
            str(self.competition_id)
            + "_"
            + str(self.event_id)
            + "_"
            + str(self.round_type)
            + "_"
            + str(self.person_id)
        )
