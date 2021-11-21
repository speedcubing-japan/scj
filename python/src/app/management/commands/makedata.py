import pyjq
import os
import json
import pprint
from app.defines.gender import Gender
from app.defines.prefecture import PrefectureAndOversea
from app.defines.competitor import GENERATION_MAX
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.utils.timezone import localtime
from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Person


class Command(BaseCommand):
    help = "making rank from scj.json"

    def get_fixtures_path(self, model):
        return os.path.join(settings.BASE_DIR, "app/fixtures/" + model + ".json")

    def get_generation(self, birth_at, competition_close_at):
        close_at = localtime(
            datetime.fromisoformat(competition_close_at.replace("Z", "+00:00"))
        ).date()
        age = relativedelta(close_at, birth_at).years
        return age // GENERATION_MAX

    def handle(self, *args, **kwargs):
        persons = Person.objects.all()

        with open(self.get_fixtures_path("result")) as file:
            json_object = json.loads(file.read())

            # 記録にあるイベントIDを取得
            query = "[ .[].fields.event_id ] | unique | .[]"
            event_ids = pyjq.all(query, json_object)

        with open(self.get_fixtures_path("competition")) as file:
            json_object = json.loads(file.read())

            query = "[ .[].fields ] | map({ id: .id, name_id: .name_id, name: .name, open_at: .open_at, close_at: .close_at }) | .[]"
            datas = pyjq.all(query, json_object)
            competiton_datas = {}
            for data in datas:
                competiton_datas[data["id"]] = data

        person_datas = {}
        for person in persons:
            person_datas[person.id] = person

        rank_data = self.calc_result(person_datas, event_ids, competiton_datas, "best")
        with open(self.get_fixtures_path("bestrank"), mode="w") as f:
            f.write(json.dumps(rank_data))

        rank_data = self.calc_result(
            person_datas, event_ids, competiton_datas, "average"
        )
        with open(self.get_fixtures_path("averagerank"), mode="w") as f:
            f.write(json.dumps(rank_data))

    def calc_result(self, person_datas, event_ids, competiton_datas, rank_type):
        rank_data = []

        with open(self.get_fixtures_path("result")) as file:
            json_object = json.loads(file.read())

            index = 0
            for event_id in event_ids:
                # イベントごとに順位でソートされた記録を取得
                query = (
                    "[ [.[].fields ] | \
                    map(select ( .event_id == "
                    + str(event_id)
                    + " )) | \
                    group_by(.person_id) | .[] | sort_by(."
                    + rank_type
                    + ") | \
                    .[0] ] | \
                    sort_by(."
                    + rank_type
                    + ") | \
                    .[] | \
                    { id, event_id, person_id, "
                    + rank_type
                    + ", competition_id, value1, value2, value3, value4, value5 }"
                )

                results = pyjq.all(query, json_object)

                rank = 0
                gender_ranks = dict(map(lambda x: (x.value[0], 0), Gender))
                generation_ranks = dict(
                    map(lambda x: (x * GENERATION_MAX, 0), range(0, 10))
                )
                prefecture_ranks = dict(
                    map(lambda x: (x.value, 0), PrefectureAndOversea)
                )

                before_record = 0
                skip_count = 1
                for result in results:
                    if result[rank_type] > 0:
                        # 世代計算
                        generation = (
                            self.get_generation(
                                person_datas[result["person_id"]].birth_at,
                                competiton_datas[result["competition_id"]]["close_at"],
                            )
                            * GENERATION_MAX
                        )

                        if before_record == 0 or before_record < result[rank_type]:
                            before_record = result[rank_type]
                            gender_ranks[
                                person_datas[result["person_id"]].gender
                            ] += skip_count
                            generation_ranks[generation] += skip_count
                            prefecture_ranks[
                                person_datas[result["person_id"]].prefecture_id
                            ] += skip_count
                            rank += skip_count
                            skip_count = 1
                        else:
                            skip_count += 1

                        result["competition_id"] = result["competition_id"]
                        result["competition_name_id"] = competiton_datas[
                            result["competition_id"]
                        ]["name_id"]
                        result["competition_name"] = competiton_datas[
                            result["competition_id"]
                        ]["name"]
                        result["year"] = localtime(
                            datetime.fromisoformat(
                                competiton_datas[result["competition_id"]][
                                    "open_at"
                                ].replace("Z", "+00:00")
                            )
                        ).year
                        result["gender"] = person_datas[result["person_id"]].gender
                        result["generation"] = generation
                        result["prefecture_id"] = person_datas[
                            result["person_id"]
                        ].prefecture_id
                        result["rank"] = rank
                        result["gender_rank"] = gender_ranks[
                            person_datas[result["person_id"]].gender
                        ]
                        result["generation_rank"] = generation_ranks[generation]
                        result["prefecture_rank"] = prefecture_ranks[
                            person_datas[result["person_id"]].prefecture_id
                        ]

                        # 不要データ削除
                        result.pop("id")
                        if rank_type == "average":
                            result["best"] = result["average"]
                            result.pop("average")
                        if rank_type == "best":
                            result.pop("value1")
                            result.pop("value2")
                            result.pop("value3")
                            result.pop("value4")
                            result.pop("value5")

                        model_name = "bestrank"
                        if rank_type == "average":
                            model_name = "averagerank"

                        index += 1
                        dictionary = {}
                        dictionary["model"] = "app." + model_name
                        dictionary["pk"] = index
                        dictionary["fields"] = result

                        rank_data.append(dictionary)

        return rank_data
