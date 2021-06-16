from app.defines.define import Define
from enum import unique


@unique
class Gender(Define):
    男性 = 1
    女性 = 2

@unique
class GenderEn(Define):
    m = 1
    f = 2
