from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.forms import PersonCreateForm, UserCreateForm


class Input(TemplateView):
    def get(self, request):
        user_form = UserCreateForm(request.session.get("form_data"))
        person_form = PersonCreateForm(request.session.get("form_data"))
        context = {"user_form": user_form, "person_form": person_form}
        return render(request, "app/registration/input.html", context)

    def post(self, request):
        user_form = UserCreateForm(request.POST)
        person_form = PersonCreateForm(request.POST)

        if user_form.is_valid() and person_form.is_valid():
            request.session["form_data"] = request.POST
            return redirect("registration_confirm")

        context = {
            "user_form": user_form,
            "person_form": person_form,
        }

        return render(request, "app/registration/input.html", context)
