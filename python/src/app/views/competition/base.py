from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from app.models import Competition, Competitor, Result


class Base(TemplateView):

    user = None
    name_id = ''
    competition = None
    competitor = None
    has_results = False
    notification = None

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user

        self.set_name_id(request, kwargs)
        if not self.name_id:
            return redirect('competition_index')

        self.set_competition()
        self.set_competitor()

        if self.competition.is_private and not self.competition.is_superuser(request.user):
            return redirect('competition_index')

        self.set_has_results()

        self.set_notification(request)

        return super().dispatch(request, *args, **kwargs)

    def get_context(self):
        context = {}
        context['name_id'] = self.name_id
        context['competition'] = self.competition
        context['has_results'] = self.has_results
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
        self.competition = Competition.objects.get(name_id=self.name_id)

    def set_competitor(self):
        if self.user.is_authenticated:
            self.competitor = Competitor.get_competitor(self, self.competition.id, self.user.person.id)

    def set_has_results(self):
        self.has_results = Result.objects.filter(competition_id=self.competition.id).exists()

    def set_notification(self, request):
        self.notification = request.session.get('notification')
        if request.session.get('notification') is not None:
            del request.session['notification']

    def is_wca_authenticated(self):
        if self.user.is_authenticated:
            if self.user.person.is_wca_authenticated() and self.user.person.is_wca_email_authenticated():
                return True
        return False