import datetime
from django.conf import settings
from django.shortcuts import render
from app.models import Person, StripeProgress
from app.defines.session import Notification
from .base import Base
from .util import calc_fee


class Fee(Base):

    template_name = "app/competition/fee.html"
    status = ""

    def get(self, request, **kwargs):
        if "status" in request.GET:
            self.status = request.GET.get("status")

        if self.status == "cancel":
            self.notification = Notification.PAYMENT_CANCEL
        elif self.status == "success":
            self.notification = Notification.PAYMENT_SUCCESS

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        stripe_user_id = ""
        if self.competition.stripe_user_person_id != 0:
            person = Person.objects.get(pk=self.competition.stripe_user_person_id)
            stripe_user_id = person.stripe_user_id

        amount = calc_fee(self.competition, self.competitor)

        is_paid = False
        if self.competitor:
            is_paid = StripeProgress.objects.filter(
                competitor_id=self.competitor.id
            ).exists()
        if self.status == "success":
            # 一旦支払い済みにする(同期が遅いときある)
            is_paid = True

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        fee_pay_close_at_timedelta = abs(self.competition.fee_pay_close_at - now)

        # 作成時のエラー
        admin_errors = self.request.session.get("competition_admin_errors")
        if self.request.session.get("competition_admin_errors") is not None:
            del self.request.session["competition_admin_errors"]

        context["fee_pay_close_at_timedelta"] = fee_pay_close_at_timedelta
        context["fees"] = amount["fees"]
        context["prepaid_fees"] = amount["prepaid_fees"]
        context["price"] = amount["price"]
        context["is_paid"] = is_paid
        context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY
        context["stripe_user_id"] = stripe_user_id
        context["now"] = now
        context[
            "is_payment"
        ] = self.competition.is_payment or self.competition.is_superuser(self.user)
        context["admin_errors"] = admin_errors
        context["is_load_stripe_lib"] = True

        return context
