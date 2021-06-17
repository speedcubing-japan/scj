from django import template
import pprint

register = template.Library()

def mbf_convert(value):
    value = str(int(value))
    pprint.pprint(value)
    difference = 99 - int(value[0:2])
    seconds = value[2:7]
    missed = value[7:9]

    solved = difference + int(missed)
    attempted = solved + int(missed)

    minutes = int(seconds) // 60
    seconds = int(seconds) - minutes * 60

    return str(solved) + '/' + str(attempted) + ' ' + str(minutes) + ':' + str(seconds).zfill(2)

@register.filter
def result_convert(result, event_id):

    if result == -1:
        return 'DNF'
    elif result == -2:
        return 'DNS'
    elif result == 0:
        pass
    elif event_id == 17:
        return mbf_convert(result)
    elif result == 'n/a':
        return result
    else:
        return str('{:.02f}'.format(result))