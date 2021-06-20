from django.views.generic import TemplateView


class PrivacyPolicy(TemplateView):
    template_name = 'app/scj/privacy_policy.html'