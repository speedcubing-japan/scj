import app.models
from django.shortcuts import render
from app.models import Competitor, Round
from app.defines.event import Event, WinFormat
from app.defines.competition import RoundType
from app.views.util.record import Record
from .base import Base


class Result(Base):

    template_name = "app/competition/result.html"

    OUTLIERS = 99999999999

    def get(self, request, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        competitors = Competitor.objects.filter(competition_id=self.competition.id)
        results = app.models.Result.objects.filter(competition_id=self.competition.id)
        rounds = Round.objects.filter(competition_id=self.competition.id)

        sorted_results = []
        results_by_event_id_dict = {}
        for result in results:
            results_by_event_id_dict.setdefault(result.event_id, []).append(result)

        for event_id in self.competition.event_ids:

            if event_id not in results_by_event_id_dict:
                continue

            if Event.get_win_format(event_id) == WinFormat.AVERAGE:
                sorted_event_results = sorted(
                    results_by_event_id_dict[event_id],
                    key=lambda result: (
                        result.average if result.average > 0 else self.OUTLIERS,
                        result.best if result.best > 0 else self.OUTLIERS,
                    ),
                )
            elif Event.get_win_format(event_id) == WinFormat.BEST:
                sorted_event_results = sorted(
                    results_by_event_id_dict[event_id],
                    key=lambda result: (
                        result.best if result.best > 0 else self.OUTLIERS,
                    ),
                )

            order_dict = {}
            ordered_dict = {}
            for result in sorted_event_results:
                record = Record(
                    result.value1,
                    result.value2,
                    result.value3,
                    result.value4,
                    result.value5,
                    result.event_id
                )
                result.format_values = record.format_values()
                result.set_round_name(RoundType.get_name(result.round_type))

                if result.event_id not in order_dict:
                    order_dict[result.event_id] = {}
                    ordered_dict[result.event_id] = {}

                if result.round_type not in order_dict[result.event_id]:
                    order_dict[result.event_id][result.round_type] = {}
                    ordered_dict[result.event_id][result.round_type] = {}

                item = (result.average, result.best)
                if item in order_dict[result.event_id][result.round_type]:
                    order = order_dict[result.event_id][result.round_type][item]
                else:
                    order = len(order_dict[result.event_id][result.round_type])
                    order_dict[result.event_id][result.round_type][item] = order

                ordered_dict[result.event_id][result.round_type][item] = order

                for round in rounds:
                    if (
                        round.event_id == result.event_id
                        and round.type == result.round_type
                    ):
                        round.set_is_hold(True)

            for result in sorted_event_results:
                item = (result.average, result.best)
                result.rank = ordered_dict[result.event_id][result.round_type][item] + 1

            sorted_results.extend(sorted_event_results)

        rounds = sorted(rounds, key=lambda x: x.type, reverse=True)

        events = list(
            {"event_id": k, "event_name": v}
            for k, v in Event.get_events(self.competition.event_ids).items()
        )

        competition_rounds = {}
        for round in rounds:
            if round.event_id in competition_rounds:
                competition_rounds[round.event_id].append(round)
            else:
                competition_rounds[round.event_id] = [round]

        competitor_names = {}
        for competitor in competitors:
            competitor_names[competitor.person.id] = competitor.person.get_full_name()

        competitor_wca_names = {}
        for competitor in competitors:
            competitor_wca_names[competitor.person.id] = competitor.person.wca_name

        competitor_prefectures = {}
        for competitor in competitors:
            competitor_prefectures[
                competitor.person.id
            ] = competitor.person.get_prefecture_id_display()

        context["competitor_names"] = competitor_names
        context["competitor_wca_names"] = competitor_wca_names
        context["competitor_prefectures"] = competitor_prefectures
        context["competition_rounds"] = competition_rounds
        context["events"] = events
        context["results"] = sorted_results
        context["best_only_event_ids"] = Event.get_best_only_values()

        return context
