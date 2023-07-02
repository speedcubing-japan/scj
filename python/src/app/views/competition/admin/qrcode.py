from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from app.views.competition.base import Base
from datetime import timezone, timedelta


class QRCode(LoginRequiredMixin, Base):
    template_name = "app/competition/admin/qrcode.html"

    def get(self, request, **kwargs):
        reception_page_url = self.competition.get_reception_url(request.get_host())
        qr = self.competition.get_qr_image(reception_page_url)
        return render(request, self.template_name, self.get_context(qr))

    def get_context(self, qr):
        context = super().get_context()
        context["qr"] = qr
        context["date"] = self.competition.open_at.strftime("%Y/%m/%d")
        return context
