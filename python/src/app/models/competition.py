import datetime
import json
from django.db import models
from django_mysql.models import JSONField
from app.defines.prefecture import PrefectureAndOversea
from app.defines.competition import Type as CompetitionType
from app.defines.fee import PayType as FeePayType
from app.defines.fee import CalcType as FeeCalcType
from app.defines.competition import WCA_COMPETITION_NAME_ID_BY_REGISTRATION_ONLY_HAS_WCA_ID
from django.utils import timezone
from django.utils.timezone import localtime


class Competition(models.Model):

    type = models.SmallIntegerField('大会タイプ', default=0, choices=CompetitionType.choices())
    name = models.CharField('大会名', max_length=64)
    name_id = models.CharField('大会名ID', max_length=64)
    open_at = models.DateTimeField('開始日', default=timezone.now)
    close_at = models.DateTimeField('終了日', default=timezone.now)
    registration_open_at = models.DateTimeField('申し込み開始日時', default=timezone.now)
    registration_close_at = models.DateTimeField('申し込み終了日時', default=timezone.now)
    judge_person_ids = JSONField('審判員ID')
    stripe_user_person_id = models.IntegerField('Stripe使用者ID', default=0)
    event_ids = JSONField('イベントID')
    prefecture_id = models.SmallIntegerField('都道府県ID', choices=PrefectureAndOversea.choices())
    organizer_name = models.CharField('主催者名', default='', max_length=64)
    organizer_email = models.EmailField('メールアドレス', default='')
    organizer_person_ids = JSONField('主催者SCJID')
    venue_name = models.CharField('開催地名', max_length=256)
    venue_address = models.CharField('開催地住所', max_length=256)
    venue_url = models.CharField('開催地URL', default='', max_length=256)
    latitude = models.FloatField('開催地緯度')
    longitude = models.FloatField('開催地経度')
    limit = models.IntegerField('制限人数')
    guest_limit = models.SmallIntegerField('ゲスト最大人数')
    is_display_pending_competitor = models.BooleanField('承認前の競技者の一覧表示フラグ', default=False)
    fee_pay_type = models.SmallIntegerField('参加費支払いタイプ', default=0, choices=FeePayType.choices())
    fee_calc_type = models.SmallIntegerField('参加費計算タイプ', default=0, choices=FeeCalcType.choices())
    fee_pay_close_at = models.DateTimeField('参加費支払い期限', default=None, null=True)
    twin_competition_id = models.IntegerField('双子大会ID', default=0)
    description = models.TextField('大会説明', default='')
    description_en = models.TextField('大会説明(英文)', default='')
    requirement = models.TextField('参加要件', default='')
    requirement_en = models.TextField('参加要件(英文)', default='')
    refund_description = models.TextField('返金ポリシー', default='')
    refund_description_en = models.TextField('返金ポリシー(英文)', default='')
    is_cancel = models.BooleanField('キャンセル可否', default=False)
    is_payment = models.BooleanField('課金可否', default=False)
    is_display = models.BooleanField('表示可否', default=False)
    is_private = models.BooleanField('プライベート可否', default=False)

    is_superuser = False

    class Meta:
        indexes = [
            models.Index(name='idx_name_id', fields=['name_id'])
        ]

    def create(self, competition, judge_person_id):
        self.type = competition['type']
        self.name = competition['name']
        self.name_id = competition['name_id']
        self.open_at = competition['open_at']
        self.close_at = competition['close_at']
        self.registration_open_at = competition['registration_open_at']
        self.registration_close_at = competition['registration_close_at']
        self.judge_person_ids = [judge_person_id]
        self.stripe_user_person_id = competition['stripe_user_person_id']
        self.event_ids = list(json.loads(competition['event_ids']))
        self.prefecture_id = competition['prefecture_id']
        self.organizer_name = competition['organizer_name']
        self.organizer_email = competition['organizer_email']
        self.organizer_person_ids = list(json.loads(competition['organizer_person_ids']))
        self.venue_name = competition['venue_name']
        self.venue_address = competition['venue_address']
        self.venue_url = competition['venue_url']
        self.latitude = competition['latitude']
        self.longitude = competition['longitude']
        self.limit = competition['limit']
        self.guest_limit = competition['guest_limit']
        self.is_display_pending_competitor = bool(competition['is_display_pending_competitor'])
        self.fee_pay_type = competition['fee_pay_type']
        self.fee_calc_type = competition['fee_calc_type']
        self.fee_pay_close_at = competition['fee_pay_close_at']
        self.twin_competition_id = competition['twin_competition_id']
        self.description = competition['description']
        self.description_en = competition['description_en']
        self.requirement = competition['requirement']
        self.requirement_en = competition['requirement_en']
        self.refund_description = competition['refund_description']
        self.refund_description_en = competition['refund_description_en']
        self.is_cancel = False
        self.is_payment = True
        self.is_display = False
        self.is_private = True
        self.save()

    def update(self, competition):
        self.type = competition['type']
        self.name = competition['name']
        self.open_at = competition['open_at']
        self.close_at = competition['close_at']
        self.registration_open_at = competition['registration_open_at']
        self.registration_close_at = competition['registration_close_at']
        self.stripe_user_person_id = competition['stripe_user_person_id']
        self.event_ids = list(json.loads(competition['event_ids']))
        self.prefecture_id = competition['prefecture_id']
        self.organizer_name = competition['organizer_name']
        self.organizer_email = competition['organizer_email']
        self.organizer_person_ids = list(json.loads(competition['organizer_person_ids']))
        self.venue_name = competition['venue_name']
        self.venue_address = competition['venue_address']
        self.venue_url = competition['venue_url']
        self.latitude = competition['latitude']
        self.longitude = competition['longitude']
        self.limit = competition['limit']
        self.guest_limit = competition['guest_limit']
        self.is_display_pending_competitor = bool(competition['is_display_pending_competitor'])
        self.fee_pay_type = competition['fee_pay_type']
        self.fee_calc_type = competition['fee_calc_type']
        self.fee_pay_close_at = competition['fee_pay_close_at']
        self.twin_competition_id = competition['twin_competition_id']
        self.description = competition['description']
        self.description_en = competition['description_en']
        self.requirement = competition['requirement']
        self.requirement_en = competition['requirement_en']
        self.refund_description = competition['refund_description']
        self.refund_description_en = competition['refund_description_en']
        self.save()

    def delete(self):
        Competition.objects.filter(id=self.id).delete()

    def publish(self):
        self.is_display = True
        self.is_private = False
        self.save()

    def hidden(self):
        self.is_display = False
        self.is_private = False
        self.save()

    def is_open(self):
        now = localtime(datetime.datetime.now(tz=datetime.timezone.utc))
        open_at = localtime(self.open_at)
        close_at = localtime(self.close_at)
        return open_at.date() <= now.date() and close_at.date() >= now.date()

    def is_finish(self):
        now = localtime(datetime.datetime.now(tz=datetime.timezone.utc))
        close_at = localtime(self.close_at)
        return close_at.date() < now.date()

    def is_registration_open(self):
        now = localtime(datetime.datetime.now(tz=datetime.timezone.utc))
        registration_open_at = localtime(self.registration_open_at)
        registration_close_at = localtime(self.registration_close_at)
        return registration_open_at <= now and registration_close_at >= now

    def is_registration_open_to_close(self):
        now = localtime(datetime.datetime.now(tz=datetime.timezone.utc))
        registration_open_at = localtime(self.registration_open_at)
        close_at = localtime(self.close_at)
        return registration_open_at <= now and close_at.date() >= now.date()

    def is_superuser(self, user):
        is_superuser = False
        if user.is_authenticated:
            if user.is_superuser:
                is_superuser = True
            if user.person.id in self.organizer_person_ids:
                is_superuser = True
            if user.person.id in self.judge_person_ids:
                is_superuser = True

        return is_superuser

    def is_judge(self, user):
        is_judge = False
        if user.is_authenticated:
            if user.is_superuser:
                is_judge = True
            if user.person.id in self.judge_person_ids:
                is_judge = True
        return is_judge

    def set_is_superuser(self, user):
        self.is_superuser = self.is_superuser(user)

    def is_refunder(self, user):
        is_refunder = False
        if user.is_authenticated:
           if user.is_superuser:
               is_refunder = True
           if user.person.id == self.stripe_user_person_id:
               is_refunder = True
        return is_refunder

    def is_registration_only_has_wca_id(self):
        return self.name_id in WCA_COMPETITION_NAME_ID_BY_REGISTRATION_ONLY_HAS_WCA_ID

    def __str__(self):
        return self.name