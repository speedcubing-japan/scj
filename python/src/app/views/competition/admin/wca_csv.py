import csv
import urllib
import datetime
from django.utils.timezone import localtime
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from app.defines.event import Event
from app.defines.gender import GenderEn
from app.defines.country import Country
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus
from app.models import Competition, Competitor


class WcaCsv(LoginRequiredMixin, View):
    def post(self, request, **kwargs):
        if "name_id" not in kwargs:
            return redirect("competition_index")
        name_id = kwargs.get("name_id")

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect("competition_index")
        competition = competition.first()

        if competition.type != CompetitionType.WCA.value:
            return redirect("competition_index")

        if not competition.is_superuser(request.user):
            return redirect("competition_index")

        competitors = Competitor.objects.filter(competition_id=competition.id).order_by(
            "created_at"
        )

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        now_str = localtime(now).strftime("%Y%m%d%H%M%S")

        response = HttpResponse(content_type="text/csv; charset=UTF-8")
        filename = urllib.parse.quote(
            (name_id + "_registration_" + now_str + ".csv").encode("utf8")
        )
        response["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(
            filename
        )
        writer = csv.writer(response)

        event_name_dict = {}
        event_id_names = Event.get_event_id_names()
        for event_id in competition.event_ids:
            event_name_dict[event_id] = event_id_names[event_id]

        country_names = dict(Country.choices())
        gender = dict(GenderEn.choices())

        event_name_id_list = []
        for event_id, event_id_name in event_name_dict.items():
            if event_id in competition.event_ids:
                event_name_id_list.append(event_id_name)

        columns = [
            "Status",
            "Name",
            "Country",
            "WCA ID",
            "Birth Date",
            "Gender",
            "Email",
        ]
        columns.extend(list(event_name_dict.values()))

        writer.writerow(columns)

        for competitor in competitors:
            if request.POST.get("competitor_id_" + str(competitor.id)):

                status = "null"
                if competitor.status == CompetitorStatus.REGISTRATION.value:
                    status = "a"
                elif competitor.status == CompetitorStatus.CANCEL.value:
                    status = "d"

                event_join_list = []
                for event_id in event_name_dict.keys():
                    if event_id in competitor.event_ids:
                        event_join_list.append(1)
                    else:
                        event_join_list.append(0)

                row = [
                    status,
                    competitor.person.wca_name,
                    country_names[competitor.person.wca_country_iso2],
                    competitor.person.wca_id,
                    competitor.person.wca_birth_at,
                    gender[competitor.person.gender],
                    competitor.person.wca_email,
                ]
                row.extend(event_join_list)

                writer.writerow(row)

        return response
