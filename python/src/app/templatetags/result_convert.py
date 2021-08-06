from django import template
from app.defines.define import OUTLIERS
from app.views.util.record import mbf_convert


register = template.Library()


@register.filter
def result_convert(result, event_id):

    if result == -1:
        return "DNF"
    elif result == -2:
        return "DNS"
    elif result == 0:
        pass
    elif result == OUTLIERS:
        return "n/a"
    elif event_id == 17:
        return mbf_convert(result)
    else:
        return str("{:.02f}".format(result))
