import datetime
from django.db import models
from django_mysql.models import JSONField
from app.defines.prefecture import PrefectureAndOversea
from app.defines.competition import Type as CompetitionType
from app.defines.fee import PayType as FeePayType
from app.defines.fee import CalcType as FeeCalcType
from django.utils import timezone
from django.utils.timezone import localtime


class Competition(models.Model):

    id = models.IntegerField('大会ID', primary_key=True)
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
    organizer_person_ids = JSONField('主催者SCJID')
    venue_name = models.CharField('開催地名', max_length=256)
    venue_address = models.CharField('開催地住所', max_length=256)
    latitude = models.FloatField('開催地緯度')
    longitude = models.FloatField('開催地経度')
    limit = models.IntegerField('制限人数')
    guest_limit = models.SmallIntegerField('ゲスト最大人数')
    is_display_pending_competitor = models.BooleanField('承認前の競技者の一覧表示フラグ', default=False)
    fee_pay_type = models.SmallIntegerField('参加費支払いタイプ', default=0, choices=FeePayType.choices())
    fee_calc_type = models.SmallIntegerField('参加費計算タイプ', default=0, choices=FeeCalcType.choices())
    description = models.TextField('大会説明', default='')
    requirement = models.TextField('参加要件', default='')
    is_cancel = models.BooleanField('キャンセル可否', default=False)
    is_payment = models.BooleanField('課金可否', default=False)

    class Meta:
        indexes = [
            models.Index(name='idx_name_id', fields=['name_id'])
        ]

    def is_open(self):
        now = localtime(datetime.datetime.now(tz=datetime.timezone.utc))
        open_at = localtime(self.open_at)
        close_at = localtime(self.close_at)
        return open_at.date() <= now.date() and close_at.date() >= now.date()

    def is_close(self):
        now = localtime(datetime.datetime.now(tz=datetime.timezone.utc))
        close_at = localtime(self.close_at)
        return close_at.date() < now.date()

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

    def is_refunder(self, user):
        is_refunder = False
        if user.is_authenticated:
           if user.is_superuser:
               is_refunder = True
           if user.person.id == self.stripe_user_person_id:
               is_refunder = True
        return is_refunder

    def __str__(self):
        return self.name