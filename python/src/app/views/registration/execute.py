import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import View
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import dumps
from app.forms import PersonCreateForm, UserCreateForm


class Execute(View):
    def post(self, request):
        session_form_data = request.session.get('form_data')
        if session_form_data is None:
            return redirect('registration_input')

        captcha = self.request.POST.get('g-recaptcha-response')
        if captcha:
            auth_url = 'https://www.google.com/recaptcha/api/siteverify?secret={}&response={}'
            auth_url = auth_url.format(settings.RECAPTCHA_SECRET_KEY, captcha)
            response = requests.get(auth_url)
            if not response.json().get('success'):
                request.session['recaptcha'] = True
                return redirect('registration_confirm')
        else:
            request.session['recaptcha'] = True
            return redirect('registration_confirm')

        del request.session['form_data']

        user_form = UserCreateForm(session_form_data)
        person_form = PersonCreateForm(session_form_data)

        if user_form.is_valid() and person_form.is_valid():

            user = user_form.save(commit=False)
            user.is_active = False
            user.last_name = person_form.cleaned_data.get('last_name')
            user.first_name = person_form.cleaned_data.get('first_name')
            user.save()

            person = person_form.save(commit=False)
            person.user = user
            person.save()

            current_site = get_current_site(self.request)
            domain = current_site.domain
            context = {
                'protocol': self.request.scheme,
                'domain': domain,
                'token': dumps(user.pk),
                'user': user,
            }

            subject = render_to_string('app/mail/registration_subject.txt', context).strip()
            message = render_to_string('app/mail/registration_message.txt', context).strip()
            user.email_user(subject, message, settings.EMAIL_HOST_USER)

            request.session['notification'] = 'is_just_registration'

            return redirect('index')

        return redirect('registration_input')