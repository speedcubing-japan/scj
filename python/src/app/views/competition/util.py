from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from app.defines.fee import CalcTypeEn as FeeCalcTypeEn
from app.models import FeePerEvent, FeePerEventCount


def send_mail(request, user, competition, subject_path, message_path, **kwargs):
    current_site = get_current_site(request)
    domain = current_site.domain
    context = {
        'protocol': 'https' if request.is_secure() else 'http',
        'domain': domain,
        'user': user,
        'competition':  competition
    }

    if 'price' in kwargs:
        context['price'] = kwargs.get('price')

    subject = render_to_string(subject_path, context).strip()
    message = render_to_string(message_path, context).strip()
    user.email_user(subject, message, settings.EMAIL_HOST_USER)

def calc_fee(competition, competitor):

    fees = {}
    prepaid_fees = {}
    price = 0

    if competition.fee_calc_type == FeeCalcTypeEn.EVENT.value:
        results = FeePerEvent.objects.filter(competition_id=competition.id)
        for result in results:
            fees[result.event_id] = result.price
            prepaid_fees[result.event_id] = result.prepaid_price

        if competitor:
            for result in results:
                if result.event_id == 0:
                    price += result.prepaid_price
                if result.event_id in competitor.event_ids:
                    price += result.prepaid_price

    elif competition.fee_calc_type == FeeCalcTypeEn.EVENT_COUNT.value:
        results = FeePerEventCount.objects.filter(competition_id=competition.id)
        for result in results:
            fees[result.event_count] = result.price
            prepaid_fees[result.event_count] = result.prepaid_price

        if competitor:
            event_count = len(competitor.event_ids)
            for result in results:
                if result.event_count == 0:
                    price += result.prepaid_price
                if result.event_count == event_count:
                    price += result.prepaid_price

    return {'fees': fees, 'prepaid_fees': prepaid_fees, 'price': price}