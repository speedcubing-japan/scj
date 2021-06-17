from enum import Enum


class Define(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def contains_value(cls, value):
        return value in [x.value for x in cls]

    @classmethod
    def contains_name(cls, name):
        return name in [x.name for x in cls]

    @classmethod
    def get_value(cls, name):
        for x in cls:
            if x.name == name:
                return x.value

    @classmethod
    def get_name(cls, value):
        for x in cls:
            if x.value == value:
                return x.name

    @classmethod
    def count(cls):
        return len(cls)