from django.shortcuts import redirect
from django.views.generic import View


class ChangeComplete(View):
    def get(self, request):
        self.request.session['notification'] = 'is_just_password_change'
        return redirect('index')