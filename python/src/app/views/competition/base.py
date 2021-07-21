from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.views.competition.util import send_mail
from app.models import Competition, Competitor, Result
from app.defines.competitor import Status as CompetitorStatus


class Base(TemplateView):

    request = None
    user = None
    name_id = ''
    competition = None
    competitor = None
    has_results = False
    notification = None
    pending_competitor_count = 0

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.user = request.user

        self.set_name_id(request, kwargs)
        if not self.name_id:
            return redirect('competition_index')

        self.set_competition()
        if not self.competition:
            return redirect('competition_index')

        self.set_competitor()
        self.set_has_results()
        self.set_pending_competitor_count()
        self.set_notification()

        return super().dispatch(request, *args, **kwargs)

    def get_context(self):
        context = {}
        context['name_id'] = self.name_id
        context['competition'] = self.competition
        context['competitor'] = self.competitor
        context['has_results'] = self.has_results
        context['pending_competitor_count'] = self.pending_competitor_count
        context['is_superuser'] = self.competition.is_superuser(self.user)
        context['is_refunder'] = self.competition.is_refunder(self.user)
        context['is_wca_authenticated'] = self.is_wca_authenticated()
        return context

    def set_name_id(self, request, kwargs):
        if request.method == 'GET':
            if 'name_id' in kwargs:
                self.name_id = kwargs.get('name_id')
        if request.method == 'POST':
            if 'name_id' in kwargs:
                self.name_id = kwargs.get('name_id')

    def set_competition(self):
        competition = Competition.objects.filter(name_id=self.name_id)
        if competition.exists():
            self.competition = competition.first()

    def set_competitor(self):
        if self.user.is_authenticated:
            self.competitor = Competitor.get_competitor(self, self.competition.id, self.user.person.id)

    def set_has_results(self):
        self.has_results = Result.objects.filter(competition_id=self.competition.id).exists()

    def set_pending_competitor_count(self):
        self.pending_competitor_count = Competitor.get_count_by_status(self, self.competition.id, CompetitorStatus.PENDING.value)

    def set_notification(self):
        self.notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

    def save_notification(self, notification):
        self.request.session['notification'] = notification

    def send_mail(self, type):
        send_mail(self.request,
            self.user,
            self.competition,
            'app/mail/competition/{}_subject.txt'.format(type),
            'app/mail/competition/{}_message.txt'.format(type)
        )

    def send_mail_refund(self, type, price):
        send_mail(self.request,
            self.user,
            self.competition,
            'app/mail/competition/{}_subject.txt'.format(type),
            'app/mail/competition/{}_message.txt'.format(type),
            price=price
        )

    def is_wca_authenticated(self):
        if self.competitor:
            return True
        if self.request.session.get('is_wca_authenticated') is not None:
            return True
        return False

    def delete_is_wca_authenticated(self):
        if self.request.session.get('is_wca_authenticated') is not None:
            del self.request.session['is_wca_authenticated']