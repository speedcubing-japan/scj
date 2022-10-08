import app.models
from django.shortcuts import render, redirect
from app.models import BestRank, AverageRank, WcaRank
from app.defines.event import Event, WinFormat
from app.defines.record import Type as RecordType
from app.defines.define import OUTLIERS
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus
from app.utils.country import Country
from app.views.util.record import NA
from .base import Base


class Competitor(Base):

    template_name = "app/competition/competitor.html"
    event_id_name = ""

    def get(self, request, **kwargs):
        if "event_id_name" not in kwargs:
            return redirect("competition_index")
        self.event_id_name = kwargs.get("event_id_name")

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        event_id = 0
        if self.event_id_name != "list":
            event_id = Event.get_value_by_id_name(self.event_id_name)

        if event_id:
            competitors = app.models.Competitor.objects.filter(
                competition_id=self.competition.id, event_ids__contains=event_id
            )
        else:
            competitors = app.models.Competitor.objects.filter(
                competition_id=self.competition.id
            )

        if self.competition.is_display_pending_competitor:
            competitors = competitors.exclude(
                status=CompetitorStatus.CANCEL.value
            ).order_by("created_at")
        else:
            competitors = competitors.filter(
                status=CompetitorStatus.REGISTRATION.value
            ).order_by("created_at")

        bests = {}
        averages = {}
        sort_key = WinFormat.AVERAGE.name.lower()
        if event_id:
            sort_key = Event.get_win_format(event_id).name.lower()
            if self.competition.type == CompetitionType.SCJ.value:
                person_ids = []
                for competitor in competitors:
                    person_ids.append(competitor.person.id)

                best_ranks = BestRank.objects.filter(
                    event_id=event_id, person_id__in=person_ids
                )
                for best_rank in best_ranks:
                    bests[best_rank.person.id] = {
                        "rank": best_rank.rank,
                        "best": best_rank.best,
                    }

                average_ranks = AverageRank.objects.filter(
                    event_id=event_id, person_id__in=person_ids
                )
                for average_rank in average_ranks:
                    averages[average_rank.person.id] = {
                        "rank": average_rank.rank,
                        "best": average_rank.best,
                    }

            elif self.competition.type == CompetitionType.WCA.value:
                wca_ids = [competitor.person.wca_id for competitor in competitors]
                wca_ranks = WcaRank.get_by_wca_ids_and_event_id(wca_ids, event_id)
                for wca_rank in wca_ranks:
                    if wca_rank.type == RecordType.SINGLE.value:
                        bests[wca_rank.wca_id] = wca_rank
                    elif wca_rank.type == RecordType.AVERAGE.value:
                        averages[wca_rank.wca_id] = wca_rank

        competitor_list = []
        name = ""
        country = ""
        en_country = ""
        prefecture = ""
        best_rank = ""
        average_rank = ""
        is_first_timer = False
        country_info = Country()
        scj_competition_returner_list = self.get_scj_competition_returner_list()
        for competitor in competitors:
            if self.competition.type == CompetitionType.SCJ.value:
                name = competitor.person.get_full_name()
                prefecture = competitor.person.get_prefecture_id_display()
                best = (
                    bests[competitor.person.id]["best"]
                    if competitor.person.id in bests
                    else OUTLIERS
                )
                average = (
                    averages[competitor.person.id]["best"]
                    if competitor.person.id in averages
                    and averages[competitor.person.id]["best"] > 0
                    else OUTLIERS
                )
                best_rank = (
                    bests[competitor.person.id]["rank"]
                    if competitor.person.id in bests
                    else NA
                )
                average_rank = (
                    averages[competitor.person.id]["rank"]
                    if competitor.person.id in averages
                    and averages[competitor.person.id]["best"] > 0
                    else NA
                )
                is_first_timer = (
                    competitor.person.id not in scj_competition_returner_list
                )
            elif self.competition.type == CompetitionType.WCA.value:
                name = competitor.person.wca_name
                country = country_info.name(code=competitor.person.wca_country_iso2)
                en_country = country_info.en_name(
                    code=competitor.person.wca_country_iso2
                )
                prefecture = competitor.person.get_prefecture_id_display()
                best = (
                    bests[competitor.person.wca_id].best
                    if competitor.person.wca_id in bests
                    else OUTLIERS
                )
                average = (
                    averages[competitor.person.wca_id].best
                    if competitor.person.wca_id in averages
                    and averages[competitor.person.wca_id].best > 0
                    else OUTLIERS
                )
                best_rank = (
                    bests[competitor.person.wca_id].world_rank
                    if competitor.person.wca_id in bests
                    else NA
                )
                average_rank = (
                    averages[competitor.person.wca_id].world_rank
                    if competitor.person.wca_id in averages
                    and averages[competitor.person.wca_id].best > 0
                    else NA
                )

                is_first_timer = competitor.person.wca_id == ""
            competitor_list.append(
                {
                    "status": competitor.status,
                    "name": name,
                    "country": country,
                    "en_country": en_country,
                    "prefecture": prefecture,
                    "best": best,
                    "average": average,
                    "best_rank": best_rank,
                    "average_rank": average_rank,
                    "person": competitor.person,
                    "is_first_timer": is_first_timer,
                }
            )

        competitor_list = sorted(competitor_list, key=lambda x: x[sort_key])
        event_infos = list(
            map(lambda x: self.event_info(x), self.competition.event_ids)
        )

        context["competitors"] = competitor_list
        context["competitors_count_info"] = self.competitior_count_info(competitor_list)
        context["event_id"] = event_id
        context["event_id_name"] = self.event_id_name
        context["event_infos"] = event_infos

        return context

    def event_info(self, event_id):
        return {
            "event_id": event_id,
            "event_id_name": Event.get_id_name(event_id),
            "event_name": Event.get_name(event_id),
        }

    def competitior_count_info(self, competitors):
        returners = 0
        first_timers = 0
        country_count = 0
        pending_count = 0
        registration_count = 0
        for competitor in competitors:
            if competitor["status"] == CompetitorStatus.PENDING.value:
                pending_count += 1
                continue

            if competitor["is_first_timer"]:
                first_timers += 1
            else:
                returners += 1
        if self.competition.type == CompetitionType.WCA.value:
            countries = set(
                map(
                    lambda x: x["person"].wca_country_iso2
                    if x["status"] == CompetitorStatus.REGISTRATION.value
                    else NA,
                    competitors,
                )
            )
            if NA in countries:
                countries.remove(NA)
            country_count = len(countries)

        elif self.competition.type == CompetitionType.SCJ.value:
            countries = set(
                map(
                    lambda x: x["person"].prefecture_id
                    if x["status"] == CompetitorStatus.REGISTRATION.value
                    else NA,
                    competitors,
                )
            )
            if NA in countries:
                countries.remove(NA)
            country_count = len(countries)

        registration_count = max(0, returners + first_timers - pending_count)

        return {
            "sum": returners + first_timers,
            "returners": returners,
            "first_timers": first_timers,
            "country_count": country_count,
            "pending_count": pending_count,
            "registration_count": registration_count,
        }

    def get_scj_competition_returner_list(self):
        returners = []
        if self.competition.type == CompetitionType.SCJ.value:
            person_ids = []
            competitors = app.models.Competitor.objects.filter(
                competition_id=self.competition.id
            )
            for competitor in competitors:
                person_ids.append(competitor.person.id)
            # 大会経験者か確認するために全BestRank引く
            all_best_ranks = BestRank.objects.filter(person_id__in=person_ids)

            for best_rank in all_best_ranks:
                returners.append(best_rank.person.id)
        return returners
