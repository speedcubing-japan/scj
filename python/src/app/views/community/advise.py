from django.views.generic import TemplateView


class Advise(TemplateView):
    template_name = "app/community/advise.html"
