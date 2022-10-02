from django import template


register = template.Library()


@register.filter
def index(list, index):
    if 0 <= index < len(list):
        return list[index]
    else:
        return ""
