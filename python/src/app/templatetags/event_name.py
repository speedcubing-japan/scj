from django import template
import app.consts


register = template.Library()

@register.filter
def event_name(event_id):
    event_names = dict(app.consts.EVENT)

    if not event_id in event_names:
        return ''

    return event_names[event_id]