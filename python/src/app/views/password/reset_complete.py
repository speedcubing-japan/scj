from django.urls import reverse_lazy
from app.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView


class ResetComplete(PasswordResetConfirmView):
    success_url = reverse_lazy('index')
    template_name = 'app/auth/password_reset_complete.html'
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session['notification'] = 'is_just_password_reset_complete'
        return context