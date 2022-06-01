from django.shortcuts import redirect
from django.views.generic import View
from app.defines.session import Notification
from app.models.person import Person

class ChangeComplete(View):
    def get(self, request):

        self.request.session["notification"] = Notification.NAME_CHANGE
        return redirect("index")
