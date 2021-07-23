from app.forms import MailChangeForm
from django.conf import settings
from django.shortcuts import redirect
from django.core.signing import dumps
from django.core.mail import send_mail
from django.views.generic import FormView
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from app.defines.session import Notification


class Change(LoginRequiredMixin, FormView):
    template_name = 'app/mail/change.html'
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

        subject = render_to_string('app/mail/mail_change_subject.txt', context).strip()
        message = render_to_string('app/mail/mail_change_message.txt', context).strip()
        send_mail(subject, message, settings.EMAIL_HOST_USER, [new_email])

        self.request.session['notification'] = Notification.MAIL_CHANGE

        return redirect('index')
