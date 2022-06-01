from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import FormView
from app.forms import NameChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models.person import Person


class Change(LoginRequiredMixin, FormView):
    template_name = "app/name/change.html"
    form_class = NameChangeForm
    success_url = reverse_lazy("name_change_complete")

    def get(self, request):
        user_id = request.user.person.id
        person = Person.objects.get(id=user_id)
        initial_dict = dict(
            last_name=person.last_name,
            last_name_kana=person.last_name_kana,
            last_name_roma=person.last_name_roma,
            first_name=person.first_name,
            first_name_kana=person.first_name_kana,
            first_name_roma=person.first_name_roma,
        )
        form = NameChangeForm(initial=initial_dict)
        return render(request, "app/name/change.html", dict(form=form))

    def form_valid(self, form):
        user_id = self.request.user.person.id
        person = Person.objects.get(id=user_id)
        person.last_name = form.data.get("last_name")
        person.last_name_kana = form.data.get("last_name_kana")
        person.last_name_roma = form.data.get("last_name_roma")
        person.first_name = form.data.get("first_name")
        person.first_name_kana = form.data.get("first_name_kana")
        person.first_name_roma = form.data.get("first_name_roma")
        person.save()
        return super().form_valid(form)
