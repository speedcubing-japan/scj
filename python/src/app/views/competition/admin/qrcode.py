from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Competitor
from app.defines.competitor import ReceptionStatus
from app.views.competition.base import Base
from app.defines.session import Notification
from app.forms import ReceptionForm
from PIL import Image
import qrcode
import base64
from io import BytesIO
import hashlib
from datetime import timezone, timedelta


class QRCode(LoginRequiredMixin, Base):
    template_name = "app/competition/admin/qrcode.html"

    def get(self, request, **kwargs):
        encoded = f"{str(self.competition.id) + self.competition.name_id}".encode()
        competition_serial = hashlib.md5(encoded).hexdigest()
        img = qrcode.make(
            f"https://{request.get_host()}/competition/{self.competition.name_id}/reception/{competition_serial}"
        )
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr = base64.b64encode(buffer.getvalue()).decode().replace("'", "")
        return render(request, self.template_name, self.get_context(qr))

    def get_context(self, qr):
        context = super().get_context()
        tzobj = timezone(timedelta(hours=+9), "JST")
        context["qr"] = qr
        context["date"] = self.competition.open_at.astimezone(tzobj).strftime(
            "%Y/%m/%d"
        )
        return context
