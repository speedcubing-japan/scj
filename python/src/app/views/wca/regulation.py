from django.views.generic import TemplateView


class Regulation(TemplateView):
    template_name = 'app/wca/regulation.html'