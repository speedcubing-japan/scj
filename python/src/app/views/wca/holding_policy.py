from django.views.generic import TemplateView


class HoldingPolicy(TemplateView):
    template_name = 'app/wca/holding_policy.html'