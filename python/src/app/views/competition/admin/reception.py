from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competitor
from app.defines.competitor import Status as CompetitorStatus, ReceptionStatus
from app.views.competition.base import Base
from app.views.competition.util import set_is_diffrence_event_and_price
from app.defines.session import Notification


class Reception(LoginRequiredMixin, Base):
    template_name = "app/competition/admin/reception.html"
    competitors = None

    def get(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_index")

        if not self.competition.use_reception:
            return redirect("competition_detail", self.competition.name_id)

        self.competitors = self.competition.get_competitors().filter(
            status=CompetitorStatus.REGISTRATION.value
        )

        return render(request, self.template_name, self.get_context())

    def post(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_index")

        if "self" in request.POST:
            competitor_id = request.POST.get("self")
            competitor = Competitor.objects.get(id=competitor_id)
            reception_status = competitor.reception_status
            if competitor.guest_count == 0:
                reception_status = ReceptionStatus.ALL_RECEPTION.value
            else:
                reception_status = ReceptionStatus.SELF_RECEPTION.value
            competitor.update_reception_status(reception_status)
        elif "all" in request.POST:
            competitor_id = request.POST.get("all")
            competitor = Competitor.objects.get(id=competitor_id)
            competitor.update_reception_status(ReceptionStatus.ALL_RECEPTION.value)

        self.competitors = self.competition.get_competitors()
        self.request.session["notification"] = Notification.COMPETITOR_RECEPTION_SUCCESS

        return redirect("competition_admin_reception", self.competition.name_id)

    def get_context(self):
        context = super().get_context()

        not_yet_reception_competitors = []
        self_reception_competitors = []
        all_reception_competitors = []
        guest_count = 0

        # 支払額チェック
        set_is_diffrence_event_and_price(self.competition, self.competitors)

        for number, competitor in enumerate(self.competitors):
            competitor.set_registration_number(number + 1)

            if competitor.reception_status == ReceptionStatus.NOT_YET_RECEPTION.value:
                not_yet_reception_competitors.append(competitor)
            elif competitor.reception_status == ReceptionStatus.SELF_RECEPTION.value:
                self_reception_competitors.append(competitor)
            elif competitor.reception_status == ReceptionStatus.ALL_RECEPTION.value:
                all_reception_competitors.append(competitor)

        reception_count = len(self_reception_competitors) + len(
            all_reception_competitors
        )
        context["not_yet_reception_competitors"] = not_yet_reception_competitors
        context["self_reception_competitors"] = self_reception_competitors
        context["all_reception_competitors"] = all_reception_competitors
        context["not_yet_reception_count"] = len(not_yet_reception_competitors)
        context["reception_count"] = reception_count
        context["guest_count"] = guest_count
        context["all_count"] = reception_count + guest_count
        context["competitors_count"] = (
            len(not_yet_reception_competitors)
            + len(self_reception_competitors)
            + len(all_reception_competitors)
        )

        return context
