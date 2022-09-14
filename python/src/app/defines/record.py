from app.defines.define import Define
from enum import unique


@unique
class Type(Define):
    SINGLE = 1
    AVERAGE = 2
