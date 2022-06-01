from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from app.models import Person
from copy import deepcopy
from app.defines.prefecture import Prefecture
from app.defines.gender import Gender
from django.shortcuts import render, redirect


class AdminPerson(LoginRequiredMixin, TemplateView):
    template_name = "app/scj/admin/person.html"

    def get(self, request, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return super().get(request, **kwargs)
        else:
            return redirect("index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_list = Person.objects.all()
        modified = []
        for person in person_list.values():
            new_person = deepcopy(person)
            new_person["gender"] = Gender.get_name(person["gender"])
            new_person["prefecture"] = Prefecture.get_name(person["prefecture_id"])
            modified.append(new_person)
        context["modified"] = modified

        notification = self.request.session.get("notification")
        if self.request.session.get("notification") is not None:
            del self.request.session["notification"]
        context["notification"] = notification
        return context
