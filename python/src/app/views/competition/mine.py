from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competition, Competitor
from app.defines.competitor import Status as CompetitorStatus


# 参加する大会、企画している大会(公開/非表示/非公開)
class Mine(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):

        participate_competition_list = []
        current_competition_list = []
        hide_competition_list = []
        private_competition_list = []

        person_id = request.user.person.id

        # すべての大会
        competitions = Competition.objects.order_by('open_at').reverse()

        # 参加した大会
        competitors = Competitor.objects.filter(person__id=person_id).exclude(status=CompetitorStatus.CANCEL.value)
        participate_competition_ids = set(map(lambda x: x.competition_id, competitors))

        for competition in competitions:
            competition.set_is_superuser(request.user)

            # 非公開の企画している大会
            if competition.is_private \
                    and (request.user.is_superuser or person_id in competition.organizer_person_ids or person_id in competition.judge_person_ids):
                private_competition_list.append(competition)

            # 非表示の企画している大会
            elif not competition.is_display and not competition.is_private \
                    and (request.user.is_superuser or person_id in competition.organizer_person_ids or person_id in competition.judge_person_ids):
                hide_competition_list.append(competition)

            elif not competition.is_private and competition.is_display and competition.id in participate_competition_ids:
                if not competition.is_finish():
                    current_competition_list.append(competition)
                else:
                    participate_competition_list.append(competition)

        context = {
            'current_competitions': current_competition_list,
            'participate_competitions': participate_competition_list,
            'hide_competitions': hide_competition_list,
            'private_competitions': private_competition_list
        }

        return render(request, 'app/competition/mine.html', context)
