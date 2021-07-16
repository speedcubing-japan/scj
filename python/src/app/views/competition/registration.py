import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from app.models import Competition, Competitor, Result, StripeProgress, Person
from app.forms import CompetitionRegistrationForm
from app.defines.event import Event
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus
from app.defines.session import Notification
from .util import send_mail
from .util import calc_fee


class Registration(TemplateView):
    def get(self, request, **kwargs):
        form = CompetitionRegistrationForm()
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        status = ''
        if 'status' in request.GET:
            status = request.GET.get('status')

        context = self.create_context(request, form, name_id)
        if not context:
            return redirect('competition_detail', name_id=name_id)

        # 事前決済オンリーのときのnotification設定
        if status == 'cancel':
            context['notification'] = Notification.REGISTRATION_CANCEL
        elif status == 'success':
            context['notification'] = Notification.COMPETITION_REGISTER

        return render(request, 'app/competition/registration.html', context)

    def post(self, request, **kwargs):
        form = CompetitionRegistrationForm(request.POST)
        name_id = request.POST.get(key='name_id')
        if not name_id:
            return redirect('competition_index')

        # formを再生成しないとエラーになる。
        context = self.create_context(request, form, name_id)

        if not context:
            return redirect('competition_detail', name_id=name_id)

        if not form.is_valid():
            return render(request, 'app/competition/registration.html', context)

        elif form.is_valid():
            name_id = form.cleaned_data['name_id']
            event_ids = [int(x) for x in form.cleaned_data['event_ids']]
            guest_count = form.cleaned_data['guest_count']
            comment = form.cleaned_data['comment']

            if not request.user.is_authenticated:
                return redirect('login')

            competition = Competition.objects.filter(name_id=name_id)
            if not competition.exists():
                return redirect('competition_index')
            competition = competition.first()

            if not competition.is_registration_open() and not competition.is_superuser(request.user):
                return redirect('competition_detail', name_id=name_id)
            
            if competition.type == CompetitionType.WCA.value and not context['is_wca_authenticated']:
                return redirect('competition_detail', name_id=name_id)

            competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=request.user.person.id
            )

            if competitor.exists():
                competitor = competitor.first()
                before_status = competitor.status

                competitor.status = CompetitorStatus.PENDING.value
                competitor.event_ids = event_ids
                competitor.guest_count = guest_count
                competitor.comment = comment
                # CANCEL時だけ新規保存扱いのため、作成時間を更新する。
                if before_status == CompetitorStatus.CANCEL.value:
                    competitor.created_at = datetime.datetime.now(tz=datetime.timezone.utc)

                competitor.save(update_fields=[
                    'event_ids',
                    'guest_count',
                    'comment',
                    'status',
                    'created_at',
                    'updated_at'
                ])
                if before_status == CompetitorStatus.PENDING.value:
                    context['notification'] = Notification.COMPETITION_REGISTER_EDIT
                elif before_status == CompetitorStatus.CANCEL.value:
                    context['notification'] = Notification.COMPETITION_REGISTER
            else:
                competitor = Competitor()
                competitor.competition_id = competition.id
                competitor.status = CompetitorStatus.PENDING.value
                competitor.event_ids = event_ids
                competitor.guest_count = guest_count
                competitor.comment = comment
                competitor.person = request.user.person
                competitor.save()

                context['notification'] = Notification.COMPETITION_REGISTER

            send_mail(request,
                request.user,
                competition,
                'app/mail/competition/registration_submit_subject.txt',
                'app/mail/competition/registration_submit_message.txt')

            context['competitor'] = competitor

            return render(request, 'app/competition/registration.html', context)

    def create_context(self, request, form, name_id):
        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return None
        competition = competition.first()

        if competition.is_private and not competition.is_superuser(request.user):
            return None

        has_results = Result.objects.filter(competition_id=competition.id).exists()
        if has_results:
            return None

        competitor = None
        is_prepaid = False
        is_wca_authenticated = False
        if self.request.user.is_authenticated:
            competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=self.request.user.person.id)
            if competitor.exists():
                competitor = competitor.first()
                is_prepaid = StripeProgress.objects.filter(competitor_id=competitor.id).exists()
            if request.user.person.is_wca_authenticated() and request.user.person.is_wca_email_authenticated():
                is_wca_authenticated = True

        registration_competitor_count = Competitor.objects.filter(
            competition_id=competition.id,
            status=CompetitorStatus.REGISTRATION.value).count()
        is_limit = registration_competitor_count >= competition.limit

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        registration_open_at = competition.registration_open_at
        registration_close_at = competition.registration_close_at
        registration_open_timedelta = registration_open_at - now
        registration_close_timedelta = now - registration_close_at

        guests = []
        for guest_count in range(competition.guest_limit + 1):
            guests.append((int(guest_count), str(guest_count) + '人'))
        form.fields['guest_count'].choices = guests

        events = []
        for event_id in competition.event_ids:
            if event_id in dict(Event.choices()):
                events.append((str(event_id), Event.get_name(event_id)))
        form.fields['event_ids'].choices = events

        form.fields['name_id'].initial = name_id

        if competitor:
            form.fields['event_ids'].initial = competitor.event_ids
            form.fields['guest_count'].initial = competitor.guest_count
            form.fields['comment'].initial = competitor.comment

        protocol = 'https' if request.is_secure() else 'http'
        current_site = get_current_site(request)
        domain = current_site.domain
        redirect_uri = protocol + '://' + domain + '/wca/authorization/?type=competition'
        # WCA認証で2つ以上のパラメータを渡せないため、セッションで管理。
        request.session['wca_authorization_name_id'] = name_id

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        stripe_user_id = ''
        if competition.stripe_user_person_id != 0:
            person = Person.objects.get(pk=competition.stripe_user_person_id)
            stripe_user_id = person.stripe_user_id

        # 事前決済オンリーのため計算
        amount = calc_fee(competition, None)

        context = {
            'form': form,
            'is_limit': is_limit,
            'is_prepaid': is_prepaid,
            'competition': competition,
            'competitor': competitor,
            'now': now,
            'registration_open_timedelta': registration_open_timedelta,
            'registration_close_after_timedelta': registration_close_timedelta,
            'registration_close_before_timedelta': abs(registration_close_timedelta),
            'wca_oauth_authorization': settings.WCA_OAUTH_AUTHORIZATION,
            'wca_client_id': settings.WCA_CLIENT_ID,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'stripe_user_id': stripe_user_id,
            'redirect_uri': redirect_uri,
            'is_wca_authenticated': is_wca_authenticated,
            'prepaid_fees': amount['prepaid_fees'],
            'notification': notification,
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user)
        }
        return context