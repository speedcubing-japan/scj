from django import template
import datetime


register = template.Library()


@register.filter(expects_localtime=True)
def is_today(value):
    if type(value) is datetime.datetime:
        value = value.date()
    return value == value.today()
