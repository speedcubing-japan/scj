from django.core.management.base import BaseCommand
from django.conf import settings
import os
import requests
import zipfile
import csv
from app.defines.event import Event


class Command(BaseCommand):
    help = "get data from wca"

    def handle(self, *args, **kwargs):

        single_tsv_filename = "WCA_export_RanksSingle.tsv"
        average_tsv_filename = "WCA_export_RanksAverage.tsv"

        filepath = os.path.join(settings.BASE_DIR, "app/fixtures/wca.zip")
        dirpath = os.path.join(settings.BASE_DIR, "app/fixtures/")

        res = requests.get(settings.WCA_TSV_URL, stream=True)
        with open(filepath, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

        with zipfile.ZipFile(filepath) as existing_zip:
            existing_zip.extract(single_tsv_filename, dirpath)
            existing_zip.extract(average_tsv_filename, dirpath)

        # 不要になったので元zipファイルは消す
        os.remove(filepath)

        rank_sql = self.make_json(dirpath + single_tsv_filename, "wcabestrank")
        with open(dirpath + "sql/wcabestrank.sql", mode="w") as file:
            file.write(rank_sql)

        rank_sql = self.make_json(dirpath + average_tsv_filename, "wcaaveragerank")
        with open(dirpath + "sql/wcaaveragerank.sql", mode="w") as file:
            file.write(rank_sql)

    def make_json(self, filepath, model_name):

        event_id_name_dict = Event.get_event_id_names()
        event_name_id_dict = {v: k for k, v in event_id_name_dict.items()}

        sql = "TRUNCATE TABLE app_" + model_name + "; "
        sql += "INSERT INTO app_" + model_name + " VALUES "

        with open(filepath) as file:
            tsv = csv.reader(file, delimiter="\t")
            datas = [row for row in tsv]

            rank_data = []
            index = 0
            for data in datas:
                if index == 0:
                    index += 1
                    continue

                if not data[1] in event_name_id_dict:
                    continue

                rank_data.append(
                    "("
                    + str(index)
                    + ', "'
                    + str(data[0])
                    + '", '
                    + str(event_name_id_dict[data[1]])
                    + ", "
                    + str(data[2])
                    + ", "
                    + str(data[3])
                    + ")"
                )

                index += 1

        sql += ", ".join(rank_data)
        os.remove(filepath)
        return sql
