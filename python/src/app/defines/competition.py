from app.defines.define import Define
from enum import unique
from django.utils.translation import gettext_lazy as _


SCJ_COMPETITON_FIRST_YEAR = 2020

WCA_COMPETITION_NAME_ID_BY_REGISTRATION_ONLY_HAS_WCA_ID = (
    'WCAJapanChampionship2021'
)

@unique
class Type(Define):
    SCJ = 1
    WCA = 2

@unique
class RoundType(Define):
    予選 = (1, _('予選'))
    二次予選 = (2, _('二次予選'))
    準決勝 = (3, _('準決勝'))
    決勝 = (4, _('決勝'))

    @classmethod
    def choices(cls):
        return tuple((x.value[0], x.value[1]) for x in cls)

    @classmethod
    def get_name(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.value[1]

@unique
class RoundLimitType(Define):
    時間制限 = 1
    累計時間制限 = 2