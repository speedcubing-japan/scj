from django.core.management.base import BaseCommand
from django.conf import settings
import os
import requests
import json


class Command(BaseCommand):
    help = "get data from google app script api"

    def handle(self, *args, **kwargs):
        sheet_names = [
            "competition",
            "round",
            "result",
            "scramble",
            "feeperevent",
            "feepereventcount",
        ]
        for sheet_name in sheet_names:
            params = (("sheet_name", sheet_name),)
            response = requests.get(settings.GAS_URL, params=params)
            path = os.path.join(
                settings.BASE_DIR, "app/fixtures/" + sheet_name + ".json"
            )
            if response.status_code == 401:
                print("responce is 401. check out token.")
                return
            json_string = json.dumps(response.json())
            with open(path, mode="w") as f:
                f.write(json_string)
