from django.views.generic import TemplateView


class PublicAnnouncement(TemplateView):
    template_name = 'app/scj/public_announcement.html'