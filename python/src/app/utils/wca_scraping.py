import bs4
import requests
from django.conf import settings
from app.defines.event import Event
from app.defines.record import Type as RecordType
from app.utils.convert import Convert
from app.models import WcaRank
from requests.exceptions import Timeout, RequestException


class WCAScraping:

    TIMEOUT_SEC = 3.5
    RANK_NAMES = ["country-rank", "continent-rank", "world-rank"]

    def __init__(self, wca_id):
        self.wca_id = wca_id

    def get_personal_info(self):

        if not self.wca_id:
            return {}

        convert = Convert()
        try:
            res = requests.get(
                settings.WCA_PERSONS_URL + "/" + self.wca_id, timeout=self.TIMEOUT_SEC
            )
            res.raise_for_status()
        except (Timeout, RequestException):
            return {}

        soup = bs4.BeautifulSoup(res.text, "html.parser")

        # 種目存在判定
        event_id_name_list = [
            el.get("data-event")
            for el in soup.find_all(
                "td", attrs={"data-event": Event.get_event_id_names().values()}
            )
        ]

        # それぞれのランクを取得
        all_rank_list = []
        for rank_name in self.RANK_NAMES:
            rank_list = []
            for el in soup.find_all("td", attrs={"class": rank_name}):
                rank = 0
                if el.text:
                    rank = int(el.text)
                rank_list.append(rank)
            all_rank_list.append(rank_list)

        # それぞれの記録を取得
        record_list = []
        for el in soup.find_all(attrs={"class": "plain"}):
            record = 0
            text = el.text.split()
            if text:
                if "/" in el.text:
                    record = convert.mbf_convert_to_number(" ".join(text))
                else:
                    record = convert.seconds_convert(text[0])
            record_list.append(float(record))

        # 最後にデータを集計する
        data = {}
        for index, event_id_name in enumerate(event_id_name_list):
            data[event_id_name] = {}
            # 並びはSCJのevent_id順がWCAのevent_id順と同じためそのまま。
            # single, average, single, averageの順でスクレイピングしているためindexがこうなります   。
            single_index = index * 2
            average_index = index * 2 + 1

            single = {}
            average = {}
            for rank_index, rank_name in enumerate(self.RANK_NAMES):
                single.update({rank_name: all_rank_list[rank_index][single_index]})
                average.update({rank_name: all_rank_list[rank_index][average_index]})

            single.update({"record": record_list[single_index]})
            average.update({"record": record_list[average_index]})

            data[event_id_name][RecordType.SINGLE] = single
            data[event_id_name][RecordType.AVERAGE] = average

        return data

    def save(self):
        wca_data = self.get_personal_info()
        # 古いものを消す
        WcaRank.delete_by_wca_id(self.wca_id)

        if not wca_data:
            return

        for event_id_name in Event.get_event_id_names().values():
            if event_id_name in wca_data:
                for record_type in RecordType:
                    data = wca_data[event_id_name][record_type]
                    # 保存するのはevent_idなので取得しておく
                    event_id = Event.get_value_by_id_name(event_id_name)
                    wca_rank = WcaRank.create(
                        self.wca_id,
                        event_id,
                        record_type.value,
                        data["record"],
                        data["world-rank"],
                        data["continent-rank"],
                        data["country-rank"],
                    )
                    wca_rank.save()
