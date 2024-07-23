from django import template

register = template.Library()

@register.filter
def competition_pdf(competition):
    return "app/pdf/competition/" + competition.name_id + ".pdf"
