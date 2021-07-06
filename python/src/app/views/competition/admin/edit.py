from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competition, Competitor
from app.defines.event import Event
from app.defines.session import Notification


class Edit(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        if 'competitor_id' not in kwargs:
            return redirect('competition_index')
        competitor_id = kwargs.get('competitor_id')

        context = self.create_context(request, name_id, competitor_id)
        if not context:
            return redirect('competition_detail', name_id=name_id)

        return render(request, 'app/competition/admin/edit.html', context)

    def post(self, request, **kwargs):
        name_id = request.POST.get(key='name_id')
        competitor_id = request.POST.get(key='competitor_id')
        if not name_id or not competitor_id:
            return redirect('competition_index')

        context = self.create_context(request, name_id, competitor_id)
        if not context:
            return redirect('competition_detail', name_id=name_id)

        return render(request, 'app/competition/admin/edit.html', context)

    def create_context(self, request, name_id, competitor_id):
        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return None
        competition = competition.first()

        if not competition.is_superuser(request.user):
            return None

        competitor = Competitor.objects.get(pk=competitor_id)
        if not competitor:
            return None

        events = Event.get_events(competition.event_ids)

        notification = ''
        if request.method == 'POST':
            event_ids = []
            for event_id in competition.event_ids:
                if request.POST.get('event_id_' + str(event_id)):
                    event_ids.append(event_id)

            guest_count = 0
            if request.POST.get('guest_count'):
                guest_count = int(request.POST.get('guest_count'))

            if event_ids:
                competitor.event_ids = event_ids
                competitor.guest_count = guest_count
                competitor.save(update_fields=[
                    'event_ids',
                    'guest_count',
                    'updated_at'
                ])
                notification = Notification.UPDATE
            else:
                notification = Notification.COMPETITOR_EVENT_NOT_SELECTED

        context = {
            'events': events,
            'competition': competition,
            'competitor': competitor,
            'guest_counts': range(competition.guest_limit + 1),
            'notification': notification,
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }
        return context