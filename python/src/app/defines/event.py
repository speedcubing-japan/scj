from app.defines.define import Define
from enum import unique


# 空白文字をnameに使えないので参照時にreplaceする。
@unique
class Format(Define):
    Best_of_1 = 1
    Best_of_2 = 2
    Best_of_3 = 3
    Average_of_5 = 4
    Mean_of_3 = 5

    @classmethod
    def choices(cls):
        return tuple((m.value, m.name.replace('_', ' ')) for m in cls)

# nameをイベント名にすると数字のリテラルは先頭では使えないので苦肉の策。
class Event(Define):
    EVENT1 = '3x3x3 キューブ'
    EVENT2 = '2x2x2 キューブ'
    EVENT3 = '4x4x4 キューブ'
    EVENT4 = '5x5x5 キューブ'
    EVENT5 = '6x6x6 キューブ'
    EVENT6 = '7x7x7 キューブ'
    EVENT7 = '3x3x3 目隠し'
    EVENT8 = '3x3x3 最少手数'
    EVENT9 = '3x3x3 片手'
    EVENT10 = 'クロック'
    EVENT11 = 'メガミンクス'
    EVENT12 = 'ピラミンクス'
    EVENT13 = 'スキューブ'
    EVENT14 = 'スクエア1'
    EVENT15 = '4x4x4 目隠し'
    EVENT16 = '5x5x5 目隠し'
    EVENT17 = '3x3x3 複数目隠し'
    
    # event_idからevent_nameを引く
    @classmethod
    def get_name(cls, value):
        return super().get_value('EVENT' + str(value))
    
    # event_nameからevent_idを引く
    @classmethod
    def get_value(cls, name):
        return int(super().get_name(name).replace('EVENT', ''))

    @classmethod
    def choices(cls):
        return tuple((int(x.name.replace('EVENT', '')), x.value) for x in cls)

    @classmethod
    def dict(cls):
        return dict(cls.choices())
    