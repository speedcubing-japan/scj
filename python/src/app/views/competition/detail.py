import datetime
from django.conf import settings
from django.shortcuts import render
from django.utils.timezone import localtime
from django.views.generic import TemplateView
from app.models import Competition, Person, Competitor, Result
from app.defines.fee import PayType as FeePayType
from app.defines.fee import CalcType as FeeCalcType
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus


class Detail(TemplateView):
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

        fee_pay_type_text = FeePayType.get_name(competition.fee_pay_type)
        fee_calc_type_text = FeeCalcType.get_name(competition.fee_calc_type)

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
            status=CompetitorStatus.REGISTRATION.value).count()
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
            'is_superuser': competition.is_superuser(request.user),
            'is_refunder': competition.is_refunder(request.user),
            'now': now,
            'has_results': has_results,
            'notification': notification
        }

        return render(request, 'app/competition/detail.html', context)