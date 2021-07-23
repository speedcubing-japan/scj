from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Round, FeePerEvent, FeePerEventCount
from app.views.competition.base import Base


class Delete(LoginRequiredMixin, Base):
    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return redirect("competition_detail", name_id=self.name_id)

        if not self.competition.is_judge(request.user):
            return redirect("competition_detail", name_id=self.name_id)

        if not self.competition.is_private and self.competition.is_display:
            return redirect("competition_detail", name_id=self.name_id)

        self.competition.delete()
        Round.delete(self.competition.id)
        FeePerEvent.delete(self.competition.id)
        FeePerEventCount.delete(self.competition.id)

        return redirect("competition_create")
