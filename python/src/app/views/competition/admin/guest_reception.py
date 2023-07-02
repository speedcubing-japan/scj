from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competitor
from app.defines.competitor import ReceptionStatus
from app.views.competition.base import Base
from app.defines.session import Notification
from app.forms import ReceptionForm


class GuestReception(LoginRequiredMixin, Base):
    template_name = "app/competition/admin/guest_reception.html"
    competitors = None
    form_class = ReceptionForm

    def get(self, request, **kwargs):
        competitor_id = kwargs.get("competitor_id")
        competitor = Competitor.objects.get(id=competitor_id)
        competitor_dict = competitor.__dict__
        competitor_dict["full_name"] = competitor.person.get_full_name()
        form = ReceptionForm(initial=competitor_dict)
        return render(request, self.template_name, self.get_context(form))

    def get_context(self, form):
        context = super().get_context()
        context["form"] = form
        return context

    def post(self, request, **kwargs):
        if "cancel" in request.POST:
            competitor = Competitor.objects.get(id=kwargs["competitor_id"])
            competitor.update_reception_status(ReceptionStatus.NOT_YET_RECEPTION.value)
            self.request.session["notification"] = Notification.RECEPTION_CANCEL
            return redirect("competition_admin_reception", self.competition.name_id)
        return self.form_valid(request.POST, request, **kwargs)

    def form_valid(self, form, request, **kwargs):
        competitor = Competitor.objects.get(id=kwargs["competitor_id"])
        competitor.reception_status = ReceptionStatus.ALL_RECEPTION.value
        save_form = ReceptionForm(form, instance=competitor)
        if not save_form.is_valid():
            return render(request, self.template_name, self.get_context(save_form))
        save_form.save()
        self.request.session["notification"] = Notification.GUEST_RECEPTION_SUCCESS
        return redirect("competition_admin_reception", self.competition.name_id)
