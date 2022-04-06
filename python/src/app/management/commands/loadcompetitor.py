from django.core.management.base import BaseCommand
from django.conf import settings
from app.models import Competitor, Person
import os
import json


class Command(BaseCommand):
    help = "load competitor data."

    def get_fixtures_path(self, model):
        return os.path.join(settings.BASE_DIR, "app/fixtures/" + model + ".json")

    def handle(self, *args, **options):

        competitor_list = []
        competitors = Competitor.objects.all()
        for competitor in competitors:
            competitor_list.append(
                str(competitor.competition_id) + "_" + str(competitor.person_id)
            )

        with open(self.get_fixtures_path("competitor")) as file:
            json_competitor = json.loads(file.read())
            competitors = []
            for record in json_competitor:

                person = Person.objects.filter(id=record["fields"]["person_id"])
                if not person.exists():
                    print(
                        "person_id: "
                        + str(record["fields"]["person_id"])
                        + " is not exist"
                    )
                    continue

                person = person.first()
                # 存在したら挿入しない。
                if (
                    str(record["fields"]["competition_id"]) + "_" + str(person.id)
                    in competitor_list
                ):
                    print(
                        "competition_id: "
                        + str(record["fields"]["competition_id"])
                        + " person_id: "
                        + str(person.id)
                        + " is exist"
                    )
                    continue

                competitor = Competitor()
                competitor.init(
                    record["fields"]["competition_id"],
                    record["fields"]["status"],
                    record["fields"]["event_ids"],
                    record["fields"]["guest_count"],
                    record["fields"]["comment"],
                    person,
                )
                competitors.append(competitor)

            Competitor.objects.bulk_create(competitors)
