import json
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from app.models import Competition, Person, FeePerEvent, FeePerEventCount
from app.defines.competition import Type as CompetitionType
from app.defines.prefecture import Prefecture
from app.defines.fee import PayType as FeePayType
from app.defines.fee import CalcType as FeeCalcType
from app.defines.fee import CalcTypeEn as FeeCalcTypeEn
from app.defines.event import Event, Format
from app.defines.competition import RoundType, RoundLimitType


def send_mail(request, user, competition, subject_path, message_path, **kwargs):
    current_site = get_current_site(request)
    domain = current_site.domain
    context = {
        'protocol': 'https' if request.is_secure() else 'http',
        'domain': domain,
        'user': user,
        'competition': competition
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


def check_date(date, format):
    try:
        return True
    except ValueError:
        return False


def check_competition(data, type):
    errors = []

    if not data['name']:
        errors.append('nemaは必須です。')
    if not data['name_id']:
        errors.append('nema_idは必須です。')
    if not CompetitionType.has(int(data['type'])):
        errors.append('typeに規定外の値が設定されています。')
    if len(data['name']) > 64:
        errors.append('nameが64文字を超えて設定されています。')
    if type == 'create' and Competition.objects.filter(name=data['name']).exists():
        errors.append('nameがすでに存在しています。')
    if len(data['name_id']) > 64:
        errors.append('name_idが64文字を超えて設定されています。')
    if type == 'create' and Competition.objects.filter(name_id=data['name_id']).exists():
        errors.append('name_idがすでに存在しています。')
    if not check_date(str(data['open_at']), '%Y-%m-%d'):
        errors.append('open_atのformatが規定外です。YYYY-MM-DD で記述してください。')
    if not check_date(str(data['close_at']), '%Y-%m-%d'):
        errors.append('close_atのformatが規定外です。YYYY-MM-DD で記述してください。')
    if not check_date(data['registration_open_at'], '%Y-%m-%dT%H:%M:%S'):
        errors.append('registration_open_atのformatが規定外です。YYYY-MM-DD HH:MM:SS で記述してください。')
    if not check_date(data['registration_close_at'], '%Y-%m-%dT%H:%M:%S'):
        errors.append('registration_close_atのformatが規定外です。YYYY-MM-DD HH:MM:SS で記述してください。')
    if int(data['stripe_user_person_id']) > 0 and not Person.objects.filter(id=data['stripe_user_person_id']).exists():
        errors.append('stripe_user_person_idが存在しないIDです。')
    event_ids = set(json.loads(data['event_ids']))
    if not Event.has(event_ids):
        errors.append('event_idsに規定外の値が設定されています。')
    if not Prefecture.has(int(data['prefecture_id'])):
        errors.append('prefecutre_idに規定外の値が設定されています。')
    organizer_person_ids = set(json.loads(data['organizer_person_ids']))
    if len(organizer_person_ids) != Person.objects.filter(id__in=organizer_person_ids).count():
        errors.append('organizer_person_idsに規定外の値が設定されています。')
    if not FeePayType.has(int(data['fee_pay_type'])):
        errors.append('fee_pay_typeに規定外の値が設定されています。')
    if not FeeCalcType.has(int(data['fee_calc_type'])):
        errors.append('fee_calc_typeに規定外の値が設定されています。')

    return errors


def check_round(line, data, event_ids):
    errors = []

    if int(data['event_id']) != 0:
        if not Event.get_name(int(data['event_id'])):
            errors.append('event_idが規定外です。' + line + '行目 event_id: ' + data['event_id'])
        if not RoundType.get_name(int(data['type'])):
            errors.append('round_typeが規定外です。' + line + '行目 type: ' + data['type'])
        if not Format.get_name(int(data['format_id'])):
            errors.append('format_idが規定外です。' + line + '行目 format_id: ' + data['format_id'])
        if int(data['limit_type']) != 0 and not RoundLimitType.get_name(int(data['limit_type'])):
            errors.append('limit_typeが規定外です。' + line + '行目 limit_type: ' + data['limit_type'])
        if not int(data['event_id']) in event_ids:
            errors.append('event_idがcompetition.event_idsに含まれていません。' + line + '行目')
    if int(data['event_id']) == 0 and \
        (int(data['attempt_count']) != 0 or
         int(data['type']) != 0 or
         int(data['format_id']) != 0 or
         int(data['limit_type']) != 0 or
         int(data['limit_time']) != 0 or
         int(data['cutoff_attempt_count']) != 0 or
         int(data['cutoff_time']) != 0 or
         int(data['proceed_count']) != 0):
        errors.append('event_idが0のときはevent_name、room_name、begin_at, end_atが0でなければなりません。' + line + '行目')

    return errors


def check_feeperevent(line, data, event_ids):
    errors = []

    if int(data['event_id']) != 0 and not Event.get_name(int(data['event_id'])):
        errors.append('event_idが規定外です。' + line + '行目 event_id: ' + data['event_id'])

    return errors


def check_feepereventcount(line, data):
    return []
