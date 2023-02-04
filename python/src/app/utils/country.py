import os
import json
import pyjq
from django.conf import settings


class Country:

    cache = {}
    en_cache = {}
    id_cache = {}

    def __init__(self):
        with open(self.get_json_path()) as file:
            self.json = json.loads(file.read())

    def get_json_path(self):
        return os.path.join(settings.BASE_DIR, "app/defines/json/country.json")

    def name(self, code=""):
        if code in self.cache:
            return self.cache[code]

        query = '.[] | select(.iso2 == "' + code + '")'
        result = pyjq.first(query, self.json)
        return result["name"]

    def en_name(self, code=""):
        if code in self.en_cache:
            return self.en_cache[code]

        query = '.[] | select(.iso2 == "' + code + '")'
        result = pyjq.first(query, self.json)
        return result["en_name"]

    def id(self, code=""):
        if code in self.id_cache:
            return self.id_cache[code]

        query = '.[] | select(.iso2 == "' + code + '")'
        result = pyjq.first(query, self.json)
        return result["id"]
