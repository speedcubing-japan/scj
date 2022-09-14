class Convert:
    # MBLDの表示用テキストを数値に変換します。
    def mbf_convert_to_number(self, display_value):

        DEFAULT_NUMBER = 99

        values = display_value.split()
        solved = int(values[0].split("/")[0])
        attempted = int(values[0].split("/")[1])

        minutes = int(values[1].split(":")[0])
        seconds = int(values[1].split(":")[1])

        missed = attempted - solved

        dd = DEFAULT_NUMBER - (solved - missed)
        tt = minutes * 60 + seconds

        return str(dd) + str(tt).zfill(5) + str(missed).zfill(2)

    # MBLDの数値を表示用テキストに変換します。
    def mbf_convert_to_display(self, value):
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

    # 秒を分:秒表記に変換する
    def minutes_convert(self, result):
        minutes, seconds = divmod(result, 60)
        seconds = "{:05.02f}".format(seconds)

        return str(int(minutes)) + ":" + str(seconds)

    # 分表記を秒に変換する
    def seconds_convert(self, result):
        time = result
        if ":" in result:
            value = result.split(".")
            minutes = int(value[0].split(":")[0])
            seconds = int(value[0].split(":")[1])
            time = str(minutes * 60 + seconds) + "." + value[1]
        return time
