from django.views.generic import TemplateView
from app.models import Competition
from app.defines.competition import Type as CompetitionType
import datetime


class CompetitionHistory(TemplateView):
    template_name = "app/scj/competition_history.html"
    limit_date = datetime.datetime(2024, 7, 31, 23, 59, 59, 000000)

    def get_context_data(self):

        competitions = (
            Competition.objects.filter(type=CompetitionType.SCJ.value, open_at__lte=self.limit_date, is_display=True, is_private=False, is_cancel=False)
            .order_by("open_at")
            .reverse()
        )

        new_competitions = (
            Competition.objects.filter(type=CompetitionType.SCJ.value, open_at__gte=self.limit_date, is_display=True, is_private=False, is_cancel=False)
            .order_by("open_at")
            .reverse()
        )

        context = {
            "competitions": competitions,
            "new_competitions": new_competitions,
        }

        return context
