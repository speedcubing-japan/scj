import json
import datetime
import app.consts
import stripe
import pprint
import csv
import urllib
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.timezone import make_aware
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import localtime
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from app.forms import CompetitionForm, CompetitionRegistrationForm, CompetitionAdminCompetitorEditForm
from app.models import Competition, Competitor, Person, Result, Round, FeePerEvent, FeePerEventCount


def is_superuser(self, request, competition):
    is_superuser = False
    if request.user.is_authenticated:
        if request.user.is_superuser:
            is_superuser = True
        if request.user.person.id in competition.organizer_person_ids:
            is_superuser = True
        if request.user.person.id in competition.judge_person_ids:
            is_superuser = True
    return is_superuser

def is_refunder(self, request, competition):
    is_refunder = False
    if request.user.is_authenticated:
       if request.user.is_superuser:
           is_refunder = True
       if request.user.person.id == competition.stripe_user_person_id:
           is_refunder = True
    return is_refunder

def send_mail(self, request, user, competition, subject_path, message_path, **kwargs):
    current_site = get_current_site(request)
    domain = current_site.domain
    context = {
        'protocol': 'https' if request.is_secure() else 'http',
        'domain': domain,
        'user': user,
        'competition':  competition
    }

    if 'price' in kwargs:
        context['price'] = kwargs.get('price')

    subject = render_to_string(subject_path, context).strip()
    message = render_to_string(message_path, context).strip()
    user.email_user(subject, message, settings.EMAIL_HOST_USER)

def calc_fee(self, competition, competitor):
    
    fees = {}
    price = 0

    if competition.fee_calc_type == app.consts.FEE_CALC_TYPE_EVENT:
        events = dict(app.consts.EVENT)
        results = FeePerEvent.objects.filter(competition_id=competition.id)
        for result in results:
            if result.event_id == 0:
                fees['基本料金'] = result.price
            else:
                fees[events[result.event_id]] = result.price
            
        if competitor:
            for result in results:
                if result.event_id == 0:
                    price += result.price
                if result.event_id in competitor.event_ids:
                    price += result.price

    elif competition.fee_calc_type == app.consts.FEE_CALC_TYPE_EVENT_COUNT:
        results = FeePerEventCount.objects.filter(competition_id=competition.id)
        for result in results:
            if result.event_count == 0:
                fees['基本料金'] = result.price
            else:
                fees[result.event_count] = result.price
            
        if competitor:
            event_count = len(competitor.event_ids)
            for result in results:
                if result.event_count == 0:
                    price += result.price
                if result.event_count == event_count:
                    price += result.price
    
    return {'fees': fees, 'price': price}

class CompetitionAbout(TemplateView):
    template_name = 'app/competition/about.html'

class CompetitionRegulation(TemplateView):
    template_name = 'app/competition/regulation.html'

class CompetitionIndex(TemplateView):
    def get(self, request):

        event_id = int(self.request.GET.get(key='event_id', default=0))
        year = int(self.request.GET.get(key='year', default=0))
        prefecture_id = int(self.request.GET.get(key='prefecture_id', default=0))

        form = CompetitionForm(initial = {
            'event_id': event_id,
            'year': year,
            'prefecture_id': prefecture_id,
        })

        event = list(app.consts.EVENT)
        event.insert(0, (0, "全種目"))
        form.fields['event_id'].choices = tuple(event)

        years = [(0, "最新")]
        current_year = datetime.date.today().year
        for target_year in range(app.consts.SCJ_COMPETITON_FIRST_YEAR, current_year + 1):
            years.append((target_year, str(target_year) + "年"))
        form.fields['year'].choices = tuple(years)

        prefectures = [(0, "全都道府県")]
        for prefecture in app.consts.PREFECTURE:
            if prefecture[0] <= app.consts.PREFECTURE_COUNT:
                prefectures.append(prefecture)
        form.fields['prefecture_id'].choices = tuple(prefectures)

        competition = Competition.objects.order_by('open_at').reverse()

        if event_id != 0:
            competition = competition.filter(event_ids__contains=[event_id])

        if year != 0:
            competition = competition.filter(open_at__year=year)
        
        if prefecture_id != 0:
            competition = competition.filter(prefecture_id=prefecture_id)

        competitions = []
        finish_competitions = []

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        for comp in competition:
            if comp.close_at >= now:
                competitions.append(comp)
            else:
                finish_competitions.append(comp)

        context = {
            'form': form,
            'competitions': competitions,
            'finish_competitions': finish_competitions
        }

        return render(request, 'app/competition/index.html', context)

class CompetitionDetail(TemplateView):
    def get(self, request, **kwargs):

        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        # 日付計算
        timedelta = competition.close_at - competition.open_at
        competition_day_count = timedelta.days
        # SCJ審査員/WCA Delegate
        judges = Person.objects.filter(id__in=competition.judge_person_ids)
        # 主催者
        organizers = Person.objects.filter(id__in=competition.organizer_person_ids)
        # イベント
        event_names = []
        events = dict(app.consts.EVENT)
        for event_id in competition.event_ids:
            event_names.append(events[event_id])

        fee_pay_types = dict(app.consts.FEE_PAY_TYPE)
        fee_pay_type_text = fee_pay_types[competition.fee_pay_type]

        fee_calc_types = dict(app.consts.FEE_CALC_TYPE)
        fee_calc_type_text = fee_calc_types[competition.fee_calc_type]

        notification = ''
        if competition.is_cancel:
            notification = 'is_canceled_competition'

        # 結果があるか
        has_results = Result.objects.filter(competition_id=competition.id).count() > 0

        context = {
            'title': competition.name,
            'competition': competition,
            'competition_day_count': competition_day_count,
            'judges': judges,
            'organizers': organizers,
            'event_names': event_names,
            'fee_pay_type_text': fee_pay_type_text,
            'fee_calc_type_text': fee_calc_type_text,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition),
            'has_results': has_results,
            'notification': notification
        }

        return render(request, 'app/competition/detail.html', context)

class CompetitionRegistration(TemplateView):

    def get(self, request, **kwargs):
        form = CompetitionRegistrationForm()
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        context = self.create_context(request, form, name_id)
        if not context:
            return redirect('competition_detail', name_id=name_id)

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

            competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=request.user.person.id
            )
            if competitor.exists():
                return redirect('competition_registration', name_id=name_id)
        
            competitor = Competitor()
            competitor.competition_id = competition.id
            competitor.status = app.consts.COMPETITOR_STATUS_PENDING
            competitor.event_ids = event_ids
            competitor.guest_count = guest_count
            competitor.comment = comment
            competitor.competition = competition
            competitor.person = request.user.person
            competitor.save()

            send_mail(self,
                request,
                request.user, 
                competition, 
                'mail/competition/registration_submit_subject.txt', 
                'mail/competition/registration_submit_message.txt')

            context['is_just_offer'] = True

            return render(request, 'app/competition/registration.html', context)

    def create_context(self, request, form, name_id):
        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return None
        competition = competition.first()

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0
        if has_results:
            return None

        is_offer = False
        is_prepaid = False
        if self.request.user.is_authenticated:
            competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=self.request.user.person.id)
            if competitor.exists():
                is_offer = True
                competitor = competitor.first()
                if competitor.stripe_id:
                    is_prepaid = True
        
        registration_competitor_count = Competitor.objects.filter(status=app.consts.COMPETITOR_STATUS_REGISTRATION).count()
        is_limit = registration_competitor_count == competition.limit

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
            if event_id in dict(app.consts.EVENT):
                events.append((str(event_id), dict(app.consts.EVENT)[event_id]))
        form.fields['event_ids'].choices = events

        form.fields['name_id'].initial = name_id

        protocol = 'https' if request.is_secure() else 'http'
        current_site = get_current_site(request)
        domain = current_site.domain
        redirect_uri = protocol + '://' + domain + '/wca/authorization/?type=competition'
        # WCA認証で2つ以上のパラメータを渡せないため、セッションで管理。
        request.session['wca_authorization_name_id'] = name_id

        context = {
            'form': form,
            'is_limit': is_limit,
            'is_offer': is_offer,
            'is_prepaid': is_prepaid,
            'is_just_offer': False,
            'competition': competition,
            'now': now,
            'registration_open_timedelta': registration_open_timedelta,
            'registration_close_after_timedelta': registration_close_timedelta,
            'registration_close_before_timedelta': abs(registration_close_timedelta),
            'wca_oauth_authorization': settings.WCA_OAUTH_AUTHORIZATION,
            'wca_client_id': settings.WCA_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }
        return context

class CompetitionCompetitor(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        if 'event_name' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0
        if has_results:
            return redirect('competition_detail', name_id=name_id)

        event_id = 0
        event_name = kwargs.get('event_name')
        if event_name != 'list':
            event_ids = [k for k, v in dict(app.consts.EVENT).items() if v == event_name]
            if not event_ids:
                return redirect('competition_detail', name_id=name_id)
            event_id = event_ids[0]

        if event_id:
            competitors = Competitor.objects.filter(
                competition_id=competition.id,
                event_ids__contains=event_id, 
                status=app.consts.COMPETITOR_STATUS_REGISTRATION).order_by('created_at')
        else:
            competitors = Competitor.objects.filter(
                competition_id=competition.id,
                status=app.consts.COMPETITOR_STATUS_REGISTRATION).order_by('created_at')

        event_names = []
        for event_id in competition.event_ids:
            if event_id in dict(app.consts.EVENT):
                event_names.append(dict(app.consts.EVENT)[event_id])

        context = {
            'competition': competition,
            'competitors': competitors,
            'event_name': event_name,
            'event_names': event_names,
            'name_id': name_id,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition),
        }

        return render(request, 'app/competition/competitor.html', context)

class CompetitionResult(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        competitors = Competitor.objects.filter(competition_id=competition.id)
        results = Result.objects.filter(competition_id=competition.id)
        rounds = Round.objects.filter(competition_id=competition.id)

        results = sorted(results, key=lambda x: x.rank)
        rounds = sorted(rounds, key=lambda x: x.type, reverse=True)

        competition_rounds = {}
        for round in rounds:
            if round.event_id in competition_rounds:
                competition_rounds[round.event_id].append(round.get_type_display())
            else:
                competition_rounds[round.event_id] = [round.get_type_display()]

        events = []
        for event_id in competition.event_ids:
            if event_id in dict(app.consts.EVENT):
                events.append({'event_id': event_id, 'event_name': dict(app.consts.EVENT)[event_id]})

        competitor_names = {}
        for competitor in competitors:
            competitor_names[competitor.person.id] = competitor.person.get_full_name()

        competitor_wca_names = {}
        for competitor in competitors:
            competitor_wca_names[competitor.person.id] = competitor.person.wca_name

        competitor_prefectures = {}
        for competitor in competitors:
            competitor_prefectures[competitor.person.id] = competitor.person.get_prefecture_id_display()

        context = {
            'competition': competition,
            'competitor_names': competitor_names,
            'competitor_wca_names': competitor_wca_names,
            'competitor_prefectures': competitor_prefectures,
            'events': events,
            'rounds': competition_rounds,
            'results': results,
            'has_results': True
        }

        return render(request, 'app/competition/result.html', context)

class CompetitionRound(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()
        
        has_results = Result.objects.filter(competition_id=competition.id).count() > 0
        if has_results:
            return redirect('competition_detail', name_id=name_id)

        rounds = Round.objects.filter(competition_id=competition.id)

        context = {
            'competition': competition,
            'rounds': rounds,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }

        return render(request, 'app/competition/round.html', context)

class CompetitionFee(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        context = self.create_context(request, name_id)
        if not context:
            return redirect('competition_detail', name_id=name_id)

        return render(request, 'app/competition/fee.html', context)
    
    def post(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        context = self.create_context(request, name_id)
        if not context:
            return redirect('competition_detail', name_id=name_id)

        return render(request, 'app/competition/fee.html', context)

    def create_context(self, request, name_id):
        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return None
        competition = competition.first()

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0
        if has_results:
            return None

        competitor = None
        if request.user.is_authenticated:
            competitor = Competitor.objects.filter(competition_id=competition.id, person_id=request.user.person.id)
            if request.method == 'POST' and not competitor.exists():
                return redirect('competition_index')
            if competitor.exists():
                competitor = competitor.first()
        
        amount = calc_fee(self, competition, competitor)
        
        notification = ''
        
        if request.method == 'POST':
            stripe.api_key = settings.STRIPE_SECRET_KEY
            token = request.POST.get('stripeToken')

            description = ''
            if competition.type == app.consts.COMPETITION_TYPE_WCA:
                description = '大会名: {} WCA_ID: {} WCA_USER_ID: {} 氏名: {}' \
                    .format(competition.name, \
                    request.user.person.wca_id, \
                    request.user.person.wca_user_id, \
                    request.user.person.get_full_name())
            elif competition.type == app.consts.COMPETITION_TYPE_SCJ:
                description = '大会名: {} SCJ_ID: {} 氏名: {}' \
                    .format(competition.name, \
                    request.user.person.id, \
                    request.user.person.get_full_name())

            try:
                # 購入処理
                charge = None
                if competition.stripe_user_person_id == 0:
                    charge = stripe.Charge.create(
                        amount=amount['price'],
                        currency='jpy',
                        source=token,
                        description=description
                    )
                else:
                    person = Person.objects.get(pk=competition.stripe_user_person_id)
                    charge = stripe.Charge.create(
                        amount=amount['price'],
                        currency='jpy',
                        source=token,
                        stripe_account=person.stripe_user_id,
                        description=description
                    )
            except stripe.error.CardError as e:
                # カード決済が上手く行かなかった(限度額超えとか)ので、メッセージと一緒に再度ページ表示
                notification = 'is_just_payment_error'
            else:
                # 上手く購入できた。Django側にも購入履歴を入れておく
                competitor.stripe_id = charge.id
                competitor.save(update_fields=['stripe_id', 'updated_at'])

                send_mail(self,
                    request,
                    competitor.person.user,
                    competition,
                    'mail/competition/registration_payment_subject.txt',
                    'mail/competition/registration_payment_message.txt',
                    price=amount['price'])

                notification = 'is_just_payment_success'

        context = {
            'competition': competition,
            'competitor': competitor,
            'fees': amount['fees'],
            'price': amount['price'],
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'notification': notification,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }

        return context

class CompetitionAdmin(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not is_superuser(self, request, competition):
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

        if not is_superuser(self, request, competition):
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

        for competitor in competitors:
            if request.POST.get('competitor_id_' + str(competitor.id)):
                if type == 'admit':
                    competitor.status = app.consts.COMPETITOR_STATUS_REGISTRATION
                    competitor.save(update_fields=[
                        'status',
                        'updated_at'
                    ])

                    send_mail(self,
                        request,
                        competitor.person.user,
                        competition,
                        'mail/competition/registration_admit_subject.txt',
                        'mail/competition/registration_admit_message.txt')

                if type == 'cancel':
                    competitor.status = app.consts.COMPETITOR_STATUS_CANCEL
                    competitor.save(update_fields=[
                        'status',
                        'updated_at'
                    ])
                
                    send_mail(self,
                        request,
                        competitor.person.user,
                        competition,
                        'mail/competition/registration_cancel_subject.txt',
                        'mail/competition/registration_cancel_message.txt')
        
        context = self.create_context(request, competition, competitors)
        context['notification'] = 'is_just_update'
        
        return render(request, 'app/competition/admin/index.html', context)
        
    def create_context(self, request, competition, competitors):
        pending_competitors = []
        registration_competitors = []
        cancel_competitors = []
        for competitor in competitors:
            if competitor.status == app.consts.COMPETITOR_STATUS_PENDING:
                pending_competitors.append(competitor)
            if competitor.status == app.consts.COMPETITOR_STATUS_REGISTRATION:
                registration_competitors.append(competitor)
            if competitor.status == app.consts.COMPETITOR_STATUS_CANCEL:
                cancel_competitors.append(competitor)

        context = {
            'competition': competition,
            'pending_competitors': pending_competitors,
            'registration_competitors': registration_competitors,
            'cancel_competitors': cancel_competitors,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }

        return context

class CompetitionAdminRefund(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not is_refunder(self, request, competition):
            return redirect('competition_index')

        competitors = Competitor.objects.filter(competition_id=competition.id)
        competitors = competitors.exclude(stripe_id='')

        context = {
            'competition': competition,
            'competitors': competitors,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }
        return render(request, 'app/competition/admin/refund.html', context)

    def post(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not is_refunder(self, request, competition):
            return redirect('competition_index')

        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_user_person = None
        if competition.stripe_user_person_id > 0:
            stripe_user_person = Person.objects.get(pk=competition.stripe_user_person_id)

        competitors = Competitor.objects.filter(competition_id=competition.id)
        competitors = competitors.exclude(stripe_id='')

        for competitor in competitors:
            if request.POST.get('refund_' + str(competitor.person.id)):
                if stripe_user_person:
                    stripe.Refund.create(
                        charge=competitor.stripe_id,
                        stripe_account=stripe_user_person.stripe_user_id
                    )
                else:
                    stripe.Refund.create(
                        charge=competitor.stripe_id
                    )

                competitor.stripe_id = ''
                competitor.save(update_fields=[
                    'stripe_id',
                    'updated_at'
                ])

                amount = calc_fee(self, competition, competitor)
                send_mail(self,
                    request,
                    competitor.person.user,
                    competition,
                    'mail/competition/registration_refund_subject.txt',
                    'mail/competition/registration_refund_message.txt',
                    price=amount['price'])

        current_prepaid_competitors = []
        for competitor in competitors:
            if competitor.stripe_id != '':
                current_prepaid_competitors.append(competitor)

        context = {
            'competition': competition,
            'competitors': current_prepaid_competitors,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }
        return render(request, 'app/competition/admin/refund.html', context)

class CompetitionAdminCompetitorEdit(LoginRequiredMixin, TemplateView):
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

        if not is_superuser(self, request, competition):
            return None

        competitor = Competitor.objects.get(pk=competitor_id)
        if not competitor:
            return None

        events = {}
        for event_id in competition.event_ids:
            if event_id in dict(app.consts.EVENT):
                events[event_id] = dict(app.consts.EVENT)[event_id]

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
                notification = 'is_just_update'
            else:
                notification = 'is_just_admin_competitor_event_not_selected'

        context = {
            'events': events,
            'competition': competition,
            'competitor': competitor,
            'guest_counts': range(competition.guest_limit + 1),
            'notification': notification,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }
        return context
        
class CompetitionAdminCompetitorCsv(LoginRequiredMixin, TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if not is_superuser(self, request, competition):
            return redirect('competition_index')
    
        competitors = Competitor.objects.filter(competition_id=competition.id, status=app.consts.COMPETITOR_STATUS_REGISTRATION)

        response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
        filename = urllib.parse.quote((name_id + '_competitor.csv').encode("utf8"))
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        writer = csv.writer(response)

        event_name_dict = {}
        event_id_names = dict(app.consts.EVENT_ID_NAME)
        for event_id in competition.event_ids:
            event_name_dict[event_id] = event_id_names[event_id]

        if competition.type == app.consts.COMPETITION_TYPE_WCA:
            row = [
                'wca_id',
                'wca_user_id',
                'full_name',
                'full_name_kana',
                'full_name_rome',
                'email'
            ]
            row.extend(list(event_name_dict.values()))
            row.extend([
                'guest_count'
                'stripe_id',
                'created_at'
            ])
            writer.writerow(row)
        elif competition.type == app.consts.COMPETITION_TYPE_SCJ:
            row = [
                'scj_id',
                'full_name',
                'full_name_kana',
                'full_name_rome',
                'email'
            ]
            row.extend(list(event_name_dict.values()))
            row.extend([
                'guest_count',
                'stripe_id',
                'comment',
                'created_at'
            ])
            writer.writerow(row)

        for index, competitor in enumerate(competitors):

            event_join_list = []
            for event_id in event_name_dict.keys():
                if event_id in competitor.event_ids:
                    event_join_list.append(1)
                else:
                    event_join_list.append(0)

            if competition.type == app.consts.COMPETITION_TYPE_WCA:
                row = [
                    competitor.person.wca_id,
                    competitor.person.wca_user_id,
                    competitor.person.get_full_name(),
                    competitor.person.get_full_name_kana(),
                    competitor.person.get_full_name_roma(),
                    competitor.person.user.email,
                ]
                row.extend(event_join_list)
                row.extend([
                    competitor.guest_count,
                    competitor.stripe_id,
                    competitor.comment,
                    competitor.created_at,
                ])
            elif competition.type == app.consts.COMPETITION_TYPE_SCJ:
                id = competitor.person.id
                row = [
                    id,
                    competitor.person.get_full_name(),
                    competitor.person.get_full_name_kana(),
                    competitor.person.get_full_name_roma(),
                    competitor.person.user.email
                ]
                row.extend(event_join_list)
                row.extend([
                    competitor.guest_count,
                    competitor.stripe_id,
                    competitor.comment,
                    competitor.created_at
                ])

            writer.writerow(row)

        return response