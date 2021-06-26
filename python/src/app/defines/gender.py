from app.defines.define import Define
from enum import unique
from django.utils.translation import gettext_lazy as _


@unique
class Gender(Define):
    男性 = 1
    女性 = 2

    @classmethod
    def choices(cls):
        return tuple((x.value, _(x.name)) for x in cls)

@unique
class GenderEn(Define):
    m = 1
    f = 2
