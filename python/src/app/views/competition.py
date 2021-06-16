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
from app.models import Competition, Competitor, Person, Result, Round, FeePerEvent, FeePerEventCount, BestRank, AverageRank, WcaBestRank, WcaAverageRank, StripeProgress


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
            fees[result.event_id] = result.price
            
        if competitor:
            for result in results:
                if result.event_id == 0:
                    price += result.price
                if result.event_id in competitor.event_ids:
                    price += result.price

    elif competition.fee_calc_type == app.consts.FEE_CALC_TYPE_EVENT_COUNT:
        results = FeePerEventCount.objects.filter(competition_id=competition.id)
        for result in results:
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

        type = int(self.request.GET.get(key='type', default=0))
        event_id = int(self.request.GET.get(key='event_id', default=0))
        year = int(self.request.GET.get(key='year', default=0))
        prefecture_id = int(self.request.GET.get(key='prefecture_id', default=0))

        form = CompetitionForm(initial = {
            'type': type,
            'event_id': event_id,
            'year': year,
            'prefecture_id': prefecture_id,
        })

        competition_type = list(app.consts.COMPETITION_TYPE)
        competition_type.insert(0, (0, '全種別'))
        form.fields['type'].choices = tuple(competition_type)

        event = list(app.consts.EVENT)
        event.insert(0, (0, '全種目'))
        form.fields['event_id'].choices = tuple(event)

        years = [(0, '最新')]
        current_year = datetime.date.today().year
        years += list(map(lambda x: (x, str(x) + '年'), reversed(range(app.consts.SCJ_COMPETITON_FIRST_YEAR, current_year + 1))))
        form.fields['year'].choices = tuple(years)

        prefectures = [(0, '全都道府県')]
        for prefecture in app.consts.PREFECTURE:
            if prefecture[0] <= app.consts.PREFECTURE_COUNT:
                prefectures.append(prefecture)
        form.fields['prefecture_id'].choices = tuple(prefectures)

        competitions = Competition.objects.order_by('open_at').reverse()

        if type != 0:
            competitions = competitions.filter(type=type)

        if event_id != 0:
            competitions = competitions.filter(event_ids__contains=[event_id])

        if year != 0:
            competitions = competitions.filter(open_at__year=year)
        
        if prefecture_id != 0:
            competitions = competitions.filter(prefecture_id=prefecture_id)

        competition_list = []
        finish_competition_list = []

        for competition in competitions:
            if competition.is_open() or not competition.is_close():
                competition_list.append(competition)
            else:
                finish_competition_list.append(competition)

        context = {
            'form': form,
            'competitions': competition_list,
            'finish_competitions': finish_competition_list
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

        fee_pay_types = dict(app.consts.FEE_PAY_TYPE)
        fee_pay_type_text = fee_pay_types[competition.fee_pay_type]

        fee_calc_types = dict(app.consts.FEE_CALC_TYPE)
        fee_calc_type_text = fee_calc_types[competition.fee_calc_type]

        notification = ''
        if competition.is_cancel:
            notification = 'is_canceled_competition'

        competitor = None
        if request.user.is_authenticated:
            competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=request.user.person.id
            )
            competitor = competitor.first()

        # 承認者数
        competitor_registration_count = Competitor.objects.filter(
            competition_id=competition.id,
            status=app.consts.COMPETITOR_STATUS_REGISTRATION).count()
        competitor_registration_rate = int(competitor_registration_count * 100 / competition.limit)

        # google calendar date params
        open_at = localtime(competition.open_at).strftime('%Y%m%d')
        close_at = localtime(competition.close_at).strftime('%Y%m%d')
        google_calendar_date_param = open_at + '/' + close_at

        # 結果があるか
        has_results = Result.objects.filter(competition_id=competition.id).count() > 0
        # 現在時刻
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        context = {
            'title': competition.name,
            'competition': competition,
            'competition_day_count': competition_day_count,
            'judges': judges,
            'organizers': organizers,
            'competitor': competitor,
            'competitor_registration_count': competitor_registration_count,
            'competitor_registration_rate': competitor_registration_rate,
            'fee_pay_type_text': fee_pay_type_text,
            'fee_calc_type_text': fee_calc_type_text,
            'google_api_key': settings.GOOGLE_API_KEY,
            'google_map_url': settings.GOOGLE_MAP_URL,
            'google_calendar_url': settings.GOOGLE_CALENDAR_URL,
            'google_calendar_date_param': google_calendar_date_param,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition),
            'now': now,
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
            competitor.pay_at = None
            competitor.refund_at = None
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
        is_wca_authenticated = False
        if self.request.user.is_authenticated:
            competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=self.request.user.person.id)
            if competitor.exists():
                is_offer = True
                competitor = competitor.first()
                is_prepaid = StripeProgress.objects.filter(competitor_id=competitor.id).exists()
            if request.user.person.is_wca_authenticated() and request.user.person.is_wca_email_authenticated():
                is_wca_authenticated = True
        
        registration_competitor_count = Competitor.objects.filter(
            competition_id=competition.id,
            status=app.consts.COMPETITOR_STATUS_REGISTRATION).count()
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
            'is_wca_authenticated': is_wca_authenticated,
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
            event_id = [k for k, v in dict(app.consts.EVENT).items() if v == event_name][0]

        if event_id:
            competitors = Competitor.objects.filter(competition_id=competition.id, event_ids__contains=event_id)
        else:
            competitors = Competitor.objects.filter(competition_id=competition.id)

        if competition.is_display_pending_competitor:
            competitors = competitors.exclude(status=app.consts.COMPETITOR_STATUS_CANCEL).order_by('created_at')
        else:
            competitors = competitors.filter(status=app.consts.COMPETITOR_STATUS_REGISTRATION).order_by('created_at')

        bests = {}
        averages = {}
        if event_id:
            if competition.type == app.consts.COMPETITION_TYPE_SCJ:
                person_ids = []
                for competitor in competitors:
                    person_ids.append(competitor.person.id)

                best_ranks = BestRank.objects.filter(event_id=event_id, person_id__in=person_ids)
                for best_rank in best_ranks:
                    bests[best_rank.person.id] = best_rank.best

                average_ranks = AverageRank.objects.filter(event_id=event_id, person_id__in=person_ids)
                for average_rank in average_ranks:
                    averages[average_rank.person.id] = average_rank.best

            elif competition.type == app.consts.COMPETITION_TYPE_WCA:
                wca_ids = []
                for competitor in competitors:
                    wca_ids.append(competitor.person.wca_id)

                wca_best_ranks = WcaBestRank.objects.filter(event_id=event_id, wca_id__in=wca_ids)
                for wca_best_rank in wca_best_ranks:
                    bests[wca_best_rank.wca_id] = wca_best_ranks.best

                wca_average_ranks = WcaAverageRank.objects.filter(event_id=event_id, wca_id__in=wca_ids)
                for wca_average_rank in wca_average_ranks:
                    averages[wca_average_rank.wca_id] = wca_average_rank.best

        competitor_list = []
        name = ''
        prefecture = ''
        for competitor in competitors:
            if competition.type == app.consts.COMPETITION_TYPE_SCJ:
                name = competitor.person.get_full_name()
                prefecture = competitor.person.get_prefecture_id_display()
                best = bests[competitor.person.id] if competitor.person.id in bests else 'n/a'
                average = averages[competitor.person.id] if competitor.person.id in averages else 'n/a'
            elif competition.type == app.consts.COMPETITION_TYPE_WCA:
                name = competitor.person.wca_name
                best = bests[competitor.person.wca_id] if competitor.person.wca_id in bests else 'n/a'
                average = averages[competitor.person.wca_id] if competitor.person.wca_id in averages else 'n/a'

            competitor_list.append({
                'status': competitor.status,
                'name': name,
                'prefecture': prefecture,
                'best': best,
                'average': average,
            })

        competitor_list = sorted(competitor_list, key=lambda x: x['average'])

        event_names = []
        for event_id in competition.event_ids:
            if event_id in dict(app.consts.EVENT):
                event_names.append(dict(app.consts.EVENT)[event_id])

        context = {
            'competition': competition,
            'competitors': competitor_list,
            'event_id': event_id,
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
            'has_results': True,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }

        return render(request, 'app/competition/result.html', context)

class CompetitionSchedule(TemplateView):
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

        # 日付 -> 会場 -> record
        round_dict = {}
        for round in rounds:
            date = localtime(round.begin_at).strftime('%Y年%m月%d日')
            if date in round_dict and round.room_name in round_dict[date]:
                round_dict[date][round.room_name].append(round)
            else:
                round_dict[date] = {round.room_name: [round]}

        # 種目ごとにラウンドを分ける(FMCが複数レコードある)
        event_round_types = {}
        for round in rounds:
            if round.event_id > 0:
                if round.event_id in event_round_types:
                    event_round_types[round.event_id].add(round.type)
                else:
                    event_round_types[round.event_id] = set([round.type])

        event_round_count_dict = {}
        for event_id, round_types in event_round_types.items():
            event_round_count_dict[event_id] = len(round_types)

        context = {
            'competition': competition,
            'round_dict': round_dict,
            'event_round_count_dict': event_round_count_dict,
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }

        return render(request, 'app/competition/schedule.html', context)

class CompetitionFee(TemplateView):
    def get(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        status = ''
        if 'status' in request.GET:
            status = request.GET.get('status')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_detail', name_id=name_id)
        competition = competition.first()

        stripe_user_id = ''
        if competition.stripe_user_person_id != 0:
            person = Person.objects.get(pk=competition.stripe_user_person_id)
            stripe_user_id = person.stripe_user_id

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0
        if has_results:
            return redirect('competition_detail', name_id=name_id)

        competitor = None
        if request.user.is_authenticated:
            competitor = Competitor.objects.filter(competition_id=competition.id, person_id=request.user.person.id)
            if request.method == 'POST' and not competitor.exists():
                return redirect('competition_index')
            if competitor.exists():
                competitor = competitor.first()

        amount = calc_fee(self, competition, competitor)

        paid = False
        if competitor:
            paid = StripeProgress.objects.filter(competitor_id=competitor.id).exists()
        if status == 'success':
            # 一旦支払い済みにする(同期が遅いときある)
            paid = True
        
        notification = ''
        if status == 'cancel':
            notification = 'is_just_payment_cancel'
        elif status == 'success':
            notification = 'is_just_payment_success'

        context = {
            'competition': competition,
            'competitor': competitor,
            'fees': amount['fees'],
            'price': amount['price'],
            'paid': paid,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'stripe_user_id': stripe_user_id,
            'notification': notification,
            'is_payment': competition.is_payment or is_superuser(self, request, competition),
            'is_superuser': is_superuser(self, request, competition),
            'is_refunder': is_refunder(self, request, competition)
        }

        return render(request, 'app/competition/fee.html', context)

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
        
        is_updated = False
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

            if competitor.status == app.consts.COMPETITOR_STATUS_PENDING:
                pending_competitors.append(competitor)
            if competitor.status == app.consts.COMPETITOR_STATUS_REGISTRATION:
                registration_competitors.append(competitor)
            if competitor.status == app.consts.COMPETITOR_STATUS_CANCEL:
                cancel_competitors.append(competitor)

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0

        context = {
            'competition': competition,
            'has_results': has_results,
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

        competitor_ids = []
        stripe_progresses = StripeProgress.objects.filter(competition_id=competition.id, refund_price=0)
        for stripe_progress in stripe_progresses:
            competitor_ids.append(stripe_progress.competitor_id)

        competitors = Competitor.objects.filter(id__in=competitor_ids)
        for competitor in competitors:
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id: 
                    competitor.set_stripe_progress(stripe_progress)

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'competition': competition,
            'has_results': has_results,
            'competitors': competitors,
            'notification': notification,
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

        competitor_ids = []
        stripe_progresses = StripeProgress.objects.filter(competition_id=competition.id, refund_price=0)
        for stripe_progress in stripe_progresses:
            competitor_ids.append(stripe_progress.competitor_id)

        competitors = Competitor.objects.filter(id__in=competitor_ids)
        for competitor in competitors:
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id: 
                    competitor.set_stripe_progress(stripe_progress)

        for competitor in competitors:
            if request.POST.get('competitor_id_' + str(competitor.id)):
                stripe_progress = StripeProgress.objects.get(competitor_id=competitor.id)

                fee = calc_fee(self, competition, competitor)
                amount = int(fee['price'])
                if request.POST.get('competitor_refund_' + str(competitor.id)):
                    part_amount = int(request.POST.get('competitor_refund_' + str(competitor.id)))
                    if amount < part_amount:
                        request.session['notification'] = 'is_just_over_refund_amount'
                        return redirect('competition_admin_refund', name_id=name_id)
                    amount = part_amount

                if stripe_user_person:
                    stripe.Refund.create(
                        amount=int(amount),
                        charge=stripe_progress.charge_id,
                        stripe_account=stripe_user_person.stripe_user_id
                    )
                else:
                    stripe.Refund.create(
                        amount=int(amount),
                        charge=stripe_progress.charge_id
                    )

                competitor.status = app.consts.COMPETITOR_STATUS_CANCEL
                competitor.save(update_fields=[
                    'status',
                    'updated_at'
                ])

                stripe_progress.refund_price = int(amount)
                stripe_progress.refund_at = datetime.datetime.now(tz=datetime.timezone.utc)
                stripe_progress.save()

                amount = calc_fee(self, competition, competitor)
                send_mail(self,
                    request,
                    competitor.person.user,
                    competition,
                    'mail/competition/registration_refund_subject.txt',
                    'mail/competition/registration_refund_message.txt',
                    price=amount['price'])

        has_results = Result.objects.filter(competition_id=competition.id).count() > 0

        context = {
            'competition': competition,
            'has_results': has_results,
            'competitors': competitors,
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
        stripe_progresses = StripeProgress.objects.filter(competition_id=competition.id, refund_price=0)
        for competitor in competitors:
            for stripe_progress in stripe_progresses:
                if competitor.id == stripe_progress.competitor_id:
                    competitor.set_stripe_progress(stripe_progress)

        response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
        filename = urllib.parse.quote((name_id + '_competitor.csv').encode('utf8'))
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
                'name',
                'email'
            ]
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
            'stripe_charge_id',
            'comment',
            'pay_at',
            'created_at'
        ])
        writer.writerow(row)

        for index, competitor in enumerate(competitors):
            if request.POST.get('competitor_id_' + str(competitor.id)):
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
                        competitor.person.wca_name,
                        competitor.person.wca_email,
                    ]

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
                    competitor.stripe_progress.charge_id if competitor.stripe_progress != None else '',
                    competitor.comment,
                    localtime(competitor.stripe_progress.pay_at) if competitor.stripe_progress != None else '',
                    localtime(competitor.created_at),
                ])

                writer.writerow(row)

        return response

class CompetitionAdminCompetitorCsvWcaImport(LoginRequiredMixin, TemplateView):
    def post(self, request, **kwargs):
        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if competition.type != app.consts.COMPETITION_TYPE_WCA:
            return redirect('competition_index')

        if not is_superuser(self, request, competition):
            return redirect('competition_index')

        competitors = Competitor.objects.filter(competition_id=competition.id)

        response = HttpResponse(content_type='text/csv; charset=Shift-JIS')
        filename = urllib.parse.quote((name_id + '_registration.csv').encode('utf8'))
        response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)
        writer = csv.writer(response)

        event_name_dict = {}
        event_id_names = dict(app.consts.EVENT_ID_NAME)
        for event_id in competition.event_ids:
            event_name_dict[event_id] = event_id_names[event_id]

        country_names = dict(app.consts.COUNTRY)
        gender = dict(app.consts.GENDER_EN)

        event_name_id_list = []
        for event_id, event_id_name in event_name_dict.items():
            if event_id in competition.event_ids:
                event_name_id_list.append(event_id_name)

        columns = [
            'Status',
            'Name',
            'Country',
            'WCA ID',
            'Birth Date',
            'Gender',
            'Email'
        ]
        columns.extend(list(event_name_dict.values()))

        writer.writerow(columns)

        for competitor in competitors:
            if request.POST.get('competitor_id_' + str(competitor.id)):

                status = 'null'
                if competitor.status == app.consts.COMPETITOR_STATUS_REGISTRATION:
                    status = 'a'
                elif competitor.status == app.consts.COMPETITOR_STATUS_CANCEL:
                    status = 'd'

                event_join_list = []
                for event_id in event_name_dict.keys():
                    if event_id in competitor.event_ids:
                        event_join_list.append(1)
                    else:
                        event_join_list.append(0)

                row = [
                    status,
                    competitor.person.wca_name,
                    country_names[competitor.person.wca_country_iso2],
                    competitor.person.wca_id,
                    competitor.person.birth_at,
                    gender[competitor.person.gender],
                    competitor.person.wca_email
                ]
                row.extend(event_join_list)

                writer.writerow(row)

        return response