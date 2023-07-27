from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.defines.session import Notification
from app.defines.competitor import Status as CompetitionStatus, ReceptionStatus
from .base import Base
import datetime
from app.forms import ReceptionForm
from django.utils.timezone import localtime


class Reception(LoginRequiredMixin, Base):
    template_name = "app/competition/reception.html"
    form_class = ReceptionForm

    def get(self, request, **kwargs):
        if not self.competition.use_reception:
            return redirect("competition_detail", self.competition.name_id)

        competition_serial = self.competition.get_serial()
        now = localtime(datetime.datetime.now(tz=datetime.timezone.utc))

        if kwargs.get("serial", "") != competition_serial:
            self.request.session["notification"] = Notification.INVALID_RECEPTION_PAGE
            return redirect("competition_detail", self.competition.name_id)

        if (
            self.competitor is None
            or self.competitor.status != CompetitionStatus.REGISTRATION.value
        ):
            self.request.session[
                "notification"
            ] = Notification.COMPETITON_NOT_REGISTRATION
            return redirect("competition_detail", self.competition.name_id)

        if self.competitor.reception_status != ReceptionStatus.NOT_YET_RECEPTION.value:
            return redirect("competition_detail", self.competition.name_id)

        if self.competition.open_at > now:
            self.request.session["notification"] = Notification.NOT_OPEN_COMPETITION
            return redirect("competition_detail", self.competition.name_id)

        competitor_dict = self.competitor.__dict__
        competitor_dict["full_name"] = self.competitor.person.get_full_name()
        form = ReceptionForm(initial=competitor_dict)
        return render(request, self.template_name, self.get_context(form))

    def get_context(self, form):
        context = super().get_context()
        context["form"] = form
        return context

    def post(self, request, **kwargs):
        return self.form_valid(request.POST, request, **kwargs)

    def form_valid(self, form, request, **kwargs):
        if form["guest_count"] == "0":
            if self.competitor.is_diffrence_event_and_price:
                self.competitor.reception_status = ReceptionStatus.SELF_RECEPTION.value
            else:
                self.competitor.reception_status = ReceptionStatus.ALL_RECEPTION.value
        else:
            self.competitor.reception_status = ReceptionStatus.SELF_RECEPTION.value
        save_form = ReceptionForm(form, instance=self.competitor)
        if not save_form.is_valid():
            return render(request, self.template_name, self.get_context(save_form))
        save_form.save()

        return redirect("competition_reception_complete", self.competition.name_id)
