from django.conf import settings
from django_mysql.models import JSONField
from django.db import models
from django.utils import timezone
from app.consts import COMPETITION_TYPE, FEE_PAY_TYPE, FEE_CALC_TYPE, PREFECTURE, GENDER, FORMAT, EVENT, ROUND_TYPE, REGIONAL_RECORD, COMPETITOR_STATUS, ROUND_LIMIT_TYPE

# Create your models here.
class Person(models.Model):

    first_name = models.CharField('名', max_length=64)
    last_name = models.CharField('姓', max_length=64)
    first_name_kana = models.CharField('メイ', max_length=64)
    last_name_kana = models.CharField('セイ', max_length=64)
    first_name_roma = models.CharField('名(ローマ字)', max_length=64)
    last_name_roma = models.CharField('姓(ローマ字)', max_length=64)
    gender = models.SmallIntegerField('性別', choices=GENDER)
    birth_at = models.DateField('生年月日')
    prefecture_id = models.SmallIntegerField('都道府県', choices=PREFECTURE)
    wca_id = models.CharField('WCA_ID', max_length=10)
    wca_user_id = models.IntegerField('WCA_USER_ID', default=0)
    wca_name = models.CharField('WCA氏名', max_length=256, default='')
    wca_access_token = models.CharField('WCAアクセストークン', max_length=256)
    wca_refresh_token = models.CharField('WCAリフレッシュトークン', max_length=256)
    wca_avatar_url = models.CharField('アバター', max_length=256)
    wca_avatar_thumb_url = models.CharField('アバターサムネイル', max_length=256)
    stripe_user_id = models.CharField('STRIPE_USER_ID', max_length=256, default='')
    is_judge = models.BooleanField('審判員フラグ', default=False)
    is_community_posting_offer = models.BooleanField('宣伝申請許可', default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def is_wca_authenticated(self):
        return self.wca_id != '' or self.wca_user_id != 0

    def is_avater_exist(self):
        return self.wca_avatar_url != '' and self.wca_avatar_thumb_url != ''

    def get_full_name(self):
        return self.last_name + ' ' + self.first_name

    def get_full_name_kana(self):
        return self.last_name_kana + ' ' + self.first_name_kana

    def get_full_name_roma(self):
        return self.last_name_roma + ' ' + self.first_name_roma

    def __str__(self):
        return self.get_full_name()

class Competition(models.Model):

    id = models.IntegerField('大会ID', primary_key=True)
    type = models.SmallIntegerField('大会タイプ', default=0, choices=COMPETITION_TYPE)
    name = models.CharField('大会名', max_length=64)
    name_id = models.CharField('大会名ID', max_length=64)
    open_at = models.DateTimeField('開始日', default=timezone.now)
    close_at = models.DateTimeField('終了日', default=timezone.now)
    registration_open_at = models.DateTimeField('申し込み開始日時', default=timezone.now)
    registration_close_at = models.DateTimeField('申し込み終了日時', default=timezone.now)
    judge_person_ids = JSONField('審判員ID')
    stripe_user_person_id = models.IntegerField('Stripe使用者ID', default=0)
    event_ids = JSONField('イベントID')
    prefecture_id = models.SmallIntegerField('都道府県ID', choices=PREFECTURE)
    organizer_person_ids = JSONField('主催者SCJID')
    venue_name = models.CharField('開催地名', max_length=256)
    venue_address = models.CharField('開催地住所', max_length=256)
    latitude = models.FloatField('開催地緯度')
    longitude = models.FloatField('開催地経度')
    limit = models.IntegerField('制限人数')
    guest_limit = models.SmallIntegerField('ゲスト最大人数')
    is_display_pending_competitor = models.BooleanField('承認前の競技者の一覧表示フラグ', default=False)
    fee_pay_type = models.SmallIntegerField('参加費支払いタイプ', default=0, choices=FEE_PAY_TYPE)
    fee_calc_type = models.SmallIntegerField('参加費計算タイプ', default=0, choices=FEE_CALC_TYPE)
    description_ja = models.TextField('大会説明(日本語)')
    description_en = models.TextField('大会説明(英語)')
    requirement_ja = models.TextField('参加要件(日本語)')
    requirement_en = models.TextField('参加要件(英語)')
    is_cancel = models.BooleanField('キャンセル可否', default=False)

    class Meta:
        indexes = [
            models.Index(name='idx_name_id', fields=['name_id'])
        ]

    def __str__(self):
        return self.name
    
class Competitor(models.Model):

    competition_id = models.IntegerField("大会ID")
    status = models.SmallIntegerField('状態', choices=COMPETITOR_STATUS)
    event_ids = JSONField('申し込み種目ID')
    guest_count = models.SmallIntegerField('見学者数')
    comment = models.TextField('コメント')
    stripe_id = models.CharField('Stripe決済ID', max_length=256, default='')
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        indexes = [
            models.Index(name='idx_competition_id_person', fields=['competition_id', 'person'])
        ]

    def __str__(self):
        return self.competition.name + ' [' + self.person.get_full_name() + ']'

class Round(models.Model):

    id = models.IntegerField('ラウンドID', primary_key=True)
    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=EVENT)
    attempt_count = models.SmallIntegerField('挑戦回数', default=0)
    type = models.SmallIntegerField('ラウンドタイプ', choices=ROUND_TYPE)
    format_id = models.IntegerField('フォーマットID', choices=FORMAT)
    limit_type = models.SmallIntegerField('制限タイプ', default=0, choices=ROUND_LIMIT_TYPE)
    limit_time = models.IntegerField('制限時間')
    cutoff_attempt_count = models.SmallIntegerField('カットオフ回数', default=0)
    cutoff_time = models.IntegerField('カットオフ時間')
    proceed_count = models.IntegerField('通過人数')
    room_name = models.CharField('会場名', max_length=64, default='')
    begin_at = models.DateTimeField('開始時刻', default=timezone.now)
    end_at = models.DateTimeField('終了時刻', default=timezone.now)

class Result(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=EVENT)
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

class AverageRank(models.Model):

    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None) 
    event_id = models.SmallIntegerField('イベントID', db_index=True, choices=EVENT)
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
    gender = models.SmallIntegerField("性別", default=0, db_index=True, choices=GENDER)
    generation = models.SmallIntegerField("世代", db_index=True, default=0)
    prefecture_id = models.SmallIntegerField("都道府県ID", default=0, db_index=True, choices=PREFECTURE)
    rank = models.IntegerField('ランク', default=0)
    gender_rank = models.IntegerField('性別ランク', default=0)
    generation_rank = models.IntegerField('世代ランク', default=0)
    prefecture_rank = models.IntegerField('県ランク', default=0)

    def __str__(self):
        return str(self.person_id)

class BestRank(models.Model):

    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)
    event_id = models.SmallIntegerField('イベントID', db_index=True, choices=EVENT)
    competition_id = models.IntegerField('大会ID')
    competition_name_id = models.CharField('大会名ID', max_length=64, default='')
    competition_name = models.CharField('大会名', max_length=64, default='')
    year = models.SmallIntegerField('年', default=0)
    best = models.FloatField('ベスト')
    gender = models.SmallIntegerField("性別", default=0, db_index=True, choices=GENDER)
    generation = models.SmallIntegerField("世代", default=0, db_index=True)
    prefecture_id = models.SmallIntegerField("都道府県ID", default=0, db_index=True, choices=PREFECTURE)
    rank = models.IntegerField('ランク', default=0)
    gender_rank = models.IntegerField('性別ランク', default=0)
    generation_rank = models.IntegerField('世代ランク', default=0)
    prefecture_rank = models.IntegerField('県ランク', default=0)

    def __str__(self):
        return str(self.person_id)

class Scramble(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=EVENT)
    round_id = models.IntegerField('ラウンドID')
    group_id = models.CharField('グループID', max_length=4)
    scramble = models.CharField('スクランブル', max_length=64)

class FeePerEvent(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_id = models.SmallIntegerField('イベントID', choices=EVENT)
    price = models.IntegerField('料金')

class FeePerEventCount(models.Model):

    competition_id = models.IntegerField('大会ID')
    event_count = models.SmallIntegerField('イベント数')
    price = models.IntegerField('料金')

class WcaAverageRank(models.Model):

    wca_id = models.CharField('WCA_ID', max_length=10)
    event_id = models.SmallIntegerField('イベントID', choices=EVENT)
    best = models.IntegerField('ベスト')
    rank = models.IntegerField('順位')

    class Meta:
        indexes = [
            models.Index(name='idx_event_id_wca_id', fields=['event_id', 'wca_id'])
        ]

class WcaBestRank(models.Model):

    wca_id = models.CharField('WCA_ID', max_length=10)
    event_id = models.SmallIntegerField('イベントID', choices=EVENT)
    best = models.IntegerField('ベスト')
    rank = models.IntegerField('順位')

    class Meta:
        indexes = [
            models.Index(name='idx_event_id_wca_id', fields=['event_id', 'wca_id'])
        ]