from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import View
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads
from app.models import User


class Complete(View):
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