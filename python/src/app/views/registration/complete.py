from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import View
from django.http import HttpResponseBadRequest
from django.core.signing import BadSignature, SignatureExpired, loads
from app.models import User
from app.defines.session import Notification


class Complete(View):
    timeout_seconds = settings.ACTIVATION_TIMEOUT_SECONDS

    def get(self, request, **kwargs):
        token = kwargs.get("token")
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        except SignatureExpired:
            request.session["notification"] = Notification.REGISTRATION_EXPIRED
            return redirect("index")

        except BadSignature:
            request.session["notification"] = Notification.REGISTRATION_BAD_SIGNATURE
            return redirect("index")

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

                    request.session["notification"] = Notification.REGISTRATION_COMPLETE

                    return redirect("index")
                else:
                    login(request, user)
                    request.session[
                        "notification"
                    ] = Notification.REGISTRATION_ALREADY_COMPLETED
                    return redirect("index")

        return HttpResponseBadRequest()
