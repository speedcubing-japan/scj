import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition, Person, Competitor, Result, StripeProgress
from app.defines.event import Event
from app.defines.competition import Type as CompetitionType
from app.defines.session import Notification
from .base import Base
from .util import calc_fee


class Fee(Base):

    template_name = 'app/competition/fee.html'
    status = ''

    def get(self, request, **kwargs):
        if 'status' in request.GET:
            self.status = request.GET.get('status')

        if self.competition.is_private and not self.competition.is_superuser(request.user):
            return redirect('competition_index')

        if self.status == 'cancel':
            self.notification = Notification.PAYMENT_CANCEL
        elif self.status == 'success':
            self.notification = Notification.PAYMENT_SUCCESS

        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        stripe_user_id = ''
        if self.competition.stripe_user_person_id != 0:
            person = Person.objects.get(pk=self.competition.stripe_user_person_id)
            stripe_user_id = person.stripe_user_id

        amount = calc_fee(self.competition, self.competitor)

        paid = False
        if self.competitor:
            paid = StripeProgress.objects.filter(competitor_id=self.competitor.id).exists()
        if self.status == 'success':
            # 一旦支払い済みにする(同期が遅いときある)
            paid = True

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        fee_pay_close_at_timedelta = abs(self.competition.fee_pay_close_at - now)

        context['fee_pay_close_at_timedelta'] = fee_pay_close_at_timedelta
        context['fees'] = amount['fees']
        context['prepaid_fees'] = amount['prepaid_fees']
        context['price'] = amount['price']
        context['paid'] = paid
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['stripe_user_id'] = stripe_user_id
        context['notification'] = self.notification
        context['now'] = now
        context['is_payment'] = self.competition.is_payment or self.competition.is_superuser(request.user)

        return context