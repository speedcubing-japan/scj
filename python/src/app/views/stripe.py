import json
import pyjq
import requests
import pprint
import stripe
import app.consts
import datetime
from app.views.competition import calc_fee, send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import reverse
from django.http import JsonResponse
from app.models import Competition, Competitor, Person, StripeProgress

class StripeAuthorization(TemplateView):
    def get(self, request):

        if not request.user.is_authenticated or not request.user.person.is_judge:
            return redirect('index')

        code = self.request.GET.get('code')
        if code == None:
            return redirect('index')

        params = {
            'grant_type': 'authorization_code',
            'client_secret': settings.STRIPE_SECRET_KEY,
            'code': code,
        }

        response = requests.post(settings.STRIPE_OAUTH_TOKEN_URL, params)
        if response.status_code == requests.codes.ok:
            stripe_user_id = response.json()['stripe_user_id']

            person = request.user.person
            person.stripe_user_id = stripe_user_id
            person.save(update_fields=[
                'stripe_user_id',
                'updated_at'
            ])

            request.session['notification'] = 'is_just_stripe_authorization_complete'   

        return redirect('profile')

class StripeCreate(View):
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not request.user.is_authenticated:
            return redirect('login')

        datas = json.loads(request.body)

        competition = Competition.objects.get(pk=datas['competition_id'])
        if not competition or competition.is_close():
            return redirect('index')

        competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=request.user.person.id
            ).first()

        amount = calc_fee(self, competition, competitor)

        name = ''
        description = ''
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'

        if competition.type == app.consts.COMPETITION_TYPE_SCJ:
            name = request.user.person.get_full_name()
            image_path = protocol + '://' + domain + static('app/image/scj_logo_s.png')
            spcific_id = request.user.person.id
            description = 'SCJ_ID: {} 氏名: {}' \
                    .format(request.user.person.id, \
                    request.user.person.get_full_name())

        elif competition.type == app.consts.COMPETITION_TYPE_WCA:
            name = request.user.person.wca_name
            image_path = protocol + '://' + domain + static('app/image/wca.svg')
            spcific_id = request.user.person.wca_id
            description = 'WCA_ID: {} 氏名: {}' \
                .format(request.user.person.wca_id, \
                request.user.person.get_full_name())

        stripe_user_id = ''
        if competition.stripe_user_person_id != 0:
            person = Person.objects.get(pk=competition.stripe_user_person_id)
            stripe_user_id = person.stripe_user_id
        
        customer = stripe.Customer.create(
            name=request.user.person.get_full_name(),
            email=request.user.email,
            metadata={
                'competition_id': competition.id,
                'competitor_id': competitor.id
            },
            stripe_account=stripe_user_id
        )

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'jpy',
                            'unit_amount': amount['price'],
                            'product_data': {
                                'name': competition.name + ' 大会参加費',
                                'images': [image_path]
                            }
                        },
                        'description': description,
                        'quantity': 1
                    }
                ],
                payment_intent_data={
                    'application_fee_amount': amount['price'],
                },
                metadata={
                    'competition_id': competition.id,
                    'competition_name': competition.name,
                    'spcific_id': spcific_id,
                    'name': name
                },
                customer=customer,
                client_reference_id=competitor.id,
                mode='payment',
                stripe_account=stripe_user_id,
                success_url=request.build_absolute_uri(reverse('competition_fee', args=[competition.name_id])) + '?status=success',
                cancel_url=request.build_absolute_uri(reverse('competition_fee', args=[competition.name_id])) + '?status=cancel'
            )
            return JsonResponse({ 'id': session.id })

        except Exception as e:
            return JsonResponse({ 'error':str(e) })

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhook(View):
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

            send_mail(self,
                request,
                competitor.person.user,
                competition,
                'mail/competition/registration_payment_subject.txt',
                'mail/competition/registration_payment_message.txt',
                price=checkout_session.amount_total)

        # Handle the event
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
                    'pay_ar',
                    'updated_at'
                ])

        return HttpResponse(status=200)
