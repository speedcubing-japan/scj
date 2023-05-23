from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competitor
from app.defines.competitor import Status as CompetitorStatus, ReceptionStatus
from app.views.competition.base import Base
from app.defines.session import Notification
from app.models import StripeProgress
from app.views.competition.util import calc_fee


class Reception(LoginRequiredMixin, Base):
    template_name = "app/competition/admin/reception.html"
    competitors = None

    def get(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_index")

        if not self.competition.use_reception:
            return redirect("competition_detail", self.competition.name_id)

        self.competitors = (
            Competitor.objects.filter(competition_id=self.competition.id)
            .filter(status=CompetitorStatus.REGISTRATION.value)
            .order_by("created_at")
        )

        return render(request, self.template_name, self.get_context())

    def post(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_index")

        if "self" in request.POST:
            competitor_id = request.POST.get("self")
            competitor = Competitor.objects.get(id=competitor_id)
            if competitor.guest_count == 0:
                competitor.reception_status = ReceptionStatus.ALL_RECEPTION.value
            else:
                competitor.reception_status = ReceptionStatus.SELF_RECEPTION.value
            competitor.save()
        elif "all" in request.POST:
            competitor_id = request.POST.get("all")
            competitor = Competitor.objects.get(id=competitor_id)
            competitor.reception_status = ReceptionStatus.ALL_RECEPTION.value
            competitor.save()

        self.competitors = Competitor.objects.filter(
            competition_id=self.competition.id
        ).order_by("created_at")
        self.request.session["notification"] = Notification.COMPETITOR_RECEPTION_SUCCESS

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        not_yet_reception_competitors = []
        self_reception_competitors = []
        all_reception_competitors = []
        guest_count = 0
        visitor_count = self.competition.free_visitor_count

        stripe_progresses = StripeProgress.objects.filter(
            competition_id=self.competition.id
        )
        for number, competitor in enumerate(self.competitors):
            competitor.set_registration_number(number + 1)

            amount = calc_fee(self.competition, competitor)
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)
                    if amount["price"] != stripe_progress.pay_price:
                        competitor.set_is_diffrence_event_and_price()

            if competitor.reception_status == ReceptionStatus.NOT_YET_RECEPTION.value:
                not_yet_reception_competitors.append(competitor)
            elif competitor.reception_status == ReceptionStatus.SELF_RECEPTION.value:
                self_reception_competitors.append(competitor)
            elif competitor.reception_status == ReceptionStatus.ALL_RECEPTION.value:
                all_reception_competitors.append(competitor)
                guest_count += competitor.actual_guest_count
                visitor_count += competitor.visitor_count

        reception_count = len(self_reception_competitors) + len(
            all_reception_competitors
        )
        context["not_yet_reception_competitors"] = not_yet_reception_competitors
        context["self_reception_competitors"] = self_reception_competitors
        context["all_reception_competitors"] = all_reception_competitors
        context["not_yet_reception_count"] = len(not_yet_reception_competitors)
        context["reception_count"] = reception_count
        context["guest_count"] = guest_count
        context["visitor_count"] = visitor_count
        context["free_visitor_count"] = self.competition.free_visitor_count
        context["all_count"] = reception_count + guest_count + visitor_count
        context["competitors_count"] = (
            len(not_yet_reception_competitors)
            + len(self_reception_competitors)
            + len(all_reception_competitors)
        )

        return context
