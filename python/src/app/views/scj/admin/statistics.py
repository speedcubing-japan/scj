from django.views.generic import TemplateView
from .admin_base import AdminBase


class AdminStatistics(AdminBase, TemplateView):
    template_name = "app/scj/admin/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
