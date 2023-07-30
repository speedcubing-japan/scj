import stripe
import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Person, Competitor, StripeProgress
from app.views.competition.base import Base
from app.views.competition.util import calc_fee
from app.defines.session import Notification
from app.defines.competitor import Status as CompetitorStatus


class Refund(LoginRequiredMixin, Base):

    template_name = "app/competition/admin/refund.html"
    refund_competitor_list = []

    def get(self, request, **kwargs):
        if not self.competition.is_refunder(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        stripe_progresses = StripeProgress.objects.filter(
            competition_id=self.competition.id, refund_price=0
        )
        competitors = Competitor.objects.filter(competition_id=self.competition.id)

        self.refund_competitor_list = []
        self.set_refund_competitor_list(competitors, stripe_progresses)

        return render(request, self.template_name, self.get_context())

    def post(self, request, **kwargs):
        if not self.competition.is_refunder(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        if self.competition.is_registration_open():
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
        competitors = Competitor.objects.filter(competition_id=self.competition.id)

        self.refund_competitor_list = []
        self.set_refund_competitor_list(competitors, stripe_progresses)

        for competitor in self.refund_competitor_list:

            if request.POST.get("competitor_id_" + str(competitor.id)):
                stripe_progress = competitor.stripe_progress

                # 返金額が参加者の種目変更で変動するので、参加種目からの計算は良くない。あくまで支払った金額をamountにする。
                amount = competitor.stripe_progress.pay_price
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

                stripe_progress.refund_price = amount
                stripe_progress.refund_at = datetime.datetime.now(
                    tz=datetime.timezone.utc
                )
                stripe_progress.save(
                    update_fields=[
                        "refund_price",
                        "refund_at",
                        "updated_at",
                    ]
                )
                competitor.unset_stripe_progress()

                self.send_mail_refund(
                    competitor.person.user, "registration_refund", price=amount
                )

        # 課金記録が残っているもので再度リストを生成しなおす
        self.refund_competitor_list = [
            x for x in self.refund_competitor_list if x.stripe_progress
        ]

        return render(request, self.template_name, self.get_context())

    def set_refund_competitor_list(self, competitors, stripe_progresses):
        for competitor in competitors:
            amount = calc_fee(self.competition, competitor)
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)
                    if amount["price"] < stripe_progress.pay_price:
                        competitor.set_is_over_payment_price(
                            stripe_progress.pay_price - amount["price"]
                        )
                        self.refund_competitor_list.append(competitor)
                    elif competitor.status == CompetitorStatus.CANCEL.value:
                        self.refund_competitor_list.append(competitor)

    def get_context(self):
        context = super().get_context()
        sorted_refund_competitor_list = self.sort_pay_at(self.refund_competitor_list)
        context["over_payment_competitiors"] = [
            x for x in sorted_refund_competitor_list if x.is_over_payment_price > 0
        ]
        context["non_registration_competitiors"] = [
            x for x in sorted_refund_competitor_list if x.is_over_payment_price == 0
        ]
        context["now"] = datetime.datetime.now(tz=datetime.timezone.utc)
        return context

    def sort_pay_at(self, competitors):
        return sorted(competitors, key=lambda x: x.stripe_progress.pay_at)
