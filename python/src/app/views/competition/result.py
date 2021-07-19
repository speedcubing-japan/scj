import app.models
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition, Competitor, Round
from app.defines.event import Event
from .base import Base


class Result(Base):

    template_name = 'app/competition/result.html'

    def get(self, request, **kwargs):

        if self.competition.is_private and not self.competition.is_superuser(request.user):
            return redirect('competition_index')

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        competitors = Competitor.objects.filter(competition_id=self.competition.id)
        results = app.models.Result.objects.filter(competition_id=self.competition.id)
        rounds = Round.objects.filter(competition_id=self.competition.id)

        results = sorted(results, key=lambda x: x.rank)
        rounds = sorted(rounds, key=lambda x: x.type, reverse=True)

        competition_rounds = {}
        for round in rounds:
            if round.event_id in competition_rounds:
                competition_rounds[round.event_id].append(round.get_type_display())
            else:
                competition_rounds[round.event_id] = [round.get_type_display()]

        events = list({'event_id': k, 'event_name': v} for k, v in Event.get_events(self.competition.event_ids).items())

        competitor_names = {}
        for competitor in competitors:
            competitor_names[competitor.person.id] = competitor.person.get_full_name()

        competitor_wca_names = {}
        for competitor in competitors:
            competitor_wca_names[competitor.person.id] = competitor.person.wca_name

        competitor_prefectures = {}
        for competitor in competitors:
            competitor_prefectures[competitor.person.id] = competitor.person.get_prefecture_id_display()

        context['competitor_names'] = competitor_names
        context['competitor_wca_names'] = competitor_wca_names
        context['competitor_prefectures'] = competitor_prefectures
        context['events'] = events
        context['rounds'] = competition_rounds
        context['results'] = results
        context['best_only_event_ids'] = Event.get_best_only_values()

        return context
