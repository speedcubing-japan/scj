from django.views.generic import TemplateView


class ChallengeTour(TemplateView):
    template_name = "app/certificate/challenge_tour.html"
