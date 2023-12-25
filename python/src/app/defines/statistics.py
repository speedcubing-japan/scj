from app.defines.define import Define
from enum import unique


@unique
class Type(Define):
    PERSONS = "persons"
    COMPETITIONS = "competitions"
    RESULTS = "results"
    PREFECTURES = "prefectures"
