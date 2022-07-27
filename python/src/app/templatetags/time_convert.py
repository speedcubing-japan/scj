from django import template
from django.utils.translation import ugettext as _


register = template.Library()


@register.filter
def time_convert(seconds):
    text = ""

    if seconds > 0:
        if seconds // 3600 > 0:
            text += str(seconds // 3600) + _(" 時間")
            seconds -= seconds // 3600 * 3600
        if seconds // 60 > 0:
            if text != "":
                text += " "
            text += str(seconds // 60) + _(" 分")
            seconds -= seconds // 60 * 60
        if seconds > 0:
            if text != "":
                text += " "
            text += str(seconds) + _(" 秒")

    return text
