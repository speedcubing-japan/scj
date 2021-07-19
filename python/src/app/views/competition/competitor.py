import app.models
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition, Competitor, Result, BestRank, AverageRank, WcaBestRank, WcaAverageRank
from app.defines.event import Event
from app.defines.country import Country
from app.defines.define import OUTLIERS
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus
from .base import Base


class Competitor(Base):

    template_name = 'app/competition/competitor.html'
    event_name = ''

    def get(self, request, **kwargs):
        if 'event_name' not in kwargs:
            return redirect('competition_index')
        self.event_name = kwargs.get('name_id')

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        event_id = 0
        if self.event_name != 'list':
            event_id = Event.get_value(self.event_name)

        if event_id:
            competitors = app.models.Competitor.objects.filter(competition_id=self.competition.id, event_ids__contains=event_id)
        else:
            competitors = app.models.Competitor.objects.filter(competition_id=self.competition.id)

        if self.competition.is_display_pending_competitor:
            competitors = competitors.exclude(status=CompetitorStatus.CANCEL.value).order_by('created_at')
        else:
            competitors = competitors.filter(status=CompetitorStatus.REGISTRATION.value).order_by('created_at')

        bests = {}
        averages = {}
        if event_id:
            if self.competition.type == CompetitionType.SCJ.value:
                person_ids = []
                for competitor in competitors:
                    person_ids.append(competitor.person.id)

                best_ranks = BestRank.objects.filter(event_id=event_id, person_id__in=person_ids)
                for best_rank in best_ranks:
                    bests[best_rank.person.id] = best_rank.best

                average_ranks = AverageRank.objects.filter(event_id=event_id, person_id__in=person_ids)
                for average_rank in average_ranks:
                    averages[average_rank.person.id] = average_rank.best

            elif self.competition.type == CompetitionType.WCA.value:
                wca_ids = []
                for competitor in competitors:
                    wca_ids.append(competitor.person.wca_id)

                wca_best_ranks = WcaBestRank.objects.filter(event_id=event_id, wca_id__in=wca_ids)
                for wca_best_rank in wca_best_ranks:
                    bests[wca_best_rank.wca_id] = wca_best_rank.best / 100

                wca_average_ranks = WcaAverageRank.objects.filter(event_id=event_id, wca_id__in=wca_ids)
                for wca_average_rank in wca_average_ranks:
                    averages[wca_average_rank.wca_id] = wca_average_rank.best / 100

        competitor_list = []
        name = ''
        country = ''
        prefecture = ''
        for competitor in competitors:
            if self.competition.type == CompetitionType.SCJ.value:
                name = competitor.person.get_full_name()
                prefecture = competitor.person.get_prefecture_id_display()
                best = bests[competitor.person.id] if competitor.person.id in bests else OUTLIERS
                average = averages[competitor.person.id] if competitor.person.id in averages else OUTLIERS
            elif self.competition.type == CompetitionType.WCA.value:
                name = competitor.person.wca_name
                country_names = dict(Country.choices())
                country = country_names[competitor.person.wca_country_iso2]
                best = bests[competitor.person.wca_id] if competitor.person.wca_id in bests else OUTLIERS
                average = averages[competitor.person.wca_id] if competitor.person.wca_id in averages else OUTLIERS

            competitor_list.append({
                'status': competitor.status,
                'name': name,
                'country': country,
                'prefecture': prefecture,
                'best': best,
                'average': average,
            })

        competitor_list = sorted(competitor_list, key=lambda x: x['average'])
        event_names = Event.get_names(self.competition.event_ids)

        context['competitors'] = competitor_list
        context['event_id'] = event_id
        context['event_name'] = self.event_name
        context['event_names'] = event_names

        return context