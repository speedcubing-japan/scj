from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competition, Competitor
from app.defines.competitor import Status as CompetitorStatus
from app.views.competition.util import send_mail
from app.defines.session import Notification


class Cancel(LoginRequiredMixin, TemplateView):
    def post(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')
        
        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()
        
        if not competition.is_registration_open() and not competition.is_superuser(request.user):
            return redirect('competition_detail', name_id=name_id)
    
        competitor = Competitor.objects.filter(
            competition_id=competition.id,
            person_id=request.user.person.id
        )
        
        if not competitor.exists():
            return redirect('competition_registration', name_id=name_id)

        # CancelができるのはPending時。
        competitor = competitor.first()
        if competitor.status != CompetitorStatus.PENDING.value:
            return redirect('competition_registration', name_id=name_id)

        competitor.status = CompetitorStatus.CANCEL.value
        competitor.save(update_fields=[
            'status',
            'updated_at'
        ])
        
        send_mail(request,
            competitor.person.user,
            competition,
            'app/mail/competition/registration_cancel_subject.txt',
            'app/mail/competition/registration_cancel_message.txt')
        
        request.session['notification'] = Notification.COMPETITOR_CANCEL

        return redirect('competition_registration', name_id=name_id)