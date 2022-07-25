from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from app.views.util.decorator import superuser_required


@method_decorator(superuser_required("index"), name="dispatch")
class AdminBase(LoginRequiredMixin, TemplateView):
    pass
