from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from app.forms import PersonEditForm
from app.models import Person, User
from django.shortcuts import render, redirect
from app.defines.session import Notification


class AdminPersonEdit(LoginRequiredMixin, FormView):
    template_name = "app/scj/admin/person_edit.html"
    form_class = PersonEditForm

    def get(self, request, **kwargs):
        user_id = kwargs.get("user_id")
        person = Person.objects.get(id=user_id)
        person_dict = person.__dict__
        person_dict["is_active"] = person.user.is_active
        form = PersonEditForm(initial=person_dict)
        return render(request, "app/scj/admin/person_edit.html", dict(form=form))

    def post(self, request, **kwargs):
        return self.form_valid(request.POST, **kwargs)

    def form_valid(self, form, **kwargs):
        person = Person.objects.get(id=kwargs["user_id"])
        save_form = PersonEditForm(form, instance=person)
        save_form.save()
        user = User.objects.get(id=kwargs["user_id"])
        user.is_active = save_form.cleaned_data["is_active"]
        user.save()
        self.request.session["notification"] = Notification.PERSON_INFO_CHANGE
        return redirect("admin_person")
