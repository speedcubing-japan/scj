from app.defines.define import Define
from enum import unique

GENERATION_MAX = 10


@unique
class Status(Define):
    PENDING = 1
    REGISTRATION = 2
    CANCEL = 3


@unique
class ReceptionStatus(Define):
    NOT_YET_RECEPTION = 0
    SELF_RECEPTION = 1
    ALL_RECEPTION = 2
