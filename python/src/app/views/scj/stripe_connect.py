from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class StripeConnect(LoginRequiredMixin, TemplateView):
    def get(self, request):

        notification = self.request.session.get("notification")
        if self.request.session.get("notification") is not None:
            del self.request.session["notification"]

        context = {
            "stripe_oauth_authorization": settings.STRIPE_OAUTH_AUTHORIZATION,
            "stripe_client_id": settings.STRIPE_CLIENT_ID,
            "notification": notification,
        }

        return render(request, "app/scj/stripe_connect.html", context)
