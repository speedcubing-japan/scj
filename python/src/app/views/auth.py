import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView, PasswordContextMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import Http404, HttpResponseBadRequest
from django.views.generic import View, DetailView, UpdateView, FormView, TemplateView
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from app.forms import PersonCreateForm, UserCreateForm, LoginForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, MailChangeForm, ProfileForm
from app.models import Person

User = get_user_model()

class RegistrationInput(View):
    def get(self, request):
        user_form = UserCreateForm(request.session.get('form_data'))
        person_form = PersonCreateForm(request.session.get('form_data')) 
        context = {
            'user_form': user_form,
            'person_form': person_form,
            'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY
        }
        return render(request, 'app/auth/registration_input.html', context)

    def post(self, request):
        user_form = UserCreateForm(request.POST)
        person_form = PersonCreateForm(request.POST)

        recaptcha = None
        if user_form.is_valid() and person_form.is_valid():
            recaptcha = '私はロボットではありませんにチェックを入れてください。'
            captcha = self.request.POST.get('g-recaptcha-response')
            if captcha:
                auth_url = 'https://www.google.com/recaptcha/api/siteverify?secret={}&response={}'
                auth_url = auth_url.format(settings.RECAPTCHA_SECRET_KEY, captcha)
                response = requests.get(auth_url)
                if response.json().get('success'):
                    request.session['form_data'] = request.POST
                    return redirect('registration_confirm')
        
        context = {
            'recaptcha': recaptcha,
            'user_form': user_form,
            'person_form': person_form,
        }

        return render(request, 'app/auth/registration_input.html', context)

class RegistrationConfirm(View):
    def get(self, request):
        session_form_data = request.session.get('form_data')
        if session_form_data is None:
            return redirect('registration_input')

        user_form = UserCreateForm(session_form_data, label_suffix="")
        person_form = PersonCreateForm(session_form_data, label_suffix="")

        context = {
            'user_form': user_form,
            'person_form': person_form,
            # get_xxx_displayを使う方法が見つからない。
            'gender': dict(person_form.fields['gender'].choices)[int(person_form.data['gender'])],
            'prefecture': dict(person_form.fields['prefecture_id'].choices)[int(person_form.data['prefecture_id'])],
        }
        return render(request, 'app/auth/registration_confirm.html', context)

class Registration(View):
    def post(self, request):
        session_form_data = request.session.get('form_data')
        if session_form_data is None:
            return redirect('registration_input')

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

            subject = render_to_string('mail/registration_subject.txt', context).strip()
            message = render_to_string('mail/registration_message.txt', context).strip()
            user.email_user(subject, message, settings.EMAIL_HOST_USER)

            request.session['notification'] = 'is_just_registration'

            return redirect('index')

        return redirect('registration_input')

class RegistrationComplete(View):
    timeout_seconds = settings.ACTIVATION_TIMEOUT_SECONDS
    
    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        except SignatureExpired:
            return HttpResponseBadRequest()

        except BadSignature:
            return HttpResponseBadRequest()

        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    user.is_active = True
                    user.save()

                    login(request, user)

                    request.session['notification'] = 'is_just_registration_complete'

                    return redirect('index')

        return HttpResponseBadRequest()    

class Login(LoginView):
    template_name = 'app/auth/login.html'
    form_class = LoginForm

class Logout(LogoutView):
    template_name = 'app/index.html'

class PasswordChange(PasswordChangeView):
    template_name = 'app/auth/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_complete')

class PasswordChangeComplete(View):
    def get(self, request):
        self.request.session['notification'] = 'is_just_password_change'
        return redirect('index')

class PasswordReset(FormView):
    template_name = 'app/auth/password_reset.html'
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = User.objects.get(email=email)

        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': default_token_generator.make_token(user),
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        }

        subject = render_to_string('mail/password_reset_subject.txt', context).strip()
        message = render_to_string('mail/password_reset_message.txt', context).strip()
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        self.request.session['notification'] = 'is_just_password_reset'
        return redirect('index')

class PasswordResetComplete(PasswordResetConfirmView):
    success_url = reverse_lazy('index')
    template_name = 'app/auth/password_reset_complete.html'
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session['notification'] = 'is_just_password_reset_complete'
        return context

class MailChange(LoginRequiredMixin, FormView):
    template_name = 'app/auth/mail_change.html'
    form_class = MailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('mail/mail_change_subject.txt', context).strip()
        message = render_to_string('mail/mail_change_message.txt', context).strip()
        send_mail(subject, message, settings.EMAIL_HOST_USER, [new_email])

        self.request.session['notification'] = 'is_just_mail_change'

        return redirect('index')

class MailChangeComplete(LoginRequiredMixin, View):
    timeout_seconds = settings.ACTIVATION_TIMEOUT_SECONDS

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        except SignatureExpired:
            return HttpResponseBadRequest()

        except BadSignature:
            return HttpResponseBadRequest()

        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()

            login(request, request.user)

            self.request.session['notification'] = 'is_just_mail_change_complete'

            return redirect('index')

        return HttpResponseBadRequest()
