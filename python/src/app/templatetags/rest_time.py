from django import template
import datetime
import math


register = template.Library()

@register.filter
def rest_time(timedelta, suffix):
    text = ''
    if type(timedelta) is datetime.timedelta:
        total_seconds = int(timedelta.total_seconds())
        if timedelta.days > 0:
            if timedelta.days > 30:
                text = "約" + str(timedelta.days // 30) + "ヶ月" + str(suffix)
            else:
                text = str(timedelta.days) + "日" + str(suffix)
        elif total_seconds > 0:
            if total_seconds // 3600 > 0:
                text = str(total_seconds // 3600) + "時間" + str(suffix)
            elif total_seconds // 60 > 0:
                text = str(total_seconds // 60) + "分" + str(suffix)
            elif timedelta.total_seconds() > 0:
                text = str(total_seconds) + "秒" + str(suffix)
    return text
        