from django.db import models
from django_mysql.models import JSONField
from .person import Person
from app.defines.competitor import Status as CompetitorStatus


class Competitor(models.Model):

    competition_id = models.IntegerField("大会ID")
    status = models.SmallIntegerField('状態', choices=CompetitorStatus.choices())
    event_ids = JSONField('申し込み種目ID')
    guest_count = models.SmallIntegerField('見学者数')
    comment = models.TextField('コメント')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    stripe_progress = None

    class Meta:
        indexes = [
            models.Index(name='idx_competition_id_person', fields=['competition_id', 'person'])
        ]

    def set_stripe_progress(self, stripe_progress):
        self.stripe_progress = stripe_progress

    def __str__(self):
        return self.competition.name + ' [' + self.person.get_full_name() + ']'