from django import template
import app.consts

register = template.Library()

@register.filter
def competition_logo(competition):

    if competition.type == app.consts.COMPETITION_TYPE_WCA:
        return 'app/image/wca.svg'
    elif competition.type == app.consts.COMPETITION_TYPE_SCJ:
        return 'app/image/scj_logo_s.png'
