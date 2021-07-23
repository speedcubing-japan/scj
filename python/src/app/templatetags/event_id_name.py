from django import template
from app.defines.event import Event


register = template.Library()


@register.filter
def event_id_name(event_id):
    return Event.get_id_name(event_id)
