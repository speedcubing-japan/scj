from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competition, Competitor
from app.defines.competitor import Status as CompetitorStatus
from app.views.competition.util import send_mail
from app.defines.session import Notification
from .base import Base


class Cancel(LoginRequiredMixin, Base):
    def post(self, request, **kwargs):

        if self.competition.is_private and not self.competition.is_superuser(request.user):
            return redirect('competition_index')

        if not self.competition.is_registration_open() and not self.competition.is_superuser(request.user):
            return redirect('competition_detail', name_id=self.name_id)

        if not self.competitor:
            return redirect('competition_registration', name_id=self.name_id)

        # CancelができるのはPending時。
        if self.competitor.status != CompetitorStatus.PENDING.value:
            return redirect('competition_registration', name_id=name_id)

        self.competitor.update_status(CompetitorStatus.CANCEL.value)
        self.send_mail('registration_cancel')
        self.save_notification(Notification.COMPETITOR_CANCEL)
        self.set_pending_competitor_count()

        return redirect('competition_registration', name_id=self.name_id)