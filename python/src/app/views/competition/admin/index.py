import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competitor, StripeProgress
from app.defines.competitor import Status as CompetitorStatus
from app.defines.competition import Type as CompetitionType
from app.views.competition.base import Base
from app.defines.session import Notification
from app.views.competition.util import calc_fee


class Index(LoginRequiredMixin, Base):

    competitors = None

    def get(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_index")

        self.competitors = Competitor.objects.filter(
            competition_id=self.competition.id
        ).order_by("created_at")

        return render(request, self.get_template_name(), self.get_context())

    def post(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_index")

        if "type" not in request.POST:
            return redirect("competition_index")

        type = request.POST.get("type")

        self.competitors = Competitor.objects.filter(
            competition_id=self.competition.id
        ).order_by("created_at")

        registration_count = 0
        for competitor in self.competitors:
            if competitor.status == CompetitorStatus.REGISTRATION.value:
                registration_count += 1

        for competitor in self.competitors:
            if request.POST.get("competitor_id_" + str(competitor.id)):
                if (
                    type == "admit"
                    and competitor.status != CompetitorStatus.REGISTRATION.value
                ):
                    registration_count += 1

                if (
                    type == "cancel"
                    and competitor.status != CompetitorStatus.CANCEL.value
                ):
                    registration_count -= 1

        if registration_count > self.competition.limit:
            self.notification = Notification.COMPETITION_LIMIT
            return render(request, self.get_template_name(), self.get_context())

        is_updated = False
        users = []
        mail_type = ""
        for competitor in self.competitors:
            if request.POST.get("competitor_id_" + str(competitor.id)):
                if (
                    type == "admit"
                    and competitor.status != CompetitorStatus.REGISTRATION.value
                ):
                    competitor.update_status(CompetitorStatus.REGISTRATION.value)
                    users.append(competitor.person.user)
                    mail_type = "registration_admit"
                    is_updated = True

                if (
                    type == "cancel"
                    and competitor.status != CompetitorStatus.CANCEL.value
                ):
                    competitor.update_status(CompetitorStatus.CANCEL.value)
                    users.append(competitor.person.user)
                    mail_type = "registration_cancel"
                    is_updated = True

        if mail_type and users:
            self.send_mass_mail_user(users, mail_type)

        if is_updated:
            self.notification = Notification.UPDATE
            self.set_pending_competitor_count()
        else:
            self.notification = Notification.NOT_UPDATE

        return render(request, self.get_template_name(), self.get_context())

    def get_context(self):
        context = super().get_context()

        # 重複確認
        twin_competition_competitor_person_ids = []
        if self.competition.twin_competition_id != 0:
            twin_competition_competitors = Competitor.objects.filter(
                competition_id=self.competition.twin_competition_id
            )
            for twin_competition_competitor in twin_competition_competitors:
                if twin_competition_competitor.status != CompetitorStatus.CANCEL.value:
                    twin_competition_competitor_person_ids.append(
                        twin_competition_competitor.person_id
                    )

        pending_competitors = []
        registration_competitors = []
        cancel_competitors = []

        stripe_progresses = StripeProgress.objects.filter(
            competition_id=self.competition.id
        )
        for competitor in self.competitors:

            amount = calc_fee(self.competition, competitor)
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)
                    if amount["price"] != stripe_progress.pay_price:
                        competitor.set_is_diffrence_event_and_price()

            if competitor.person.id in twin_competition_competitor_person_ids:
                competitor.set_is_duplicated_twin_competitions()

            if competitor.status == CompetitorStatus.PENDING.value:
                pending_competitors.append(competitor)
            if competitor.status == CompetitorStatus.REGISTRATION.value:
                registration_competitors.append(competitor)
            if competitor.status == CompetitorStatus.CANCEL.value:
                cancel_competitors.append(competitor)

        context["pending_competitors"] = pending_competitors
        context["registration_competitors"] = registration_competitors
        context["cancel_competitors"] = cancel_competitors
        context["now"] = datetime.datetime.now(tz=datetime.timezone.utc)
        context["is_registration_open"] = self.competition.is_registration_open()

        return context

    def get_template_name(self):
        competition_type = ""
        if self.competition.type == CompetitionType.SCJ.value:
            competition_type = CompetitionType.SCJ.name.lower()
        elif self.competition.type == CompetitionType.WCA.value:
            competition_type = CompetitionType.WCA.name.lower()

        return "app/competition/admin/index_{}.html".format(competition_type)
