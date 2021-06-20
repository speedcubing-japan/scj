import datetime
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import Competition
from app.forms import CompetitionForm
from app.defines.event import Event
from app.defines.prefecture import Prefecture
from app.defines.competition import Type as CompetitionType
from app.defines.competition import SCJ_COMPETITON_FIRST_YEAR


class Index(TemplateView):
    def get(self, request):
        type = int(self.request.GET.get(key='type', default=0))
        event_id = int(self.request.GET.get(key='event_id', default=0))
        year = int(self.request.GET.get(key='year', default=0))
        prefecture_id = int(self.request.GET.get(key='prefecture_id', default=0))

        form = CompetitionForm(initial = {
            'type': type,
            'event_id': event_id,
            'year': year,
            'prefecture_id': prefecture_id,
        })

        competition_types = [(0, '全種別')]
        competition_types += list(map(lambda x: (x[0], str(x[1]) + '大会'), CompetitionType.choices()))
        form.fields['type'].choices = competition_types

        events = [(0, '全種目')]
        events += Event.choices()
        form.fields['event_id'].choices = tuple(events)

        years = [(0, '最新')]
        current_year = datetime.date.today().year
        years += list(map(lambda x: (x, str(x) + '年'), reversed(range(SCJ_COMPETITON_FIRST_YEAR, current_year + 1))))
        form.fields['year'].choices = tuple(years)

        prefectures = [(0, '全都道府県')]
        prefectures += list(map(lambda x: (x.value, x.name), Prefecture))
        form.fields['prefecture_id'].choices = tuple(prefectures)

        competitions = Competition.objects.order_by('open_at').reverse()

        if type != 0:
            competitions = competitions.filter(type=type)

        if event_id != 0:
            competitions = competitions.filter(event_ids__contains=[event_id])

        if year != 0:
            competitions = competitions.filter(open_at__year=year)

        if prefecture_id != 0:
            competitions = competitions.filter(prefecture_id=prefecture_id)

        competition_list = []
        finish_competition_list = []

        for competition in competitions:
            if competition.is_open() or not competition.is_close():
                competition_list.append(competition)
            else:
                finish_competition_list.append(competition)

        context = {
            'form': form,
            'competitions': competition_list,
            'finish_competitions': finish_competition_list
        }

        return render(request, 'app/competition/index.html', context)