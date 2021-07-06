import stripe
import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competition, Person, Competitor, Result, StripeProgress
from app.defines.competitor import Status as CompetitorStatus
from app.views.competition.util import send_mail, calc_fee
from app.defines.session import Notification


class Refund(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not competition.is_refunder(request.user):
            return redirect('competition_index')

        competitor_ids = []
        stripe_progresses = StripeProgress.objects.filter(competition_id=competition.id, refund_price=0)
        competitors = Competitor.objects.filter(competition_id=competition.id)

        competitor_list = []
        for competitor in competitors:
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)
                    competitor_list.append(competitor)

        has_results = Result.objects.filter(competition_id=competition.id).exists()

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'competition': competition,
            'has_results': has_results,
            'competitors': competitor_list,
            'notification': notification,
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }
        return render(request, 'app/competition/admin/refund.html', context)

    def post(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not competition.is_refunder(request.user):
            return redirect('competition_index')

        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_user_person = None
        if competition.stripe_user_person_id > 0:
            stripe_user_person = Person.objects.get(pk=competition.stripe_user_person_id)

        competitor_ids = []
        stripe_progresses = StripeProgress.objects.filter(competition_id=competition.id, refund_price=0)
        competitors = Competitor.objects.filter(competition_id=competition.id)

        competitor_list = []
        for competitor in competitors:

            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)

            if request.POST.get('competitor_id_' + str(competitor.id)):
                stripe_progress = competitor.stripe_progress

                fee = calc_fee(competition, competitor)
                amount = int(fee['price'])
                if request.POST.get('competitor_refund_' + str(competitor.id)):
                    part_amount = int(request.POST.get('competitor_refund_' + str(competitor.id)))
                    if amount < part_amount:
                        request.session['notification'] = Notification.REFUND_AMOUNT_OVER
                        return redirect('competition_admin_refund', name_id=name_id)
                    amount = part_amount

                if stripe_user_person:
                    stripe.Refund.create(
                        amount=amount,
                        charge=stripe_progress.charge_id,
                        stripe_account=stripe_user_person.stripe_user_id
                    )
                else:
                    stripe.Refund.create(
                        amount=amount,
                        charge=stripe_progress.charge_id
                    )

                # 全額返金時(種目追加時)のみcompetitor_idを0にして再度支払えるようにする
                if fee['price'] == amount:
                    stripe_progress.competitor_id = 0
                else:
                    stripe_progress.pay_price -= amount

                stripe_progress.refund_price = amount
                stripe_progress.refund_at = datetime.datetime.now(tz=datetime.timezone.utc)
                stripe_progress.save(update_fields=[
                    'competitor_id',
                    'pay_price',
                    'refund_price',
                    'refund_at',
                    'updated_at'
                ])
                competitor.unset_stripe_progress()

                send_mail(request,
                    competitor.person.user,
                    competition,
                    'app/mail/competition/registration_refund_subject.txt',
                    'app/mail/competition/registration_refund_message.txt',
                    price=amount)

            if competitor.stripe_progress:
                competitor_list.append(competitor)

        has_results = Result.objects.filter(competition_id=competition.id).exists()

        context = {
            'competition': competition,
            'has_results': has_results,
            'competitors': competitor_list,
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }
        return render(request, 'app/competition/admin/refund.html', context)