from app.forms import LoginForm
from django.contrib.auth.views import LoginView


class Login(LoginView):
    template_name = "app/entrance/login.html"
    form_class = LoginForm