from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.views.competition.base import Base
from app.defines.session import Notification
from app.forms import VisitorForm


class VisitorReception(LoginRequiredMixin, Base):
    template_name = "app/competition/admin/visitor_reception.html"
    form_class = VisitorForm

    def get(self, request, **kwargs):
        competition_dict = self.competition.__dict__
        form = VisitorForm(initial=competition_dict)
        return render(request, self.template_name, self.get_context(form))

    def get_context(self, form):
        context = super().get_context()
        context["form"] = form
        return context

    def post(self, request, **kwargs):
        return self.form_valid(request.POST, request, **kwargs)

    def form_valid(self, form, request, **kwargs):
        save_form = VisitorForm(form, instance=self.competition)
        if not save_form.is_valid():
            return render(request, self.template_name, self.get_context(save_form))
        save_form.save()
        self.request.session["notification"] = Notification.VISITOR_RECEPTION_SUCCESS
        return redirect("competition_admin_reception", self.competition.name_id)
