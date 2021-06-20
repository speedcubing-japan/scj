from django.db import models
from .person import Person
from app.defines.gender import Gender
from app.defines.event import Event
from app.defines.prefecture import PrefectureAndOversea


class AverageRank(models.Model):

    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None) 
    event_id = models.SmallIntegerField('イベントID', choices=Event.choices())
    competition_id = models.IntegerField('大会ID')
    competition_name_id = models.CharField('大会名ID', max_length=64, default='')
    competition_name = models.CharField('大会名', max_length=64, default='')
    year = models.SmallIntegerField('年', default=0)
    best = models.FloatField('ベスト')
    value1 = models.FloatField('値1', default=0)
    value2 = models.FloatField('値2', default=0)
    value3 = models.FloatField('値3', default=0)
    value4 = models.FloatField('値4', default=0)
    value5 = models.FloatField('値5', default=0)
    gender = models.SmallIntegerField("性別", default=0, choices=Gender.choices())
    generation = models.SmallIntegerField("世代", default=0)
    prefecture_id = models.SmallIntegerField("都道府県ID", default=0, choices=PrefectureAndOversea.choices())
    rank = models.IntegerField('ランク', default=0)
    gender_rank = models.IntegerField('性別ランク', default=0)
    generation_rank = models.IntegerField('世代ランク', default=0)
    prefecture_rank = models.IntegerField('県ランク', default=0)

    class Meta:
        indexes = [
            models.Index(name='idx_person', fields=['person'])
        ]

    def __str__(self):
        return str(self.person_id)