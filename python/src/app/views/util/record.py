from app.defines.define import OUTLIERS

RESULT_DNF = -1
RESULT_DNS = -2
DNF = "DNF"
DNS = "DNS"
NA = "n/a"


def format_values(result):
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
    event_id = result.event_id
    modify_list = []
    include_dnf_dns = RESULT_DNF in values or RESULT_DNS in values
    max_flag = False
    min_flag = False

    # ao5, mo3, bo1の判定式
    if len(values) >= 4:
        for value in values:
            # bestがDNF or DNSなら全部記録なし
            if result.best == RESULT_DNF or result.best == RESULT_DNS:
                modify_list.append(add_brackets(convert(value, event_id)))
                continue
            # DNF判定
            if value == RESULT_DNF:
                # すでにmax判定されてないかチェック
                if max_flag:
                    modify_list.append(DNF)
                else:
                    modify_list.append(add_brackets(DNF))
                    max_flag = True
                continue
            # DNS判定
            if value == RESULT_DNS:
                # すでにmax判定されてないかチェック
                if max_flag:
                    modify_list.append(DNS)
                else:
                    modify_list.append(add_brackets(DNS))
                    max_flag = True
                continue
            # min判定
            if result.best == value and not min_flag:
                modify_list.append(add_brackets(convert(value, event_id)))
                min_flag = True
            # max判定
            elif max(values) == value and not max_flag:
                # 一つでもDNF or DNSがあれば()つけない
                if include_dnf_dns:
                    modify_list.append(convert(value, event_id))
                else:
                    modify_list.append(add_brackets(convert(value, event_id)))
                    max_flag = True
            else:
                modify_list.append(convert(value, event_id))
    else:
        for value in values:
            # DNF判定
            if value == RESULT_DNF:
                modify_list.append(DNF)
            # DNS判定
            elif value == RESULT_DNS:
                modify_list.append(DNS)
            else:
                modify_list.append(convert(value, event_id))
    return modify_list


def minutes_convert(result):
    minutes, seconds = divmod(result, 60)
    seconds = "{:05.02f}".format(seconds)

    return str(int(minutes)) + ":" + str(seconds)


def convert(result, event_id):
    if result == RESULT_DNF:
        return DNF
    elif result == RESULT_DNS:
        return DNS
    elif result == 0:
        pass
    elif result == OUTLIERS:
        return NA
    elif event_id == 17:
        return mbf_convert(result)
    elif float(result) > 60.00:
        return minutes_convert(result)
    else:
        return str("{:.02f}".format(result))


def add_brackets(result):
    return f"({result})"


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
