import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from app.models import Competition
from requests.exceptions import Timeout, RequestException
from app.defines.competition import Type as CompetitionType


class Command(BaseCommand):
    help = "open wca comp page from wca'page info"

    TIMEOUT_SEC = 3.5

    def handle(self, *args, **options):
        competitions = Competition.objects.filter(
            type=CompetitionType.WCA.value, is_display=False, is_private=False
        )
        if not competitions:
            exit()

        for competition in competitions:
            is_open = self.get_wca_competition_page_info(competition.name_id)
            if is_open:
                competition.publish()

    def get_wca_competition_page_info(self, name_id):
        try:
            response = requests.get(
                settings.WCA_API_URL + "/search/competitions?q=" + name_id,
                timeout=self.TIMEOUT_SEC,
            )
            if response.status_code == requests.codes.ok:
                return len(response.json()["result"]) > 0

        except (Timeout, RequestException):
            return False
