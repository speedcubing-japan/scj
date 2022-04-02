from django.db import models
from django_mysql.models import JSONField
from .person import Person
from app.defines.competitor import Status as CompetitorStatus
from app.defines.competition import Type as CompetitionType


class Competitor(models.Model):

    competition_id = models.IntegerField("大会ID")
    status = models.SmallIntegerField("状態", choices=CompetitorStatus.choices())
    event_ids = JSONField("申し込み種目ID")
    guest_count = models.SmallIntegerField("同伴者数")
    comment = models.TextField("コメント")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    stripe_progress = None
    is_duplicated_twin_competitions = False
    is_diffrence_event_and_price = False

    class Meta:
        indexes = [
            models.Index(
                name="idx_competition_id_person", fields=["competition_id", "person"]
            )
        ]

    def get_competitor(self, competition_id, person_id):
        competitor = Competitor.objects.filter(
            competition_id=competition_id, person_id=person_id
        )

        if competitor.exists():
            return competitor.first()

        return None

    def get_specific_id(self, competition_type):
        specific_id = None
        if competition_type == CompetitionType.SCJ.value:
            specific_id = self.person.id
        elif competition_type == CompetitionType.WCA.value:
            specific_id = self.person.wca_id
        return specific_id

    def get_count_by_status(self, competition_id, status):
        return Competitor.objects.filter(
            competition_id=competition_id, status=status
        ).count()

    def exist(self, competition_id, person_id):
        return Competitor.objects.filter(
            competition_id=competition_id, person_id=person_id
        ).exists()

    def set_stripe_progress(self, stripe_progress):
        self.stripe_progress = stripe_progress

    def unset_stripe_progress(self):
        self.stripe_progress = None

    def set_is_duplicated_twin_competitions(self):
        self.is_duplicated_twin_competitions = True

    def set_is_diffrence_event_and_price(self):
        self.is_diffrence_event_and_price = True

    def create(self, competition_id, status, event_ids, guest_count, comment, person):
        self.competition_id = competition_id
        self.status = status
        self.event_ids = event_ids
        self.guest_count = guest_count
        self.comment = comment
        self.person = person
        self.save()

    def update(
        self, status, event_ids, guest_count, comment, is_update_created_at, now
    ):
        self.status = status
        self.event_ids = event_ids
        self.guest_count = guest_count
        self.comment = comment
        if is_update_created_at:
            self.created_at = now
        self.save(
            update_fields=[
                "event_ids",
                "guest_count",
                "comment",
                "status",
                "created_at",
                "updated_at",
            ]
        )

    def update_status(self, status):
        self.status = status
        self.save(update_fields=["status", "updated_at"])

    def update_admin_competitor(
        self,
        event_ids,
        guest_count,
        wca_name,
        last_name,
        first_name,
        last_name_kana,
        first_name_kana,
        last_name_roma,
        first_name_roma,
    ):
        self.event_ids = event_ids
        self.guest_count = guest_count
        self.save(
            update_fields=[
                "event_ids",
                "guest_count",
                "updated_at",
            ]
        )
        self.person.user.update_first_name_and_last_name(first_name, last_name)
        self.person.update_names(
            first_name,
            last_name,
            first_name_kana,
            last_name_kana,
            first_name_roma,
            last_name_roma,
            wca_name,
        )

    def __str__(self):
        return self.competition_id + " [" + self.person.get_full_name() + "]"
