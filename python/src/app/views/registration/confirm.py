from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.forms import PersonCreateForm, UserCreateForm


class Confirm(TemplateView):
    def get(self, request):
        session_form_data = request.session.get('form_data')
        if session_form_data is None:
            return redirect('registration_input')

        user_form = UserCreateForm(session_form_data, label_suffix="")
        person_form = PersonCreateForm(session_form_data, label_suffix="")

        recaptcha = False
        if 'recaptcha' in request.session:
            recaptcha = True

        context = {
            'user_form': user_form,
            'person_form': person_form,
            # get_xxx_displayを使う方法が見つからない。
            'gender': dict(person_form.fields['gender'].choices)[int(person_form.data['gender'])],
            'prefecture': dict(person_form.fields['prefecture_id'].choices)[int(person_form.data['prefecture_id'])],
            'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY,
            'recaptcha': recaptcha
        }
        return render(request, 'app/auth/registration_confirm.html', context)