from django.utils.timezone import localtime
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition, Result, Round
from app.defines.event import Event


class Schedule(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0
        if has_results:
            return redirect('competition_detail', name_id=name_id)

        rounds = Round.objects.filter(competition_id=competition.id)

        # 日付 -> 会場 -> record
        round_dict = {}
        for round in rounds:
            date = localtime(round.begin_at).strftime('%Y年%m月%d日')
            if date in round_dict and round.room_name in round_dict[date]:
                round_dict[date][round.room_name].append(round)
            else:
                round_dict[date] = {round.room_name: [round]}

        # 種目ごとにラウンドを分ける(FMCが複数レコードある)
        event_round_types = {}
        for round in rounds:
            if round.event_id > 0:
                if round.event_id in event_round_types:
                    event_round_types[round.event_id].add(round.type)
                else:
                    event_round_types[round.event_id] = set([round.type])

        event_round_count_dict = {}
        for event_id, round_types in event_round_types.items():
            event_round_count_dict[event_id] = len(round_types)

        context = {
            'competition': competition,
            'round_dict': round_dict,
            'event_round_count_dict': event_round_count_dict,
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }

        return render(request, 'app/competition/schedule.html', context)
