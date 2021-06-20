from django.views.generic import TemplateView


class PostingRequest(TemplateView):
    template_name = 'app/community/posting_request.html'