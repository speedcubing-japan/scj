from app.defines.define import Define
from enum import unique
from django.utils.translation import gettext_lazy as _


SCJ_COMPETITON_FIRST_YEAR = 2020


@unique
class Type(Define):
    SCJ = 1
    WCA = 2


@unique
class RoundType(Define):
    一回戦 = (1, _("一回戦"))
    二回戦 = (2, _("二回戦"))
    三回戦 = (3, _("三回戦"))
    決勝 = (4, _("決勝"))

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
    LIMIT = 1
    CUMULATIVE = 2


@unique
class ProceedType(Define):
    NONE = 0
    COUNT = 1
    RATE = 2
