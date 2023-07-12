from django import template

register = template.Library()


@register.filter
def sum_attribute_param(attribute_list, param_name):
    return sum([getattr(x, param_name) for x in attribute_list])
