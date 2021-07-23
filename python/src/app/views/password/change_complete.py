from django.shortcuts import redirect
from django.views.generic import View
from app.defines.session import Notification


class ChangeComplete(View):
    def get(self, request):
        self.request.session["notification"] = Notification.PASSWORD_CHANGE
        return redirect("index")
