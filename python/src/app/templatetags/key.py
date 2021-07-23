from django import template


register = template.Library()


@register.filter
def key(value, arg):
    if arg in value:
        return value[arg]
    else:
        return ''
