from django import template
from app.defines.competition import Type as CompetitionType


register = template.Library()


@register.filter
def competition_logo(competition):

    if competition.type == CompetitionType.WCA.value:
        return "app/image/wca.svg"
    elif competition.type == CompetitionType.SCJ.value:
        return "app/image/scj_logo_s.png"
