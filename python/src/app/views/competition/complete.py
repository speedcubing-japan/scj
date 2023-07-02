from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .base import Base


class Complete(LoginRequiredMixin, Base):
    template_name = "app/competition/complete.html"

    def get(self, request, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        context = super().get_context()
        return context
