import datetime
from django import forms
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from app.models import Competitor, StripeProgress, Person
from app.forms import CompetitionRegistrationForm
from app.defines.event import Event
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus
from app.defines.session import Notification
from app.defines.fee import PayTypeEn as FeePayType
from .base import Base
from .util import calc_fee


class Registration(Base):

    template_name = "app/competition/registration.html"
    form = None

    def get(self, request, **kwargs):
        self.form = CompetitionRegistrationForm()
        self.create_form()

        status = ""
        if "status" in request.GET:
            status = request.GET.get("status")

        # 事前決済オンリーのときのnotification設定
        if status == "cancel":
            self.notification = Notification.REGISTRATION_PAY_CANCEL
        elif status == "success":
            self.notification = Notification.REGISTRATION_PAY_SUCCESS

        return render(request, self.template_name, self.get_context(status))

    def post(self, request, **kwargs):
        self.form = CompetitionRegistrationForm(request.POST)
        self.create_form()

        if (
            not self.competition.is_registration_open()
            and not self.competition.is_superuser(request.user)
        ):
            return redirect("competition_detail", name_id=self.name_id)

        if not request.user.is_authenticated:
            return redirect("competition_detail", name_id=self.name_id)

        if self.competition.is_registration_at_other:
            return redirect("competition_detail", name_id=self.name_id)

        if (
            self.competition.type == CompetitionType.WCA.value
            and not self.is_wca_authenticated()
        ):
            return redirect("competition_detail", name_id=self.name_id)

        if not self.form.is_valid():
            return render(request, self.template_name, self.get_context())

        elif self.form.is_valid():
            event_ids = [int(x) for x in self.form.cleaned_data["event_ids"]]
            guest_count = self.form.cleaned_data["guest_count"]
            comment = self.form.cleaned_data["comment"]

            if not request.user.is_authenticated:
                return redirect("competiion_index")

            if self.competitor:
                before_status = self.competitor.status

                # REGISTRATIONはもう申し込み/変更等はできない。
                if self.competitor.status == CompetitorStatus.REGISTRATION.value:
                    return redirect("competition_detail", name_id=self.name_id)

                self.competitor.update(
                    CompetitorStatus.PENDING.value,
                    event_ids,
                    guest_count,
                    comment,
                    before_status == CompetitorStatus.CANCEL.value,
                    datetime.datetime.now(tz=datetime.timezone.utc),
                )

                if before_status == CompetitorStatus.PENDING.value:
                    self.notification = Notification.COMPETITION_REGISTER_EDIT
                elif before_status == CompetitorStatus.CANCEL.value:
                    self.notification = Notification.COMPETITION_REGISTER
                    self.send_mail("registration_submit")
                    self.set_pending_competitor_count()
            else:
                self.competitor = Competitor()
                self.competitor.create(
                    self.competition.id,
                    CompetitorStatus.PENDING.value,
                    event_ids,
                    guest_count,
                    comment,
                    request.user.person,
                )
                self.notification = Notification.COMPETITION_REGISTER
                self.send_mail("registration_submit")
                self.set_pending_competitor_count()
                self.delete_is_wca_authenticated()

        return render(request, self.template_name, self.get_context())

    def get_context(self, status=""):
        context = super().get_context()

        registration_competitor_count = Competitor.get_count_by_status(
            self, self.competition.id, CompetitorStatus.REGISTRATION.value
        )
        is_limit = registration_competitor_count >= self.competition.limit

        is_prepaid = False
        if self.request.user.is_authenticated:
            competitor = Competitor.objects.filter(
                competition_id=self.competition.id,
                person_id=self.request.user.person.id,
            )
            if competitor.exists():
                competitor = competitor.first()
                is_prepaid = StripeProgress.objects.filter(
                    competitor_id=competitor.id, refund_price=0
                ).exists()

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if not self.competition.is_registration_at_other:
            registration_open_at = self.competition.registration_open_at
            registration_close_at = self.competition.registration_close_at
            registration_open_timedelta = registration_open_at - now
            registration_close_timedelta = now - registration_close_at

        stripe_user_id = ""
        if self.competition.stripe_user_person_id != 0:
            person = Person.objects.get(pk=self.competition.stripe_user_person_id)
            stripe_user_id = person.stripe_user_id

        protocol = "https" if self.request.is_secure() else "http"
        current_site = get_current_site(self.request)
        domain = current_site.domain
        redirect_uri = (
            protocol + "://" + domain + "/wca/authorization/?type=competition"
        )
        # WCA認証で2つ以上のパラメータを渡せないため、セッションで管理。
        self.request.session["wca_authorization_name_id"] = self.name_id

        amount = calc_fee(self.competition, None)

        # 自分が他のシリーズ大会に申し込んでいるかどうか
        # シリーズ大会
        is_registration_another_series_competition = False
        if self.request.user.is_authenticated:
            if self.competition.series_competition_ids:
                # 自大会は除く
                self.competition.series_competition_ids.remove(self.competition.id)
                if (
                    Competitor.objects.filter(
                        competition_id__in=self.competition.series_competition_ids,
                        person__id=self.user.person.id,
                    )
                    .exclude(status=CompetitorStatus.CANCEL.value)
                    .count()
                    > 0
                ):
                    is_registration_another_series_competition = True

        context["form"] = self.form
        context["is_limit"] = is_limit
        context["is_prepaid"] = is_prepaid
        context["now"] = now
        if not self.competition.is_registration_at_other:
            context["registration_open_timedelta"] = registration_open_timedelta
            context["registration_close_after_timedelta"] = registration_close_timedelta
            context["registration_close_before_timedelta"] = abs(
                registration_close_timedelta
            )
        context["is_registration_open"] = self.competition.is_registration_open()
        context["wca_oauth_authorization"] = settings.WCA_OAUTH_AUTHORIZATION
        context["wca_client_id"] = settings.WCA_CLIENT_ID
        context["redirect_uri"] = redirect_uri
        context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY
        context["stripe_user_id"] = stripe_user_id
        context["prepaid_fees"] = amount["prepaid_fees"]
        context["is_load_stripe_lib"] = (
            self.competition.fee_pay_type == FeePayType.REMOTE_ONLY.value
        )
        context[
            "is_registration_another_series_competition"
        ] = is_registration_another_series_competition
        if status == "success":
            context["is_paid"] = True

        return context

    def create_form(self):
        guests = []
        if self.competition.guest_limit:
            for guest_count in range(self.competition.guest_limit + 1):
                guests.append((int(guest_count), str(guest_count) + "人"))
                self.form.fields["guest_count"].choices = guests
        else:
            self.form.fields["guest_count"].initial = 0
            self.form.fields["guest_count"].widget = forms.HiddenInput()

        events = []
        for event_id in self.competition.event_ids:
            if event_id in dict(Event.choices()):
                events.append((str(event_id), Event.get_name(event_id)))
        self.form.fields["event_ids"].choices = events

        if self.competitor is not None:
            self.form.fields["event_ids"].initial = self.competitor.event_ids
            self.form.fields["guest_count"].initial = self.competitor.guest_count
            self.form.fields["comment"].initial = self.competitor.comment

            if self.competitor.status == CompetitorStatus.REGISTRATION.value:
                self.form.fields["event_ids"].widget.attrs["disabled"] = "disabled"
                self.form.fields["guest_count"].widget.attrs["disabled"] = "disabled"
                self.form.fields["comment"].widget.attrs["disabled"] = "disabled"
