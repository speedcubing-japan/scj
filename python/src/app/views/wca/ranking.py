from django.views.generic import TemplateView


class Ranking(TemplateView):
    template_name = 'app/wca/ranking.html'