from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from app.models import (
    Person,
    Competition,
    Round,
    Result,
    AverageRank,
    BestRank,
    Scramble,
    FeePerEvent,
    FeePerEventCount,
)
import os
import json


class Command(BaseCommand):
    help = "bulkdata from json"

    def get_fixtures_path(self, model):
        return os.path.join(settings.BASE_DIR, "app/fixtures/" + model + ".json")

    def handle(self, *args, **kwargs):

        person_list = {}
        persons = Person.objects.all()
        for person in persons:
            person_list[person.id] = person

        with open(self.get_fixtures_path("round")) as file:
            json_round = json.loads(file.read())
            rounds = []
            for record in json_round:
                round = Round(
                    id=record["fields"]["id"],
                    competition_id=record["fields"]["competition_id"],
                    event_id=record["fields"]["event_id"],
                    event_name=record["fields"]["event_name"],
                    attempt_count=record["fields"]["attempt_count"],
                    type=record["fields"]["type"],
                    format_id=record["fields"]["format_id"],
                    limit_type=record["fields"]["limit_type"],
                    limit_time=record["fields"]["limit_time"],
                    cutoff_attempt_count=record["fields"]["cutoff_attempt_count"],
                    cutoff_time=record["fields"]["cutoff_time"],
                    proceed_count=record["fields"]["proceed_count"],
                    room_name=record["fields"]["room_name"],
                    begin_at=record["fields"]["begin_at"],
                    end_at=record["fields"]["end_at"],
                )
                rounds.append(round)

            cursor = connection.cursor()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("TRUNCATE TABLE app_round")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            Round.objects.bulk_create(rounds)

            # 参照のためdictとして保持
            tmpRounds = {}
            for round in rounds:
                tmpRounds[round.id] = round

        with open(self.get_fixtures_path("result")) as file:
            json_result = json.loads(file.read())
            results = []
            for record in json_result:
                result = Result(
                    id=record["pk"],
                    competition_id=record["fields"]["competition_id"],
                    event_id=record["fields"]["event_id"],
                    person_id=record["fields"]["person_id"],
                    round=tmpRounds[record["fields"]["round_id"]],
                    rank=record["fields"]["rank"],
                    best=record["fields"]["best"],
                    average=record["fields"]["average"],
                    value1=record["fields"]["value1"],
                    value2=record["fields"]["value2"],
                    value3=record["fields"]["value3"],
                    value4=record["fields"]["value4"],
                    value5=record["fields"]["value5"],
                )
                results.append(result)

            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE app_result")

            Result.objects.bulk_create(results)

        with open(self.get_fixtures_path("averagerank")) as file:
            json_average_rank = json.loads(file.read())
            average_ranks = []
            for record in json_average_rank:
                average_rank = AverageRank(
                    id=record["pk"],
                    person=person_list[record["fields"]["person_id"]],
                    event_id=record["fields"]["event_id"],
                    competition_id=record["fields"]["competition_id"],
                    competition_name_id=record["fields"]["competition_name_id"],
                    competition_name=record["fields"]["competition_name"],
                    year=record["fields"]["year"],
                    best=record["fields"]["best"],
                    value1=record["fields"]["value1"],
                    value2=record["fields"]["value2"],
                    value3=record["fields"]["value3"],
                    value4=record["fields"]["value4"],
                    value5=record["fields"]["value5"],
                    gender=record["fields"]["gender"],
                    generation=record["fields"]["generation"],
                    prefecture_id=record["fields"]["prefecture_id"],
                    rank=record["fields"]["rank"],
                    gender_rank=record["fields"]["gender_rank"],
                    generation_rank=record["fields"]["generation_rank"],
                    prefecture_rank=record["fields"]["prefecture_rank"],
                )
                average_ranks.append(average_rank)

            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE app_averagerank")

            AverageRank.objects.bulk_create(average_ranks)

        with open(self.get_fixtures_path("bestrank")) as file:
            json_best_rank = json.loads(file.read())
            best_ranks = []
            for record in json_best_rank:
                best_rank = BestRank(
                    id=record["pk"],
                    person=person_list[record["fields"]["person_id"]],
                    event_id=record["fields"]["event_id"],
                    competition_id=record["fields"]["competition_id"],
                    competition_name_id=record["fields"]["competition_name_id"],
                    competition_name=record["fields"]["competition_name"],
                    year=record["fields"]["year"],
                    best=record["fields"]["best"],
                    gender=record["fields"]["gender"],
                    generation=record["fields"]["generation"],
                    prefecture_id=record["fields"]["prefecture_id"],
                    rank=record["fields"]["rank"],
                    gender_rank=record["fields"]["gender_rank"],
                    generation_rank=record["fields"]["generation_rank"],
                    prefecture_rank=record["fields"]["prefecture_rank"],
                )
                best_ranks.append(best_rank)

            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE app_bestrank")

            BestRank.objects.bulk_create(best_ranks)

        with open(self.get_fixtures_path("competition")) as file:
            json_competition = json.loads(file.read())
            competitions = []
            for record in json_competition:

                registration_open_at = None
                registration_close_at = None
                if (
                    record["fields"]["registration_open_at"] != ""
                    or record["fields"]["registration_close_at"] != ""
                ):
                    registration_open_at = record["fields"]["registration_open_at"]
                    registration_close_at = record["fields"]["registration_close_at"]

                competition = Competition(
                    id=record["fields"]["id"],
                    type=record["fields"]["type"],
                    name=record["fields"]["name"],
                    name_id=record["fields"]["name_id"],
                    open_at=record["fields"]["open_at"],
                    close_at=record["fields"]["close_at"],
                    registration_open_at=registration_open_at,
                    registration_close_at=registration_close_at,
                    is_registration_at_other=record["fields"][
                        "is_registration_at_other"
                    ],
                    stripe_user_person_id=record["fields"]["stripe_user_person_id"],
                    judge_person_ids=record["fields"]["judge_person_ids"],
                    event_ids=record["fields"]["event_ids"],
                    prefecture_id=record["fields"]["prefecture_id"],
                    organizer_name=record["fields"]["organizer_name"],
                    organizer_email=record["fields"]["organizer_email"],
                    organizer_person_ids=record["fields"]["organizer_person_ids"],
                    venue_name=record["fields"]["venue_name"],
                    venue_address=record["fields"]["venue_address"],
                    venue_url=record["fields"]["venue_url"],
                    latitude=record["fields"]["latitude"],
                    longitude=record["fields"]["longitude"],
                    limit=record["fields"]["limit"],
                    guest_limit=record["fields"]["guest_limit"],
                    is_display_pending_competitor=record["fields"][
                        "is_display_pending_competitor"
                    ],
                    fee_pay_type=record["fields"]["fee_pay_type"],
                    fee_calc_type=record["fields"]["fee_calc_type"],
                    fee_pay_close_at=record["fields"]["fee_pay_close_at"],
                    twin_competition_id=record["fields"]["twin_competition_id"],
                    description=record["fields"]["description"],
                    description_en=record["fields"]["description_en"],
                    qualification_description=record["fields"][
                        "qualification_description"
                    ],
                    qualification_description_en=record["fields"][
                        "qualification_description_en"
                    ],
                    disclaimer=record["fields"]["disclaimer"],
                    disclaimer_en=record["fields"]["disclaimer_en"],
                    refund_description=record["fields"]["refund_description"],
                    refund_description_en=record["fields"]["refund_description_en"],
                    awards_description=record["fields"]["awards_description"],
                    awards_description_en=record["fields"]["awards_description_en"],
                    assignment_description=record["fields"]["assignment_description"],
                    assignment_description_en=record["fields"][
                        "assignment_description_en"
                    ],
                    is_cancel=record["fields"]["is_cancel"],
                    is_payment=record["fields"]["is_payment"],
                    is_display=record["fields"]["is_display"],
                    is_private=record["fields"]["is_private"],
                )
                competitions.append(competition)

            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE app_competition")

            Competition.objects.bulk_create(competitions)

        with open(self.get_fixtures_path("scramble")) as file:
            json_scramble = json.loads(file.read())
            scrambles = []
            for record in json_scramble:
                scramble = Scramble(
                    id=record["pk"],
                    competition_id=record["fields"]["competition_id"],
                    event_id=record["fields"]["event_id"],
                    round_id=record["fields"]["round_id"],
                    group_id=record["fields"]["group_id"],
                    scramble=record["fields"]["scramble"],
                )
                scrambles.append(scramble)

            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE app_scramble")

            Scramble.objects.bulk_create(scrambles)

        with open(self.get_fixtures_path("feeperevent")) as file:
            json_fee_per_event = json.loads(file.read())
            fee_per_events = []
            for record in json_fee_per_event:
                fee_per_event = FeePerEvent(
                    id=record["pk"],
                    competition_id=record["fields"]["competition_id"],
                    event_id=record["fields"]["event_id"],
                    price=record["fields"]["price"],
                    prepaid_price=record["fields"]["prepaid_price"],
                )
                fee_per_events.append(fee_per_event)

            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE app_feeperevent")

            FeePerEvent.objects.bulk_create(fee_per_events)

        with open(self.get_fixtures_path("feepereventcount")) as file:
            json_fee_per_event_count = json.loads(file.read())
            fee_per_event_counts = []
            for record in json_fee_per_event_count:
                fee_per_event_count = FeePerEventCount(
                    id=record["pk"],
                    competition_id=record["fields"]["competition_id"],
                    event_count=record["fields"]["event_count"],
                    price=record["fields"]["price"],
                    prepaid_price=record["fields"]["prepaid_price"],
                )
                fee_per_event_counts.append(fee_per_event_count)

            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE app_feepereventcount")

            FeePerEventCount.objects.bulk_create(fee_per_event_counts)
