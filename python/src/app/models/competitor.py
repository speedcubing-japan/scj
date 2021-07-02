from django.db import models
from django_mysql.models import JSONField
from .person import Person
from app.defines.competitor import Status as CompetitorStatus
from app.defines.competition import Type as CompetitionType 


class Competitor(models.Model):

    competition_id = models.IntegerField("大会ID")
    status = models.SmallIntegerField('状態', choices=CompetitorStatus.choices())
    event_ids = JSONField('申し込み種目ID')
    guest_count = models.SmallIntegerField('同伴者数')
    comment = models.TextField('コメント')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    stripe_progress = None
    is_duplicated_twin_competitions = False

    class Meta:
        indexes = [
            models.Index(name='idx_competition_id_person', fields=['competition_id', 'person'])
        ]
    
    def get_specific_id(self, competition_type):
        specific_id = None
        if competition_type == CompetitionType.SCJ.value:
            specific_id = self.person.id
        elif competition_type == CompetitionType.WCA.value:
            specific_id = self.person.wca_id
        return specific_id

    def set_stripe_progress(self, stripe_progress):
        self.stripe_progress = stripe_progress

    def unset_stripe_progress(self):
        self.stripe_progress = None

    def set_is_duplicated_twin_competitions(self):
        self.is_duplicated_twin_competitions = True

    def __str__(self):
        return self.competition.name + ' [' + self.person.get_full_name() + ']'