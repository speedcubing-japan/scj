from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import View
from django.http import HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.signing import BadSignature, SignatureExpired, loads
from app.models import User


class ChangeComplete(LoginRequiredMixin, View):
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
