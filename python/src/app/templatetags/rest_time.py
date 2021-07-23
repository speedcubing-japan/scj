import datetime
from django import template
from django.utils.translation import ugettext as _


register = template.Library()


@register.filter
def rest_time(timedelta):
    text = ""
    if type(timedelta) is datetime.timedelta:
        total_seconds = int(timedelta.total_seconds())
        if timedelta.days > 0:
            if timedelta.days > 30:
                text = str(timedelta.days // 30) + _(" ヶ月")
            else:
                text = str(timedelta.days) + _(" 日")
        elif total_seconds > 0:
            if total_seconds // 3600 > 0:
                text = str(total_seconds // 3600) + _(" 時間")
            elif total_seconds // 60 > 0:
                text = str(total_seconds // 60) + _(" 分")
            elif timedelta.total_seconds() > 0:
                text = str(total_seconds) + _(" 秒")
    return text
