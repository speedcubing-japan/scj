import json
from django.conf import settings
from django.core.mail import send_mass_mail as email_mass
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
        "protocol": "https" if request.is_secure() else "http",
        "domain": domain,
        "user": user,
        "competition": competition,
    }

    if "price" in kwargs:
        context["price"] = kwargs.get("price")

    subject = render_to_string(subject_path, context).strip()
    message = render_to_string(message_path, context).strip()
    user.email_user(subject, message, settings.EMAIL_HOST_USER)


def send_mass_mail(request, users, competition, subject_path, message_path, **kwargs):
    current_site = get_current_site(request)
    domain = current_site.domain

    emails = []
    for user in users:
        context = {
            "protocol": "https" if request.is_secure() else "http",
            "domain": domain,
            "user": user,
            "competition": competition,
        }

        subject = render_to_string(subject_path, context).strip()
        message = render_to_string(message_path, context).strip()

        emails.append((subject, message, settings.EMAIL_HOST_USER, [user.email]))

    email_mass(emails)


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

    return {"fees": fees, "prepaid_fees": prepaid_fees, "price": price}


def check_date(date, format):
    try:
        return True
    except ValueError:
        return False


def check_competition(data, type):
    errors = []

    if not data["name"]:
        errors.append("nema??????????????????")
    if not data["name_id"]:
        errors.append("nema_id??????????????????")
    if not CompetitionType.has(int(data["type"])):
        errors.append("type????????????????????????????????????????????????")
    if len(data["name"]) > 64:
        errors.append("name???64?????????????????????????????????????????????")
    if type == "create" and Competition.objects.filter(name=data["name"]).exists():
        errors.append("name????????????????????????????????????")
    if len(data["name_id"]) > 64:
        errors.append("name_id???64?????????????????????????????????????????????")
    if (
        type == "create"
        and Competition.objects.filter(name_id=data["name_id"]).exists()
    ):
        errors.append("name_id????????????????????????????????????")
    if not check_date(str(data["open_at"]), "%Y-%m-%d"):
        errors.append("open_at???format?????????????????????YYYY-MM-DD ??????????????????????????????")
    if not check_date(str(data["close_at"]), "%Y-%m-%d"):
        errors.append("close_at???format?????????????????????YYYY-MM-DD ??????????????????????????????")
    if not check_date(data["registration_open_at"], "%Y-%m-%dT%H:%M:%S"):
        errors.append(
            "registration_open_at???format?????????????????????YYYY-MM-DD HH:MM:SS ??????????????????????????????"
        )
    if not check_date(data["registration_close_at"], "%Y-%m-%dT%H:%M:%S"):
        errors.append(
            "registration_close_at???format?????????????????????YYYY-MM-DD HH:MM:SS ??????????????????????????????"
        )
    if (
        int(data["stripe_user_person_id"]) > 0
        and not Person.objects.filter(id=data["stripe_user_person_id"]).exists()
    ):
        errors.append("stripe_user_person_id??????????????????ID?????????")
    event_ids = set(json.loads(data["event_ids"]))
    if not Event.has(event_ids):
        errors.append("event_ids????????????????????????????????????????????????")
    if not Prefecture.has(int(data["prefecture_id"])):
        errors.append("prefecutre_id????????????????????????????????????????????????")
    organizer_person_ids = set(json.loads(data["organizer_person_ids"]))
    if (
        len(organizer_person_ids)
        != Person.objects.filter(id__in=organizer_person_ids).count()
    ):
        errors.append("organizer_person_ids????????????????????????????????????????????????")
    if not FeePayType.has(int(data["fee_pay_type"])):
        errors.append("fee_pay_type????????????????????????????????????????????????")
    if not FeeCalcType.has(int(data["fee_calc_type"])):
        errors.append("fee_calc_type????????????????????????????????????????????????")

    return errors


def check_round(line, data, event_ids):
    errors = []

    if int(data["event_id"]) != 0:
        if not Event.get_name(int(data["event_id"])):
            errors.append("event_id?????????????????????" + line + "?????? event_id: " + data["event_id"])
        if not RoundType.get_name(int(data["type"])):
            errors.append("round_type?????????????????????" + line + "?????? type: " + data["type"])
        if not Format.get_name(int(data["format_id"])):
            errors.append(
                "format_id?????????????????????" + line + "?????? format_id: " + data["format_id"]
            )
        if int(data["limit_type"]) != 0 and not RoundLimitType.get_name(
            int(data["limit_type"])
        ):
            errors.append(
                "limit_type?????????????????????" + line + "?????? limit_type: " + data["limit_type"]
            )
        if not int(data["event_id"]) in event_ids:
            errors.append("event_id???competition.event_ids??????????????????????????????" + line + "??????")
    if int(data["event_id"]) == 0 and (
        int(data["attempt_count"]) != 0
        or int(data["type"]) != 0
        or int(data["format_id"]) != 0
        or int(data["limit_type"]) != 0
        or int(data["limit_time"]) != 0
        or int(data["cutoff_attempt_count"]) != 0
        or int(data["cutoff_time"]) != 0
        or int(data["proceed_count"]) != 0
    ):
        errors.append(
            "event_id???0????????????event_name???room_name???begin_at, end_at???0?????????????????????????????????"
            + line
            + "??????"
        )

    return errors


def check_feeperevent(line, data, event_ids):
    errors = []

    if int(data["event_id"]) != 0 and not Event.get_name(int(data["event_id"])):
        errors.append("event_id?????????????????????" + line + "?????? event_id: " + data["event_id"])

    return errors


def check_feepereventcount(line, data):
    return []
