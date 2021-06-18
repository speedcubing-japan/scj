from app.defines.define import Define
from enum import unique

GENERATION_MAX = 10

@unique
class Status(Define):
    PENDING = 1
    REGISTRATION = 2
    CANCEL = 3