from django import template


register = template.Library()

@register.filter
def guest_sum(competitors):
    return sum(int(competitor.guest_count) for competitor in competitors)