from django.core.paginator import Paginator
from django.views.generic import TemplateView
from app.models import Person, Information


class Index(TemplateView):
    template_name = 'app/scj/index.html'

    def get_context_data(self):
        PAGE_SIZE = 10

        page = self.request.GET.get(key='page', default=1)

        all_informations = Information.objects \
            .filter(is_public=True) \
            .order_by('updated_at') \
            .reverse()

        pagenator = Paginator(all_informations, PAGE_SIZE)
        informations = pagenator.get_page(page)

        name = ''
        if self.request.user.is_authenticated:
            person = Person.objects \
                .get(user_id=self.request.user.id)
            name = person.first_name + ' ' + person.last_name

        notification = self.request.session.get('notification')
        if self.request.session.get('notification') is not None:
            del self.request.session['notification']

        context = {
            'informations': informations,
            'name': name,
            'notification': notification
        }

        return context