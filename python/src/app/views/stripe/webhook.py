import stripe
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from app.models import Competition, Competitor, StripeProgress
from app.views.competition.util import send_mail

@method_decorator(csrf_exempt, name='dispatch')
class Webhook(View):
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_webhook_endpoint_secret = settings.STRIPE_WEBHOOK_ENDPOINT_SECRET_KEY

        payload = request.body.decode('utf-8')
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe_webhook_endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # それぞれのeventが別のリクエスト来る(順番は保証されない)ので、それぞれから確保できるデータを用いてレコードを組み立てる。
        if event.type == 'checkout.session.completed':
            checkout_session = event.data.object

            competition_id = int(checkout_session.metadata.competition_id)
            competitor_id = int(checkout_session.client_reference_id)

            query_set = StripeProgress.objects.filter(customer_id=checkout_session.customer)
            if query_set.first() is None:
                stripe_progress = StripeProgress()
                stripe_progress.customer_id = checkout_session.customer
                stripe_progress.competition_id = competition_id
                stripe_progress.competitor_id = competitor_id
                stripe_progress.save()
            else:
                stripe_progress = query_set.first()
                stripe_progress.competition_id = competition_id
                stripe_progress.competitor_id = competitor_id
                stripe_progress.save(update_fields=[
                    'competition_id',
                    'competitor_id',
                    'updated_at'
                ])

            competitor = Competitor.objects.get(pk=competitor_id)
            competition = Competition.objects.get(pk=competition_id)

            send_mail(request,
                competitor.person.user,
                competition,
                'app/mail/competition/registration_payment_subject.txt',
                'app/mail/competition/registration_payment_message.txt',
                price=checkout_session.amount_total)

        if event.type == 'charge.succeeded':
            charge = event.data.object

            pay_at = datetime.datetime.fromtimestamp(charge.created, tz=datetime.timezone.utc)
            query_set = StripeProgress.objects.filter(customer_id=charge.customer)
            if query_set.first() is None:
                stripe_progress = StripeProgress()
                stripe_progress.customer_id = charge.customer
                stripe_progress.charge_id = charge.id
                stripe_progress.pay_price = charge.amount
                stripe_progress.pay_at = pay_at
                stripe_progress.save()
            else:
                stripe_progress = query_set.first()
                stripe_progress.charge_id = charge.id
                stripe_progress.pay_price = charge.amount
                stripe_progress.pay_at = pay_at
                stripe_progress.save(update_fields=[
                    'charge_id',
                    'pay_price',
                    'pay_at',
                    'updated_at'
                ])

        return HttpResponse(status=200)