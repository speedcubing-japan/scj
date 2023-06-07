import re
import app.models
import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import StripeProgress
from app.defines.event import Event
from app.views.competition.base import Base
from app.defines.session import Notification
from app.defines.prefecture import PrefectureAndOversea


class Competitor(LoginRequiredMixin, Base):

    template_name = "app/competition/admin/competitor.html"
    target_competitor = None
    admin_errors = []

    def get(self, request, **kwargs):
        if not self.competition.is_superuser(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        if "competitor_id" not in kwargs:
            return redirect("competition_detail", name_id=self.name_id)

        competitor_id = kwargs.get("competitor_id")
        competitor = app.models.Competitor.objects.filter(id=competitor_id)
        if not competitor.exists():
            return redirect("competition_detail", name_id=self.name_id)
        self.target_competitor = competitor.first()

        return render(request, self.template_name, self.get_context())

    def post(self, request, **kwargs):
        self.admin_errors = []

        if not self.competition.is_superuser(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        if "competitor_id" not in request.POST:
            return redirect("competition_detail", name_id=self.name_id)

        competitor_id = request.POST.get(key="competitor_id")
        competitor = app.models.Competitor.objects.filter(id=competitor_id)
        if not competitor.exists():
            return redirect("competition_detail", name_id=self.name_id)
        self.target_competitor = competitor.first()

        event_ids = []
        for event_id in self.competition.event_ids:
            if request.POST.get("event_id_" + str(event_id)):
                event_ids.append(event_id)

        if not event_ids:
            self.admin_errors.append("種目が選択されていません")

        guest_count = 0
        if request.POST.get("guest_count"):
            guest_count = int(request.POST.get("guest_count"))

        if self.is_wca_competition():
            if not self.target_competitor.person.wca_id:
                wca_name = request.POST.get("wca_name", "")
                wca_birth_at = request.POST.get("wca_birth_at", "")
                if not wca_name:
                    self.admin_errors.append("WCA氏名が規格外です。")
                if not wca_birth_at:
                    self.admin_errors.append("WCA誕生日が規格外です。")

            if self.target_competitor.person.wca_id:
                wca_name = self.target_competitor.person.wca_name
                wca_birth_at = self.target_competitor.person.wca_birth_at
            else:
                wca_birth_at = self.get_date(wca_birth_at, True)

        birth_at = request.POST.get("birth_at", "")
        birth_at = self.get_date(birth_at, False)

        prefecture_id = int(request.POST.get("prefecture_id", ""))

        last_name = request.POST.get("last_name")
        if not last_name:
            self.admin_errors.append("名が規格外です。")

        first_name = request.POST.get("first_name")
        if not first_name:
            self.admin_errors.append("姓が規格外です。")

        re_katakana = re.compile(r"[\u30A1-\u30F4]+")

        last_name_kana = request.POST.get("last_name_kana")
        if not last_name_kana:
            self.admin_errors.append("名(カナ)が規格外です。")
        if not re_katakana.fullmatch(last_name_kana):
            self.admin_errors.append("名(カナ)に全角カタカナでない文字が含まれています。")

        first_name_kana = request.POST.get("first_name_kana")
        if not first_name_kana:
            self.admin_errors.append("姓(カナ)が規格外です。")
        if not re_katakana.fullmatch(first_name_kana):
            self.admin_errors.append("姓(カナ)に全角カタカナでない文字が含まれています。")

        last_name_roma = request.POST.get("last_name_roma")
        if not last_name_roma:
            self.admin_errors.append("名(Roma)が規格外です。")
        if re.fullmatch("[a-zA-Z]+", last_name_roma) is None:
            self.admin_errors.append("名(Roma)に半角アルファベットでない文字が含まれています。")
        if last_name_roma != last_name_roma.capitalize():
            self.admin_errors.append("名(Roma)に先頭文字が大文字、それ以降の文字は小文字でお願いします。")

        first_name_roma = request.POST.get("first_name_roma")
        if not first_name_roma:
            self.admin_errors.append("性(Roma)が規格外です。")
        if re.fullmatch("[a-zA-Z]+", first_name_roma) is None:
            self.admin_errors.append("性(Roma)に半角アルファベットでない文字が含まれています。")
        if first_name_roma != first_name_roma.capitalize():
            self.admin_errors.append("性(Roma)に先頭文字が大文字、それ以降の文字は小文字でお願いします。")

        if not self.admin_errors:
            self.target_competitor.update_admin_competitor(
                event_ids,
                guest_count,
                prefecture_id,
                birth_at,
                wca_name,
                wca_birth_at,
                last_name,
                first_name,
                last_name_kana,
                first_name_kana,
                last_name_roma,
                first_name_roma,
            )
            self.notification = Notification.UPDATE

        return render(request, self.template_name, self.get_context())

    def get_context(self):

        is_prepaid = False
        if self.target_competitor:
            is_prepaid = StripeProgress.objects.filter(
                competitor_id=self.target_competitor.id
            ).exists()

        context = super().get_context()
        context["events"] = Event.get_events(self.competition.event_ids)
        context["competitor"] = self.target_competitor
        context["guest_counts"] = range(self.competition.guest_limit + 1)
        context["is_prepaid"] = is_prepaid
        context["admin_errors"] = self.admin_errors
        context["request_method"] = self.request.method
        context["prefectures"] = PrefectureAndOversea.choices()

        return context

    def get_date(self, birth_at, is_wca):
        head_string = "誕生日"
        if is_wca:
            head_string = "WCA" + head_string

        pattern = r"(\d{4})-(\d{2})-(\d{2})"
        prog = re.compile(pattern)
        result = prog.match(birth_at)
        if not result:
            self.admin_errors.append(head_string + "がフォーマット規格外です。")
        else:
            try:
                new_data_str = "%04d-%02d-%02d" % (
                    int(result.group(1)),
                    int(result.group(2)),
                    int(result.group(3)),
                )
                return datetime.datetime.strptime(new_data_str, "%Y-%m-%d")
            except ValueError:
                self.admin_errors.append(head_string + "が不正な日付です。")
