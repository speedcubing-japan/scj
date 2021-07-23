from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from app.views.competition.base import Base
from app.models import Round, FeePerEvent, FeePerEventCount


class Publish(LoginRequiredMixin, Base):
    def get(self, request, **kwargs):
        return redirect("competition_detail", name_id=self.name_id)

    def post(self, request, **kwargs):
        # 理事のみ公開できる
        if not request.user.is_superuser:
            return redirect("competition_detail", name_id=self.name_id)

        is_round_exists = Round.objects.filter(
            competition_id=self.competition.id
        ).exists()
        is_fee_exists = (
            FeePerEvent.objects.filter(competition_id=self.competition.id).exists()
            or FeePerEventCount.objects.filter(
                competition_id=self.competition.id
            ).exists()
        )
        if not is_round_exists or not is_fee_exists:
            request.session["competition_admin_errors"] = set(
                "round、feepereventまたはfeepereventcountデータが不足しているため公開に変更できません。"
            )
            return redirect("competition_detail", name_id=self.name_id)

        self.competition.publish()

        return redirect("competition_detail", name_id=self.name_id)
