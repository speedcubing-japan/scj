from django.conf import settings
from app.forms import PasswordResetForm
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.views.generic import FormView
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from app.models import User


class Reset(FormView):
    template_name = 'app/password/reset.html'
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

        subject = render_to_string('app/mail/password_reset_subject.txt', context).strip()
        message = render_to_string('app/mail/password_reset_message.txt', context).strip()
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        self.request.session['notification'] = 'is_just_password_reset'
        return redirect('index')