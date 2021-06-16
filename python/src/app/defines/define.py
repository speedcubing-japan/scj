from enum import Enum


class Define(Enum):
    @classmethod
    def choices(cls):
        return tuple((m.value, m.name) for m in cls)

    @classmethod
    def contains_value(cls, value):
        return value in [m.value for m in cls]

    @classmethod
    def contains_name(cls, name):
        return name in [m.name for m in cls]

    @classmethod
    def get_value(cls, name):
        for m in cls:
            if m.name == name:
                return m.value

    @classmethod
    def get_name(cls, value):
        for m in cls:
            if m.value == value:
                return m.name

    @classmethod
    def count(cls):
        return len(cls)