import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.timezone import localtime
from django.views.generic import TemplateView
from app.models import Competition, Person, Competitor, Result, Round
from app.defines.fee import PayType as FeePayType
from app.defines.fee import CalcType as FeeCalcType
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus
from app.defines.session import Notification


class Detail(TemplateView):
    def get(self, request, **kwargs):

        if 'name_id' not in kwargs:
            return redirect('competition_index')
        name_id = kwargs.get('name_id')

        competition = Competition.objects.filter(name_id=name_id)
        if not competition.exists():
            return redirect('competition_index')
        competition = competition.first()

        if competition.is_private and not competition.is_superuser(request.user):
            return redirect('competition_index')

        # 日付計算
        timedelta = competition.close_at - competition.open_at
        competition_day_count = timedelta.days
        # SCJ審査員/WCA Delegate
        judges = Person.objects.filter(id__in=competition.judge_person_ids)
        # 主催者
        organizers = Person.objects.filter(id__in=competition.organizer_person_ids)

        fee_pay_type_text = FeePayType.get_name(competition.fee_pay_type)
        fee_calc_type_text = FeeCalcType.get_name(competition.fee_calc_type)

        # 現在時刻
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        # 結果があるか
        has_results = Result.objects.filter(competition_id=competition.id).exists()

        competitor = None
        if request.user.is_authenticated:
            competitor = Competitor.objects.filter(
                competition_id=competition.id,
                person_id=request.user.person.id
            )
            competitor = competitor.first()

        notification = ''
        if competition.is_cancel:
            notification = Notification.COMPETITION_CANCELED
        elif competition.registration_close_at < now:
            if competition.type == CompetitionType.SCJ.value:
                if has_results:
                    notification = Notification.COMPETITION_SCJ_HAS_RESULT_END
                else:
                    notification = Notification.COMPETITION_END
            elif competition.type == CompetitionType.WCA.value:
                notification = Notification.COMPETITION_WCA_END
        elif competitor:
            if competitor.status == CompetitorStatus.PENDING.value:
                notification = Notification.COMPETITOR_PENGING
            elif competitor.status == CompetitorStatus.REGISTRATION.value:
                notification = Notification.COMPETITOR_REGISTRATION
            elif competitor.status == CompetitorStatus.CANCEL.value:
                notification = Notification.COMPETITOR_CANCEL

        # 承認者数
        competitor_registration_count = Competitor.objects.filter(
            competition_id=competition.id,
            status=CompetitorStatus.REGISTRATION.value).count()
        competitor_registration_rate = int(competitor_registration_count * 100 / competition.limit)

        # 部屋を取得
        rounds = Round.objects.filter(competition_id=competition.id)
        room_names = set(map(lambda x: x.room_name, rounds))
        room_name = ', '.join(room_names)

        # google calendar date params
        open_at = localtime(competition.open_at).strftime('%Y%m%d')
        close_at = localtime(competition.close_at).strftime('%Y%m%d')
        google_calendar_date_param = open_at + '/' + close_at

        context = {
            'title': competition.name,
            'competition': competition,
            'room_name': room_name,
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
            'notification': notification,
            'is_noindex_nofollow': not competition.is_display
        }

        return render(request, 'app/competition/detail.html', context)