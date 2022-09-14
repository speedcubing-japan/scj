from app.defines.define import Define
from enum import unique
from django.utils.translation import gettext_lazy as _


# 空白文字をnameに使えないので参照時にreplaceする。
@unique
class Format(Define):
    FORMAT1 = (1, "Best of 1")
    FORMAT2 = (2, "Best of 2")
    FORMAT3 = (3, "Best of 3")
    FORMAT4 = (4, "Average of 5")
    FORMAT5 = (5, "Mean of 3")

    @classmethod
    def choices(cls):
        return tuple((x.value[0], x.value[1]) for x in cls)

    @classmethod
    def get_name(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.value[1]


class WinFormat(Define):
    BEST = 1
    AVERAGE = 2


# nameをイベント名にすると数字のリテラルは先頭では使えないので苦肉の策。
class Event(Define):
    EVENT1 = (1, _("3x3x3 キューブ"), "333", WinFormat.AVERAGE)
    EVENT2 = (2, _("2x2x2 キューブ"), "222", WinFormat.AVERAGE)
    EVENT3 = (3, _("4x4x4 キューブ"), "444", WinFormat.AVERAGE)
    EVENT4 = (4, _("5x5x5 キューブ"), "555", WinFormat.AVERAGE)
    EVENT5 = (5, _("6x6x6 キューブ"), "666", WinFormat.AVERAGE)
    EVENT6 = (6, _("7x7x7 キューブ"), "777", WinFormat.AVERAGE)
    EVENT7 = (7, _("3x3x3 目隠し"), "333bf", WinFormat.BEST)
    EVENT8 = (8, _("3x3x3 最少手数"), "333fm", WinFormat.BEST)
    EVENT9 = (9, _("3x3x3 片手"), "333oh", WinFormat.AVERAGE)
    EVENT10 = (10, _("クロック"), "clock", WinFormat.AVERAGE)
    EVENT11 = (11, _("メガミンクス"), "minx", WinFormat.AVERAGE)
    EVENT12 = (12, _("ピラミンクス"), "pyram", WinFormat.AVERAGE)
    EVENT13 = (13, _("スキューブ"), "skewb", WinFormat.AVERAGE)
    EVENT14 = (14, _("スクエア1"), "sq1", WinFormat.AVERAGE)
    EVENT15 = (15, _("4x4x4 目隠し"), "444bf", WinFormat.BEST)
    EVENT16 = (16, _("5x5x5 目隠し"), "555bf", WinFormat.BEST)
    EVENT17 = (17, _("3x3x3 複数目隠し"), "333mbf", WinFormat.BEST)

    def __init__(self, event_id, event_name, event_id_name, win_format):
        self.event_id = event_id
        self.event_name = event_name
        self.event_id_name = event_id_name
        self.win_format = win_format

    # event_idからevent_nameを引く
    @classmethod
    def get_name(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.value[1]

    # event_idからevent_id_nameを引く
    @classmethod
    def get_id_name(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.value[2]

    # event_idからwin_formatを引く
    @classmethod
    def get_win_format(cls, value):
        for x in cls:
            if x.value[0] == value:
                return x.value[3]

    # event_nameからevent_idを引く
    @classmethod
    def get_value(cls, name):
        for x in cls:
            if x.value[1] == name:
                return x.value[0]

    # event_id_nameからevent_idを引く
    @classmethod
    def get_value_by_id_name(cls, id_name):
        for x in cls:
            if x.value[2] == id_name:
                return x.value[0]

    @classmethod
    def get_names(cls, values):
        list = []
        for x in cls:
            if x.value[0] in values:
                list.append(x.value[1])
        return list

    @classmethod
    def get_events(cls, values):
        list = []
        for x in cls:
            if x.value[0] in values:
                list.append((x.value[0], x.value[1]))
        return dict(list)

    @classmethod
    def get_best_only_values(cls):
        list = []
        for x in cls:
            if not x.value[3]:
                list.append(x.value[0])
        return list

    @classmethod
    def get_event_id_names(cls):
        list = []
        for x in cls:
            list.append((x.value[0], x.value[2]))
        return dict(list)

    @classmethod
    def choices(cls):
        return tuple((x.value[0], x.value[1]) for x in cls)

    @classmethod
    def has(cls, event_ids):
        values = set(map(lambda x: x.value[0], cls))
        # 差集合でevent_idsにしかないものが1件以上あればFalse
        return not len(event_ids - values) > 0
