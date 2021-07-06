import app.models
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition, Competitor, Round
from app.defines.event import Event



class Result(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        competitors = Competitor.objects.filter(competition_id=competition.id)
        results = app.models.Result.objects.filter(competition_id=competition.id)
        rounds = Round.objects.filter(competition_id=competition.id)

        results = sorted(results, key=lambda x: x.rank)
        rounds = sorted(rounds, key=lambda x: x.type, reverse=True)

        competition_rounds = {}
        for round in rounds:
            if round.event_id in competition_rounds:
                competition_rounds[round.event_id].append(round.get_type_display())
            else:
                competition_rounds[round.event_id] = [round.get_type_display()]

        events = list({'event_id': k, 'event_name': v} for k, v in Event.get_events(competition.event_ids).items())

        competitor_names = {}
        for competitor in competitors:
            competitor_names[competitor.person.id] = competitor.person.get_full_name()

        competitor_wca_names = {}
        for competitor in competitors:
            competitor_wca_names[competitor.person.id] = competitor.person.wca_name

        competitor_prefectures = {}
        for competitor in competitors:
            competitor_prefectures[competitor.person.id] = competitor.person.get_prefecture_id_display()

        context = {
            'competition': competition,
            'competitor_names': competitor_names,
            'competitor_wca_names': competitor_wca_names,
            'competitor_prefectures': competitor_prefectures,
            'events': events,
            'rounds': competition_rounds,
            'results': results,
            'best_only_event_ids': Event.get_best_only_values(),
            'has_results': True,
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }

        return render(request, 'app/competition/result.html', context)