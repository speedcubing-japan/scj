from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from app.forms import PasswordChangeForm


class Change(PasswordChangeView):
    template_name = 'app/password/change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_complete')