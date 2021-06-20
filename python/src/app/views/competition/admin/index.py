from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competition, Competitor, Result, StripeProgress
from app.defines.competitor import Status as CompetitorStatus
from app.views.competition.util import send_mail


class Index(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not competition.is_superuser(request.user):
            return redirect('competition_index')

        competitors = Competitor.objects.filter(competition_id=competition.id)
        context = self.create_context(request, competition, competitors)
        return render(request, 'app/competition/admin/index.html', context)

    def post(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not competition.is_superuser(request.user):
            return redirect('competition_index')

        competitors = Competitor.objects.filter(competition_id=competition.id)

        context = self.create_context(request, competition, competitors)
        registration_count = len(context['registration_competitors'])

        type = request.POST.get('type')

        for competitor in competitors:
            if request.POST.get('competitor_id_' + str(competitor.id)):
                if type == 'admit':
                    registration_count += 1

                if type == 'cancel':
                    registration_count -= 1

        if registration_count > competition.limit:
            context['notification'] = 'is_just_admin_competition_limit'
            return render(request, 'app/competition/admin/index.html', context)

        is_updated = False
        for competitor in competitors:
            if request.POST.get('competitor_id_' + str(competitor.id)):
                if type == 'admit':
                    competitor.status = CompetitorStatus.REGISTRATION.value
                    competitor.save(update_fields=[
                        'status',
                        'updated_at'
                    ])

                    send_mail(request,
                        competitor.person.user,
                        competition,
                        'app/mail/competition/registration_admit_subject.txt',
                        'app/mail/competition/registration_admit_message.txt')

                if type == 'cancel':
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

                is_updated = True

        context = self.create_context(request, competition, competitors)

        if is_updated:
            context['notification'] = 'is_just_update'
        else:
            context['notification'] = 'is_just_not_selected'

        return render(request, 'app/competition/admin/index.html', context)

    def create_context(self, request, competition, competitors):
        pending_competitors = []
        registration_competitors = []
        cancel_competitors = []

        stripe_progresses = StripeProgress.objects.filter(competition_id=competition.id)
        for competitor in competitors:

            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)

            if competitor.status == CompetitorStatus.PENDING.value:
                pending_competitors.append(competitor)
            if competitor.status == CompetitorStatus.REGISTRATION.value:
                registration_competitors.append(competitor)
            if competitor.status == CompetitorStatus.CANCEL.value:
                cancel_competitors.append(competitor)

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0

        context = {
            'competition': competition,
            'has_results': has_results,
            'pending_competitors': pending_competitors,
            'registration_competitors': registration_competitors,
            'cancel_competitors': cancel_competitors,
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }

        return context