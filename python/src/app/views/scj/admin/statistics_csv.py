import csv
import urllib
import datetime
from django.http import HttpResponse
from app.models import Person, Result, Competition
from app.defines.statistics import Type as StatisticsType
from app.defines.prefecture import PrefectureAndOversea as Prefecture
from app.defines.competition import Type as CompetitionType
from django.utils.timezone import localtime
from django.views.generic import View
from django.shortcuts import redirect
from .admin_base import AdminBase


# カラム名がキャメルなのはWCAと合わせるため。
class AdminStatisticsCsv(AdminBase, View):
    def get(self, request, **kwargs):
        if "type" not in kwargs:
            return redirect("index")

        type = kwargs.get("type")

        response = HttpResponse(content_type="text/csv; charset=UTF-8")
        filename = urllib.parse.quote((type + ".csv").encode("utf8"))
        response["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(
            filename
        )
        writer = csv.writer(response)

        if not StatisticsType.contains_value(type):
            return redirect("index")

        if type == StatisticsType.PERSONS.value:
            row = ["id", "name", "gender", "prefectureId"]
            writer.writerow(row)

            persons = Person.objects.all()
            for person in persons:
                if person.user.is_active:
                    row = [
                        person.id,
                        person.get_full_name(),
                        person.gender,
                        person.prefecture_id,
                    ]
                    writer.writerow(row)
        elif type == StatisticsType.COMPETITIONS.value:
            row = [
                "id",
                "name",
                "year",
                "month",
                "day",
                "endMonth",
                "endDay",
                "venue",
                "latitude",
                "longitude",
                "prefectureId",
                "cancelled",
            ]
            writer.writerow(row)

            competitions = Competition.objects.filter(type=CompetitionType.SCJ.value)
            for competition in competitions:
                open_at = localtime(competition.open_at)
                close_at = localtime(competition.close_at)
                row = [
                    competition.id,
                    competition.name,
                    open_at.year,
                    open_at.month,
                    open_at.day,
                    close_at.month,
                    close_at.day,
                    competition.venue_name,
                    competition.latitude,
                    competition.longitude,
                    competition.prefecture_id,
                    int(competition.is_cancel),
                ]
                writer.writerow(row)
        elif type == StatisticsType.RESULTS.value:
            row = [
                "competitionId",
                "eventId",
                "personId",
                "roundTypeId",
            ]
            writer.writerow(row)

            results = Result.objects.all()
            for result in results:
                if result.best >= -1:  # DNSは含めない。
                    row = [
                        result.competition_id,
                        result.event_id,
                        result.person_id,
                        result.round_type,
                    ]
                    writer.writerow(row)
        elif type == StatisticsType.PREFECTURES.value:
            row = ["id", "name"]
            writer.writerow(row)

            for prefecture in Prefecture:
                row = [prefecture.value, prefecture.name]
                writer.writerow(row)

        return response
