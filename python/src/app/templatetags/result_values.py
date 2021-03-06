from django import template


register = template.Library()


def mbf_convert(value):
    value = str(int(value))
    difference = 99 - int(value[0:2])
    seconds = value[2:7]
    missed = value[7:9]

    solved = difference + int(missed)
    attempted = solved + int(missed)

    minutes = int(seconds) // 60
    seconds = int(seconds) - minutes * 60

    return (
        str(solved)
        + "/"
        + str(attempted)
        + " "
        + str(minutes)
        + ":"
        + str(seconds).zfill(2)
    )


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
