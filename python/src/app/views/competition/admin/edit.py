from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competition, Competitor, StripeProgress
from app.defines.event import Event
from app.views.competition.base import Base
from app.defines.session import Notification


class Edit(LoginRequiredMixin, Base):

    template_name = 'app/competition/admin/edit.html'
    target_competitor = None

    def get(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect('competition_detail', name_id=self.name_id)

        if not 'competitor_id' in kwargs:
            return redirect('competition_detail', name_id=self.name_id)

        competitor_id = kwargs.get('competitor_id')
        self.target_competitor = Competitor.objects.get(pk=competitor_id)

        return render(request, self.template_name, self.get_context())

    def post(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect('competition_detail', name_id=self.name_id)

        if not 'competitor_id' in request.POST:
            return redirect('competition_detail', name_id=self.name_id)

        competitor_id = request.POST.get(key='competitor_id')
        self.target_competitor = Competitor.objects.get(pk=competitor_id)
        if not self.target_competitor:
            return redirect('competition_detail', name_id=self.name_id)

        event_ids = []
        for event_id in self.competition.event_ids:
            if request.POST.get('event_id_' + str(event_id)):
                event_ids.append(event_id)

        guest_count = 0
        if request.POST.get('guest_count'):
            guest_count = int(request.POST.get('guest_count'))

        if event_ids:
            self.target_competitor.update_event_ids_and_guest_count(event_ids, guest_count)
            self.notification = Notification.UPDATE
        else:
            self.notification = Notification.COMPETITOR_EVENT_NOT_SELECTED

        return render(request, self.template_name, self.get_context())

    def get_context(self):

        is_prepaid = False
        if self.competitor:
            is_prepaid = StripeProgress.objects.filter(competitor_id=self.competitor.id).exists()

        context = super().get_context()
        context['events'] = Event.get_events(self.competition.event_ids)
        context['competitor'] = self.target_competitor
        context['guest_counts'] = range(self.competition.guest_limit + 1)
        context['is_prepaid'] = is_prepaid
        context['notification'] = self.notification

        return context