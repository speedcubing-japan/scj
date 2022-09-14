from django import template
from app.utils.convert import Convert


register = template.Library()


def mbf_convert(value):
    return Convert.mbf_convert_to_display(value)


@register.filter
def result_values(result):
    values = []
    values.append(result.value1)
    if result.value2 != 0:
        values.append(result.value2)
    if result.value3 != 0:
        values.append(result.value3)
    if result.value4 != 0:
        values.append(result.value4)
    if result.value5 != 0:
        values.append(result.value5)

    modify_list = []

    if len(values) >= 4:
        for value in values:
            if min(values) == value:
                if value == -1:
                    modify_list.append("(DNF)")
                elif value == -2:
                    modify_list.append("(DNS)")
                else:
                    modify_list.append("(" + "{:.02f}".format(value) + ")")
            elif max(values) == value:
                if value == -1:
                    modify_list.append("(DNF)")
                elif value == -2:
                    modify_list.append("(DNS)")
                else:
                    modify_list.append("(" + "{:.02f}".format(value) + ")")
            else:
                modify_list.append(str("{:.02f}".format(value)))
    else:
        for value in values:
            if value == -1:
                modify_list.append("DNF")
            elif value == -2:
                modify_list.append("DNS")
            else:
                if result.event_id == 17:
                    modify_list.append(mbf_convert(value))
                else:
                    modify_list.append("{:.02f}".format(value))

    return " ".join(modify_list)
