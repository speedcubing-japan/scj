from django import template
import app.consts


register = template.Library()

@register.filter
def event_id_name(event_id):
    event_id_names = dict(app.consts.EVENT_ID_NAME)

    if not event_id in event_id_names:
        return ''

    return event_id_names[event_id]