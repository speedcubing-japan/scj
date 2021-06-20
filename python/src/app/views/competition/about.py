from django.views.generic import TemplateView


class About(TemplateView):
    template_name = 'app/competition/about.html'