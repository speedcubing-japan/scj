from app.defines.define import Define
from enum import unique
from django.utils.translation import gettext_lazy as _


@unique
class PayType(Define):
    現地支払 = (1, _('現地支払'))
    事前支払または現地支払 = (2, _('事前支払または現地支払'))
    事前支払 = (3, _('事前支払'))

    @classmethod
    def get_name(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.value[1]

    @classmethod
    def choices(cls):
        return tuple((x.value[0], x.name) for x in cls)

# 参照用
@unique
class PayTypeEn(Define):
    LOCAL_ONLY = 1
    LOCAL_AND_REMOTE = 2
    REMOTE_ONLY = 3

@unique
class CalcType(Define):
    種目別 = (1, _('種目別'))
    種目数 = (2, _('種目数'))

    @classmethod
    def get_name(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.value[1]

    @classmethod
    def choices(cls):
        return tuple((x.value[0], x.name) for x in cls)

# 参照用
@unique
class CalcTypeEn(Define):
    EVENT = 1
    EVENT_COUNT = 2