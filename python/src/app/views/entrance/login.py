from app.forms import LoginForm
from django.contrib.auth.views import LoginView


class Login(LoginView):
    template_name = 'app/auth/login.html'
    form_class = LoginForm