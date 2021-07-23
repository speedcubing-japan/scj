import stripe
import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Person, Competitor, StripeProgress
from app.views.competition.base import Base
from app.views.competition.util import calc_fee
from app.defines.session import Notification


class Refund(LoginRequiredMixin, Base):

    template_name = "app/competition/admin/refund.html"
    competitor_list = []

    def get(self, request, **kwargs):
        if not self.competition.is_refunder(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        stripe_progresses = StripeProgress.objects.filter(
            competition_id=self.competition.id, refund_price=0
        )
        competitors = Competitor.objects.filter(competition_id=self.competition.id)

        self.competitor_list = []
        for competitor in competitors:
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)
                    self.competitor_list.append(competitor)

        return render(request, self.template_name, self.get_context())

    def post(self, request, **kwargs):
        if not self.competition.is_refunder(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_user_person = None
        if self.competition.stripe_user_person_id > 0:
            stripe_user_person = Person.objects.get(
                pk=self.competition.stripe_user_person_id
            )

        stripe_progresses = StripeProgress.objects.filter(
            competition_id=self.competition.id, refund_price=0
        )
        competitors = Competitor.objects.filter(
            competition_id=self.competition.id
        ).order_by("created_at")

        self.competitor_list = []
        for competitor in competitors:

            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)

            if request.POST.get("competitor_id_" + str(competitor.id)):
                stripe_progress = competitor.stripe_progress

                fee = calc_fee(self.competition, competitor)
                amount = int(fee["price"])
                if request.POST.get("competitor_refund_" + str(competitor.id)):
                    part_amount = int(
                        request.POST.get("competitor_refund_" + str(competitor.id))
                    )
                    if amount < part_amount:
                        request.session[
                            "notification"
                        ] = Notification.REFUND_AMOUNT_OVER
                        return redirect(
                            "competition_admin_refund", name_id=self.name_id
                        )
                    amount = part_amount

                if stripe_user_person:
                    stripe.Refund.create(
                        amount=amount,
                        charge=stripe_progress.charge_id,
                        stripe_account=stripe_user_person.stripe_user_id,
                    )
                else:
                    stripe.Refund.create(
                        amount=amount, charge=stripe_progress.charge_id
                    )

                # 全額返金時(種目追加時)のみcompetitor_idを0にして再度支払えるようにする
                if fee["price"] == amount:
                    stripe_progress.competitor_id = 0
                else:
                    stripe_progress.pay_price -= amount

                stripe_progress.refund_price = amount
                stripe_progress.refund_at = datetime.datetime.now(
                    tz=datetime.timezone.utc
                )
                stripe_progress.save(
                    update_fields=[
                        "competitor_id",
                        "pay_price",
                        "refund_price",
                        "refund_at",
                        "updated_at",
                    ]
                )
                competitor.unset_stripe_progress()

                self.send_mail_refund("registration_refund", price=amount)

            if competitor.stripe_progress:
                self.competitor_list.append(competitor)

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()
        context["competitors"] = self.competitor_list
        return context
