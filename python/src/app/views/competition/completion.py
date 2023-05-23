from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .base import Base
from app.models import StripeProgress
from app.views.competition.util import calc_fee


class Completion(LoginRequiredMixin, Base):
    template_name = "app/competition/completion.html"

    def get(self, request, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()
        stripe_progresses = StripeProgress.objects.filter(
            competition_id=self.competition.id
        )
        amount = calc_fee(self.competition, self.competitor)
        for stripe_progress in stripe_progresses:
            if self.competitor.id == stripe_progress.competitor_id:
                self.competitor.set_stripe_progress(stripe_progress)
                if amount["price"] != stripe_progress.pay_price:
                    self.competitor.set_is_diffrence_event_and_price()
        return context
