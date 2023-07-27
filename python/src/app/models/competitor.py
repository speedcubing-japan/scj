from django.db import models
from django_mysql.models import JSONField
from .person import Person
from app.defines.competitor import Status as CompetitorStatus, ReceptionStatus
from app.defines.competition import Type as CompetitionType
from app.defines.session import Notification


class Competitor(models.Model):
    competition_id = models.IntegerField("大会ID")
    status = models.SmallIntegerField("状態", choices=CompetitorStatus.choices())
    event_ids = JSONField("申し込み種目ID")
    guest_count = models.SmallIntegerField("同伴者数")
    comment = models.TextField("コメント")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    reception_status = models.SmallIntegerField(
        "受付状態", choices=ReceptionStatus.choices(), default=0
    )
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    registration_number = 0
    stripe_progress = None
    is_duplicated_series_competitions = False
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

    def set_registration_number(self, number):
        self.registration_number = number

    def set_stripe_progress(self, stripe_progress):
        self.stripe_progress = stripe_progress

    def unset_stripe_progress(self):
        self.stripe_progress = None

    def set_is_duplicated_series_competitions(self):
        self.is_duplicated_series_competitions = True

    def set_is_diffrence_event_and_price(self):
        self.is_diffrence_event_and_price = True

    def init(self, competition_id, status, event_ids, guest_count, comment, person):
        self.competition_id = competition_id
        self.status = status
        self.event_ids = event_ids
        self.guest_count = guest_count
        self.comment = comment
        self.person = person
        return self

    def create(self, competition_id, status, event_ids, guest_count, comment, person):
        self.competition_id = competition_id
        self.status = status
        self.event_ids = event_ids
        self.guest_count = guest_count
        self.comment = comment
        self.person = person
        self.save()

    def update_created_at(self, now):
        self.created_at = now
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

    def update_guest_count(self, guest_count):
        self.guest_count = guest_count
        self.save(update_fields=["guest_count", "updated_at"])

    def update_reception_status(self, reception_status):
        self.reception_status = reception_status
        self.save(update_fields=["reception_status", "updated_at"])

    def update_admin_competitor(
        self,
        event_ids,
        guest_count,
        prefecture_id,
        birth_at,
        wca_name,
        wca_birth_at,
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
        self.person.update_prefecture_id(prefecture_id)
        self.person.update_birth_at(birth_at, wca_birth_at)

    def get_notification(self, competition):
        if self.status == CompetitorStatus.CANCEL.value:
            return Notification.COMPETITOR_CANCEL
        elif self.status == CompetitorStatus.PENDING.value:
            return Notification.COMPETITOR_PENGING
        elif competition.use_reception and competition.is_open():
            if self.reception_status == ReceptionStatus.ALL_RECEPTION.value:
                return Notification.RECEPTION_FINISHED
            elif self.reception_status == ReceptionStatus.SELF_RECEPTION.value:
                if self.is_diffrence_event_and_price:
                    return Notification.SELF_RECEPTION_DIFFERENCE_PRICE
                else:
                    return Notification.SELF_RECEPTION_FINISHED
            elif self.reception_status == ReceptionStatus.NOT_YET_RECEPTION.value:
                return Notification.NOT_YET_RECEPTION
        elif self.status == CompetitorStatus.REGISTRATION.value:
            return Notification.COMPETITOR_REGISTRATION
        else:
            return ""

    def __str__(self):
        return self.competition_id + " [" + self.person.get_full_name() + "]"
