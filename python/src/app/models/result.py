from django.db import models
from .round import Round
from app.defines.event import Event


class Result(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=Event.choices())
    person_id = models.IntegerField('競技者ID')
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    rank = models.SmallIntegerField('順位')
    best = models.FloatField('Best')
    average = models.FloatField('Average')
    value1 = models.FloatField('値1')
    value2 = models.FloatField('値2')
    value3 = models.FloatField('値3')
    value4 = models.FloatField('値4')
    value5 = models.FloatField('値5')

    class Meta:
        indexes = [
            models.Index(name='idx_competition_id', fields=['competition_id'])
        ]

    def __str__(self):
        return str(self.competition_id) + '_' + str(self.event_id) + '_' + str(self.round_id) + '_' + str(self.person_id)