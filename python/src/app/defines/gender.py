from app.defines.define import Define
from enum import unique
from django.utils.translation import gettext_lazy as _


@unique
class Gender(Define):
    男性 = (1, _("男性"))
    女性 = (2, _("女性"))

    @classmethod
    def get_name(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.name

    @classmethod
    def choices(cls):
        return tuple((x.value[0], x.value[1]) for x in cls)


@unique
class GenderEn(Define):
    m = 1
    f = 2
