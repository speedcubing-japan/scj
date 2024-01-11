from app.defines.define import OUTLIERS
from app.utils.convert import Convert

RESULT_DNF = -1
RESULT_DNS = -2
DNF = "DNF"
DNS = "DNS"
NA = "n/a"



class Record:

    def __init__(self, value1, value2, value3, value4, value5, event_id):
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
        self.value4 = value4
        self.value5 = value5
        self.event_id = event_id
        self.best = self._calc_best()

    def format_values(self):
        values = []
        values.append(self.value1)
        if self.value2 != 0:
            values.append(self.value2)
        if self.value3 != 0:
            values.append(self.value3)
        if self.value4 != 0:
            values.append(self.value4)
        if self.value5 != 0:
            values.append(self.value5)
        modify_list = []
        include_dnf_dns = RESULT_DNF in values or RESULT_DNS in values
        max_flag = False
        min_flag = False

        # ao5, mo3, bo1の判定式
        if len(values) >= 4:
            for value in values:
                # bestがDNF or DNSなら全部記録なし
                if self.best == RESULT_DNF or self.best == RESULT_DNS:
                    modify_list.append(self._add_brackets(convert(value, self.event_id)))
                    continue
                # DNF判定
                if value == RESULT_DNF:
                    # すでにmax判定されてないかチェック
                    if max_flag:
                        modify_list.append(DNF)
                    else:
                        modify_list.append(self._add_brackets(DNF))
                        max_flag = True
                    continue
                # DNS判定
                if value == RESULT_DNS:
                    # すでにmax判定されてないかチェック
                    if max_flag:
                        modify_list.append(DNS)
                    else:
                        modify_list.append(self._add_brackets(DNS))
                        max_flag = True
                    continue
                # min判定
                if self.best == value and not min_flag:
                    modify_list.append(self._add_brackets(convert(value, self.event_id)))
                    min_flag = True
                # max判定
                elif max(values) == value and not max_flag:
                    # 一つでもDNF or DNSがあれば()つけない
                    if include_dnf_dns:
                        modify_list.append(convert(value, self.event_id))
                    else:
                        modify_list.append(self._add_brackets(convert(value, self.event_id)))
                        max_flag = True
                else:
                    modify_list.append(convert(value, self.event_id))
        else:
            for value in values:
                # DNF判定
                if value == RESULT_DNF:
                    modify_list.append(DNF)
                # DNS判定
                elif value == RESULT_DNS:
                    modify_list.append(DNS)
                else:
                    modify_list.append(convert(value, self.event_id))
        return modify_list

    def _add_brackets(self, result):
        return f"({result})"

    def _calc_best(self):
        value1 =  self.value1 if self.value1 > 0 else OUTLIERS
        value2 =  self.value2 if self.value2 > 0 else OUTLIERS
        value3 =  self.value3 if self.value3 > 0 else OUTLIERS
        value4 =  self.value4 if self.value4 > 0 else OUTLIERS
        value5 =  self.value5 if self.value5 > 0 else OUTLIERS
        return min(value1, value2, value3, value4, value5)

def convert(result, event_id):
    convert = Convert()
    if result == RESULT_DNF:
        return DNF
    elif result == RESULT_DNS:
        return DNS
    elif result == 0:
        pass
    elif result == OUTLIERS:
        return NA
    elif event_id == 17:
        return convert.mbf_convert_to_display(result)
    elif float(result) > 60.00:
        return convert.minutes_convert(result)
    else:
        return str("{:.02f}".format(result))
