import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition, Person, Competitor, Result, StripeProgress
from app.defines.event import Event
from app.defines.competition import Type as CompetitionType
from app.defines.session import Notification
from .util import calc_fee


class Fee(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        status = ''
        if 'status' in request.GET:
            status = request.GET.get('status')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_detail', name_id=name_id)
        competition = competition.first()

        stripe_user_id = ''
        if competition.stripe_user_person_id != 0:
            person = Person.objects.get(pk=competition.stripe_user_person_id)
            stripe_user_id = person.stripe_user_id

        has_results = Result.objects.filter(competition_id=competition.id).exists()
        if has_results:
            return redirect('competition_detail', name_id=name_id)

        competitor = None
        if request.user.is_authenticated:
            competitor = Competitor.objects.filter(competition_id=competition.id, person_id=request.user.person.id)
            if request.method == 'POST' and not competitor.exists():
                return redirect('competition_index')
            if competitor.exists():
                competitor = competitor.first()

        amount = calc_fee(competition, competitor)

        paid = False
        if competitor:
            paid = StripeProgress.objects.filter(competitor_id=competitor.id).exists()
        if status == 'success':
            # 一旦支払い済みにする(同期が遅いときある)
            paid = True

        notification = ''
        if status == 'cancel':
            notification = Notification.PAYMENT_CANCEL
        elif status == 'success':
            notification = Notification.PAYMENT_SUCCESS

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        fee_pay_close_at_timedelta = abs(competition.fee_pay_close_at - now)

        context = {
            'competition': competition,
            'competitor': competitor,
            'fee_pay_close_at_timedelta': fee_pay_close_at_timedelta,
            'fees': amount['fees'],
            'prepaid_fees': amount['prepaid_fees'],
            'price': amount['price'],
            'paid': paid,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'stripe_user_id': stripe_user_id,
            'notification': notification,
            'now': now,
            'is_payment': competition.is_payment or competition.is_superuser(request.user),
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }

        return render(request, 'app/competition/fee.html', context)