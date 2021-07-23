from django.views.generic import TemplateView


class About(TemplateView):
    template_name = "app/scj/about.html"
