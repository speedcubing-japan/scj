import json
import stripe
import requests
from django.conf import settings
from django.views.generic import View
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.staticfiles.templatetags.staticfiles import static
from app.defines.competition import Type as CompetitionType
from app.models import Competition, Competitor, Person
from app.views.competition.util import calc_fee

class Create(View):
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not request.user.is_authenticated:
            return JsonResponse({'error': 'ログインしてください。'})

        datas = json.loads(request.body)

        competition = Competition.objects.get(pk=datas['competition_id'])
        if not competition or competition.is_close():
            return JsonResponse({'error': '大会が終了しています。'})

        if not competition.is_payment and not is_superuser(self, request, competition):
            return JsonResponse({'error': '現在支払えません。'})

        competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=request.user.person.id
            ).first()

        amount = calc_fee(competition, competitor)

        name = ''
        description = ''
        current_site = get_current_site(request)
        domain = current_site.domain
        protocol = 'https' if request.is_secure() else 'http'

        if competition.type == CompetitionType.SCJ.value:
            name = request.user.person.get_full_name()
            image_path = protocol + '://' + domain + static('app/image/scj_logo_s.png')
            spcific_id = request.user.person.id
            description = 'SCJ_ID: {} 氏名: {}' \
                    .format(request.user.person.id, \
                    request.user.person.get_full_name())

        elif competition.type == CompetitionType.WCA.value:
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
            return JsonResponse({'id': session.id})

        except Exception as e:
            return JsonResponse({'error': str(e)})