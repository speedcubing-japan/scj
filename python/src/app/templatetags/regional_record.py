from django import template
import app.consts

register = template.Library()

@register.filter
def regional_record(regional_id):

    prefectures = dict(app.consts.PREFECTURE)

    if regional_id == 0:
        return ''
    elif regional_id == app.consts.NR_REGIONAL_ID:
        return '<span class="text-danger">NR</span>'
    else:
        return '<span class="text-warning">PR</span>'