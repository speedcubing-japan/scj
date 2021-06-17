from app.defines.define import Define
from enum import unique


# 空白文字をnameに使えないので参照時にreplaceする。
@unique
class Format(Define):
    FORMAT1 = (1, 'Best of 1')
    FORMAT2 = (2, 'Best of 2')
    FORMAT3 = (3, 'Best of 3')
    FORMAT4 = (4, 'Average of 5')
    FORMAT5 = (5, 'Mean of 3')

    @classmethod
    def choices(cls):
        return tuple((x.value[0], x.value[1]) for x in cls)

# nameをイベント名にすると数字のリテラルは先頭では使えないので苦肉の策。
class Event(Define):
    EVENT1 = (1, '3x3x3 キューブ', '333', True)
    EVENT2 = (2, '2x2x2 キューブ', '222', True)
    EVENT3 = (3, '4x4x4 キューブ', '444', True)
    EVENT4 = (4, '5x5x5 キューブ', '555', True)
    EVENT5 = (5, '6x6x6 キューブ', '666', True)
    EVENT6 = (6, '7x7x7 キューブ', '777', True)
    EVENT7 = (7, '3x3x3 目隠し', '333bf', True)
    EVENT8 = (8, '3x3x3 最少手数', '333fm', True)
    EVENT9 = (9, '3x3x3 片手', '333oh', True)
    EVENT10 = (10, 'クロック', 'clock', True)
    EVENT11 = (11, 'メガミンクス', 'minx', True)
    EVENT12 = (12, 'ピラミンクス', 'pyram', True)
    EVENT13 = (13, 'スキューブ', 'skewb', True)
    EVENT14 = (14, 'スクエア1', 'sq1', True)
    EVENT15 = (15, '4x4x4 目隠し', '444bf', False)
    EVENT16 = (16, '5x5x5 目隠し', '555bf', False)
    EVENT17 = (17, '3x3x3 複数目隠し', '333mbf', False)
    
    def __init__(self, event_id, event_name, event_id_name, is_best_and_average_event):
        self.event_id = event_id
        self.event_name = event_name
        self.event_id_name = event_id_name
        self.is_best_only = is_best_and_average_event

    @classmethod
    def is_best_and_average_event(cls, value):
        return cls.get_name(value)[3]

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
    
    # event_nameからevent_idを引く
    @classmethod
    def get_value(cls, name):
        for x in cls:
            if x.value[1] == name:
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