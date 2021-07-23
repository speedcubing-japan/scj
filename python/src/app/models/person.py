from django.conf import settings
from django.db import models
from app.defines.gender import Gender
from app.defines.prefecture import PrefectureAndOversea
from django.utils.translation import gettext_lazy as _


class Person(models.Model):
    first_name = models.CharField(_('名'), max_length=64)
    last_name = models.CharField(_('姓'), max_length=64)
    first_name_kana = models.CharField(_('メイ'), max_length=64)
    last_name_kana = models.CharField(_('セイ'), max_length=64)
    first_name_roma = models.CharField(_('名(ローマ字)'), max_length=64)
    last_name_roma = models.CharField(_('姓(ローマ字)'), max_length=64)
    gender = models.SmallIntegerField(_('性別'), choices=Gender.choices())
    birth_at = models.DateField(_('生年月日'))
    prefecture_id = models.SmallIntegerField(_('都道府県'), choices=PrefectureAndOversea.choices())
    wca_id = models.CharField('WCA_ID', max_length=10)
    wca_user_id = models.IntegerField('WCA_USER_ID', default=0)
    wca_email = models.EmailField('WCA EMAIL', default='')
    wca_name = models.CharField('WCA氏名', max_length=256, default='')
    wca_country_iso2 = models.CharField('WCA所属国', max_length=2, default='')
    wca_access_token = models.CharField('WCAアクセストークン', max_length=256)
    wca_refresh_token = models.CharField('WCAリフレッシュトークン', max_length=256)
    wca_avatar_url = models.CharField('アバター', max_length=256)
    wca_avatar_thumb_url = models.CharField('アバターサムネイル', max_length=256)
    stripe_user_id = models.CharField('STRIPE_USER_ID', max_length=256, default='')
    stripe_customer_id = models.CharField('STRIPE_CUSTOMER_ID', max_length=256, default='')
    is_judge = models.BooleanField('審判員フラグ', default=False)
    is_event_offerer = models.BooleanField('イベント申請者フラグ', default=False)
    is_community_posting_offer = models.BooleanField('宣伝申請許可', default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def is_wca_authenticated(self):
        return self.wca_id != '' or self.wca_user_id != 0

    def is_wca_email_authenticated(self):
        return self.wca_email != ''

    def is_avater_exist(self):
        return self.wca_avatar_url != '' and self.wca_avatar_thumb_url != ''

    def get_full_name(self):
        return self.last_name + ' ' + self.first_name

    def get_full_name_kana(self):
        return self.last_name_kana + ' ' + self.first_name_kana

    def get_full_name_roma(self):
        return self.first_name_roma + ' ' + self.last_name_roma

    def __str__(self):
        return self.get_full_name()
