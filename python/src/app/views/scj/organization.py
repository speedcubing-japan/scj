from django.views.generic import TemplateView


class Organization(TemplateView):
    template_name = "app/scj/organization.html"
