from django.contrib.auth.views import LogoutView


class Logout(LogoutView):
    template_name = "app/index.html"
