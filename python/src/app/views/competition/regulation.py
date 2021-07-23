from django.views.generic import TemplateView


class Regulation(TemplateView):
    template_name = 'app/competition/regulation.html'
