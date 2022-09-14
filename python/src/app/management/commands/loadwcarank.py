from django.core.management.base import BaseCommand
from app.utils.wca_scraping import WCAScraping
from app.defines.competitor import Status as CompetitorStatus
from app.models import Competitor, Person
import time


class Command(BaseCommand):
    help = "test wca scraiping"

    def handle(self, *args, **options):
        competition_id = options["competition_id"]

        competitors = Competitor.objects.filter(
            competition_id=competition_id, status=CompetitorStatus.REGISTRATION.value
        )
        if not competitors:
            return

        person_ids = [competitor.person.id for competitor in competitors]
        if not person_ids:
            return

        persons = Person.objects.filter(id__in=person_ids)
        wca_id_list = [person.wca_id for person in persons]

        for wca_id in wca_id_list:
            try:
                wca_scraping = WCAScraping(wca_id)
                wca_scraping.save()
                time.sleep(1)
            except Exception:
                pass

    def add_arguments(self, parser):
        parser.add_argument("competition_id", type=int, help="competition_idを指定してください。")
