from django import template
from app.views.util.record import convert


register = template.Library()


@register.filter
def result_convert(result, event_id):
    return convert(result, event_id)
