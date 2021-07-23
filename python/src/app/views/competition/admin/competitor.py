import app.models
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import StripeProgress
from app.defines.event import Event
from app.views.competition.base import Base
from app.defines.session import Notification


class Competitor(LoginRequiredMixin, Base):

    template_name = "app/competition/admin/edit.html"
    target_competitor = None

    def get(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        if "competitor_id" not in kwargs:
            return redirect("competition_detail", name_id=self.name_id)

        competitor_id = kwargs.get("competitor_id")
        competitor = app.models.Competitor.objects.filter(id=competitor_id)
        if not competitor.exists():
            return redirect("competition_detail", name_id=self.name_id)
        self.target_competitor = competitor.first()

        return render(request, self.template_name, self.get_context())

    def post(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        if "competitor_id" not in request.POST:
            return redirect("competition_detail", name_id=self.name_id)

        competitor_id = request.POST.get(key="competitor_id")
        competitor = app.models.Competitor.objects.filter(id=competitor_id)
        if not competitor.exists():
            return redirect("competition_detail", name_id=self.name_id)
        self.target_competitor = competitor.first()

        event_ids = []
        for event_id in self.competition.event_ids:
            if request.POST.get("event_id_" + str(event_id)):
                event_ids.append(event_id)

        guest_count = 0
        if request.POST.get("guest_count"):
            guest_count = int(request.POST.get("guest_count"))

        if event_ids:
            self.target_competitor.update_event_ids_and_guest_count(
                event_ids, guest_count
            )
            self.notification = Notification.UPDATE
        else:
            self.notification = Notification.COMPETITOR_EVENT_NOT_SELECTED

        return render(request, self.template_name, self.get_context())

    def get_context(self):

        is_prepaid = False
        if self.target_competitor:
            is_prepaid = StripeProgress.objects.filter(
                competitor_id=self.target_competitor.id
            ).exists()

        context = super().get_context()
        context["events"] = Event.get_events(self.competition.event_ids)
        context["competitor"] = self.target_competitor
        context["guest_counts"] = range(self.competition.guest_limit + 1)
        context["is_prepaid"] = is_prepaid

        return context
