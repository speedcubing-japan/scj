from app.defines.define import Define
from enum import unique


@unique
class PayType(Define):
    現地支払 = 1
    事前支払または現地支払 = 2
    事前支払 = 3

# 参照用
@unique
class PayTypeEn(Define):
    LOCAL_ONLY = 1
    LOCAL_AND_REMOTE = 2
    REMOTE_ONLY = 3

@unique
class CalcType(Define):
    種目別 = 1
    種目数 = 2

# 参照用
@unique
class CalcTypeEn(Define):
    EVENT = 1
    EVENT_COUNT = 2