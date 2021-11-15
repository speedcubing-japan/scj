import csv
import urllib
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from app.defines.event import Event
from app.defines.competition import Type as CompetitionType
from app.models import Competition, Competitor, StripeProgress


class Csv(LoginRequiredMixin, View):
    def post(self, request, **kwargs):
        if "name_id" not in kwargs:
            return redirect("competition_index")
        name_id = kwargs.get("name_id")

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect("competition_index")
        competition = competition.first()

        if not competition.is_superuser(request.user):
            return redirect("competition_index")

        competitors = Competitor.objects.filter(competition_id=competition.id)
        stripe_progresses = StripeProgress.objects.filter(
            competition_id=competition.id, refund_price=0
        )
        for competitor in competitors:
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)

        response = HttpResponse(content_type="text/csv; charset=UTF-8")
        filename = urllib.parse.quote((name_id + "_competitor.csv").encode("utf8"))
        response["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(
            filename
        )
        writer = csv.writer(response)

        event_name_dict = {}
        event_id_names = Event.get_event_id_names()
        for event_id in competition.event_ids:
            event_name_dict[event_id] = event_id_names[event_id]

        if competition.type == CompetitionType.WCA.value:
            row = ["wca_id", "wca_user_id", "name", "email", "birth_at"]
        elif competition.type == CompetitionType.SCJ.value:
            row = ["scj_id", "full_name", "full_name_kana", "full_name_rome", "email", "birth_at"]

        row.extend(list(event_name_dict.values()))
        row.extend(
            [
                "guest_count",
                "pay_price",
                "stripe_charge_id",
                "comment",
                "pay_at",
                "created_at",
            ]
        )
        writer.writerow(row)

        for index, competitor in enumerate(competitors):
            if request.POST.get("competitor_id_" + str(competitor.id)):
                event_join_list = []
                for event_id in event_name_dict.keys():
                    if event_id in competitor.event_ids:
                        event_join_list.append(1)
                    else:
                        event_join_list.append(0)

                if competition.type == CompetitionType.WCA.value:
                    row = [
                        competitor.person.wca_id,
                        competitor.person.wca_user_id,
                        competitor.person.wca_name,
                        competitor.person.wca_email,
                        competitor.person.wca_birth_at,
                    ]

                elif competition.type == CompetitionType.SCJ.value:
                    id = competitor.person.id
                    row = [
                        id,
                        competitor.person.get_full_name(),
                        competitor.person.get_full_name_kana(),
                        competitor.person.get_full_name_roma(),
                        competitor.person.user.email,
                        competitor.person.birth_at
                    ]

                row.extend(event_join_list)
                row.extend(
                    [
                        competitor.guest_count,
                        competitor.stripe_progress.pay_price
                        if competitor.stripe_progress is not None
                        else 0,
                        competitor.stripe_progress.charge_id
                        if competitor.stripe_progress is not None
                        else "",
                        competitor.comment.replace("\r\n", ""),
                        localtime(competitor.stripe_progress.pay_at)
                        if competitor.stripe_progress is not None
                        else "",
                        localtime(competitor.created_at),
                    ]
                )

                writer.writerow(row)

        return response
