from django.urls import reverse_lazy
from app.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView
from app.defines.session import Notification


class ResetComplete(PasswordResetConfirmView):
    success_url = reverse_lazy('index')
    template_name = 'app/password/reset_complete.html'
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session['notification'] = Notification.PASSWORD_CHANGE
        return context
