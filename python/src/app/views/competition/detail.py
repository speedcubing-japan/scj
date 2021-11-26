import datetime
from django.conf import settings
from django.shortcuts import render
from django.utils.timezone import localtime
from app.models import Person, Competitor, Result, Round
from app.defines.fee import PayType as FeePayType
from app.defines.fee import CalcType as FeeCalcType
from app.defines.competition import Type as CompetitionType
from app.defines.competitor import Status as CompetitorStatus
from app.defines.session import Notification
from .base import Base


class Detail(Base):

    template_name = "app/competition/detail.html"

    def get(self, request, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()

        # 日付計算
        timedelta = self.competition.close_at - self.competition.open_at
        competition_day_count = timedelta.days
        # SCJ審査員/WCA Delegate
        judges = Person.objects.filter(id__in=self.competition.judge_person_ids)
        # 主催者
        organizers = Person.objects.filter(id__in=self.competition.organizer_person_ids)

        fee_pay_type_text = FeePayType.get_name(self.competition.fee_pay_type)
        fee_calc_type_text = FeeCalcType.get_name(self.competition.fee_calc_type)

        # 現在時刻
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        # 結果があるか
        has_results = Result.objects.filter(competition_id=self.competition.id).exists()

        notification = ""
        if self.competition.is_private:
            notification = Notification.COMPETITION_PRIVATE
        elif not self.competition.is_display:
            notification = Notification.COMPETITION_NOT_DISPLAY
        elif self.competition.is_cancel:
            notification = Notification.COMPETITION_CANCELED
        elif self.competition.registration_close_at < now:
            if has_results:
                notification = Notification.COMPETITION_SCJ_HAS_RESULT_END
            elif self.competition.is_finish():
                if self.competition.type == CompetitionType.SCJ.value:
                    notification = Notification.COMPETITION_SCJ_END
                elif self.competition.type == CompetitionType.WCA.value:
                    notification = Notification.COMPETITION_WCA_END
            elif self.competitor:
                if self.competitor.status == CompetitorStatus.PENDING.value:
                    notification = Notification.COMPETITOR_PENGING
                elif self.competitor.status == CompetitorStatus.REGISTRATION.value:
                    notification = Notification.COMPETITOR_REGISTRATION
                elif self.competitor.status == CompetitorStatus.CANCEL.value:
                    notification = Notification.COMPETITOR_CANCEL

        # 申し込み者数(未承認+承認)
        competitor_offer_count = Competitor.objects.filter(
            competition_id=self.competition.id,
            status__in=(
                CompetitorStatus.PENDING.value,
                CompetitorStatus.REGISTRATION.value,
            ),
        ).count()

        # 承認者数
        competitor_registration_count = Competitor.objects.filter(
            competition_id=self.competition.id,
            status=CompetitorStatus.REGISTRATION.value,
        ).count()
        competitor_registration_rate = int(
            competitor_registration_count * 100 / self.competition.limit
        )

        # 部屋を取得
        rounds = Round.objects.filter(competition_id=self.competition.id)
        room_names = set(map(lambda x: x.room_name, rounds))
        room_name = ", ".join(room_names)

        # google calendar date params
        open_at = localtime(self.competition.open_at).strftime("%Y%m%d")
        close_at = localtime(self.competition.close_at).strftime("%Y%m%d")
        google_calendar_date_param = open_at + "/" + close_at

        # 作成時のエラー
        admin_errors = self.request.session.get("competition_admin_errors")
        if self.request.session.get("competition_admin_errors") is not None:
            del self.request.session["competition_admin_errors"]

        context["title"] = self.competition.name
        context["room_name"] = room_name
        context["competition_day_count"] = competition_day_count
        context["judges"] = judges
        context["organizers"] = organizers
        context["competitor_registration_count"] = competitor_registration_count
        context["competitor_registration_rate"] = competitor_registration_rate
        context["competitor_offer_count"] = competitor_offer_count
        context["fee_pay_type_text"] = fee_pay_type_text
        context["fee_calc_type_text"] = fee_calc_type_text
        context["google_api_key"] = settings.GOOGLE_API_KEY
        context["google_map_url"] = settings.GOOGLE_MAP_URL
        context["google_calendar_url"] = settings.GOOGLE_CALENDAR_URL
        context["google_calendar_date_param"] = google_calendar_date_param
        context["now"] = now
        context["is_noindex_nofollow"] = not self.competition.is_display
        context["admin_errors"] = admin_errors
        if not self.notification:
            context["notification"] = notification

        return context
