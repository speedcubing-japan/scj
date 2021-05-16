from django.template.defaultfilters import stringfilter
from django import template


register = template.Library()

@register.filter
@stringfilter
def strip(value):
    return value.strip()