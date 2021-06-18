from app.defines.define import Define
from enum import unique

SCJ_COMPETITON_FIRST_YEAR = 2020

@unique
class Type(Define):
    SCJ = 1
    WCA = 2

@unique
class RoundType(Define):
    予選 = 1
    二次予選 = 2
    準決勝 = 3
    決勝 = 4
    複合予選 = 5
    複合二次予選 = 6
    複合決勝 = 7

@unique
class RoundLimitType(Define):
    時間制限 = 1
    累計時間制限 = 2