from app.defines.define import Define
from enum import unique


@unique
class Type(Define):
    WCA大会 = 1
    SCJ大会 = 2
    イベント = 3
    お知らせ = 4


@unique
class TypeEn(Define):
    wca_competition = 1
    scj_competition = 2
    event = 3
    information = 4
